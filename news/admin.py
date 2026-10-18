from django.contrib import admin


from django.contrib import admin
from .models import News, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "source",
        "category",
        "status",
        "priority",
        "published_at",
    )

    list_filter = ("status", "category", "source")
    search_fields = ("title", "summary", "source")
    list_editable = ("status", "priority")
    readonly_fields = ("fetched_at", "created_at")
