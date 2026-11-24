# Dokumen Konteks Proyek End-to-End: UMB Academic Guide RAG

Dokumen ini disusun sebagai **referensi tunggal yang komprehensif** untuk memberikan pemahaman menyeluruh, detail, dan mendalam mengenai proyek **Chatbot RAG Panduan Akademik Universitas Mercu Buana (UMB) Tahun Akademik 2025/2026**. Dokumen ini dirancang agar dapat dibaca oleh model kecerdasan buatan (LLM) maupun pengembang perangkat lunak untuk memahami seluruh aspek arsitektur, pipeline data, spesifikasi teknis, aturan NLP, dan pembagian tugas dalam repositori ini.

---

## 1. Identitas & Ringkasan Eksekutif

- **Nama Proyek**: Chatbot RAG Panduan Akademik UMB (T.A. 2025/2026)
- **Repositori**: `zidan-maulana/umb-academic-guide-rag` (Publik di GitHub)
- **Konteks**: Tugas Besar Kelompok Mata Kuliah Natural Language Processing (NLP), Program Studi S1 Teknik Informatika, Fakultas Ilmu Komputer, Universitas Mercu Buana.
- **Tujuan Utama**: Membangun dan mendemonstrasikan sistem tanya jawab berbasis dokumen resmi menggunakan arsitektur **Retrieval-Augmented Generation (RAG)** yang dievaluasi secara kuantitatif, ilmiah, dan terukur.
- **Filosofi Rekayasa**:
  - **Bukan produk komersial**: Mengutamakan kesederhanaan, transparansi kode, dan efisiensi arsitektur.
  - **Native Implementation**: Komponen inti RAG (chunking, embedding, retrieval, penyusunan prompt) ditulis secara native tanpa framework monolitik besar seperti LangChain atau LlamaIndex, agar seluruh alur pemrosesan NLP dapat dipahami dan diuji secara modular.
  - **Zero Tolerance on Hallucination**: Model LLM diinstruksikan secara ketat untuk HANYA menjawab berdasarkan konteks dokumen yang ditemukan. Jika informasi tidak ada di panduan, sistem wajib menolak dan menjawab: `"Informasi tidak ditemukan di panduan."`.
  - **Ketertelusuran Fakta (Grounded Citations)**: Setiap klaim jawaban wajib menyertakan nomor halaman resmi dokumen asli (PDF) beserta kutipan teksnya.

---

## 2. Dokumen Sumber & Ruang Lingkup (Scope)

### 2.1. Karakteristik Dokumen Sumber
- **Nama Berkas**: `3_-Buku-Panduan-Program-Sarjana-Reguler-1-Ganjil-2025-2026.pdf`
- **Lokasi**: `data/raw/` (dikecualikan dari Git tracking / `.gitignore`).
- **Spesifikasi Fisik**: 105 halaman, ukuran A4, dokumen digital berbasis teks langsung (bukan hasil scan/OCR), tata letak regulasi berkolom dua (*two-column layout*).

### 2.2. Batasan Ruang Lingkup Dokumen (Scope)
| Kategori | Cakupan Halaman | Status | Keterangan |
|---|---|---|---|
| **In-Scope (Wajib)** | Halaman 11 | Final | Tabel Status dan Peringkat Akreditasi Program Studi (±31 baris). |
| **In-Scope (Wajib)** | Halaman 14 s.d. 25 | Final | Ketentuan Pelaksanaan Pembelajaran & Regulasi Akademik (KRS, KPRS, UAS, Cuti, Masa Studi, Sanksi, Evaluasi Kelulusan). |
| **In-Scope (Wajib)** | Halaman 27 s.d. 98 | Final | Profil Fakultas, Visi-Misi, Struktur Kurikulum, Daftar Mata Kuliah, Kode MK, SKS, dan Distribusi Semester (FDSK, FT, Fasilkom, FEB, Fikom, FPsi). |
| **Out-of-Scope (Dilewati)** | Halaman 1 s.d. 10 | Final | Sampul, Kata Pengantar, Sambutan Rektor, Daftar Isi, Mars/Himne Kampus. |
| **Out-of-Scope (Dilewati)** | Halaman 12 s.d. 13 | Final | Halaman kosong & lembar pembatas bagian regulasi. |
| **Out-of-Scope (Dilewati)** | Halaman 26 & 99 | Final | Lembar pembatas bagian fakultas dan pembatas PMB. |
| **Out-of-Scope (Dilewati)** | Halaman 100 s.d. 105 | Final | Informasi Penerimaan Mahasiswa Baru (PMB), biaya kuliah, dan lampiran akhir. |

### 2.3. Kebenaran Mutlak Nomor Halaman
- **Nomor Halaman PDF adalah Acuan Tunggal**: Berdasarkan audit verifikasi visual dokumen asli, nomor halaman cetak (*printed page*) identik 1:1 dengan nomor halaman PDF pada seluruh halaman scope.
- Sistem tidak memerlukan offset/konversi halaman. Angka `halaman` pada metadata chunk dan sitasi merujuk langsung ke nomor halaman PDF.

---

## 3. Arsitektur Sistem & Alur End-to-End

Arsitektur sistem dibagi menjadi dua pipeline utama: **Data Preparation Pipeline** (offline/batch) dan **Runtime RAG Pipeline** (online/real-time).

```
========================================================================================
                          PIPELINE 1: DATA PREPARATION (BATCH)
========================================================================================
 [data/raw/*.pdf]
       │
       ▼
 [scripts/extract.py]  ──> Ekstraksi per kolom (Regulasi) & layout parsing (Tabel Hal. 11)
       │
       ▼
 [data/clean/*.txt]    ──> Normalisasi teks (tanpa stemming / tanpa stopword removal)
       │
       ▼
 [scripts/chunk.py]    ──> Segmentasi logis (pasal, matkul, visi-misi, akreditasi) + Metadata
       │
       ▼
 [data/chunks/*.jsonl] ──> Validasi skema data-spec (Pydantic / JSON schema)
       │
       ▼
 [scripts/ingest.py]   ──> Embedding via Gemini Embedding 2 (768d) + Upsert ke PostgreSQL
       │
       ▼
 [PostgreSQL + pgvector] (Tabel: `chunks`)

========================================================================================
                           PIPELINE 2: RUNTIME RAG (REAL-TIME)
========================================================================================
 [Frontend Web Chat (UI)]
       │
       │ HTTP POST /api/v1/chat  {"question": "...", "filters": {...}}
       ▼
 [FastAPI Backend]
       │
       ├──> 1. Request Validation (Pydantic ChatRequest, batas maks 500 karakter)
       │
       ├──> 2. Filter Extraction / Pre-filtering (bagian, fakultas, prodi, jenjang)
       │
       ├──> 3. Query Embedding (Gemini Embedding 2, 768 dimensi, task_type='RETRIEVAL_QUERY')
       │
       ├──> 4. SQL Metadata Filtering + Vector Cosine Distance (<=>) di pgvector
       │        (Ambil top_k kandidat, default: 5)
       │
       ├──> 5. Threshold Filter (Cosine Similarity >= 0.65)
       │        │
       │        ├──> Jika lolos: Bentuk context chunk untuk LLM
       │        └──> Jika di bawah threshold / kosong:
       │             Return status='not_found', "Informasi tidak ditemukan di panduan.", sources=[]
       │
       ├──> 6. Strict Anti-Hallucination Prompting (backend/app/services/prompt.py)
       │
       ├──> 7. LLM Answer Generation (Gemini 3.5 Flash Lite via backend/app/services/generate.py)
       │
       └──> 8. Response Packaging (Status, Answer, Sources berisikan ID chunk, halaman & kutipan)
       │
       ▼
 [Frontend Web Chat (UI)] ──> Tampilkan balon pesan + Badge Sitasi Halaman interaktif
```

---

## 4. Spesifikasi Data & Strategi Chunking

### 4.1. Prinsip Pembersihan Teks (Text Preprocessing)
- **Kaidah NLP untuk Dense Embedding**: Jangan melakukan *stopword removal*, *stemming*, atau *lowercasing* total. Model embedding transformer modern membutuhkan struktur kalimat, tanda baca, huruf kapital (nama institusi/fakultas/kode), dan relasi semantik lengkap.
- **Tindakan Pembersihan yang Dilakukan**:
  - Menghilangkan *running header*, *running footer*, dan nomor halaman cetak yang berulang.
  - Rekonstruksi kata yang terpotong tanda hubung di akhir baris (*hyphenation de-wrapping*).
  - Normalisasi *whitespace*, baris patah di tengah klausa, dan karakter unicode/bullet yang rusak.
  - Mempertahankan persis seluruh angka, semester, SKS, kode mata kuliah, dan peringkat akreditasi. Salah ketik pada dokumen asli (misal: tulisan "PRINGKAT" pada hal. 11) tidak diubah.

### 4.2. Strategi Chunking Berbasis Semantik (Logical Unit Chunking)
Dokumen tidak dipotong secara arbitrer menggunakan ukuran token statis (seperti fixed 500 tokens dengan 50 overlap), melainkan dipecah berdasarkan entitas logis dokumen:
1. **Jenis `aturan` (Bagian Regulasi)**: Satu chunk mewakili satu pasal utuh atau satu topik aturan (misalnya: aturan beban SKS maksimum, tata tertib ujian, syarat pengajuan cuti akademik).
2. **Jenis `mata_kuliah` (Bagian Kurikulum)**: Satu chunk mewakili satu entitas mata kuliah lengkap (Kode MK, Nama Indonesia, Nama Inggris, SKS, Semester penawaran).
3. **Jenis `visi_misi` (Bagian Profil)**: Satu chunk mewakili pernyataan visi dan misi lengkap satu fakultas/prodi.
4. **Jenis `akreditasi` (Tabel Halaman 11)**: Satu chunk mewakili satu baris program studi (Nama Prodi, Jenjang, Status Terakreditasi, Peringkat Akreditasi).
5. **Jenis `ringkasan_semester`**: Satu chunk merangkum paket kurikulum per semester untuk satu prodi (memudahkan pertanyaan umum seperti "Daftar mata kuliah semester 4 TI").

### 4.3. Format & Skema Metadata Chunk (JSON Lines)
Setiap chunk disimpan dalam format JSON Lines (`data/chunks/*.jsonl`) dengan skema berikut:

| Field | Tipe | Wajib | Keterangan & Aturan Nilai |
|---|---|---|---|
| `id` | string | Ya | Unik. Konvensi: `{jenis_konten}-{halaman}-{nomor_urut}` (misal: `aturan-17-01`, `akreditasi-11-02`, `mata_kuliah-67-05`). |
| `konten` | string | Ya | Teks deskriptif chunk yang di-embed dan menjadi rujukan jawaban. |
| `halaman` | integer | Ya | Nomor halaman PDF tempat teks berada (11, 14–98). |
| `bagian` | string | Ya | Salah satu dari: `Regulasi`, `Kurikulum`, `Profil`, `Akreditasi`. |
| `jenis_konten` | string | Ya | Salah satu dari: `aturan`, `mata_kuliah`, `visi_misi`, `akreditasi`, `ringkasan_semester`. |
| `topik` | string / null | Opsional | Topik aturan regulasi (misal: `"Tata Tertib Ujian Akhir Semester"`). |
| `fakultas` | string / null | Opsional | Nilai resmi: `FDSK`, `FT`, `Fasilkom`, `FEB`, `Fikom`, `FPsi`. |
| `program_studi`| string / null | Opsional | Nama program studi persis sesuai dokumen (misal: `"Teknik Informatika"`, `"Sistem Informasi"`). |
| `jenjang` | string / null | Opsional | Nilai resmi: `Institusi`, `Diploma Tiga`, `Sarjana`, `Magister`, `Doktor`, `Profesi`. |
| `mata_kuliah` | string / null | Opsional | Nama mata kuliah bahasa Indonesia (misal: `"Kecerdasan Buatan"`). |
| `nama_inggris` | string / null | Opsional | Nama mata kuliah bahasa Inggris (misal: `"Artificial Intelligence"`). |
| `kode_mk` | string / null | Opsional | Kode resmi mata kuliah (misal: `"W152500025"`). |
| `semester` | integer / null| Opsional | Semester penawaran mata kuliah (1 s.d. 8). |
| `sks` | integer / null| Opsional | Bobot SKS mata kuliah (1 s.d. 6). |
| `peringkat_akreditasi` | string / null | Opsional | Nilai: `Unggul`, `Baik Sekali`, `Baik`, `A`, `B`, `Sementara`. |

*Catatan: Seluruh field yang tidak relevan dengan suatu jenis konten wajib bernilai `null`, bukan dihilangkan.*

---

## 5. Desain Database & Vektor (PostgreSQL + pgvector)

### 5.1. Skema Tabel `chunks`
Skema dieksekusi di database PostgreSQL 16 dengan ekstensi `vector` aktif:

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS chunks (
    id TEXT PRIMARY KEY,
    konten TEXT NOT NULL,
    halaman INTEGER NOT NULL,
    bagian TEXT NOT NULL,
    jenis_konten TEXT NOT NULL,
    topik TEXT,
    fakultas TEXT,
    program_studi TEXT,
    jenjang TEXT,
    mata_kuliah TEXT,
    nama_inggris TEXT,
    kode_mk TEXT,
    semester INTEGER,
    sks INTEGER,
    peringkat_akreditasi TEXT,
    embedding vector(768),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Indeks B-Tree untuk pra-filter metadata cepat (Pre-filtering)
CREATE INDEX IF NOT EXISTS idx_chunks_bagian ON chunks(bagian);
CREATE INDEX IF NOT EXISTS idx_chunks_fakultas ON chunks(fakultas);
CREATE INDEX IF NOT EXISTS idx_chunks_program_studi ON chunks(program_studi);
CREATE INDEX IF NOT EXISTS idx_chunks_jenis_konten ON chunks(jenis_konten);
```

### 5.2. Keputusan Vektor & Indeks
1. **Model Embedding**: Google `gemini-embedding-2` dengan dimensi keluaran **768**.
2. **Karakteristik Indeks Vektor**: Pada volume data panduan akademik ini (berkisar antara 300 hingga 1.500 chunks), **indeks vektor perkiraan (seperti HNSW atau IVFFlat) sengaja tidak digunakan**.
   - *Alasan Teknis*: Pemindaian vektor eksak (*exact sequential scan*) dengan filter metadata hanya memakan waktu < 2 ms pada dataset ukuran ini, sekaligus menjamin akurasi temu-balik 100% tanpa risiko terpotongnya recall akibat interaksi antara filter SQL dan graph HNSW.
3. **Query Retrieval SQL**:
   ```sql
   SELECT id, konten, halaman, bagian, jenis_konten, topik, fakultas, program_studi, jenjang,
          1 - (embedding <=> %(vector)s) AS similarity
   FROM chunks
   WHERE (%(bagian)s::text IS NULL OR bagian = %(bagian)s)
     AND (%(fakultas)s::text IS NULL OR fakultas = %(fakultas)s)
     AND (%(program_studi)s::text IS NULL OR program_studi = %(program_studi)s)
     AND (%(jenjang)s::text IS NULL OR jenjang = %(jenjang)s)
   ORDER BY embedding <=> %(vector)s
   LIMIT %(limit)s;
   ```
   Operator `<=>` adalah *cosine distance* bawaan pgvector. Nilai kemiripan dikonversi menjadi *cosine similarity* melalui formula `1 - distance`.

---

## 6. Spesifikasi Kontrak API (FastAPI)

Semua rute beroperasi di bawah prefiks `/api/v1` menggunakan format payload JSON UTF-8.

### 6.1. Endpoint `POST /api/v1/chat`
Endpoint utama untuk menerima pertanyaan pengguna dan mengembalikan jawaban hasil augmentasi konteks.

#### Request Body
```json
{
  "question": "Berapa batas waktu studi untuk program sarjana?",
  "filters": {
    "bagian": "Regulasi",
    "fakultas": null,
    "program_studi": null,
    "jenjang": "Sarjana"
  }
}
```
*Validasi Pydantic:* `question` bertipe string (panjang 1–500 karakter). Objek `filters` bersifat opsional.

#### Response Body (200 OK — Status `answered`)
```json
{
  "status": "answered",
  "answer": "Berdasarkan Panduan Akademik UMB (Halaman 17), batas masa studi program sarjana adalah paling lama 7 (tujuh) tahun akademik atau 14 semester.",
  "sources": [
    {
      "id": "aturan-17-01",
      "halaman": 17,
      "bagian": "Regulasi",
      "kutipan": "Batas masa studi program sarjana: paling lama 7 (tujuh) tahun akademik atau 14 semester...",
      "jenis_konten": "aturan",
      "topik": "Batas Waktu Studi",
      "fakultas": null,
      "program_studi": null
    }
  ],
  "mode": {
    "bagian": "Regulasi",
    "fakultas": null,
    "program_studi": null,
    "jenjang": "Sarjana"
  },
  "clarification": null
}
```

#### Response Body (200 OK — Status `not_found`)
Terjadi ketika tidak ada chunk yang lolos ambang batas kesamaan (*similarity threshold* < 0.65) atau konteks tidak relevan:
```json
{
  "status": "not_found",
  "answer": "Informasi tidak ditemukan di panduan.",
  "sources": [],
  "mode": null,
  "clarification": null
}
```

### 6.2. Endpoint Pendukung
- **`GET /`**: Menampilkan ringkasan status API dan versi backend.
- **`GET /api/v1/health`**: Pemeriksaan kesehatan layanan, konektivitas database pool PostgreSQL, dan kesiapan aplikasi (penting untuk menangani *cold-start* di platform cloud seperti Railway).
- **`GET /api/v1/filters`**: Mengembalikan daftar resmi nilai filter yang valid (`fakultas`, `prodi`, `jenjang`, `bagian`) untuk komponen dropdown pada antarmuka frontend.

---

## 7. Rekayasa Prompt & Strategi Generasi (NLG)

Komponen generasi dipegang oleh Anggota 3 (Devi) pada modul `backend/app/services/prompt.py` dan `generate.py`.

### 7.1. Aturan Ketat System Prompt
1. **Strict In-Context Grounding**: LLM dilarang keras menggunakan pengetahuan umum di luar teks yang disertakan pada blok konteks.
2. **Exact Rejection Phrase**: Jika potongan konteks yang diberikan kosong atau tidak mengandung informasi yang cukup untuk menjawab pertanyaan secara pasti, LLM wajib membalas **persis**:
   ```
   Informasi tidak ditemukan di panduan.
   ```
   Tanpa salam tambahan, tanpa basa-basi pembuka/penutup, dan tanpa penjelasan mengapa informasi tersebut tidak ada.
3. **Format Sitasi Inline**: Ketika jawaban berhasil disusun, LLM wajib menyebutkan nomor halaman dokumen asli (contoh: `Berdasarkan Panduan Akademik UMB (Halaman 17): ...`).
4. **Preservasi Istilah Resmi**: LLM tidak boleh memparafrasekan atau mengubah istilah akademik resmi, kode mata kuliah, nama prodi, jumlah SKS, bobot nilai, atau sanksi administratif.

### 7.2. Model Generasi
- **Model**: Google Gemini Generasi 3.5 Flash Lite (`gemini-3.5-flash-lite`).
- **Parameter Inferensi**:
  - `temperature`: 0.0 (deterministik, meminimalkan kreativitas sintesis demi akurasi faktual).
  - `max_output_tokens`: 1024.

---

## 8. Rencana Evaluasi Ilmiah & Metrik NLP

Evaluasi kuantitatif membedakan proyek ini sebagai karya ilmiah NLP dari sekadar aplikasi rekayasa perangkat lunak. Evaluasi dipimpin oleh Anggota 3 bekerja sama dengan seluruh tim.

### 8.1. Dataset Uji (*Evaluation Benchmark*)
- Jumlah pertanyaan: **80 hingga 120 pertanyaan uji**.
- Format dataset: CSV / JSON Lines di `data/eval/`.
- Komposisi kategori:
  1. Regulasi Akademik (±30 butir): Syarat UAS, cuti, sanksi, batas masa studi.
  2. Kurikulum & SKS (±25 butir): Daftar mata kuliah, prasyarat, semester penawaran.
  3. Profil & Visi Misi (±8 butir): Visi keilmuan fakultas dan prodi.
  4. Akreditasi (±8 butir): Status dan peringkat akreditasi prodi dari halaman 11.
  5. Pertanyaan Ambigu (±8 butir): Pertanyaan lintas prodi tanpa subjek spesifik.
  6. Out-of-Scope / Penolakan (±15 butir): Pertanyaan umum kampus, birokrasi non-panduan, atau informasi di halaman pembuka/penutup yang dikecualikan.
- Pemisahan Data: Dibagi rata menjadi set **`dev`** (untuk tuning prompt & parameter) dan set **`test`** (hanya dijalankan sekali untuk pelaporan metrik akhir).
- Ground Truth: Kunci jawaban dan nomor halaman referensi diverifikasi langsung oleh manusia dari PDF asli.

### 8.2. Metrik Kuantitatif
1. **Hit@3 dan Hit@5 (Retrieval Precision)**: Persentase pertanyaan yang berhasil memunculkan minimal satu chunk dari halaman kunci jawaban pada peringkat 3 atau 5 teratas.
2. **Answer Accuracy (Factual Precision)**: Dinilai secara ketat (Benar / Sebagian / Salah). Kesalahan satu angka SKS atau kode mata kuliah dianggap Salah.
3. **Citation Accuracy**: Persentase jawaban benar yang seluruh sitasi halamannya tepat merujuk ke nomor halaman PDF referensi.
4. **Correct Rejection Rate**: Persentase pertanyaan di luar cakupan yang berhasil dijawab dengan status `not_found` / `"Informasi tidak ditemukan di panduan."`.
5. **False Rejection Rate**: Persentase pertanyaan sah dalam cakupan yang keliru ditolak oleh sistem.
6. **Latensi Sistem**: Median dan p95 waktu respons (detik).

### 8.3. Matriks Eksperimen Pembanding
- **E0 (Baseline No-RAG)**: LLM Gemini murni tanpa konteks dokumen (membuktikan halusinasi model umum).
- **E1 (Sistem Utama RAG Native)**: RAG berbasis chunking semantik logis + filter metadata.
- **E2 (Ablation Chunking)**: Membandingkan chunking logis vs fixed-size token chunking.
- **E3 (Parameter Tuning)**: Pengaruh variasi `TOP_K` (k=3 vs k=5) dan `SIMILARITY_THRESHOLD`.

---

## 9. Struktur Direktori Repositori

```
umb-academic-guide-rag/
├── .env.example                     # Contoh variabel lingkungan (tanpa rahasia)
├── .gitignore                        # Menjaga .env, data mentah, dan draft laporan
├── docker-compose.yml                # Setup PostgreSQL 16 + pgvector container lokal
├── README.md                         # Panduan umum proyek & instalasi
├── AGENTS.md                         # Aturan kerja, etika, dan batasan AI coding agent
│
├── backend/                          # Kode sumber backend API & Core RAG
│   ├── requirements.txt              # Dependensi Python (FastAPI, psycopg, google-genai, dll)
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                   # Inisialisasi FastAPI, CORS, middleware lifespan
│   │   ├── config.py                 # Manajemen konfigurasi Pydantic BaseSettings
│   │   ├── db.py                     # Connection pool psycopg & context manager DB
│   │   ├── schema.sql                # DDL tabel chunks & indeks PostgreSQL
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── router.py             # Rute endpoint API (/chat, /health, /filters)
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── chat.py               # Pydantic models (ChatRequest, ChatResponse, CitationSource)
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── embedding.py          # Modul pemanggil Google Gemini Embedding 2
│   │       ├── retrieval.py          # Logika SQL filtering & pgvector cosine similarity
│   │       ├── prompt.py             # Rekayasa system prompt & template context
│   │       ├── generate.py           # Integrasi pemanggil LLM Gemini & parsing output
│   │       └── pipeline.py           # Orkestrasi alur RAG (retrieval -> prompt -> generate)
│   └── tests/
│       └── test_api.py               # Pengujian otomatis endpoint backend via TestClient
│
├── data/                             # Manajemen korpus data
│   ├── raw/                          # PDF asli & teks mentah (DI-IGNORE git)
│   ├── clean/                        # Teks bersih per halaman
│   └── chunks/                       # Korpus JSON Lines chunk siap pakai & mock chunks
│
├── frontend/                         # Antarmuka web pengguna (HTML/CSS/JS native)
│
├── scripts/                          # Skrip otomatisasi tahapan data & evaluasi
│   ├── extract.py                    # Skrip ekstraksi teks dari PDF
│   ├── clean.py                      # Skrip pembersihan teks
│   ├── chunk.py                      # Skrip segmentasi teks menjadi chunks JSON Lines
│   ├── ingest.py                     # Skrip embedding batch & upsert ke PostgreSQL
│   └── evaluate.py                   # Skrip pengujian benchmark evaluasi kuantitatif
│
└── docs/                             # Dokumentasi arsitektur & panduan kerja
    ├── prd.md                        # Product Requirements Document
    ├── sdd.md                        # Software Design Document
    ├── data-spec.md                  # Spesifikasi data & skema metadata resmi
    ├── api-contract.md               # Kontrak pertukaran data API backend-frontend
    ├── evaluation-plan.md            # Rancangan pengujian ilmiah & metrik
    ├── decisions.md                  # Log catatan keputusan arsitektur (ADR)
    ├── project-context.md            # DOKUMEN INI (Konteks komprehensif end-to-end)
    └── tasks/                        # Pembagian tugas & context prompt per anggota
        ├── anggota-1-data-preprocessing.md
        ├── anggota-2-retrieval-backend.md
        ├── anggota-3-prompt-generation-eval.md
        └── laporan-kerja-anggota-2.md (diabaikan dari Git)
```

---

## 10. Pembagian Peran & Status Pengerjaan Tim

Proyek dikerjakan secara kolaboratif oleh tim 3 orang mahasiswa dengan pembagian batas kepemilikan kode yang tegas:

### 10.1. Anggota 1 — Nauval (Data Preprocessing & Corpus Engineer)
- **Kepemilikan Berkas**: `scripts/extract.py`, `scripts/clean.py`, `scripts/chunk.py`, `data/raw/`, `data/clean/`, `data/chunks/`.
- **Fokus Kerja**:
  - Ekstraksi teks dua kolom pada bagian regulasi tanpa mengacak baris antar kolom.
  - Ekstraksi dan verifikasi manual tabel akreditasi halaman 11.
  - Pembersihan teks korpus sesuai aturan `data-spec.md`.
  - Pembentukan file chunk akhir `data/chunks/chunks.jsonl` yang tervalidasi.
- **Status**: Sedang berjalan (*in progress*).

### 10.2. Anggota 2 — Zidan (Retrieval, Database & Backend Core)
- **Kepemilikan Berkas**: `backend/app/main.py`, `config.py`, `db.py`, `schema.sql`, `api/`, `schemas/`, `services/embedding.py`, `services/retrieval.py`, `services/pipeline.py`, `scripts/ingest.py`, `backend/tests/test_api.py`.
- **Fokus Kerja**:
  - Setup infrastruktur PostgreSQL 16 + pgvector di Docker lokal dan Railway.
  - Implementasi modul embedding (`gemini-embedding-2`, 768 dimensi, penanganan task prefix).
  - Pembangunan mekanisme database connection pooling (`psycopg_pool`).
  - Query retrieval dengan integrasi SQL pre-filtering dan pgvector cosine similarity.
  - Skrip ingest idempotent (`scripts/ingest.py`) dengan verifikasi integritas data.
  - Penyelarasan skema Pydantic dengan `api-contract.md`.
  - Pembuatan automated unit testing API (100% test passing).
- **Status**: **SELESAI & TELAH DI-MERGE KE BRANCH `main`** (Branch: `feat/backend-retrieval`).

### 10.3. Anggota 3 — Devi (Prompt Engineering, NLG, Evaluasi & Web UI)
- **Kepemilikan Berkas**: `backend/app/services/prompt.py`, `backend/app/services/generate.py`, `scripts/evaluate.py`, folder `frontend/`.
- **Fokus Kerja**:
  - Merancang sistem prompt anti-halusinasi dengan penguncian konteks ketat.
  - Menghubungkan modul generasi jawaban dengan Google Gemini LLM API (`gemini-3.5-flash-lite`).
  - Parsing output LLM untuk membentuk payload `sources` dengan kutipan teks dan halaman.
  - Menyusun 80–120 butir dataset pertanyaan uji beserta kunci jawaban manual.
  - Mengembangkan skrip otomatisasi evaluasi (`scripts/evaluate.py`) untuk menghitung metrik Hit@k, Accuracy, Citation Precision, dan Rejection Rate.
  - Membangun antarmuka web chat responsif yang menampilkan badge sitasi halaman dan modal kutipan teks.
- **Status**: Siap dikerjakan (Rekomendasi branch: `feat/prompt-generation-eval`).

---

## 11. Konfigurasi Lingkungan (*Environment Variables*)

Konfigurasi dibaca secara terpusat oleh Pydantic Settings pada [backend/app/config.py](file:///c:/Documents/Projects/umb-academic-guide-rag/backend/app/config.py) melalui berkas `.env`:

```env
# Google Gemini API Key (Wajib diisi di lokal, dilarang di-commit ke Git)
GEMINI_API_KEY=AIzaSy...

# Koneksi Database PostgreSQL + pgvector
# Lokal: postgresql://postgres:postgres@localhost:5432/umb_academic_rag
# Cloud: Disediakan oleh Railway Database Service
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/umb_academic_rag

# Model Vektor Embedding (Final: gemini-embedding-2, 768 dimensi)
EMBEDDING_MODEL=gemini-embedding-2
EMBEDDING_DIM=768

# Model LLM Penyusun Jawaban (Final: gemini-3.5-flash-lite)
LLM_MODEL=gemini-3.5-flash-lite

# Parameter Temu-Balik Dokumen
TOP_K=5
SIMILARITY_THRESHOLD=0.65

# Pengaturan CORS (Frontend Local & Production)
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

---

## 12. Aturan Kerja & Pedoman Operasional AI Coding Agent

Setiap model AI yang bertindak sebagai *coding agent* pada repositori ini **wajib mematuhi aturan baku berikut**:

1. **Keamanan Kredensial**: Repositori ini PUBLIK. Jangan pernah menulis, menyisipkan, atau meng-commit API key, token, kredensial basis data, atau berkas `.env` ke dalam kode atau dokumentasi publik.
2. **Integritas Folder Data**:
   - Berkas di `data/raw/` bersifat *read-only*. Jangan pernah menimpa, mengubah, atau menghapusnya.
   - Jangan melakukan *hardcode* teks kutipan palsu atau mengarang nomor halaman.
3. **Kepatuhan Terhadap Skema**:
   - Format pertukaran API wajib patuh 100% pada [docs/api-contract.md](file:///c:/Documents/Projects/umb-academic-guide-rag/docs/api-contract.md).
   - Skema chunk dan metadata wajib patuh 100% pada [docs/data-spec.md](file:///c:/Documents/Projects/umb-academic-guide-rag/docs/data-spec.md).
4. **Idempotensi Skrip**: Semua skrip batch (`ingest.py`, `evaluate.py`, dll) harus bersifat *idempotent* (dapat dijalankan berulang kali tanpa merusak, menggandakan, atau membuat data menjadi korup).
5. **Format Kode & Bahasa**:
   - Seluruh kode Python wajib menggunakan *type hints* lengkap.
   - Validasi data masukan/keluaran menggunakan Pydantic v2.
   - Nama variabel dan fungsi menggunakan bahasa Inggris teknis standar.
   - Pesan balasan API dan string antarmuka pengguna menggunakan bahasa Indonesia resmi.
6. **Hindari Over-Engineering**: Jaga kompleksitas kode tetap rendah. Jangan menambahkan dependensi eksternal besar tanpa persetujuan eksplisit dari pemilik repositori.
