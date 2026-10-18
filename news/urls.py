from django.urls import path, re_path
from . import views

urlpatterns = [
    path("", views.home, name="home"),

    re_path(
        r"^news/(?P<slug>[-a-zA-Z0-9_\u0080-\uffff]+)/$",
        views.news_detail,
        name="news_detail",
    ),

    re_path(
        r"^category/(?P<slug>[-a-zA-Z0-9_\u0080-\uffff]+)/$",
        views.category_news,
        name="category_news",
    ),
]