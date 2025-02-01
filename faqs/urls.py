from django.urls import path
from .views import FAQListAPI

urlpatterns = [
    path('faqs/', FAQListAPI.as_view(), name='faq-list'),
]
