from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import path
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from .models import FAQ
from ckeditor.widgets import CKEditorWidget
from django import forms
import csv
import os


class FAQAdminForm(forms.ModelForm):
    class Meta:
        model = FAQ
        fields = "__all__"
        widgets = {
            "answer": CKEditorWidget(),
        }


class CSVUploadForm(forms.Form):
    csv_file = forms.FileField(
        label="Select a CSV file",
        help_text="Upload a CSV file containing FAQ data. The CSV should have 'question' and 'answer' columns.",
    )


class FAQAdmin(admin.ModelAdmin):
    form = FAQAdminForm
    change_list_template = "admin/faq/faq_changelist.html"

    list_display = ("question", "get_translations", "id", "created_at", "updated_at")
    search_fields = ("question",)
    list_filter = ("created_at", "updated_at")

    fieldsets = (
        ("Edit FAQ", {"fields": ("question", "answer")}),
        ("Translations", {"fields": ("question_translated", "answer_translated")}),
    )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("upload-csv/", self.upload_csv, name="upload_csv"),
        ]
        return custom_urls + urls

    def upload_csv(self, request):
        if request.method == "POST":
            form = CSVUploadForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = request.FILES["csv_file"]
                # Validate file extension
                if not csv_file.name.endswith(".csv"):
                    messages.error(request, "Please upload a CSV file.")
                    return HttpResponseRedirect("../")

                # Save the uploaded file temporarily
                fs = FileSystemStorage()
                filename = fs.save(csv_file.name, csv_file)
                uploaded_file_url = fs.path(filename)

                try:
                    with open(
                        uploaded_file_url, newline="", encoding="utf-8"
                    ) as csvfile:
                        reader = csv.DictReader(csvfile)

                        # Validate CSV structure
                        required_fields = ["question", "answer"]
                        if not all(
                            field in reader.fieldnames for field in required_fields
                        ):
                            messages.error(
                                request,
                                'CSV file must contain "question" and "answer" columns.',
                            )
                            return HttpResponseRedirect("../")

                        success_count = 0
                        error_count = 0

                        for row in reader:
                            try:
                                FAQ.objects.create(
                                    question=row["question"], answer=row["answer"]
                                )
                                success_count += 1
                            except Exception as e:  # noqa: F841
                                error_count += 1
                                continue

                        # Clean up the temporary file
                        os.remove(uploaded_file_url)

                        if success_count > 0:
                            messages.success(
                                request, f"Successfully imported {success_count} FAQs."
                            )
                        if error_count > 0:
                            messages.warning(
                                request, f"Failed to import {error_count} FAQs."
                            )

                except Exception as e:
                    messages.error(request, f"Error processing CSV file: {str(e)}")

                return HttpResponseRedirect("../")

        form = CSVUploadForm()
        payload = {"form": form, "opts": self.model._meta, "title": "Upload FAQ CSV"}
        return render(request, "admin/faq/csv_form.html", payload)

    def get_translations(self, obj):
        translations = []
        translations.append(f"English: {obj.get_translated_question('en')}")
        translations.append(f"Hindi: {obj.get_translated_question('hi')}")
        translations.append(f"Bengali: {obj.get_translated_question('bn')}")
        return format_html("<br> <br>".join(translations))

    get_translations.short_description = _("Translations")


# Register FAQAdmin in the admin panel
admin.site.register(FAQ, FAQAdmin)
