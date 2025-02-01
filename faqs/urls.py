from django.urls import path
from .views import FAQListAPI, faq_list_view

urlpatterns = [
    path('faqs/', FAQListAPI.as_view(), name='faq-list-api'),
    path('view/', faq_list_view, name='faq-list-view'),
]
