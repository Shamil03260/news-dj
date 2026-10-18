
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from datetime import datetime
from email.utils import parsedate_to_datetime

from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.text import slugify

from .models import News, Category


APA_URL = "https://apa.az/news/"
SOURCE_NAME = "APA"


def detect_category(title, summary):
    text = f"{title} {summary}".lower()

    categories = {
        "İdman": [
            "idman", "futbol", "oyun", "komanda",
            "çempionat", "qarabağ", "neftçi"
        ],
        "İqtisadiyyat": [
            "iqtisadiyyat", "neft", "investisiya",
            "maliyyə", "manat", "iqtisadi"
        ],
        "Texnologiya": [
            "texnologiya", "süni intellekt",
            "rəqəmsal", "kompüter"
        ],
        "Siyasət": [
            "siyasət", "prezident", "parlament",
            "nazir", "hökumət", "millət vəkili"
        ],
        "Dünya": [
            "dünya", "beynəlxalq", "xarici",
            "ukrayna", "rusiya", "amerika"
        ],
    }

    for category_name, keywords in categories.items():
        if any(keyword in text for keyword in keywords):
            category, _ = Category.objects.get_or_create(
                name=category_name,
                defaults={
                    "slug": slugify(
                        category_name,
                        allow_unicode=True
                    )
                }
            )
            return category

    category, _ = Category.objects.get_or_create(
        name="Yerli xəbərlər",
        defaults={"slug": "yerli-xeberler"}
    )

    return category


def get_soup(url, headers):
    response = requests.get(
        url,
        headers=headers,
        timeout=20
    )
    response.raise_for_status()

    return BeautifulSoup(response.content, "html.parser")


def get_meta(soup, *names):
    for name in names:
        tag = soup.find(
            "meta",
            attrs={"property": name}
        )

        if not tag:
            tag = soup.find(
                "meta",
                attrs={"name": name}
            )

        if tag and tag.get("content"):
            return tag["content"].strip()

    return ""


def parse_news_date(raw_date):
    if not raw_date:
        return None

    parsed = parse_datetime(raw_date)

    if parsed is None:
        try:
            parsed = parsedate_to_datetime(raw_date)
        except (ValueError, TypeError, OverflowError):
            return None

    if timezone.is_naive(parsed):
        parsed = timezone.make_aware(parsed)

    return parsed


def fetch_news():
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/130.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "az,en-US;q=0.9,en;q=0.8",
    }

    print("APA mənbəsi açılır:", APA_URL)

    soup = get_soup(APA_URL, headers)

    article_urls = {}

    for link in soup.find_all("a", href=True):
        href = link["href"].strip()
        title = link.get_text(" ", strip=True)

        if not title:
            continue

        url = urljoin(APA_URL, href)
        parsed_url = urlparse(url)

        # Yalnız apa.az domenindəki keçidləri qəbul edirik.
        if parsed_url.netloc.lower() not in {
            "apa.az",
            "www.apa.az",
        }:
            continue

        path_parts = parsed_url.path.strip("/").split("/")

        # Xəbər keçidlərinin son hissəsində rəqəmli ID olur.
        if len(path_parts) < 2:
            continue

        if not path_parts[-1].split("-")[-1].isdigit():
            continue

        article_urls[url] = title

    print("Tapılan xəbər keçidləri:", len(article_urls))

    added = 0

    for article_url, listing_title in list(
        article_urls.items()
    )[:30]:

        try:
            article_soup = get_soup(article_url, headers)

            title = get_meta(
                article_soup,
                "og:title",
                "twitter:title"
            )

            if not title:
                heading = article_soup.find("h1")
                title = (
                    heading.get_text(" ", strip=True)
                    if heading else listing_title
                )

            if not title:
                continue

            canonical = article_soup.find(
                "link",
                rel="canonical"
            )

            original_url = (
                canonical.get("href")
                if canonical and canonical.get("href")
                else article_url
            )

            if News.objects.filter(
                original_url=original_url
            ).exists():
                continue

            summary = get_meta(
                article_soup,
                "og:description",
                "description",
                "twitter:description"
            )

            image_url = get_meta(
                article_soup,
                "og:image",
                "twitter:image"
            )

            raw_date = get_meta(
                article_soup,
                "article:published_time",
                "date",
                "pubdate"
            )

            published_at = parse_news_date(raw_date)

            category = detect_category(title, summary)

            News.objects.create(
                title=title,
                summary=summary,
                content=summary,
                image_url=image_url,
                source=SOURCE_NAME,
                original_url=original_url,
                category=category,
                published_at=published_at,
                status=News.Status.PUBLISHED,
            )

            added += 1
            print("Əlavə edildi:", title)

        except requests.RequestException as error:
            print("Səhifə açıla bilmədi:", article_url, error)

        except Exception as error:
            print("Xəbər emal edilərkən xəta:", error)

    print("Əlavə edilən yeni xəbərlər:", added)

    return added
