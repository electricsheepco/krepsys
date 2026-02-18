"""Tests for feed API endpoints."""

# Fixtures are provided by conftest.py


def test_list_feeds_empty(client):
    """Test GET /api/feeds returns empty list."""
    response = client.get("/api/feeds")
    assert response.status_code == 200
    assert response.json() == []


def test_create_feed(client):
    """Test POST /api/feeds creates a new feed."""
    feed_data = {
        "name": "Tech News",
        "url": "https://technews.example.com/feed.xml",
        "fetch_interval": 1800
    }
    response = client.post("/api/feeds", json=feed_data)
    assert response.status_code == 201

    data = response.json()
    assert data["name"] == feed_data["name"]
    assert data["url"] == feed_data["url"]
    assert data["fetch_interval"] == feed_data["fetch_interval"]
    assert data["is_active"] is True
    assert "id" in data
    assert "created_at" in data


def test_list_feeds_with_data(client):
    """Test GET /api/feeds returns created feeds."""
    # Create two feeds
    feed1 = {"name": "Feed 1", "url": "https://feed1.example.com/feed.xml"}
    feed2 = {"name": "Feed 2", "url": "https://feed2.example.com/feed.xml"}

    client.post("/api/feeds", json=feed1)
    client.post("/api/feeds", json=feed2)

    response = client.get("/api/feeds")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Feed 1"
    assert data[1]["name"] == "Feed 2"


def test_get_feed_by_id(client):
    """Test GET /api/feeds/{id} returns specific feed."""
    # Create a feed
    feed_data = {"name": "Test Feed", "url": "https://test.example.com/feed.xml"}
    create_response = client.post("/api/feeds", json=feed_data)
    feed_id = create_response.json()["id"]

    # Get feed by ID
    response = client.get(f"/api/feeds/{feed_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == feed_id
    assert data["name"] == feed_data["name"]
    assert data["url"] == feed_data["url"]


def test_get_feed_not_found(client):
    """Test GET /api/feeds/{id} returns 404 for non-existent feed."""
    response = client.get("/api/feeds/999")
    assert response.status_code == 404


def test_update_feed(client):
    """Test PATCH /api/feeds/{id} updates a feed."""
    # Create a feed
    feed_data = {"name": "Original Name", "url": "https://original.example.com/feed.xml"}
    create_response = client.post("/api/feeds", json=feed_data)
    feed_id = create_response.json()["id"]

    # Update feed
    update_data = {
        "name": "Updated Name",
        "fetch_interval": 3600,
        "is_active": False
    }
    response = client.patch(f"/api/feeds/{feed_id}", json=update_data)
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["fetch_interval"] == 3600
    assert data["is_active"] is False
    assert data["url"] == feed_data["url"]  # URL should remain unchanged


def test_delete_feed(client):
    """Test DELETE /api/feeds/{id} deletes a feed."""
    # Create a feed
    feed_data = {"name": "To Delete", "url": "https://delete.example.com/feed.xml"}
    create_response = client.post("/api/feeds", json=feed_data)
    feed_id = create_response.json()["id"]

    # Delete feed
    response = client.delete(f"/api/feeds/{feed_id}")
    assert response.status_code == 204

    # Verify feed is deleted
    get_response = client.get(f"/api/feeds/{feed_id}")
    assert get_response.status_code == 404


def test_create_feed_duplicate_url(client):
    """Test POST /api/feeds rejects duplicate URL."""
    feed_data = {"name": "Original", "url": "https://duplicate.example.com/feed.xml"}

    # Create first feed
    response1 = client.post("/api/feeds", json=feed_data)
    assert response1.status_code == 201

    # Try to create duplicate
    duplicate_data = {"name": "Duplicate", "url": "https://duplicate.example.com/feed.xml"}
    response2 = client.post("/api/feeds", json=duplicate_data)
    assert response2.status_code == 400
    assert "already exists" in response2.json()["detail"].lower()
