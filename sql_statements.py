"""SQL statements."""

from typing import TYPE_CHECKING

from sqlalchemy import DDL, event, text
from sqlalchemy.sql.schema import Table  # noqa: TC002
from sqlmodel import SQLModel

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

first_sql_statements: list[TextClause] = []
first_sql_statements.append(enable_out_db)
first_sql_statements.append(enable_gdal_driver)
first_sql_statements.append(gdal_vsi_options)

insert_epsg_3855: TextClause = text(
    text="""--sql
INSERT INTO spatial_ref_sys (srid, auth_name, auth_srid, proj4text, srtext)
VALUES (
    3855,
    'EPSG',
    3855,
    '+vunits=m +no_defs +type=crs',
    'VERT_CS["EGM2008 height",'
    'VERT_DATUM["EGM2008 geoid",2005,AUTHORITY["EPSG","1027"]],'
    'UNIT["metre",1,AUTHORITY["EPSG","9001"]],'
    'AXIS["Gravity-related height",UP],'
    'AUTHORITY["EPSG","3855"]]'
)
ON CONFLICT (srid) DO NOTHING;
""",
)

create_z_trigger_function: DDL = DDL(
    statement="""--sql
CREATE OR REPLACE FUNCTION update_tacka_z()
RETURNS TRIGGER AS $$
DECLARE
    geom_4326 geometry;
    geom_4979 geometry;
    raster_elevation double precision;
    orthometric_height double precision;
    geoid_height double precision;
BEGIN
    IF NEW.geometry IS NOT NULL THEN
        geom_4326 := ST_Transform(NEW.geometry, 4326);

        SELECT ST_Value(rast, geom_4326)::double precision
        INTO raster_elevation
        FROM dsm_rasteri
        WHERE ST_Intersects(rast, geom_4326)
        LIMIT 1;

        IF raster_elevation IS NOT NULL THEN
            geom_4979 := ST_SetSRID(
                ST_MakePoint(ST_X(geom_4326), ST_Y(geom_4326), raster_elevation),
                4979
            );

            BEGIN
                geoid_height := ST_Z(ST_Transform(geom_4979,
                    '+proj=pipeline +step +proj=vgridshift +grids=egm08_25.gtx +multiplier=1'
                ));
                orthometric_height := raster_elevation - geoid_height;
            EXCEPTION WHEN OTHERS THEN
                BEGIN
                    geoid_height := ST_Z(ST_Transform(geom_4979,
                        '+proj=pipeline +step +proj=vgridshift +grids=us_nga_egm08_25.tif +multiplier=1'
                    ));
                    orthometric_height := raster_elevation - geoid_height;
                EXCEPTION WHEN OTHERS THEN
                    RAISE WARNING 'EGM2008 grids not found. Using approximate value. Error: %%', SQLERRM;
                    orthometric_height := raster_elevation - 43.0;
                END;
            END;

            NEW.z := ROUND(orthometric_height::numeric, 3);
        ELSE
            NEW.z := 0.0;
        END IF;
    ELSE
        NEW.z := 0.0;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
""",  # noqa: E501
)

create_z_trigger: DDL = DDL(
    statement="""--sql
CREATE TRIGGER trg_update_tacka_z
    BEFORE INSERT OR UPDATE OF geometry
    ON tacke
    FOR EACH ROW
    EXECUTE FUNCTION update_tacka_z();
""",
)

drop_z_trigger: DDL = DDL(
    statement="""--sql
DROP TRIGGER IF EXISTS trg_update_tacka_z ON tacke;
DROP FUNCTION IF EXISTS update_tacka_z();
""",
)

create_total_mag_trigger_function: DDL = DDL(
    statement="""--sql
CREATE OR REPLACE FUNCTION update_project_mag_area()
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'INSERT' OR TG_OP = 'UPDATE') THEN
        UPDATE projekti
        SET total_pov_mag = (
            SELECT COALESCE(SUM(ST_Area(ST_MakeValid(geometry))), 0)
            FROM polja_mag
            WHERE projekat_id = NEW.projekat_id
        )
        WHERE projekat_id = NEW.projekat_id;
    END IF;

    IF (TG_OP = 'DELETE' OR (TG_OP = 'UPDATE' AND OLD.projekat_id != NEW.projekat_id)) THEN
        UPDATE projekti
        SET total_pov_mag = (
            SELECT COALESCE(SUM(ST_Area(ST_MakeValid(geometry))), 0)
            FROM polja_mag
            WHERE projekat_id = OLD.projekat_id
        )
        WHERE projekat_id = OLD.projekat_id;
    END IF;

    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;
""",  # noqa: E501
)

create_total_mag_trigger: DDL = DDL(
    statement="""--sql
CREATE TRIGGER trg_update_project_mag_area
AFTER INSERT OR UPDATE OR DELETE ON polja_mag
FOR EACH ROW
EXECUTE FUNCTION update_project_mag_area();
""",
)

create_total_gpr_trigger_function: DDL = DDL(
    statement="""--sql
CREATE OR REPLACE FUNCTION update_project_gpr_area()
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'INSERT' OR TG_OP = 'UPDATE') THEN
        UPDATE projekti
        SET total_pov_gpr = (
            SELECT COALESCE(SUM(ST_Area(ST_MakeValid(geometry))), 0)
            FROM polja_gpr
            WHERE projekat_id = NEW.projekat_id
        )
        WHERE projekat_id = NEW.projekat_id;
    END IF;

    IF (TG_OP = 'DELETE' OR (TG_OP = 'UPDATE' AND OLD.projekat_id != NEW.projekat_id)) THEN
        UPDATE projekti
        SET total_pov_gpr = (
            SELECT COALESCE(SUM(ST_Area(ST_MakeValid(geometry))), 0)
            FROM polja_gpr
            WHERE projekat_id = OLD.projekat_id
        )
        WHERE projekat_id = OLD.projekat_id;
    END IF;

    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;
""",  # noqa: E501
)

create_total_gpr_trigger: DDL = DDL(
    statement="""--sql
CREATE TRIGGER trg_update_project_gpr_area
AFTER INSERT OR UPDATE OR DELETE ON polja_gpr
FOR EACH ROW
EXECUTE FUNCTION update_project_gpr_area();
""",
)

create_trigger_function_all_unique: DDL = DDL(
    statement="""--sql
CREATE OR REPLACE FUNCTION check_pogresni_redovi_unique()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.pogresni_redovi IS NOT NULL THEN
        IF array_length(NEW.pogresni_redovi, 1) !=
           (SELECT COUNT(DISTINCT val) FROM unnest(NEW.pogresni_redovi) AS val) THEN
            RAISE EXCEPTION 'Kolona pogresni_redovi mora sadržati samo jedinstvene unose';
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
""",  # noqa: E501
)

create_trigger_all_unique: DDL = DDL(
    statement="""--sql
CREATE TRIGGER trg_check_pogresni_redovi_unique
BEFORE INSERT OR UPDATE ON polja_mag
FOR EACH ROW
EXECUTE FUNCTION check_pogresni_redovi_unique();
""",
)

trigger_check_proizvodjac: DDL = DDL(
    statement="""--sql
CREATE OR REPLACE FUNCTION check_gpr_antena_proizvodjac()
RETURNS TRIGGER AS $$
DECLARE
    v_gpr_proizvodjac_id INT;
    v_antena_proizvodjac_id INT;
BEGIN
    IF NEW.gpr_id IS NULL OR NEW.antena_id IS NULL THEN
        RETURN NEW;
    END IF;
    SELECT gpr_proizvodjac_id INTO v_gpr_proizvodjac_id
    FROM georadari
    WHERE gpr_id = NEW.gpr_id;
    SELECT antena_proizvodjac_id INTO v_antena_proizvodjac_id
    FROM antene
    WHERE antena_id = NEW.antena_id;
    IF v_gpr_proizvodjac_id IS DISTINCT FROM v_antena_proizvodjac_id THEN
        RAISE EXCEPTION 'Georadar (ID: %%) i antena (ID: %%) moraju biti od istog proizvođača',
            NEW.gpr_id, NEW.antena_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_check_gpr_antena_proizvodjac
BEFORE INSERT OR UPDATE OF gpr_id, antena_id ON polja_gpr
FOR EACH ROW EXECUTE FUNCTION check_gpr_antena_proizvodjac();
""",  # noqa: E501
)


calculate_non_overlaping_area: DDL = DDL(
    statement="""--sql
CREATE OR REPLACE FUNCTION calculate_non_overlapping_area(
    p_projekat_id INTEGER,
    p_datum DATE,
    p_table_name TEXT
) RETURNS NUMERIC AS $$
DECLARE
    v_total_area NUMERIC;
    v_previous_union geometry;
BEGIN
    EXECUTE format(
        'SELECT ST_UnaryUnion(ST_Collect(ST_MakeValid(geometry)))
         FROM %%I
         WHERE projekat_id = $1 AND datum < $2',
        p_table_name
    ) INTO v_previous_union
    USING p_projekat_id, p_datum;

    IF v_previous_union IS NOT NULL THEN
        EXECUTE format(
            'SELECT COALESCE(
                ROUND(
                    ST_Area(
                        ST_UnaryUnion(
                            ST_Collect(
                                ST_Difference(ST_MakeValid(geometry), $1)
                            )
                        )
                    )::numeric,
                    3
                ),
                0
            )
            FROM %%I
            WHERE projekat_id = $2 AND datum = $3',
            p_table_name
        ) INTO v_total_area
        USING v_previous_union, p_projekat_id, p_datum;
    ELSE
        EXECUTE format(
            'SELECT COALESCE(
                ROUND(
                    ST_Area(
                        ST_UnaryUnion(ST_Collect(ST_MakeValid(geometry)))
                    )::numeric,
                    3
                ),
                0
            )
            FROM %%I
            WHERE projekat_id = $1 AND datum = $2',
            p_table_name
        ) INTO v_total_area
        USING p_projekat_id, p_datum;
    END IF;

    RETURN COALESCE(v_total_area, 0);
END;
$$ LANGUAGE plpgsql;
""",
)

update_povrsine_function: DDL = DDL(
    statement="""--sql
CREATE OR REPLACE FUNCTION update_povrsine_po_datumu()
RETURNS TRIGGER AS $$
DECLARE
    v_projekat_id INTEGER;
    v_datum DATE;
    v_area_mag NUMERIC;
    v_area_gpr NUMERIC;
BEGIN
    IF (TG_OP = 'INSERT' OR TG_OP = 'UPDATE') THEN
        v_projekat_id := NEW.projekat_id;
        v_datum := NEW.datum;
    ELSIF (TG_OP = 'DELETE') THEN
        v_projekat_id := OLD.projekat_id;
        v_datum := OLD.datum;
    END IF;

    v_area_mag := calculate_non_overlapping_area(
        v_projekat_id,
        v_datum,
        'polja_mag'
    );

    v_area_gpr := calculate_non_overlapping_area(
        v_projekat_id,
        v_datum,
        'polja_gpr'
    );

    INSERT INTO povrsine_po_datumu (projekat_id, datum, pov_mag, pov_gpr)
    VALUES (v_projekat_id, v_datum, v_area_mag, v_area_gpr)
    ON CONFLICT (projekat_id, datum)
    DO UPDATE SET
        pov_mag = EXCLUDED.pov_mag,
        pov_gpr = EXCLUDED.pov_gpr;

    IF (TG_OP = 'UPDATE' OR TG_OP = 'DELETE') THEN
        UPDATE povrsine_po_datumu ppd
        SET
            pov_mag = calculate_non_overlapping_area(ppd.projekat_id, ppd.datum, 'polja_mag'),
            pov_gpr = calculate_non_overlapping_area(ppd.projekat_id, ppd.datum, 'polja_gpr')
        WHERE ppd.projekat_id = v_projekat_id
        AND ppd.datum > v_datum;
    END IF;

    IF (TG_OP = 'DELETE') THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;
""",  # noqa: E501
)

drop_trigger_polja_mag: DDL = DDL(
    statement="""--sql
DROP TRIGGER IF EXISTS trg_polja_mag_update_povrsine ON polja_mag;
""",
)

drop_trigger_polja_gpr: DDL = DDL(
    statement="""--sql
DROP TRIGGER IF EXISTS trg_polja_gpr_update_povrsine ON polja_gpr;
""",
)

create_trigger_polja_mag: DDL = DDL(
    statement="""--sql
CREATE TRIGGER trg_polja_mag_update_povrsine
    AFTER INSERT OR UPDATE OR DELETE ON polja_mag
    FOR EACH ROW
    EXECUTE FUNCTION update_povrsine_po_datumu();
""",
)

create_trigger_polja_gpr: DDL = DDL(
    statement="""--sql
CREATE TRIGGER trg_polja_gpr_update_povrsine
    AFTER INSERT OR UPDATE OR DELETE ON polja_gpr
    FOR EACH ROW
    EXECUTE FUNCTION update_povrsine_po_datumu();
""",
)


def register_triggers() -> None:
    """Register all database triggers."""
    tacke_table: Table = SQLModel.metadata.tables["tacke"]
    polja_mag_table: Table = SQLModel.metadata.tables["polja_mag"]
    polja_gpr_table: Table = SQLModel.metadata.tables["polja_gpr"]
    projekti_table: Table = SQLModel.metadata.tables["projekti"]  # noqa: F841
    povrsine_po_datumu: Table = SQLModel.metadata.tables["povrsine_po_datumu"]

    event.listen(
        target=tacke_table,
        identifier="after_create",
        fn=create_z_trigger_function.execute_if(dialect="postgresql"),
    )
    event.listen(
        target=tacke_table,
        identifier="after_create",
        fn=create_z_trigger.execute_if(dialect="postgresql"),
    )

    event.listen(
        target=polja_mag_table,
        identifier="after_create",
        fn=create_trigger_function_all_unique.execute_if(dialect="postgresql"),
    )
    event.listen(
        target=polja_mag_table,
        identifier="after_create",
        fn=create_trigger_all_unique.execute_if(dialect="postgresql"),
    )

    event.listen(
        target=polja_mag_table,
        identifier="after_create",
        fn=create_total_mag_trigger_function.execute_if(dialect="postgresql"),
    )
    event.listen(
        target=polja_mag_table,
        identifier="after_create",
        fn=create_total_mag_trigger.execute_if(dialect="postgresql"),
    )

    event.listen(
        target=polja_gpr_table,
        identifier="after_create",
        fn=trigger_check_proizvodjac.execute_if(dialect="postgresql"),
    )

    event.listen(
        target=polja_gpr_table,
        identifier="after_create",
        fn=create_total_gpr_trigger_function.execute_if(dialect="postgresql"),
    )
    event.listen(
        target=polja_gpr_table,
        identifier="after_create",
        fn=create_total_gpr_trigger.execute_if(dialect="postgresql"),
    )

    event.listen(
        target=povrsine_po_datumu,
        identifier="after_create",
        fn=calculate_non_overlaping_area.execute_if(dialect="postgresql"),
    )

    event.listen(
        target=povrsine_po_datumu,
        identifier="after_create",
        fn=update_povrsine_function.execute_if(dialect="postgresql"),
    )

    event.listen(
        target=povrsine_po_datumu,
        identifier="after_create",
        fn=drop_trigger_polja_mag.execute_if(dialect="postgresql"),
    )

    event.listen(
        target=povrsine_po_datumu,
        identifier="after_create",
        fn=drop_trigger_polja_gpr.execute_if(dialect="postgresql"),
    )

    event.listen(
        target=povrsine_po_datumu,
        identifier="after_create",
        fn=create_trigger_polja_mag.execute_if(dialect="postgresql"),
    )

    event.listen(
        target=povrsine_po_datumu,
        identifier="after_create",
        fn=create_trigger_polja_gpr.execute_if(dialect="postgresql"),
    )


if __name__ == "__main__":
    ...
