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
}


def _country_code_to_flag(cc: str) -> str:
    """Convert a 2-letter country code to an emoji flag."""
    if len(cc) != 2:
        return ""
    return chr(127397 + ord(cc[0].upper())) + chr(127397 + ord(cc[1].upper()))


def lang_to_flag(lang: str) -> str:
    """Return an emoji flag for the given language code if known."""
    if not lang:
        return ""
    lang = lang.lower()
    cc = _LANG_TO_COUNTRY.get(lang)
    if cc:
        return _country_code_to_flag(cc)
    return ""
