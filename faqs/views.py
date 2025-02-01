from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import FAQ
from .serializers import FAQSerializer
from django.core.cache import cache

class FAQListAPI(APIView):
    """
    API endpoint to retrieve FAQs.
    Supports language selection via ?lang= query parameter.
    """

    def get(self, request):
        lang = request.GET.get('lang', 'en')
        cache_key = f"faqs_{lang}"
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data, status=status.HTTP_200_OK)
        
        faqs = FAQ.objects.all().order_by('-created_at')
        data = []
        for faq in faqs:
            # Dynamically get translated fields.
            data.append({
                'id': faq.id,
                'question': faq.get_translated_field('question', lang),
                'answer': faq.get_translated_field('answer', lang),
                'created_at': faq.created_at
            })
        # Cache the data for subsequent calls
        cache.set(cache_key, data, timeout=300)
        return Response(data, status=status.HTTP_200_OK)
