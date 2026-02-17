import pytest
from datetime import datetime
from src.database import SessionLocal, engine, Base
from src.models.feed import Feed
from src.models.article import Article


@pytest.fixture
def db_session():
    """Create a fresh database session for testing."""
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


def test_create_feed(db_session):
    """Test creating a feed."""
    feed = Feed(
        name="Test Feed",
        url="https://example.com/feed.xml",
        fetch_interval=900
    )
    db_session.add(feed)
    db_session.commit()

    assert feed.id is not None
    assert feed.name == "Test Feed"
    assert feed.is_active is True
    assert feed.created_at is not None


def test_create_article(db_session):
    """Test creating an article."""
    feed = Feed(name="Test Feed", url="https://example.com/feed.xml")
    db_session.add(feed)
    db_session.commit()

    article = Article(
        feed_id=feed.id,
        title="Test Article",
        url="https://example.com/article",
        content="<p>Test content</p>",
        content_text="Test content"
    )
    db_session.add(article)
    db_session.commit()

    assert article.id is not None
    assert article.title == "Test Article"
    assert article.is_read is False
    assert article.is_saved is False
    assert article.is_archived is False


def test_article_feed_relationship(db_session):
    """Test that articles are linked to feeds."""
    feed = Feed(name="Test Feed", url="https://example.com/feed.xml")
    db_session.add(feed)
    db_session.commit()

    article = Article(
        feed_id=feed.id,
        title="Test Article",
        url="https://example.com/article",
        content="Content",
        content_text="Content"
    )
    db_session.add(article)
    db_session.commit()

    # Refresh to load relationship
    db_session.refresh(article)
    assert article.feed.name == "Test Feed"
