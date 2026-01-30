"""SQL statements."""

from typing import TYPE_CHECKING

from sqlalchemy import Engine, text

if TYPE_CHECKING:
    from sqlalchemy.sql.elements import TextClause

enable_out_db: TextClause = text(
    text="""--sql
        ALTER DATABASE geofizika_test
        SET postgis.enable_outdb_rasters = true;
        """,
)
enable_gdal_driver: TextClause = text(
    text="""--sql
        ALTER DATABASE geofizika_test
        SET postgis.gdal_enabled_drivers TO 'ENABLE_ALL';
        """,
)
gdal_vsi_options: TextClause = text(
    text="""--sql
        ALTER DATABASE geofizika_test
        SET postgis.gdal_vsi_options = 'CPL_VSIL_CURL_ALLOWED_EXTENSIONS=.tif';
        """,
)
sql_statements: list[TextClause] = []
sql_statements.append(enable_out_db)
sql_statements.append(enable_gdal_driver)
sql_statements.append(gdal_vsi_options)

# inline-sql: disable
SYNC_TRIGGER_SQL: TextClause = text(
    text="""--sql
    CREATE OR REPLACE FUNCTION public.sync_coords_to_geometry()
    RETURNS TRIGGER AS $$
    BEGIN
        -- Case 1: INSERT - geometry is null but coordinates exist
        IF TG_OP = 'INSERT' THEN
            IF NEW.geometry IS NULL AND NEW.x IS NOT NULL AND NEW.y IS NOT NULL AND NEW.z IS NOT NULL THEN
                NEW.geometry := ST_SetSRID(ST_MakePoint(NEW.x, NEW.y, NEW.z), 6316);
            ELSIF NEW.geometry IS NOT NULL AND (NEW.x IS NULL OR NEW.y IS NULL OR NEW.z IS NULL) THEN
                NEW.x := ROUND(ST_X(NEW.geometry)::numeric, 3);
                NEW.y := ROUND(ST_Y(NEW.geometry)::numeric, 3);
                NEW.z := ROUND(ST_Z(NEW.geometry)::numeric, 3);
            END IF;
        END IF;

        -- Case 2: UPDATE - check what changed to avoid infinite loop
        IF TG_OP = 'UPDATE' THEN
            -- Coordinates changed but geometry didn't - update geometry from coordinates
            IF (OLD.x IS DISTINCT FROM NEW.x OR OLD.y IS DISTINCT FROM NEW.y OR OLD.z IS DISTINCT FROM NEW.z)
               AND OLD.geometry IS NOT DISTINCT FROM NEW.geometry THEN
                IF NEW.x IS NOT NULL AND NEW.y IS NOT NULL AND NEW.z IS NOT NULL THEN
                    NEW.geometry := ST_SetSRID(ST_MakePoint(NEW.x, NEW.y, NEW.z), 6316);
                END IF;
            -- Geometry changed but coordinates didn't - update coordinates from geometry
            ELSIF OLD.geometry IS DISTINCT FROM NEW.geometry
                  AND OLD.x IS NOT DISTINCT FROM NEW.x
                  AND OLD.y IS NOT DISTINCT FROM NEW.y
                  AND OLD.z IS NOT DISTINCT FROM NEW.z THEN
                IF NEW.geometry IS NOT NULL THEN
                    NEW.x := ROUND(ST_X(NEW.geometry)::numeric, 3);
                    NEW.y := ROUND(ST_Y(NEW.geometry)::numeric, 3);
                    NEW.z := ROUND(ST_Z(NEW.geometry)::numeric, 3);
                END IF;
            END IF;
        END IF;

        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS sync_tacke_geometry ON public.tacke;
CREATE TRIGGER sync_tacke_geometry
    BEFORE INSERT OR UPDATE ON public.tacke
    FOR EACH ROW
    EXECUTE FUNCTION public.sync_coords_to_geometry();
    """,  # noqa: E501
)

POPULATE_Z_TRIGGER_SQL: TextClause = text(
    text="""--sql
    CREATE OR REPLACE FUNCTION public.populate_z_from_dsm()
    RETURNS TRIGGER AS $$
    DECLARE
        sampled_z_ellipsoidal double precision;
        sampled_z_orthometric double precision;
        geom_4326 geometry;
        geom_6316_3d geometry;
        point_x double precision;
        point_y double precision;
    BEGIN
        -- Only populate Z if not explicitly provided
        IF NEW.z IS NULL AND NEW.geometry IS NOT NULL THEN

            -- Extract X and Y from geometry if not set in columns yet
            point_x := COALESCE(NEW.x, ROUND(ST_X(NEW.geometry)::numeric, 3));
            point_y := COALESCE(NEW.y, ROUND(ST_Y(NEW.geometry)::numeric, 3));

            -- Transform geometry to EPSG:4326 to match raster CRS (force 2D for raster sampling)
            geom_4326 := ST_Force2D(ST_Transform(NEW.geometry, 4326));

            -- Sample elevation from raster (ellipsoidal height in EPSG:4326)
            SELECT
                ST_Value(r.rast, 1, geom_4326, TRUE)::double precision
            INTO sampled_z_ellipsoidal
            FROM public.dsm_rasteri r
            WHERE
                ST_Intersects(r.rast, geom_4326)
                AND ST_Value(r.rast, 1, geom_4326, TRUE) IS NOT NULL
            ORDER BY ST_Area(ST_ConvexHull(r.rast)) ASC
            LIMIT 1;

            IF sampled_z_ellipsoidal IS NOT NULL THEN
                -- Create 3D point with ellipsoidal height in EPSG:4326
                geom_4326 := ST_SetSRID(
                    ST_MakePoint(
                        ST_X(geom_4326),
                        ST_Y(geom_4326),
                        sampled_z_ellipsoidal
                    ),
                    4326
                );

                -- Transform to EPSG:6316 (applies geoid correction ~40m)
                geom_6316_3d := ST_Transform(geom_4326, 6316);

                -- Extract orthometric height
                sampled_z_orthometric := ROUND(ST_Z(geom_6316_3d)::numeric, 3)::double precision;

                -- Update z column
                NEW.z := sampled_z_orthometric;

                -- Update geometry with the correct 3D coordinates
                NEW.geometry := ST_SetSRID(
                    ST_MakePoint(
                        point_x,
                        point_y,
                        sampled_z_orthometric
                    ),
                    6316
                );

            ELSE
                RAISE NOTICE
                    'Trigger % on table %: No DSM value found for geometry (tacka_id=%)',
                    TG_NAME,
                    TG_TABLE_NAME,
                    NEW.tacka_id;
            END IF;

        END IF;

        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    DROP TRIGGER IF EXISTS trg_populate_z_from_dsm ON public.tacke;

    CREATE TRIGGER trg_populate_z_from_dsm
    BEFORE INSERT OR UPDATE
    ON public.tacke
    FOR EACH ROW
    EXECUTE FUNCTION public.populate_z_from_dsm();
    """,  # noqa: E501
)

SORT_TRIGGERS: TextClause = text(
    text="""--sql
    -- Drop both triggers
    DROP TRIGGER IF EXISTS sync_tacke_geometry ON public.tacke;
    DROP TRIGGER IF EXISTS trg_populate_z_from_dsm ON public.tacke;

    -- Recreate sync trigger FIRST (runs first alphabetically or by creation order)
    CREATE TRIGGER sync_tacke_geometry
        BEFORE INSERT OR UPDATE ON public.tacke
        FOR EACH ROW
        EXECUTE FUNCTION public.sync_coords_to_geometry();

    -- Recreate DSM trigger SECOND (runs after sync)
    CREATE TRIGGER trg_populate_z_from_dsm
        BEFORE INSERT OR UPDATE
        ON public.tacke
        FOR EACH ROW
        EXECUTE FUNCTION public.populate_z_from_dsm();
    """,
)


def apply_sql_config(engine: Engine, statements: list[TextClause]) -> None:
    """Apply SQL config.

    Args:
        engine (Engine): Engine
        statements(list[TextClause]): SQL statements.

    """
    with engine.connect() as conn:
        for stmnt in statements:
            conn.execute(statement=stmnt)
            conn.commit()


def add_sync_trigger(
    engine: Engine,
    trigger: TextClause = SYNC_TRIGGER_SQL,
) -> None:
    """Add sync trigger.

    Args:
        engine (Engine): Engine.
        trigger (TextClause): Trigger. Defaults to SYNC_TRIGGER_SQL.

    """
    with engine.connect() as conn:
        conn.execute(statement=trigger)
        conn.commit()


def populate_z_from_dsm(
    engine: Engine,
    trigger: TextClause = POPULATE_Z_TRIGGER_SQL,
) -> None:
    """Populate z from DSM.

    Args:
        engine (Engine): Engine
        trigger (TextClause, optional): Trigger. Defaults to POPULATE_Z_TRIGGER_SQL.

    """
    with engine.connect() as conn:
        conn.execute(statement=trigger)
        conn.commit()


def sort_triggers(
    engine: Engine,
    statement: TextClause = SORT_TRIGGERS,
) -> None:
    """Sort triggers.

    Args:
        engine (Engine): Engine
        statement (TextClause): SQL statement Defaults to SORT_TRIGGERS.

    """
    with engine.connect() as conn:
        conn.execute(statement=statement)
        conn.commit()
