from django.contrib import admin

from .models import Streak


@admin.register(Streak)
class StreakAdmin(admin.ModelAdmin):
    list_display = ("user", "current_streak", "longest_streak", "total_points", "last_active_date")
    search_fields = ("user__username",)