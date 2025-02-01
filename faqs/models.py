from django.db import models, transaction
from ckeditor.fields import RichTextField
from .languages import SUPPORTED_LANGUAGES  # Import from the parent directory
from .utils import translate_text
from .redis_handler import RedisHandler

redis_handler = RedisHandler()


class FAQ(models.Model):
    question = models.TextField()
    answer = RichTextField()  # WYSIWYG editor for answer
    question_translated = models.JSONField(default=dict, blank=True)
    answer_translated = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        with transaction.atomic():  # Ensuring the transaction is atomic
            if not self.pk:
                self.translate_content()  # Translate content if it's a new FAQ

            super().save(*args, **kwargs)

            # Cache the FAQ in Redis
            cache_key = f"faq:{self.pk}"
            faq_data = {
                "id": self.pk,
                "question": str(self.question),  # Convert to string
                "answer": str(
                    self.answer
                ),  # Convert to string (ensure it's not a complex object)
                "created_at": self.created_at.isoformat(),
                "updated_at": self.updated_at.isoformat(),
            }
            redis_handler.set_cache_with_transaction(cache_key, faq_data)

    def translate_content(self):
        try:
            for lang in SUPPORTED_LANGUAGES:
                if lang != "en":
                    self.question_translated[lang] = translate_text(lang, self.question)
                    self.answer_translated[lang] = translate_text(lang, self.answer)
        except Exception as e:
            print(f"Translation failed: {e}")

    def get_translated_question(self, lang="en"):
        # For English, or if no proper translation is available, return the original question.
        if lang == "en":
            return self.question
        value = self.question_translated.get(lang)
        if not value:  # If value is None or an empty string
            return self.question
        return value

    def get_translated_answer(self, lang="en"):
        if lang == "en":
            return self.answer
        value = self.answer_translated.get(lang)
        if not value:
            return self.answer
        return value

    def __str__(self):
        return self.question
