import os

import yaml


def load_all_languages():
    """Load all language files"""
    _texts = {}
    _languages = []

    current_directory = os.path.dirname(os.path.realpath(__file__))
    language_directory = 'languages'
    language_directory_path = os.path.join(current_directory, language_directory)

    for filename in os.listdir(language_directory_path):
        if filename.endswith(".yaml"):
            lang_id = filename.replace('.yaml', '')
            _languages.append(lang_id)
            file_path = os.path.join(language_directory_path, filename)
            with open(file=file_path, mode='r', encoding="utf-8") as data:
                _texts[lang_id] = yaml.load(data, Loader=yaml.FullLoader)

    return _languages, _texts


_languages, _texts = load_all_languages()


def _(key, language) -> str | None:
    """Translate text from key and language code"""

    if language is None:
        language = 'en'
    if language in _texts and key in _texts[language]:
        return _texts[language][key]
    else:
        return None


flags = {
    'uz': '🇺🇿',
    'ru': '🇷🇺',
    'en': '🇺🇸',
    'uzk': '🇺🇿',
}


def get_all_languages():
    return _languages


async def check_for_translation(key: str, text: str) -> bool:
    if text is None:
        return False
    for language in _languages:
        if _(key, language) == text:
            return True
    return False


def get_language_code(key: str, text: str):
    for language in _languages:
        if _(key, language) == text:
            return language
