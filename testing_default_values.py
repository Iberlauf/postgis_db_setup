"""Default values fopr testing."""

from models.enums import TipMag

antena_defaults: list[dict[str, int | str]] = [
    {
        "antena_id": 1,
        "antena_naziv": "350 HS Antenna",
        "antena_serijski_broj": "0166",
        "antena_model": "350HS",
        "antena_proizvodjac_id": 2,
        "antena_frekvencija": 350,
    },
    {
        "antena_id": 2,
        "antena_naziv": "270 MHz - Shielded Antenna",
        "antena_serijski_broj": "129",
        "antena_model": "50270S",
        "antena_proizvodjac_id": 2,
        "antena_frekvencija": 270,
    },
    {
        "antena_id": 3,
        "antena_naziv": "500",
        "antena_serijski_broj": "11047",
        "antena_model": "21-001997",
        "antena_proizvodjac_id": 3,
        "antena_frekvencija": 500,
    },
    {
        "antena_id": 4,
        "antena_naziv": "100-800",
        "antena_serijski_broj": "11141",
        "antena_model": "21-001692",
        "antena_proizvodjac_id": 3,
        "antena_frekvencija": 800,
    },
    {
        "antena_id": 5,
        "antena_naziv": "Zmija",
        "antena_serijski_broj": "11165",
        "antena_model": "21-002458",
        "antena_proizvodjac_id": 3,
        "antena_frekvencija": 25,
    },
    {
        "antena_id": 6,
        "antena_naziv": "250",
        "antena_serijski_broj": "25443",
        "antena_model": "21-003000",
        "antena_proizvodjac_id": 3,
        "antena_frekvencija": 250,
    },
]

ekipa_defaults: list[dict[str, int | str]] = [
    {
        "ekipa_id": 1,
        "ekipa_ime": "Željko",
        "ekipa_prezime": "Jovianović",
    },
    {
        "ekipa_id": 2,
        "ekipa_ime": "Igor",
        "ekipa_prezime": "Milošević",
    },
    {
        "ekipa_id": 3,
        "ekipa_ime": "Ivan",
        "ekipa_prezime": "Marjanović",
    },
    {
        "ekipa_id": 4,
        "ekipa_ime": "Vladimir",
        "ekipa_prezime": "Miletić",
    },
    {
        "ekipa_id": 5,
        "ekipa_ime": "Jelena",
        "ekipa_prezime": "Miletić",
    },
    {
        "ekipa_id": 6,
        "ekipa_ime": "Predrag",
        "ekipa_prezime": "Rajčić",
    },
    {
        "ekipa_id": 7,
        "ekipa_ime": "Snimatelj:",
        "ekipa_prezime": "Nepoznat",
    },
]

georadar_defaults: list[dict[str, int | str]] = [
    {
        "gpr_id": 1,
        "gpr_naziv": "GSSI SIR-4000",
        "gpr_serijski_broj": "282",
        "gpr_model": "DC-4000 SIR 4000",
        "gpr_proizvodjac_id": 2,
    },
    {
        "gpr_id": 2,
        "gpr_naziv": "MALÅ RAMAC",
        "gpr_serijski_broj": "11151",
        "gpr_model": "21-002188",
        "gpr_proizvodjac_id": 3,
    },
]

investitor_defaults: list[dict[str, int | str]] = [
    {
        "investitor_id": 1,
        "investitor_naziv": "Arheološki institut",
        "investitor_adresa": "Kneza Mihaili 35/IV 11000 Beograd",
        "investitor_email": "institut@ai.ac.rs",
        "investitor_pib": "101824180",
        "investitor_maticni_broj": "07003234",
        "investitor_broj_telefona": "0112637191",
    },
]

magnetometar_defaults: list[dict[str, int | str]] = [
    {
        "mag_id": 1,
        "mag_naziv": "stari",
        "mag_serijski_broj": 3111330,
        "mag_model": "GSM-19GW",
        "mag_tip": TipMag.PROTONSKI_OVERHAUZER,
        "mag_proizvodjac_id": 1,
    },
    {
        "mag_id": 2,
        "mag_naziv": "novi",
        "mag_serijski_broj": 6017391,
        "mag_model": "GSM-19GW",
        "mag_tip": TipMag.PROTONSKI_OVERHAUZER,
        "mag_proizvodjac_id": 1,
    },
]

proizvodjac_defaults: list[dict[str, int | str]] = [
    {
        "proizvodjac_id": 1,
        "proizvodjac_naziv": "GEM SYSTEMS",
        "proizvodjac_drzava": "Kanada",
    },
    {
        "proizvodjac_id": 2,
        "proizvodjac_naziv": "GSSI",
        "proizvodjac_drzava": "SAD",
    },
    {
        "proizvodjac_id": 3,
        "proizvodjac_naziv": "MALÅ",
        "proizvodjac_drzava": "Švedska",
    },
]

projekat_defaults: list[dict[str, int | str]] = [
    {
        "projekat_id": 1,
        "projekat_naziv": "Viminacium",
        "investitor_id": 1,
    },
]
