# In utils.py
from googletrans import Translator

translator = Translator()


def translate_text(lang, text):
    try:
        # Ensure that the input is not empty
        if not text:
            return text

        translation = translator.translate(text, dest=lang)

        # Handle the case where translation.text might be None
        if translation.text and translation.text.strip() != "":
            return translation.text
        else:
            return text
    except Exception as e:
        print(f"Translation Error ({lang}): {e}")
        return text
