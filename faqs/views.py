from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import FAQ
from django.shortcuts import render
from .serializers import FAQSerializer
from .redis_handler import RedisHandler
from django.core.paginator import Paginator

redis_handler = RedisHandler()


class FAQListAPIView(APIView):
    """
    API endpoint to retrieve the list of FAQs and create a new FAQ.
    Supports language selection via a ?lang= query parameter.
    Caches the response in Redis.
    """

    def get(self, request):
        lang = request.GET.get("lang", "en")
        page_number = request.GET.get("page", 1)
        cache_key = f"faqs:list:{lang}"

        # Try to get cached data
        if cached_data := redis_handler.get_cache(cache_key):
            return Response(cached_data, status=status.HTTP_200_OK)

        # Query the database and serialize FAQs
        faqs = FAQ.objects.all().order_by("-created_at")

        # Pagination setup
        paginator = Paginator(faqs, 5)  # 5 FAQs per page (can be changed)
        page_obj = paginator.get_page(page_number)

        # Serialize the current page of FAQs
        serializer = FAQSerializer(
            page_obj.object_list, many=True, context={"request": request}
        )

        # Prepare paginated data response
        data = {
            "count": paginator.count,
            "total_pages": paginator.num_pages,
            "current_page": page_obj.number,
            "next": page_obj.has_next(),
            "previous": page_obj.has_previous(),
            "results": serializer.data,
        }

        # Cache the serialized data for future requests
        redis_handler.set_cache(cache_key, data)

        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Create a new FAQ.
        Returns the created FAQ's data (including the id) so that tests or clients
        can immediately use this id to request the specific FAQ.
        """
        serializer = FAQSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            faq = serializer.save()

            # Clear cache for the FAQ list (for the current language)
            lang = request.GET.get("lang", "en")
            redis_handler.client.delete(f"faqs:list:{lang}")

            # Return the created FAQ's data, including its id.
            response_data = {
                "id": faq.id,
                "question": faq.question,
                "answer": faq.answer,
                "question_translated": faq.question_translated,
                "answer_translated": faq.answer_translated,
                "created_at": faq.created_at.isoformat(),
                "updated_at": faq.updated_at.isoformat(),
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FAQDetailAPIView(APIView):
    """
    API endpoint to retrieve, update, or delete a specific FAQ.
    Supports language selection via ?lang= query parameter.
    """

    def get(self, request, pk):
        try:
            faq = FAQ.objects.get(pk=pk)
        except FAQ.DoesNotExist:
            return Response(
                {
                    "error": "FAQ not found.",
                    "message": f"No FAQ with id {pk} exists.",
                    "status": "fail",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = FAQSerializer(faq, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        try:
            faq = FAQ.objects.get(pk=pk)
        except FAQ.DoesNotExist:
            return Response(
                {
                    "error": "FAQ not found.",
                    "message": f"No FAQ with id {pk} exists to update.",
                    "status": "fail",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = FAQSerializer(faq, data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            redis_handler.client.delete(f"faq:{pk}")
            redis_handler.client.delete(f"faqs:list:{request.GET.get('lang', 'en')}")
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        try:
            faq = FAQ.objects.get(pk=pk)
        except FAQ.DoesNotExist:
            return Response(
                {
                    "error": "FAQ not found.",
                    "message": f"No FAQ with id {pk} exists to update.",
                    "status": "fail",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = FAQSerializer(
            faq, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            redis_handler.client.delete(f"faq:{pk}")
            redis_handler.client.delete(f"faqs:list:{request.GET.get('lang', 'en')}")
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            faq = FAQ.objects.get(pk=pk)
        except FAQ.DoesNotExist:
            return Response(
                {
                    "error": "FAQ not found.",
                    "message": f"No FAQ with id {pk} exists to delete.",
                    "status": "fail",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        faq.delete()
        redis_handler.client.delete(f"faq:{pk}")
        redis_handler.client.delete(f"faqs:list:{request.GET.get('lang', 'en')}")
        return Response(
            {
                "message": f"FAQ with id {pk} has been successfully deleted.",
                "status": "success",
            },
            status=status.HTTP_204_NO_CONTENT,
        )


# A view for rendering the home page remains unchanged.
def home_page_view(request):
    lang = request.GET.get("lang", "en")  # Default to English if no lang is passed
    faqs = FAQ.objects.all().order_by("-created_at")

    # Pagination
    paginator = Paginator(faqs, 5)  # 5 FAQs per page (can be adjusted)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    faq_list = []
    for faq in page_obj.object_list:
        faq_list.append(
            {
                "id": faq.id,
                "question": faq.get_translated_question(lang),  # Translate question
                "answer": faq.get_translated_answer(lang),  # Translate answer
            }
        )

    return render(request, "faqs/home.html", {"faqs": faq_list, "page_obj": page_obj, "lang": lang})
