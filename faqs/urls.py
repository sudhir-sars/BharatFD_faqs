from django.urls import path
from .views import FAQListAPIView, FAQDetailAPIView

urlpatterns = [
    path("faqs/", FAQListAPIView.as_view(), name="faq-list-api"),
    path("faqs/<int:pk>/", FAQDetailAPIView.as_view(), name="faq-detail-api"),
]
