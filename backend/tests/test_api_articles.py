"""Tests for article API endpoints."""

import pytest
from datetime import datetime, timezone
from src.models.feed import Feed
from src.models.article import Article

# Other fixtures (client, db_session, setup_database) are provided by conftest.py


@pytest.fixture
def test_feed(db_session):
    """Create a test feed."""
    feed = Feed(
        name="Test Feed",
        url="https://test.example.com/feed.xml",
        fetch_interval=900
    )
    db_session.add(feed)
    db_session.commit()
    db_session.refresh(feed)
    return feed


@pytest.fixture
def test_articles(db_session, test_feed):
    """Create test articles."""
    now = datetime.now(timezone.utc)

    articles = [
        Article(
            feed_id=test_feed.id,
            title="Article 1",
            url="https://example.com/article1",
            author="Author 1",
            content="<p>Content 1</p>",
            content_text="Content 1",
            published_at=now,
            is_read=False,
            is_saved=False,
            is_archived=False
        ),
        Article(
            feed_id=test_feed.id,
            title="Article 2",
            url="https://example.com/article2",
            author="Author 2",
            content="<p>Content 2</p>",
            content_text="Content 2",
            published_at=now,
            is_read=True,
            is_saved=False,
            is_archived=False
        ),
        Article(
            feed_id=test_feed.id,
            title="Article 3",
            url="https://example.com/article3",
            author="Author 3",
            content="<p>Content 3</p>",
            content_text="Content 3",
            published_at=now,
            is_read=False,
            is_saved=True,
            is_archived=False
        ),
        Article(
            feed_id=test_feed.id,
            title="Article 4",
            url="https://example.com/article4",
            author="Author 4",
            content="<p>Content 4</p>",
            content_text="Content 4",
            published_at=now,
            is_read=False,
            is_saved=False,
            is_archived=True
        ),
    ]

    for article in articles:
        db_session.add(article)

    db_session.commit()

    for article in articles:
        db_session.refresh(article)

    return articles


def test_list_articles_empty(client):
    """Test GET /api/articles returns empty list."""
    response = client.get("/api/articles")
    assert response.status_code == 200
    assert response.json() == []


def test_list_articles(client, test_articles):
    """Test GET /api/articles returns all articles."""
    response = client.get("/api/articles")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 4

    # Check first article structure
    article = data[0]
    assert "id" in article
    assert "feed_id" in article
    assert "title" in article
    assert "url" in article
    assert "author" in article
    assert "content" in article
    assert "content_text" in article
    assert "published_at" in article
    assert "fetched_at" in article
    assert "is_read" in article
    assert "is_saved" in article
    assert "is_archived" in article


def test_list_articles_filter_by_feed(client, db_session, test_articles):
    """Test GET /api/articles filters by feed_id."""
    # Create another feed with articles
    feed2 = Feed(name="Feed 2", url="https://feed2.example.com/feed.xml")
    db_session.add(feed2)
    db_session.commit()
    db_session.refresh(feed2)

    article_feed2 = Article(
        feed_id=feed2.id,
        title="Article from Feed 2",
        url="https://example.com/article_feed2",
        is_read=False,
        is_saved=False,
        is_archived=False
    )
    db_session.add(article_feed2)
    db_session.commit()

    # Filter by first feed
    response = client.get(f"/api/articles?feed_id={test_articles[0].feed_id}")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 4  # Only articles from test_feed
    for article in data:
        assert article["feed_id"] == test_articles[0].feed_id


def test_list_articles_filter_unread(client, test_articles):
    """Test GET /api/articles filters by is_read=false."""
    response = client.get("/api/articles?is_read=false")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 3  # Articles 1, 3, 4 are unread
    for article in data:
        assert article["is_read"] is False


def test_list_articles_filter_read(client, test_articles):
    """Test GET /api/articles filters by is_read=true."""
    response = client.get("/api/articles?is_read=true")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1  # Only Article 2 is read
    assert data[0]["is_read"] is True


def test_list_articles_filter_saved(client, test_articles):
    """Test GET /api/articles filters by is_saved=true."""
    response = client.get("/api/articles?is_saved=true")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1  # Only Article 3 is saved
    assert data[0]["is_saved"] is True


def test_list_articles_filter_archived(client, test_articles):
    """Test GET /api/articles filters by is_archived=true."""
    response = client.get("/api/articles?is_archived=true")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1  # Only Article 4 is archived
    assert data[0]["is_archived"] is True


def test_list_articles_filter_not_archived(client, test_articles):
    """Test GET /api/articles filters by is_archived=false."""
    response = client.get("/api/articles?is_archived=false")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 3  # Articles 1, 2, 3 are not archived


def test_list_articles_multiple_filters(client, test_articles):
    """Test GET /api/articles with multiple filters."""
    response = client.get("/api/articles?is_read=false&is_saved=false&is_archived=false")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1  # Only Article 1 matches all criteria
    assert data[0]["is_read"] is False
    assert data[0]["is_saved"] is False
    assert data[0]["is_archived"] is False


def test_list_articles_sort_newest(client, test_articles):
    """Test GET /api/articles sorts by newest first (default)."""
    response = client.get("/api/articles?sort=newest")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 4

    # Articles should be sorted by published_at or fetched_at descending
    # All test articles have same published_at, so check IDs in descending order
    for i in range(len(data) - 1):
        # Newer articles (higher IDs in our test) should come first
        assert data[i]["id"] >= data[i + 1]["id"]


def test_list_articles_sort_oldest(client, test_articles):
    """Test GET /api/articles sorts by oldest first."""
    response = client.get("/api/articles?sort=oldest")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 4

    # Articles should be sorted by published_at or fetched_at ascending
    # Check IDs in ascending order
    for i in range(len(data) - 1):
        assert data[i]["id"] <= data[i + 1]["id"]


def test_get_article_by_id(client, test_articles):
    """Test GET /api/articles/{id} returns specific article."""
    article_id = test_articles[0].id

    response = client.get(f"/api/articles/{article_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == article_id
    assert data["title"] == "Article 1"
    assert data["url"] == "https://example.com/article1"
    assert data["author"] == "Author 1"
    assert data["content"] == "<p>Content 1</p>"


def test_get_article_not_found(client):
    """Test GET /api/articles/{id} returns 404 for non-existent article."""
    response = client.get("/api/articles/999")
    assert response.status_code == 404


def test_update_article_mark_read(client, test_articles):
    """Test PATCH /api/articles/{id} marks article as read."""
    article_id = test_articles[0].id

    # Article should start as unread
    assert test_articles[0].is_read is False

    # Mark as read
    update_data = {"is_read": True}
    response = client.patch(f"/api/articles/{article_id}", json=update_data)
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == article_id
    assert data["is_read"] is True
    assert data["is_saved"] is False  # Other fields unchanged
    assert data["is_archived"] is False


def test_update_article_mark_unread(client, test_articles):
    """Test PATCH /api/articles/{id} marks article as unread."""
    article_id = test_articles[1].id

    # Article 2 starts as read
    assert test_articles[1].is_read is True

    # Mark as unread
    update_data = {"is_read": False}
    response = client.patch(f"/api/articles/{article_id}", json=update_data)
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == article_id
    assert data["is_read"] is False


def test_update_article_save(client, test_articles):
    """Test PATCH /api/articles/{id} saves article."""
    article_id = test_articles[0].id

    # Mark as saved
    update_data = {"is_saved": True}
    response = client.patch(f"/api/articles/{article_id}", json=update_data)
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == article_id
    assert data["is_saved"] is True


def test_update_article_archive(client, test_articles):
    """Test PATCH /api/articles/{id} archives article."""
    article_id = test_articles[0].id

    # Mark as archived
    update_data = {"is_archived": True}
    response = client.patch(f"/api/articles/{article_id}", json=update_data)
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == article_id
    assert data["is_archived"] is True


def test_update_article_multiple_fields(client, test_articles):
    """Test PATCH /api/articles/{id} updates multiple fields."""
    article_id = test_articles[0].id

    # Update multiple fields
    update_data = {
        "is_read": True,
        "is_saved": True,
        "is_archived": False
    }
    response = client.patch(f"/api/articles/{article_id}", json=update_data)
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == article_id
    assert data["is_read"] is True
    assert data["is_saved"] is True
    assert data["is_archived"] is False


def test_update_article_partial_update(client, test_articles):
    """Test PATCH /api/articles/{id} only updates provided fields."""
    article_id = test_articles[2].id

    # Article 3: is_read=False, is_saved=True, is_archived=False

    # Update only is_read
    update_data = {"is_read": True}
    response = client.patch(f"/api/articles/{article_id}", json=update_data)
    assert response.status_code == 200

    data = response.json()
    assert data["is_read"] is True
    assert data["is_saved"] is True  # Unchanged
    assert data["is_archived"] is False  # Unchanged


def test_update_article_not_found(client):
    """Test PATCH /api/articles/{id} returns 404 for non-existent article."""
    update_data = {"is_read": True}
    response = client.patch("/api/articles/999", json=update_data)
    assert response.status_code == 404
