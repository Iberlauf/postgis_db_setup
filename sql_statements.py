"""SQL statements."""

from sqlalchemy import DDL, Engine, event, text
from sqlalchemy.sql.elements import TextClause
from sqlalchemy.sql.schema import Table
from sqlmodel import SQLModel

from config import settings
from defaults import srid

enable_out_db: TextClause = text(
    text=f"""--sql
ALTER DATABASE {settings.postgis_db_name}
SET postgis.enable_outdb_rasters = true;
""",
)
enable_gdal_driver: TextClause = text(
    text=f"""--sql
ALTER DATABASE {settings.postgis_db_name}
SET postgis.gdal_enabled_drivers TO 'ENABLE_ALL';
""",
)
gdal_vsi_options: TextClause = text(
    text=f"""--sql
ALTER DATABASE {settings.postgis_db_name}
SET postgis.gdal_vsi_options = 'CPL_VSIL_CURL_ALLOWED_EXTENSIONS=.tif';
""",
)

first_sql_statements: list[TextClause] = []
first_sql_statements.append(enable_out_db)
first_sql_statements.append(enable_gdal_driver)
first_sql_statements.append(gdal_vsi_options)

create_z_trigger_function: DDL = DDL(
    statement="""--sql
DROP TRIGGER IF EXISTS trg_update_tacka_z ON tacke;
DROP FUNCTION IF EXISTS update_tacka_z() CASCADE;
CREATE OR REPLACE FUNCTION update_tacka_z()
RETURNS TRIGGER AS $$
DECLARE
    raster_elevation double precision;
    orthometric_height double precision;
    geoid_height double precision;
    geom_4326 geometry;
    geom_4979 geometry;
BEGIN
    IF NEW.geom IS NOT NULL THEN
        geom_4326 := ST_Transform(NEW.geom, 4326);
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
                    RAISE WARNING 'EGM2008 grid nije u bazi podataka. Približna vrednost će biti korišćena. Error: %%', SQLERRM;
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
BEFORE INSERT OR UPDATE OF geom
ON tacke
FOR EACH ROW
EXECUTE FUNCTION update_tacka_z();
""",
)

create_total_mag_trigger_function: DDL = DDL(
    statement="""--sql
DROP TRIGGER IF EXISTS trg_update_project_mag_area ON polja_mag;
DROP FUNCTION IF EXISTS update_project_mag_area() CASCADE;
CREATE OR REPLACE FUNCTION update_project_mag_area()
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'INSERT' OR TG_OP = 'UPDATE') THEN
        UPDATE projekti
        SET total_pov_mag = (
            SELECT COALESCE(SUM(ST_Area(geom)), 0)
            FROM polja_mag
            WHERE projekat_id = NEW.projekat_id
        )
        WHERE projekat_id = NEW.projekat_id;
    END IF;
    IF (TG_OP = 'DELETE' OR (TG_OP = 'UPDATE' AND OLD.projekat_id != NEW.projekat_id)) THEN
        UPDATE projekti
        SET total_pov_mag = (
            SELECT COALESCE(SUM(ST_Area(geom)), 0)
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
DROP TRIGGER IF EXISTS trg_update_project_gpr_area ON polja_gpr;
DROP FUNCTION IF EXISTS update_project_gpr_area() CASCADE;
CREATE OR REPLACE FUNCTION update_project_gpr_area()
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'INSERT' OR TG_OP = 'UPDATE') THEN
        UPDATE projekti
        SET total_pov_gpr = (
            SELECT COALESCE(SUM(ST_Area(geom)), 0)
            FROM polja_gpr
            WHERE projekat_id = NEW.projekat_id
        )
        WHERE projekat_id = NEW.projekat_id;
    END IF;
    IF (TG_OP = 'DELETE' OR (TG_OP = 'UPDATE' AND OLD.projekat_id != NEW.projekat_id)) THEN
        UPDATE projekti
        SET total_pov_gpr = (
            SELECT COALESCE(SUM(ST_Area(geom)), 0)
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

create_total_elektrika_trigger_function: DDL = DDL(
    statement="""--sql
DROP TRIGGER IF EXISTS trg_update_project_elektrika_area ON polja_elektrika;
DROP FUNCTION IF EXISTS update_project_elektrika_area() CASCADE;
CREATE OR REPLACE FUNCTION update_project_elektrika_area()
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'INSERT' OR TG_OP = 'UPDATE') THEN
        UPDATE projekti
        SET total_pov_elektrika = (
            SELECT COALESCE(SUM(ST_Area(geom)), 0)
            FROM polja_elektrika
            WHERE projekat_id = NEW.projekat_id
        )
        WHERE projekat_id = NEW.projekat_id;
    END IF;
    IF (TG_OP = 'DELETE' OR (TG_OP = 'UPDATE' AND OLD.projekat_id != NEW.projekat_id)) THEN
        UPDATE projekti
        SET total_pov_elektrika = (
            SELECT COALESCE(SUM(ST_Area(geom)), 0)
            FROM polja_elektrika
            WHERE projekat_id = OLD.projekat_id
        )
        WHERE projekat_id = OLD.projekat_id;
    END IF;
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;
""",  # noqa: E501
)

create_total_elektrika_trigger: DDL = DDL(
    statement="""--sql
CREATE TRIGGER trg_update_project_elektrika_area
AFTER INSERT OR UPDATE OR DELETE ON polja_elektrika
FOR EACH ROW
EXECUTE FUNCTION update_project_elektrika_area();
""",
)

create_total_profajler_trigger_function: DDL = DDL(
    statement="""--sql
DROP TRIGGER IF EXISTS trg_update_project_profajler_area ON polja_profajler;
DROP FUNCTION IF EXISTS update_project_profajler_area() CASCADE;
CREATE OR REPLACE FUNCTION update_project_profajler_area()
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'INSERT' OR TG_OP = 'UPDATE') THEN
        UPDATE projekti
        SET total_pov_profajler = (
            SELECT COALESCE(SUM(ST_Area(geom)), 0)
            FROM polja_profajler
            WHERE projekat_id = NEW.projekat_id
        )
        WHERE projekat_id = NEW.projekat_id;
    END IF;
    IF (TG_OP = 'DELETE' OR (TG_OP = 'UPDATE' AND OLD.projekat_id != NEW.projekat_id)) THEN
        UPDATE projekti
        SET total_pov_elektrika = (
            SELECT COALESCE(SUM(ST_Area(geom)), 0)
            FROM polja_profajler
            WHERE projekat_id = OLD.projekat_id
        )
        WHERE projekat_id = OLD.projekat_id;
    END IF;
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;
""",  # noqa: E501
)

create_total_profajler_trigger: DDL = DDL(
    statement="""--sql
CREATE TRIGGER trg_update_project_profajler_area
AFTER INSERT OR UPDATE OR DELETE ON polja_profajler
FOR EACH ROW
EXECUTE FUNCTION update_project_profajler_area();
""",
)

trigger_check_proizvodjac: DDL = DDL(
    statement="""--sql
DROP TRIGGER IF EXISTS trigger_check_gpr_antena_proizvodjac ON polja_gpr;
DROP FUNCTION IF EXISTS check_gpr_antena_proizvodjac() CASCADE;
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

calculate_non_overlapping_area: DDL = DDL(
    statement="""--sql
DROP FUNCTION IF EXISTS calculate_non_overlapping_area(INTEGER, DATE, TEXT) CASCADE;
CREATE OR REPLACE FUNCTION calculate_non_overlapping_area(
    p_projekat_id INTEGER,
    p_datum       DATE,
    p_table_name  TEXT
)
RETURNS NUMERIC AS $$
DECLARE
    v_total_area     NUMERIC;
    v_previous_union GEOMETRY;
BEGIN
    EXECUTE format(
        'SELECT ST_UnaryUnion(ST_Collect(geom))
         FROM %%I
         WHERE projekat_id = $1
           AND datum < $2',
        p_table_name
    )
    INTO v_previous_union
    USING p_projekat_id, p_datum;

    IF v_previous_union IS NOT NULL THEN

        EXECUTE format(
            'SELECT COALESCE(
                ROUND(
                    ST_Area(
                        ST_UnaryUnion(
                            ST_Collect(
                                ST_Difference(geom, $1)
                            )
                        )
                    )::NUMERIC,
                    3
                ),
                0
            )
            FROM %%I
            WHERE projekat_id = $2
              AND datum = $3',
            p_table_name
        )
        INTO v_total_area
        USING v_previous_union, p_projekat_id, p_datum;
    ELSE
        EXECUTE format(
            'SELECT COALESCE(
                ROUND(
                    ST_Area(
                        ST_UnaryUnion(ST_Collect(geom))
                    )::NUMERIC,
                    3
                ),
                0
            )
            FROM %%I
            WHERE projekat_id = $1
              AND datum = $2',
            p_table_name
        )
        INTO v_total_area
        USING p_projekat_id, p_datum;
    END IF;
    RETURN COALESCE(v_total_area, 0);
END;
$$ LANGUAGE plpgsql;
""",
)

update_povrsine_function: DDL = DDL(
    statement="""--sql
DROP FUNCTION IF EXISTS update_povrsine_po_datumu() CASCADE;
CREATE OR REPLACE FUNCTION update_povrsine_po_datumu()
RETURNS TRIGGER AS $$
DECLARE
    v_projekat_id INTEGER;
    v_datum       DATE;
    v_old_datum   DATE := NULL;
    v_area_mag    NUMERIC;
    v_area_gpr    NUMERIC;
    v_area_elektrika    NUMERIC;
    v_area_profajler    NUMERIC;
BEGIN
    IF (TG_OP = 'INSERT' OR TG_OP = 'UPDATE') THEN
        v_projekat_id := NEW.projekat_id;
        v_datum := NEW.datum;
    ELSE
        v_projekat_id := OLD.projekat_id;
        v_datum := OLD.datum;
    END IF;
    IF (TG_OP = 'UPDATE') THEN
        v_old_datum := OLD.datum;
        IF v_old_datum IS NOT NULL AND v_datum IS NULL THEN
            UPDATE povrsine_po_datumu ppd
            SET
                pov_mag = calculate_non_overlapping_area(ppd.projekat_id, ppd.datum, 'polja_mag'),
                pov_gpr = calculate_non_overlapping_area(ppd.projekat_id, ppd.datum, 'polja_gpr'),
                pov_elektrika = calculate_non_overlapping_area(ppd.projekat_id, ppd.datum, 'polja_elektrika'),
                pov_profajler = calculate_non_overlapping_area(ppd.projekat_id, ppd.datum, 'polja_profajler')
            WHERE ppd.projekat_id = v_projekat_id
            AND ppd.datum >= v_old_datum;
            RETURN NEW;
        END IF;
    END IF;
    IF v_datum IS NULL THEN
        RETURN COALESCE(NEW, OLD);
    END IF;
    v_area_mag := calculate_non_overlapping_area(v_projekat_id, v_datum, 'polja_mag');
    v_area_gpr := calculate_non_overlapping_area(v_projekat_id, v_datum, 'polja_gpr');
    v_area_elektrika := calculate_non_overlapping_area(v_projekat_id, v_datum, 'polja_elektrika');
    v_area_profajler := calculate_non_overlapping_area(v_projekat_id, v_datum, 'polja_profajler');
    INSERT INTO povrsine_po_datumu (projekat_id, datum, pov_mag, pov_gpr, pov_elektrika, pov_profajler)
    VALUES (v_projekat_id, v_datum, v_area_mag, v_area_gpr, v_area_elektrika, v_area_profajler)
    ON CONFLICT (projekat_id, datum)
    DO UPDATE SET
        pov_mag = EXCLUDED.pov_mag,
        pov_gpr = EXCLUDED.pov_gpr,
        pov_elektrika = EXCLUDED.pov_elektrika,
        pov_profajler = EXCLUDED.pov_profajler;
    UPDATE povrsine_po_datumu ppd
    SET
        pov_mag = calculate_non_overlapping_area(ppd.projekat_id, ppd.datum, 'polja_mag'),
        pov_gpr = calculate_non_overlapping_area(ppd.projekat_id, ppd.datum, 'polja_gpr'),
        pov_elektrika = calculate_non_overlapping_area(ppd.projekat_id, ppd.datum, 'polja_elektrika'),
        pov_profajler = calculate_non_overlapping_area(ppd.projekat_id, ppd.datum, 'polja_profajler')
    WHERE ppd.projekat_id = v_projekat_id
    AND ppd.datum > v_datum;
    IF (TG_OP = 'UPDATE' AND v_old_datum IS NOT NULL AND v_old_datum <> v_datum) THEN
        UPDATE povrsine_po_datumu ppd
        SET
            pov_mag = calculate_non_overlapping_area(ppd.projekat_id, ppd.datum, 'polja_mag'),
            pov_gpr = calculate_non_overlapping_area(ppd.projekat_id, ppd.datum, 'polja_gpr'),
            pov_elektrika = calculate_non_overlapping_area(ppd.projekat_id, ppd.datum, 'polja_elektrika'),
            pov_profajler = calculate_non_overlapping_area(ppd.projekat_id, ppd.datum, 'polja_profajler')
        WHERE ppd.projekat_id = v_projekat_id
        AND ppd.datum >= v_old_datum
        AND ppd.datum <= v_datum;
    END IF;
    RETURN COALESCE(NEW, OLD);
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

drop_trigger_polja_elektrika: DDL = DDL(
    statement="""--sql
DROP TRIGGER IF EXISTS trg_polja_elektrika_update_povrsine ON polja_elektrika;
""",
)

drop_trigger_polja_profajler: DDL = DDL(
    statement="""--sql
DROP TRIGGER IF EXISTS trg_polja_profajler_update_povrsine ON polja_profajler;
""",
)

create_trigger_polja_elektrika: DDL = DDL(
    statement="""--sql
CREATE TRIGGER trg_polja_elektrika_update_povrsine
    AFTER INSERT OR UPDATE OR DELETE ON polja_elektrika
    FOR EACH ROW
    EXECUTE FUNCTION update_povrsine_po_datumu();
""",
)

create_trigger_polja_profajler: DDL = DDL(
    statement="""--sql
CREATE TRIGGER trg_polja_rofajler_update_povrsine
    AFTER INSERT OR UPDATE OR DELETE ON polja_profajler
    FOR EACH ROW
    EXECUTE FUNCTION update_povrsine_po_datumu();
""",
)


create_calculate_mag_nula_xy_coordinates_function: DDL = DDL(
    statement="""--sql
DROP FUNCTION IF EXISTS calculate_mag_nula_xy_coordinates() CASCADE;
CREATE OR REPLACE FUNCTION calculate_mag_nula_xy_coordinates()
RETURNS TRIGGER AS $$
DECLARE
    nula_point GEOMETRY;
BEGIN
    IF NEW.nule_id IS NOT NULL AND NEW.geom IS NOT NULL THEN
        nula_point := ST_PointN(
            ST_ExteriorRing(ST_Normalize(NEW.geom)),
            NEW.nule_id
        );
        NEW.nula_x := ST_X(nula_point);
        NEW.nula_y := ST_Y(nula_point);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
""",
)

create_calculate_gpr_nula_xy_coordinates_function: DDL = DDL(
    statement="""--sql
DROP FUNCTION IF EXISTS calculate_gpr_nula_xy_coordinates() CASCADE;
CREATE OR REPLACE FUNCTION calculate_gpr_nula_xy_coordinates()
RETURNS TRIGGER AS $$
DECLARE
    nula_point GEOMETRY;
BEGIN
    IF NEW.nule_id IS NOT NULL AND NEW.geom IS NOT NULL THEN
        nula_point := ST_PointN(
            ST_ExteriorRing(ST_Normalize(ST_OrientedEnvelope(NEW.geom))),
            NEW.nule_id
        );
        NEW.nula_x := ST_X(nula_point);
        NEW.nula_y := ST_Y(nula_point);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
""",
)

create_nula_xy_trigger_mag: DDL = DDL(
    statement="""--sql
DROP TRIGGER IF EXISTS trigger_calculate_nula_xy_mag ON polja_mag;
CREATE TRIGGER trigger_calculate_nula_xy_mag
BEFORE INSERT OR UPDATE OF geom, nule_id ON polja_mag
FOR EACH ROW
EXECUTE FUNCTION calculate_mag_nula_xy_coordinates();
""",
)

create_nula_xy_trigger_gpr: DDL = DDL(
    statement="""--sql
DROP TRIGGER IF EXISTS trigger_calculate_nula_xy_gpr ON polja_gpr;
CREATE TRIGGER trigger_calculate_nula_xy_gpr
BEFORE INSERT OR UPDATE OF geom, nule_id ON polja_gpr
FOR EACH ROW
EXECUTE FUNCTION calculate_gpr_nula_xy_coordinates();
""",
)

create_mag_angle_function: DDL = DDL(
    statement="""--sql
DROP FUNCTION IF EXISTS calculate_mag_nula_angle() CASCADE;
CREATE OR REPLACE FUNCTION calculate_mag_nula_angle()
RETURNS TRIGGER AS $$
DECLARE
    current_point GEOMETRY;
    next_point GEOMETRY;
BEGIN
    IF NEW.nule_id IS NOT NULL AND NEW.geom IS NOT NULL THEN
        current_point := ST_PointN(
            ST_ExteriorRing(ST_Normalize(NEW.geom)),
            NEW.nule_id
        );
        IF NEW.nule_id < 4 THEN
            next_point := ST_PointN(
                ST_ExteriorRing(ST_Normalize(NEW.geom)),
                NEW.nule_id + 1
            );
        ELSE
            next_point := ST_PointN(
                ST_ExteriorRing(ST_Normalize(NEW.geom)),
                1
            );
        END IF;
        NEW.mag_nula_angle := ST_Azimuth(current_point, next_point);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
""",
)

create_mag_angle_trigger: DDL = DDL(
    statement="""--sql
DROP TRIGGER IF EXISTS trigger_calculate_mag_angle ON polja_mag;
CREATE TRIGGER trigger_calculate_mag_angle
BEFORE INSERT OR UPDATE OF geom, nule_id ON polja_mag
FOR EACH ROW
EXECUTE FUNCTION calculate_mag_nula_angle();
""",
)

create_gpr_angle_function: DDL = DDL(
    statement="""--sql
DROP FUNCTION IF EXISTS calculate_gpr_nula_angle() CASCADE;
CREATE OR REPLACE FUNCTION calculate_gpr_nula_angle()
RETURNS TRIGGER AS $$
DECLARE
    ring GEOMETRY;
    current_point GEOMETRY;
    adjacent_point GEOMETRY;
    prev_idx INT;
    next_idx INT;
BEGIN
    IF NEW.nule_id IS NOT NULL AND NEW.geom IS NOT NULL THEN
        ring := ST_ExteriorRing(ST_Normalize(ST_OrientedEnvelope(NEW.geom)));
        current_point := ST_PointN(ring, NEW.nule_id);
        prev_idx := CASE WHEN NEW.nule_id > 1 THEN NEW.nule_id - 1 ELSE 4 END;
        next_idx := CASE WHEN NEW.nule_id < 4 THEN NEW.nule_id + 1 ELSE 1 END;
        adjacent_point := CASE
            WHEN NEW.smer_snimanja = 'desno' THEN ST_PointN(ring, prev_idx)
            ELSE ST_PointN(ring, next_idx)
        END;
        NEW.gpr_nula_angle := ST_Azimuth(current_point, adjacent_point);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
""",
)

create_gpr_angle_trigger: DDL = DDL(
    statement="""--sql
DROP TRIGGER IF EXISTS trigger_calculate_gpr_angle ON polja_gpr;
CREATE TRIGGER trigger_calculate_gpr_angle
BEFORE INSERT OR UPDATE OF geom, nule_id, smer_snimanja ON polja_gpr
FOR EACH ROW
EXECUTE FUNCTION calculate_gpr_nula_angle();
""",
)

create_right_angles_function: DDL = DDL(
    statement="""--sql
DROP FUNCTION IF EXISTS check_right_angles(GEOMETRY) CASCADE;
CREATE OR REPLACE FUNCTION check_right_angles(geom GEOMETRY)
RETURNS BOOLEAN AS $$
DECLARE
    n INTEGER;
    i INTEGER;
    p1 GEOMETRY;
    p2 GEOMETRY;
    p3 GEOMETRY;
    angle FLOAT;
BEGIN
    n := ST_NPoints(geom) - 1;
    FOR i IN 1..n LOOP
        IF i = 1 THEN
            p1 := ST_PointN(ST_ExteriorRing(geom), n);
        ELSE
            p1 := ST_PointN(ST_ExteriorRing(geom), i - 1);
        END IF;
        p2 := ST_PointN(ST_ExteriorRing(geom), i);
        IF i = n THEN
            p3 := ST_PointN(ST_ExteriorRing(geom), 1);
        ELSE
            p3 := ST_PointN(ST_ExteriorRing(geom), i + 1);
        END IF;
        angle := ST_Angle(p1, p2, p3);
        IF abs(angle - pi() / 2) >= 0.0001 AND abs(angle - 3 * pi() / 2) >= 0.0001 THEN
            RETURN FALSE;
        END IF;
    END LOOP;
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql IMMUTABLE STRICT;
""",
)

create_profile_dimensions_function: DDL = DDL(
    statement="""--sql
DROP FUNCTION IF EXISTS calculate_profile_dimensions() CASCADE;
CREATE OR REPLACE FUNCTION calculate_rofile_dimensions()
RETURNS TRIGGER AS $$
DECLARE
    current_point GEOMETRY;
    left_point GEOMETRY;
    right_point GEOMETRY;
    left_index INTEGER;
    right_index INTEGER;
BEGIN
    IF NEW.nule_id IS NOT NULL AND NEW.geom IS NOT NULL THEN
        current_point := ST_PointN(
            ST_ExteriorRing(ST_Normalize(NEW.geom)),
            NEW.nule_id
        );
        left_index  := CASE WHEN NEW.nule_id < 4 THEN NEW.nule_id + 1 ELSE 1 END;
        right_index := CASE WHEN NEW.nule_id > 1 THEN NEW.nule_id - 1 ELSE 4 END;
        left_point := ST_PointN(
            ST_ExteriorRing(ST_Normalize(NEW.geom)),
            left_index
        );
        right_point := ST_PointN(
            ST_ExteriorRing(ST_Normalize(NEW.geom)),
            right_index
        );
        NEW.duzina_profila := ROUND(ST_Distance(current_point, left_point))::INTEGER;
        NEW.sirina_polja := ROUND(ST_Distance(current_point, right_point))::INTEGER;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
""",
)

create_mag_profile_dimensions_trigger: DDL = DDL(
    statement="""--sql
DROP TRIGGER IF EXISTS trigger_calculate_mag_profile_dimensions ON polja_mag;
CREATE TRIGGER trigger_calculate_profile_dimensions
BEFORE INSERT OR UPDATE OF geom, nule_id ON polja_mag
FOR EACH ROW
EXECUTE FUNCTION calculate_mag_profile_dimensions();
""",
)

create_profajler_profile_dimensions_trigger: DDL = DDL(
    statement="""--sql
DROP TRIGGER IF EXISTS trigger_calculate_mag_profile_dimensions ON polja_profajler;
CREATE TRIGGER trigger_calculate_profile_dimensions
BEFORE INSERT OR UPDATE OF geom, nule_id ON polja_profajler
FOR EACH ROW
EXECUTE FUNCTION calculate_mag_profile_dimensions();
""",
)

create_elektrika_profile_dimensions_trigger: DDL = DDL(
    statement="""--sql
DROP TRIGGER IF EXISTS trigger_calculate_mag_profile_dimensions ON polja_elektrika;
CREATE TRIGGER trigger_calculate_profile_dimensions
BEFORE INSERT OR UPDATE OF geom, nule_id ON polja_elektrika
FOR EACH ROW
EXECUTE FUNCTION calculate_mag_profile_dimensions();
""",
)

restrict_ekipa_delete: DDL = DDL(
    statement="""--sql
DROP TRIGGER IF EXISTS restrict_ekipa_delete ON ekipa;
DROP FUNCTION IF EXISTS fn_restrict_ekipa_delete();
CREATE OR REPLACE FUNCTION fn_restrict_ekipa_delete()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'Brisanje članova ekipe nije dozvoljeno.';
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER restrict_ekipa_delete
BEFORE DELETE ON ekipa
FOR EACH ROW EXECUTE FUNCTION fn_restrict_ekipa_delete();
""",
)

create_lokacija_sync_function: DDL = DDL(
    statement="""--sql
CREATE OR REPLACE FUNCTION sync_lokacija_in_projekat()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE projekti
        SET lokacije_ids = array_append(
            COALESCE(lokacije_ids, ARRAY[]::integer[]),
            NEW.lokacija_id
        )
        WHERE projekat_id = NEW.projekat_id;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE projekti
        SET lokacije_ids = array_remove(lokacije_ids, OLD.lokacija_id)
        WHERE projekat_id = OLD.projekat_id;
    ELSIF TG_OP = 'UPDATE' AND OLD.projekat_id IS DISTINCT FROM NEW.projekat_id THEN
        UPDATE projekti
        SET lokacije_ids = array_remove(lokacije_ids, OLD.lokacija_id)
        WHERE projekat_id = OLD.projekat_id;
        UPDATE projekti
        SET lokacije_ids = array_append(
            COALESCE(lokacije_ids, ARRAY[]::integer[]),
            NEW.lokacija_id
        )
        WHERE projekat_id = NEW.projekat_id;
    END IF;
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;
""",
)

create_sync_lokacija_trigger: DDL = DDL(
    statement="""--sql
CREATE OR REPLACE TRIGGER trg_sync_lokacija_in_projekat
AFTER INSERT OR UPDATE OR DELETE ON lokacije
FOR EACH ROW
EXECUTE FUNCTION sync_lokacija_in_projekat();
""",
)

create_new_podesavanje_trigger: DDL = DDL(
    statement="""--sql
CREATE OR REPLACE FUNCTION create_podesavanja_for_projekat()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO podesavanja (projekat_id)
    VALUES (NEW.projekat_id);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER trigger_create_podesavanja
AFTER INSERT ON projekti
FOR EACH ROW
EXECUTE FUNCTION create_podesavanja_for_projekat();
""",
)


create_set_geom_from_xy_function: DDL = DDL(
    statement=f"""--sql
    CREATE OR REPLACE FUNCTION set_geom_from_xy()
    RETURNS TRIGGER AS $$
    BEGIN
        IF NEW.geom IS NULL AND NEW.x IS NOT NULL AND NEW.y IS NOT NULL THEN
            NEW.geom := ST_SetSRID(ST_MakePoint(NEW.x, NEW.y, COALESCE(NEW.z, 0)), {srid});
        END IF;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
""",  # noqa: E501
)

create_set_geom_from_xy_trigger: DDL = DDL(
    statement="""--sql
    DROP TRIGGER IF EXISTS trg_kotiranja_set_geom ON kotiranja;
    CREATE TRIGGER trg_kotiranja_set_geom
    BEFORE INSERT ON kotiranja
    FOR EACH ROW EXECUTE FUNCTION set_geom_from_xy();
""",
)


def register_triggers() -> None:
    """Register all database triggers."""
    tacke_table: Table = SQLModel.metadata.tables["tacke"]
    polja_mag_table: Table = SQLModel.metadata.tables["polja_mag"]
    polja_gpr_table: Table = SQLModel.metadata.tables["polja_gpr"]
    polja_elektrika_table: Table = SQLModel.metadata.tables["polja_elektrika"]
    polja_profajler_table: Table = SQLModel.metadata.tables["polja_profajler"]
    povrsine_po_datumu: Table = SQLModel.metadata.tables["povrsine_po_datumu"]
    ekipa_table: Table = SQLModel.metadata.tables["ekipa"]
    lokacije: Table = SQLModel.metadata.tables["lokacije"]
    podesavanja: Table = SQLModel.metadata.tables["podesavanja"]
    kotiranja: Table = SQLModel.metadata.tables["kotiranja"]

    trigger_config: dict[Table, list[DDL]] = {
        ekipa_table: [restrict_ekipa_delete],
        tacke_table: [
            create_z_trigger_function,
            create_z_trigger,
        ],
        polja_mag_table: [
            create_total_mag_trigger_function,
            create_total_mag_trigger,
            create_calculate_mag_nula_xy_coordinates_function,
            create_nula_xy_trigger_mag,
            create_mag_angle_function,
            create_mag_angle_trigger,
            create_profile_dimensions_function,
            create_mag_profile_dimensions_trigger,
        ],
        polja_gpr_table: [
            trigger_check_proizvodjac,
            create_total_gpr_trigger_function,
            create_total_gpr_trigger,
            create_calculate_gpr_nula_xy_coordinates_function,
            create_nula_xy_trigger_gpr,
            create_gpr_angle_function,
            create_gpr_angle_trigger,
        ],
        polja_elektrika_table: [
            create_total_elektrika_trigger_function,
            create_total_elektrika_trigger,
            drop_trigger_polja_elektrika,
            create_trigger_polja_elektrika,
            create_elektrika_profile_dimensions_trigger,
        ],
        polja_profajler_table: [
            create_total_profajler_trigger_function,
            create_total_profajler_trigger,
            drop_trigger_polja_profajler,
            create_trigger_polja_profajler,
            create_profajler_profile_dimensions_trigger,
        ],
        povrsine_po_datumu: [
            calculate_non_overlapping_area,
            update_povrsine_function,
        ],
        lokacije: [
            create_lokacija_sync_function,
            create_sync_lokacija_trigger,
        ],
        podesavanja: [
            create_new_podesavanje_trigger,
        ],
        kotiranja: [
            create_set_geom_from_xy_function,
            create_set_geom_from_xy_trigger,
        ],
    }

    for table, trigger_functions in trigger_config.items():
        for trigger_fn in trigger_functions:
            event.listen(
                target=table,
                identifier="after_create",
                fn=trigger_fn.execute_if(dialect="postgresql"),
            )

    event.listen(
        target=SQLModel.metadata,
        identifier="before_create",
        fn=create_right_angles_function.execute_if(dialect="postgresql"),
    )


create_immutability_function: TextClause = text(
    text="""--sql
CREATE OR REPLACE FUNCTION prevent_changes()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'This table is immutable';
END;
$$ LANGUAGE plpgsql;
""",
)


def register_immutability_triggers(engine: Engine) -> None:
    """Register immutability triggers after initial data load."""
    with engine.connect() as conn:
        conn.execute(statement=create_immutability_function)
        immutable_tables: list[str] = ["nule"]
        for table_name in immutable_tables:
            conn.execute(
                statement=text(
                    text=f"""--sql
                            DROP TRIGGER IF EXISTS immutable_trigger ON {table_name};
                            CREATE TRIGGER immutable_trigger
                            BEFORE UPDATE OR DELETE ON {table_name}
                            FOR EACH ROW EXECUTE FUNCTION prevent_changes();
                        """,
                ),
            )

        conn.commit()


def register_cros_table_ddls(engine: Engine) -> None:
    """Register cros table ddls.

    Args:
        engine (Engine): Engine.

    """
    cross_table_ddls: list[DDL] = [
        drop_trigger_polja_mag,
        drop_trigger_polja_gpr,
        create_trigger_polja_mag,
        create_trigger_polja_gpr,
    ]
    with engine.begin() as conn:
        for ddl in cross_table_ddls:
            ddl_pg: DDL = ddl.execute_if(dialect="postgresql")
            ddl_pg(
                target=SQLModel.metadata.tables["povrsine_po_datumu"],
                bind=conn,
                checkfirst=False,
            )
