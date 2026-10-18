# UMB Academic Guide RAG

Chatbot tanya jawab Panduan Akademik Universitas Mercu Buana (UMB) Tahun Akademik 2025/2026. Jawaban hanya berasal dari isi panduan dan disertai sitasi nomor halaman. Jika informasi tidak ada di panduan, chatbot menolak menjawab.

Proyek kelompok mata kuliah Natural Language Processing, S1 Teknik Informatika, Universitas Mercu Buana.

> Status: dalam pengembangan. Bagian yang belum selesai ditandai "menyusul".

## Cara kerja singkat

Sistem memakai pendekatan RAG (Retrieval-Augmented Generation), yaitu "AI menjawab sambil membuka buku":

1. Panduan dipotong menjadi bagian kecil (chunk), diberi label (halaman, bagian, fakultas, prodi), lalu diubah menjadi vektor (embedding).
2. Saat pengguna bertanya, sistem mencari chunk yang paling relevan dengan filter metadata.
3. LLM menyusun jawaban hanya dari chunk tersebut.
4. Antarmuka web menampilkan jawaban beserta sumber halaman.

## Teknologi

- Backend: Python, FastAPI
- Database: PostgreSQL dengan pgvector
- Embedding dan LLM: Google Gemini API
- Frontend: web (menyusul)
- Deploy: Railway (backend dan database), Vercel atau Netlify (frontend)

## Struktur repositori

```
backend/    # FastAPI dan pipeline RAG
frontend/   # antarmuka web (menyusul)
data/       # data mentah (tidak di-commit), data bersih, dan chunk
scripts/    # skrip preprocessing, ingest, dan evaluasi
docs/       # dokumentasi proyek
```

## Dokumentasi

- [Spesifikasi data](docs/data-spec.md)
- [Kontrak API](docs/api-contract.md)
- [Software Design Document](docs/sdd.md)
- [Product Requirements Document](docs/prd.md)
- [Rencana evaluasi](docs/evaluation-plan.md)
- [Catatan keputusan](docs/decisions.md)

## Data

PDF Panduan Akademik TIDAK disertakan di repositori ini. Unduh dari sumber resmi UMB (Biro Administrasi Akademik, baa.mercubuana.ac.id), lalu letakkan di `data/raw/`. Folder tersebut diabaikan oleh git.

Scope yang dipakai: halaman 14 sampai 98, ditambah tabel akreditasi di halaman 11. Rincian ada di [spesifikasi data](docs/data-spec.md).

## Menjalankan proyek

Menyusul. Bagian ini akan diisi setelah setup selesai, dengan langkah:

1. Menyiapkan lingkungan Python dan dependensi.
2. Menjalankan PostgreSQL dengan pgvector lewat Docker.
3. Mengisi file `.env`.
4. Menjalankan skrip ingest untuk memasukkan chunk ke database.
5. Menjalankan server FastAPI.
6. Menjalankan evaluasi.

### Variabel environment

Salin `.env.example` menjadi `.env`, lalu isi nilainya. Jangan pernah meng-commit file `.env`.

| Variabel | Keterangan |
|---|---|
| `GEMINI_API_KEY` | Kunci API Gemini |
| `DATABASE_URL` | URL koneksi PostgreSQL |
| `EMBEDDING_MODEL` | Model embedding |
| `EMBEDDING_DIM` | Dimensi vektor (harus sama dengan kolom database) |
| `LLM_MODEL` | Model Gemini untuk menyusun jawaban |
| `TOP_K` | Jumlah chunk yang diambil |
| `SIMILARITY_THRESHOLD` | Ambang kemiripan minimum |
| `ALLOWED_ORIGINS` | Domain frontend yang diizinkan (CORS) |

## Tim

Proyek kelompok Natural Language Processing. Daftar anggota dan peran: menyusul.