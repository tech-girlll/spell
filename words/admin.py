from django.contrib import admin

from .models import Word


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ("text", "length", "difficulty_level", "has_dictionary_data", "created_at")
    list_filter = ("difficulty_level",)
    search_fields = ("text",)
    readonly_fields = ("length", "created_at", "updated_at")

    @admin.display(boolean=True, description="Has dict data")
    def has_dictionary_data(self, obj):
        return bool(obj.definition)
    
    