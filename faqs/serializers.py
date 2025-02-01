from rest_framework import serializers
from .models import FAQ


class FAQSerializer(serializers.ModelSerializer):
    question = serializers.CharField()  # Change to CharField for POST request
    answer = serializers.CharField()  # Change to CharField for POST request
    question_translated = serializers.JSONField(required=False)
    answer_translated = serializers.JSONField(required=False)

    class Meta:
        model = FAQ
        fields = (
            "id",
            "question",
            "answer",
            "question_translated",
            "answer_translated",
            "created_at",
            "updated_at",
        )

    def create(self, validated_data):
        """
        Override the create method to handle translations automatically on FAQ creation.
        """
        faq = FAQ.objects.create(**validated_data)

        # You can call the translate_content method here to populate translations after the FAQ is saved
        faq.translate_content()

        return faq

    def get_question(self, obj):
        """
        Get translated question.
        Used only for GET requests to return translated content.
        """
        request = self.context.get("request")
        lang = request.GET.get("lang", "en") if request else "en"
        return obj.get_translated_question(lang)

    def get_answer(self, obj):
        """
        Get translated answer.
        Used only for GET requests to return translated content.
        """
        request = self.context.get("request")
        lang = request.GET.get("lang", "en") if request else "en"
        return obj.get_translated_answer(lang)
