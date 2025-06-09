"""Mapping between language codes and their flag emoji representations."""

# Simple mapping from language codes to flag emojis
# Supports both 2-letter and 3-letter language codes

_LANG_TO_COUNTRY = {
    # English
    "en": "GB",
    "eng": "GB",
    # Spanish
    "es": "ES",
    "spa": "ES",
    # German
    "de": "DE",
    "deu": "DE",
    "ger": "DE",
    # French
    "fr": "FR",
    "fra": "FR",
    "fre": "FR",
    # Italian
    "it": "IT",
    "ita": "IT",
    # Portuguese
    "pt": "PT",
    "por": "PT",
    # Russian
    "ru": "RU",
    "rus": "RU",
    # Japanese
    "ja": "JP",
    "jpn": "JP",
    # Chinese
    "zh": "CN",
    "zho": "CN",
    "chi": "CN",
    # Persian (Farsi)
    "fa": "IR",
    "fas": "IR",
    "per": "IR",
    # Arabic
    "ar": "SA",
    "ara": "SA",
    # Dutch
    "nl": "NL",
    "nld": "NL",
    "dut": "NL",
    # Polish
    "pl": "PL",
    "pol": "PL",
    # Turkish
    "tr": "TR",
    "tur": "TR",
    # Korean
    "ko": "KR",
    "kor": "KR",
    # Hindi
    "hi": "IN",
    "hin": "IN",
    # Vietnamese
    "vi": "VN",
    "vie": "VN",
    # Swedish
    "sv": "SE",
    "swe": "SE",
    # Greek
    "el": "GR",
    "ell": "GR",
    "gre": "GR",
    # Hebrew
    "he": "IL",
    "heb": "IL",
    # Thai
    "th": "TH",
    "tha": "TH",
    # Danish
    "da": "DK",
    "dan": "DK",
    # Finnish
    "fi": "FI",
    "fin": "FI",
    # Hungarian
    "hu": "HU",
    "hun": "HU",
    # Norwegian
    "no": "NO",
    "nor": "NO",
    # Romanian
    "ro": "RO",
    "ron": "RO",
    "rum": "RO",
    # Bulgarian
    "bg": "BG",
    "bul": "BG",
    # Czech
    "cs": "CZ",
    "ces": "CZ",
    "cze": "CZ",
    # Slovak
    "sk": "SK",
    "slk": "SK",
    "slo": "SK",
    # Croatian
    "hr": "HR",
    "hrv": "HR",
    # Ukrainian
    "uk": "UA",
    "ukr": "UA",
    # Indonesian
    "id": "ID",
    "ind": "ID",
    # Malay
    "ms": "MY",
    "msa": "MY",
    "may": "MY",
    # Filipino/Tagalog
    "tl": "PH",
    "tgl": "PH",
}

# Mapping from ISO 3166-1 alpha-3 codes to alpha-2 codes for basic coverage
_COUNTRY_ALPHA3_TO_ALPHA2 = {
    "GBR": "GB",
    "ESP": "ES",
    "DEU": "DE",
    "FRA": "FR",
    "ITA": "IT",
    "PRT": "PT",
    "RUS": "RU",
    "JPN": "JP",
    "CHN": "CN",
    "IRN": "IR",
    "SAU": "SA",
    "NLD": "NL",
    "POL": "PL",
    "TUR": "TR",
    "KOR": "KR",
    "IND": "IN",
    "VNM": "VN",
    "SWE": "SE",
    "GRC": "GR",
    "ISR": "IL",
    "THA": "TH",
    "DNK": "DK",
    "FIN": "FI",
    "HUN": "HU",
    "NOR": "NO",
    "ROU": "RO",
    "BGR": "BG",
    "CZE": "CZ",
    "SVK": "SK",
    "HRV": "HR",
    "UKR": "UA",
    "IDN": "ID",
    "MYS": "MY",
    "PHL": "PH",
    "USA": "US",
    "CAN": "CA",
}


def _country_code_to_flag(cc: str) -> str:
    """Convert a country code (alpha-2 or alpha-3) to an emoji flag.

    Invalid or unknown codes yield an empty string.
    """
    if not cc or not cc.isalpha():
        return ""
    cc = cc.upper()
    if len(cc) == 3:
        cc = _COUNTRY_ALPHA3_TO_ALPHA2.get(cc, "")
        if not cc:
            return ""
    elif len(cc) != 2:
        return ""
    return chr(127397 + ord(cc[0])) + chr(127397 + ord(cc[1]))


def lang_to_flag(lang: str) -> str:
    """Return an emoji flag for the given language code if known."""
    if not lang:
        return ""
    lang = lang.lower()
    cc = _LANG_TO_COUNTRY.get(lang)
    if not cc:
        if "-" in lang or "_" in lang:
            country = lang.split("-")[1] if "-" in lang else lang.split("_")[1]
            if len(country) == 2:
                cc = country.upper()
    if not cc:
        import locale

        loc = locale.getdefaultlocale()[0] or ""
        if not loc:
            loc = locale.getlocale()[0] or ""
        if loc and ("_" in loc or "-" in loc):
            country = loc.split("_")[1] if "_" in loc else loc.split("-")[1]
            if len(country) == 2:
                cc = country.upper()
    return _country_code_to_flag(cc) if cc else ""
