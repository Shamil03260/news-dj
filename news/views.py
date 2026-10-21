from django.shortcuts import render, get_object_or_404
from .models import News, Category


def home(request):
    news_list = News.objects.filter(
        status=News.Status.PUBLISHED
    ).select_related("category").order_by(
        "-published_at",
        "-created_at"
    )

    categories = Category.objects.all().order_by("name")

    context = {
        "news_list": news_list,
        "categories": categories,
    }

    return render(request, "home.html", context)


def news_detail(request, slug):
    news = get_object_or_404(
        News,
        slug=slug,
        status=News.Status.PUBLISHED
    )

    News.objects.filter(pk=news.pk).update(
        views_count=news.views_count + 1
    )
    news.views_count += 1

    related_news = News.objects.filter(
        status=News.Status.PUBLISHED,
        category=news.category
    ).exclude(pk=news.pk).order_by("-published_at")[:5]

    context = {
        "news": news,
        "related_news": related_news,
        "categories": Category.objects.all().order_by("name"),
    }

    return render(request, "news_detail.html", context)


def category_news(request, slug):
    category = get_object_or_404(
        Category,
        slug=slug
    )

    news_list = News.objects.filter(
        category=category,
        status=News.Status.PUBLISHED
    ).order_by("-published_at", "-created_at")

    categories = Category.objects.all().order_by("name")

    context = {
        "category": category,
        "news_list": news_list,
        "categories": categories,
    }

    return render(request, "category.html", context)