# faqs/tests.py

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from .models import FAQ


class FAQModelTest(TestCase):
    def setUp(self):
        """
        Setting up a consistent FAQ instance to test various model methods.
        """
        self.faq = FAQ.objects.create(
            question="What is REST?",
            answer="REST is an architectural style for web services.",
        )

    def test_auto_translation(self):
        """
        Test that auto translation populates translation for a supported language.
        """
        self.faq.refresh_from_db()
        translated_question = self.faq.get_translated_question(
            "hi"
        )  # Hindi translation
        self.assertIsNotNone(translated_question)
        self.assertNotEqual(translated_question, "")
        self.assertNotEqual(translated_question, self.faq.question)

    def test_get_translated_question(self):
        """
        Test that get_translated_question returns the original question for English,
        and falls back to the original if no translation exists.
        """
        self.faq.refresh_from_db()
        self.assertEqual(self.faq.get_translated_question("en"), self.faq.question)
        self.assertEqual(
            self.faq.get_translated_question("xx"), self.faq.question
        )  # Unsupported language

    def test_translation_fallback(self):
        """
        Test that when a translation is not available, it falls back to the original language (English).
        """
        self.faq.refresh_from_db()
        translated_answer = self.faq.get_translated_answer("es")  # Spanish translation
        self.assertIsNotNone(translated_answer)
        self.assertNotEqual(translated_answer, "")  # Ensure we got something


class FAQAPICreationAndDetailTest(APITestCase):
    def test_create_and_retrieve_faq(self):
        """
        Test the creation and retrieval of an FAQ using API endpoints.
        """
        payload = {
            "question": "What is REST?",
            "answer": "REST is an architectural style for web services.",
        }
        list_url = reverse("faq-list-api")
        create_response = self.client.post(list_url, payload, format="json")
        self.assertEqual(create_response.status_code, 201)

        faq_id = create_response.data.get("id")
        self.assertIsNotNone(faq_id, "FAQ id should be returned after creation.")

        detail_url = reverse("faq-detail-api", kwargs={"pk": faq_id})
        get_response = self.client.get(detail_url)
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(get_response.data.get("question"), payload["question"])

    def test_create_faq_invalid_data(self):
        """
        Test that FAQ creation fails with missing required fields (e.g., question or answer).
        """
        payload = {
            "question": "",  # Missing or empty question
            "answer": "REST is an architectural style for web services.",
        }
        list_url = reverse("faq-list-api")
        create_response = self.client.post(list_url, payload, format="json")
        self.assertEqual(
            create_response.status_code, 400
        )  # Bad request due to missing question

    def test_get_faq_with_invalid_id(self):
        """
        Test that accessing a non-existing FAQ returns a 404 error.
        """
        invalid_id = 99999  # A very high ID that doesn't exist
        detail_url = reverse("faq-detail-api", kwargs={"pk": invalid_id})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 404)  # Should return a 404 error
