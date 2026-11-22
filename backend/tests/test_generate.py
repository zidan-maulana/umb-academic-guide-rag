"""Pengujian generate.py dengan klien Gemini palsu (tanpa panggilan API)."""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from backend.app.services import generate as generate_mod
from backend.app.services.generate import (
    FALLBACK_MESSAGE,
    extract_pages,
    generate_answer,
)


@pytest.fixture(autouse=True)
def reset_gemini_client() -> None:
    generate_mod._client = None
    yield
    generate_mod._client = None


def _mock_client(text: str | None) -> MagicMock:
    client = MagicMock()
    client.models.generate_content.return_value = SimpleNamespace(text=text)
    return client


def test_generate_answer_normal_pages_unique_sorted() -> None:
    chunks = [
        {"id": "a", "halaman": 12},
        {"id": "b", "halaman": "13"},
        {"id": "c", "halaman": 12},
        {"id": "d", "halaman": 45},
    ]
    client = _mock_client("Batas SKS semester adalah 24 (hal. 12).")

    with patch.object(generate_mod, "_get_client", return_value=client):
        result = generate_answer("prompt uji", chunks)

    assert result["is_fallback"] is False
    assert result["answer"] == "Batas SKS semester adalah 24 (hal. 12)."
    assert result["pages"] == [12, 13, 45]
    client.models.generate_content.assert_called_once()


def test_generate_answer_fallback_clears_pages() -> None:
    chunks = [{"halaman": 11}, {"halaman": 66}]
    client = _mock_client(f"  {FALLBACK_MESSAGE}  ")

    with patch.object(generate_mod, "_get_client", return_value=client):
        result = generate_answer("prompt uji", chunks)

    assert result["answer"] == FALLBACK_MESSAGE
    assert result["is_fallback"] is True
    assert result["pages"] == []


def test_extract_pages_skips_missing_halaman() -> None:
    chunks = [
        {"id": "tanpa-halaman", "konten": "teks"},
        {"id": "halaman-kosong", "halaman": None},
        SimpleNamespace(id="objek", konten="x"),
        {"id": "valid", "halaman": "20"},
    ]
    assert extract_pages(chunks) == [20]


def test_generate_answer_chunks_without_halaman_ok() -> None:
    chunks = [{"id": "a", "konten": "tanpa metadata halaman"}]
    client = _mock_client("Jawaban dari konteks yang ada.")

    with patch.object(generate_mod, "_get_client", return_value=client):
        result = generate_answer("prompt uji", chunks)

    assert result["is_fallback"] is False
    assert result["pages"] == []


def test_missing_gemini_api_key_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    with patch.object(generate_mod, "load_dotenv"):
        with pytest.raises(RuntimeError, match="GEMINI_API_KEY belum di-set"):
            generate_mod._get_client()
