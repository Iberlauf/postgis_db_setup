"""Mandatory defaluts."""

color_maps: list[str] = [
    "GrayScale",
    "Terrain",
    "ChromaDepth",
    "Rainbow",
    "Rainbow2",
    "Rainbow3",
    "Rainbow4",
    "Rainbow5",
    "Rainbow6",
    "Rainbow7",
    "Rainbow8",
    "Rainbow9",
    "Rainbow10",
    "Rainbow11",
    "Rainbow12",
    "Rainbow13",
    "Rainbow14",
    "Rainbow15",
    "Rainbow16",
    "Rainbow17",
    "Rainbow18",
    "Gray-Yellow",
    "Pink-Purple",
    "Yellow-Brown",
    "Yellow-Red",
    "BrightYellow-Red",
    "Gray-YellowGreen",
    "Green-Yellow",
    "Green-Blue",
    "Green-Blue-Purple",
    "Blue-White",
    "Blue-Green-Yellow",
    "Blue-Purple",
    "Blue-Green-Brown",
    "BrightBlue-Red",
    "Purple-Blue",
    "Purple-Yellow",
    "DarkPurple-Yellow",
    "Brown-Yellow",
    "Pinks",
    "Reds",
    "Oranges",
    "Greens",
    "Blues",
    "Purples",
    "Browns",
    "Orange-Blue",
    "Green-YellowPurple",
    "Green-Brown",
    "GreenYellow-BrownPurple",
    "Green-Red",
    "BrightGreen-Red",
    "Green-Pink",
    "Green-Purple",
    "BlueGreen-OrangeRed",
    "BlueWhite-WhiteBlue",
    "Blue-OrangeRed",
    "Blue-YellowRed",
    "BrightBlue-Green",
    "Blue-Red",
    "Blue-Yellow",
    "Blue-YellowOrange",
    "Blue-BrownYellow",
    "Blue-RedOrangeYellow",
    "Purple-Orange",
    "Brown-Aqua",
    "Brown-Blue",
    "Brown-Green",
    "Gray-Red",
    "Accents",
    "BlueSteel",
    "LiDAR_Classification",
    "LiDAR_Intensity",
    "HighPoints",
    "HighPoints2",
    "Construction",
    "Exploration",
    "Ice",
    "Ice2",
    "Paulje",
]

kolor_rampe: list[dict[str, int | str]] = [
    {"kolor_rampa_id": idx, "kolor_rampa_naziv": preset}
    for idx, preset in enumerate(iterable=color_maps, start=1)
]

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
