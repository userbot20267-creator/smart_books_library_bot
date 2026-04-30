"""API Tests Module"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestRootEndpoint:
    """Test root endpoint"""

    def test_root(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["message"] == "Welcome to Smart Books Library Bot API"


class TestHealthCheck:
    """Test health check endpoint"""

    def test_health_check(self):
        """Test health check"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestBooksAPI:
    """Test books API endpoints"""

    def test_get_books(self):
        """Test get books endpoint"""
        response = client.get("/api/books/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_featured_books(self):
        """Test get featured books"""
        response = client.get("/api/books/featured")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_trending_books(self):
        """Test get trending books"""
        response = client.get("/api/books/trending")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestSearchAPI:
    """Test search API endpoints"""

    def test_text_search(self):
        """Test text search"""
        response = client.get("/api/search/text?query=python")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_semantic_search(self):
        """Test semantic search"""
        response = client.get("/api/search/semantic?query=programming")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_advanced_search(self):
        """Test advanced search"""
        response = client.get("/api/search/advanced?query=book&sort_by=newest")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
