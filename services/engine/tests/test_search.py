import pytest
import httpx
from unittest.mock import patch, MagicMock
import os
from main import app
from routers.search import search_songs

@pytest.fixture
async def client():
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
def mock_ytmusic():
    with patch('routers.search.YTMusic') as mock:
        instance = mock.return_value
        yield instance

def test_search_mapping(mock_ytmusic):
    # Mock YTMusic search response
    mock_ytmusic.search.return_value = [
        {
            "videoId": "test123",
            "title": "Test Song",
            "artists": [{"name": "Artist 1"}, {"name": "Artist 2"}],
            "thumbnails": [{"url": "http://example.com/thumb.jpg"}]
        }
    ]
    
    # Call search function
    results = search_songs("test query")
    
    # Verify mapping
    assert len(results) == 1
    assert results[0] == {
        "id": "test123",
        "title": "Test Song",
        "artists": ["Artist 1", "Artist 2"],
        "thumbnail": "http://example.com/thumb.jpg",
        "uri": "youtube:video:test123"
    }

def test_search_caching(mock_ytmusic):
    # Mock YTMusic search response
    mock_ytmusic.search.return_value = [
        {
            "videoId": "test123",
            "title": "Test Song",
            "artists": [{"name": "Artist 1"}],
            "thumbnails": [{"url": "http://example.com/thumb.jpg"}]
        }
    ]
    
    # Call search function twice with same query
    search_songs("test query")
    search_songs("test query")
    
    # Verify YTMusic.search was called only once
    mock_ytmusic.search.assert_called_once_with("test query", filter='songs', limit=20)

@pytest.mark.asyncio
async def test_search_endpoint(client, mock_ytmusic):
    # Mock YTMusic search response
    mock_ytmusic.search.return_value = [
        {
            "videoId": "test123",
            "title": "Test Song",
            "artists": [{"name": "Artist 1"}],
            "thumbnails": [{"url": "http://example.com/thumb.jpg"}]
        }
    ]
    
    # Call search endpoint
    response = await client.get("/api/search?q=test query")
    assert response.status_code == 200
    
    # Verify response format
    results = response.json()
    assert len(results) == 1
    assert results[0]["id"] == "test123"
    assert results[0]["title"] == "Test Song"
    assert results[0]["artists"] == ["Artist 1"]
    assert results[0]["thumbnail"] == "http://example.com/thumb.jpg"
    assert results[0]["uri"] == "youtube:video:test123"

@pytest.mark.asyncio
async def test_search_error_handling(client, mock_ytmusic):
    # Mock YTMusic search error
    mock_ytmusic.search.side_effect = Exception("YTMusic error")
    
    # Call search endpoint
    response = await client.get("/api/search?q=test query")
    assert response.status_code == 502
    assert "Search service temporarily unavailable" in response.json()["detail"] 