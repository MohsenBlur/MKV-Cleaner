from core.flags import lang_to_flag


def test_lang_to_flag_known_codes():
    assert lang_to_flag('eng') == lang_to_flag('en') == '🇬🇧'
    assert lang_to_flag('fra') == lang_to_flag('fre') == lang_to_flag('fr') == '🇫🇷'
    assert lang_to_flag('spa') == '🇪🇸'
    assert lang_to_flag('deu') == '🇩🇪'
    assert lang_to_flag('fas') == lang_to_flag('fa') == '🇮🇷'
    assert lang_to_flag('pol') == '🇵🇱'
    assert lang_to_flag('dan') == lang_to_flag('da') == '🇩🇰'
    assert lang_to_flag('ces') == lang_to_flag('cs') == '🇨🇿'
    assert lang_to_flag('hrv') == lang_to_flag('hr') == '🇭🇷'


def test_lang_to_flag_unknown(monkeypatch):
    import locale

    monkeypatch.setattr(locale, 'getdefaultlocale', lambda: (None, None))
    monkeypatch.setattr(locale, 'getlocale', lambda: (None, None))
    assert lang_to_flag('xxx') == ''


def test_lang_to_flag_locale_fallback(monkeypatch):
    import locale

    monkeypatch.setattr(locale, 'getdefaultlocale', lambda: ('fr_FR', 'UTF-8'))
    monkeypatch.setattr(locale, 'getlocale', lambda: ('fr_FR', 'UTF-8'))
    assert lang_to_flag('xxx') == '🇫🇷'
