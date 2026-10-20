# Panduan Kerja & Context Prompt: Anggota 2 - Zidan (Retrieval, Database & Backend Core)

Dokumen ini memuat batasan tugas & alur kerja Anggota 2 (Zidan).

---

## 1. Profil & Tanggung Jawab

- **Nama**: Zidan
- **Peran**: Backend & Dense Retrieval Engineer
- **Fokus NLP**: Representasi Vektor (*Dense Embeddings*), Ruang Vektor Semantik, dan Temu Balik Informasi (*Vector Information Retrieval*).
- **Kepemilikan Berkas & Folder**:
  - `backend/app/services/embedding.py`
  - `backend/app/services/retrieval.py`
  - `backend/app/services/pipeline.py`
  - `backend/app/db.py`
  - `backend/app/config.py`
  - `backend/app/main.py`
  - `scripts/ingest.py`
  - `docker-compose.yml`

---

## 2. Rincian Scope Kerja

1. **Setup Database Vektor**:
   - Menjalankan PostgreSQL dengan ekstensi `pgvector` via Docker Compose.
   - Merancang skema tabel `chunks` (id, konten, halaman, bagian, jenis_konten, topik, fakultas, program_studi, jenjang, embedding vector) dan koneksi pool di `backend/app/db.py`.
2. **Layanan Embedding (`embedding.py`)**:
   - Integrasi Google Gemini Embedding API.
   - Mengelola format prefiks (query vs dokumen) dan dimensi vektor sesuai konfigurasi terpusat.
3. **Skrip Ingest (`scripts/ingest.py`)**:
   - Membaca berkas chunk JSON Lines dari `data/chunks/`.
   - Meng-embed isi teks chunk dan melakukan upsert ke tabel pgvector.
4. **Layanan Temu Balik / Retrieval (`retrieval.py`)**:
   - Menerima teks pertanyaan dan filter metadata.
   - Menghitung kemiripan kosinus (*cosine distance*) di pgvector digabung dengan filter SQL WHERE.
   - Mengambil Top-K chunk terdekat (default K=5).
5. **Orkestrasi Pipeline & Endpoint API (`pipeline.py`, `main.py`)**:
   - Menghubungkan alur retrieval ke alur prompt/generate (yang dibuat Anggota 3 - Devi).
   - Menyediakan endpoint `POST /api/v1/chat` sesuai kontrak API.

---

## 3. Context Prompt

```markdown
Konteks Proyek:
Anda adalah asisten coding untuk proyek "umb-academic-guide-rag", sebuah chatbot RAG Panduan Akademik Universitas Mercu Buana (UMB).
Repo ini publik: JANGAN PERNAH menaruh API key, password, kredensial, atau rahasia ke dalam berkas apa pun. Baca nilai dari environment variable via backend/app/config.py.

Peran & Batasan Saya:
Saya adalah Zidan (Anggota 2: Backend Core & Retrieval).
Tanggung jawab saya HANYA pada backend, database pgvector, embedding, retrieval, dan ingest:
- Berkas saya: backend/app/services/embedding.py, retrieval.py, pipeline.py, backend/app/db.py, config.py, main.py, scripts/ingest.py, dan docker-compose.yml.
- JANGAN mengubah skrip data preprocessing (extract.py, clean.py, chunk.py) di folder scripts/.
- JANGAN mengubah frontend/ atau logika prompt/generate milik Devi (Anggota 3).
- Konvensi: Python dengan type hints, fungsi pendek, Pydantic untuk validasi, nama variabel bahasa Inggris, dan jangan gunakan em dash.

Dokumen Rujukan Wajib:
1. AGENTS.md (aturan umum dan batasan proyek).
2. docs/sdd.md bagian 6 (desain database chunks & query SQL) dan bagian 7 (spesifikasi model embedding).
3. docs/api-contract.md (kontrak endpoint chat).

Tugas Saat Ini:
Bantu saya mengimplementasikan modul koneksi database pgvector di backend/app/db.py, integrasi Gemini embedding di backend/app/services/embedding.py, dan skrip ingest di scripts/ingest.py secara bertahap dan teruji.
```
