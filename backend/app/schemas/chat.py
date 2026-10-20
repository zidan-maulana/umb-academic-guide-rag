"""Skema Pydantic untuk request, response, filter, dan hasil retrieval (docs/api-contract.md)."""

from typing import List, Optional
from pydantic import BaseModel, Field


class ChatFilter(BaseModel):
    """Filter metadata pencarian dokumen."""
    bagian: Optional[str] = Field(default=None, description="Regulasi, Kurikulum, Profil, Akreditasi")
    fakultas: Optional[str] = Field(default=None, description="FDSK, FT, Fasilkom, FEB, Fikom, FPsi")
    program_studi: Optional[str] = Field(default=None, description="Nama program studi resmi")
    jenjang: Optional[str] = Field(default=None, description="Diploma Tiga, Sarjana, dll")


class RetrievedChunk(BaseModel):
    """Representasi satu potongan dokumen yang ditemukan beserta skor kemiripannya."""
    id: str
    konten: str
    halaman: int
    bagian: str
    jenis_konten: str
    topik: Optional[str] = None
    fakultas: Optional[str] = None
    program_studi: Optional[str] = None
    jenjang: Optional[str] = None
    similarity: float


class CitationSource(BaseModel):
    """Sitasi sumber jawaban yang dikembalikan ke antarmuka pengguna."""
    id: str
    halaman: int
    bagian: str
    kutipan: str
    jenis_konten: Optional[str] = None
    topik: Optional[str] = None
    fakultas: Optional[str] = None
    program_studi: Optional[str] = None
    similarity: Optional[float] = Field(default=None, exclude=True)


class ClarificationInfo(BaseModel):
    """Detail klarifikasi saat pertanyaan ambigu (Usulan, api-contract bagian 3)."""
    message: str
    field: str
    options: List[str]


class ChatRequest(BaseModel):
    """Payload request pertanyaan dari klien."""
    question: str = Field(min_length=1, max_length=500, description="Pertanyaan seputar panduan akademik")
    filters: Optional[ChatFilter] = None


class ChatResponse(BaseModel):
    """Format response API tanya jawab RAG."""
    status: str = Field(description="answered, not_found, atau needs_clarification")
    answer: str
    sources: List[CitationSource] = Field(default_factory=list)
    mode: Optional[ChatFilter] = Field(default=None, description="Filter yang dipakai backend")
    clarification: Optional[ClarificationInfo] = None
