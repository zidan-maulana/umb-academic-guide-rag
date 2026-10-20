"""Pengujian otomatis endpoint FastAPI backend UMB Academic Guide RAG."""

from fastapi.testclient import TestClient
from backend.app.main import app


def test_root_endpoint():
    """Uji endpoint root informasi layanan."""
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"


def test_health_endpoint():
    """Uji endpoint pemantauan kesehatan layanan."""
    with TestClient(app) as client:
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


def test_chat_retrieval_success():
    """Uji pertanyaan nyata panduan akademik dan periksa sitasi sumber halaman."""
    with TestClient(app) as client:
        payload = {"question": "Berapa lama batas waktu studi program sarjana?"}
        response = client.post("/api/v1/chat", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "answered"
        assert "mode" in data
        assert "aturan-17-01" in [s["id"] for s in data["sources"]]
        assert 17 in [s["halaman"] for s in data["sources"]]


def test_chat_with_metadata_filter():
    """Uji pertanyaan dengan filter metadata fakultas."""
    with TestClient(app) as client:
        payload = {
            "question": "Bagaimana akreditasi program studi?",
            "filters": {"fakultas": "FEB"},
        }
        response = client.post("/api/v1/chat", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "answered"
        assert data["mode"]["fakultas"] == "FEB"
        for s in data["sources"]:
            assert s["id"] == "akreditasi-11-02"
            assert s["halaman"] == 11


if __name__ == "__main__":
    test_root_endpoint()
    print("test_root_endpoint: PASSED")
    test_health_endpoint()
    print("test_health_endpoint: PASSED")
    test_chat_retrieval_success()
    print("test_chat_retrieval_success: PASSED")
    test_chat_with_metadata_filter()
    print("test_chat_with_metadata_filter: PASSED")
    print("\nSeluruh pengujian API lolos 100%!")
