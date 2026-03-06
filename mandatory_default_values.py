"""Mandatory defaluts."""

epsg_3855: dict[str, int | str] = {
    "srid": 3855,
    "auth_name": "EPSG",
    "auth_srid": 3855,
    "proj4text": "+vunits=m +no_defs +type=crs",
    "srtext": (
        'VERT_CS["EGM2008 height",'
        'VERT_DATUM["EGM2008 geoid",2005,AUTHORITY["EPSG","1027"]],'
        'UNIT["metre",1,AUTHORITY["EPSG","9001"]],'
        'AXIS["Gravity-related height",UP],'
        'AUTHORITY["EPSG","3855"]]'
    ),
}

nule_defaults: list[dict[str, int | str]] = [
    {"nule_id": 1, "nule_naziv": "zapad"},
    {"nule_id": 2, "nule_naziv": "sever"},
    {"nule_id": 3, "nule_naziv": "istok"},
    {"nule_id": 4, "nule_naziv": "jug"},
]

if __name__ == "__main__":
    ...
