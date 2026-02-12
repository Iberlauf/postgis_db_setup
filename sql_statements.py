"""SQL statements."""

from typing import TYPE_CHECKING

from sqlalchemy import DDL, text

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

create_z_trigger_function: DDL = DDL("""--sql
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

            -- Try different EGM2008 grid file names
            BEGIN
                -- Attempt 1: Standard EGM2008 grid
                geoid_height := ST_Z(ST_Transform(geom_4979,
                    '+proj=pipeline +step +proj=vgridshift +grids=egm08_25.gtx +multiplier=1'
                ));
                orthometric_height := raster_elevation - geoid_height;
            EXCEPTION WHEN OTHERS THEN
                BEGIN
                    -- Attempt 2: PROJ CDN version
                    geoid_height := ST_Z(ST_Transform(geom_4979,
                        '+proj=pipeline +step +proj=vgridshift +grids=us_nga_egm08_25.tif +multiplier=1'
                    ));
                    orthometric_height := raster_elevation - geoid_height;
                EXCEPTION WHEN OTHERS THEN
                    -- Fallback: Use approximate geoid undulation
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
""")  # noqa: E501

create_z_trigger: DDL = DDL("""--sql
CREATE TRIGGER trg_update_tacka_z
    BEFORE INSERT OR UPDATE OF geometry
    ON tacke
    FOR EACH ROW
    EXECUTE FUNCTION update_tacka_z();
""")

drop_z_trigger: DDL = DDL("""--sql
DROP TRIGGER IF EXISTS trg_update_tacka_z ON tacke;
DROP FUNCTION IF EXISTS update_tacka_z();
""")


if __name__ == "__main__":
    ...
