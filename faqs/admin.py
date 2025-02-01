from django.contrib import admin
from .models import FAQ

class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'created_at')
    search_fields = ('question',)
    readonly_fields = ('created_at',)
    
    # Optionally, override formfield_for_dbfield to provide a custom widget (like CKEditor) for answer fields.
    # django-ckeditor should already hook into TextField/RichTextField.

admin.site.register(FAQ, FAQAdmin)
