from core.flags import lang_to_flag


def test_lang_to_flag_known_codes():
    assert lang_to_flag('eng') == lang_to_flag('en') == '🇬🇧'
    assert lang_to_flag('spa') == '🇪🇸'
    assert lang_to_flag('deu') == '🇩🇪'
    assert lang_to_flag('fas') == lang_to_flag('fa') == '🇮🇷'
    assert lang_to_flag('pol') == '🇵🇱'


def test_lang_to_flag_unknown():
    assert lang_to_flag('xxx') == ''
