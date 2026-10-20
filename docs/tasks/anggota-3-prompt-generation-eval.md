# Panduan Kerja & Context Prompt: Anggota 3 - Devi (Prompting, Generasi NLG, Evaluasi & UI)

Dokumen ini memuat batasan tugas & alur kerja Anggota 3 (Devi).

---

## 1. Profil & Tanggung Jawab

- **Nama**: Devi
- **Peran**: Prompt Engineer, NLG & Evaluation Specialist
- **Fokus NLP**: Rekayasa Prompt (*Prompt Engineering*), Pembelajaran Berbasis Konteks (*In-Context Learning*), Mitigasi Halusinasi, dan Evaluasi Sistem Tanya Jawab (*QA Evaluation Metrics*).
- **Kepemilikan Berkas & Folder**:
  - `backend/app/services/prompt.py`
  - `backend/app/services/generate.py`
  - `scripts/evaluate.py`
  - `frontend/` (antarmuka web chat untuk demo)

---

## 2. Rincian Scope Kerja

1. **Rekayasa Prompt & Anti-Halusinasi (`prompt.py`)**:
   - Merancang template *system prompt* yang mengunci instruksi agar model menjawab **HANYA** berdasarkan konteks teks panduan yang diberikan.
   - Menginstruksikan LLM membalas persis: `"Informasi tidak ditemukan di panduan."` jika konteks kosong atau tidak memuat jawaban.
   - Meminta format balasan yang memuat teks jawaban dan ID chunk yang dipakai untuk membentuk sitasi halaman resmi.
2. **Layanan Generasi Jawaban (`generate.py`)**:
   - Integrasi ke Google Gemini LLM API (membaca API key dari konfigurasi).
   - Menangani error pemanggilan API dan timeout.
   - Mem-parsing jawaban akhir dan memetakan ID chunk ke sitasi nomor halaman PDF.
3. **Skrip Evaluasi Chatbot (`scripts/evaluate.py`)**:
   - Membaca daftar pertanyaan uji beserta kunci jawaban dan nomor halaman referensi dari buku panduan.
   - Menguji akurasi sistem secara kuantitatif:
     - Berapa persen pertanyaan dijawab dengan benar (*accuracy*).
     - Berapa persen sitasi nomor halaman tepat (*citation accuracy*).
     - Berapa persen pertanyaan di luar cakupan berhasil ditolak (*rejection rate*).
4. **Antarmuka Web Sederhana (`frontend/`)**:
   - Membangun antarmuka chat sederhana dan responsif di folder `frontend/`.
   - Mengirim request `POST /api/v1/chat` ke server FastAPI backend.
   - Menampilkan balon chat pertanyaan dan jawaban.
   - Menampilkan tombol badge sitasi sumber halaman (`sources`). Jika badge diklik, tampilkan modal/tooltip berisi kutipan teks panduan aslinya.

---

## 3. Context Prompt

```markdown
Konteks Proyek:
Anda adalah asisten coding untuk proyek "umb-academic-guide-rag", sebuah chatbot RAG Panduan Akademik Universitas Mercu Buana (UMB).
Repo ini publik: JANGAN PERNAH menaruh API key, password, kredensial, atau rahasia ke dalam berkas apa pun. Semua panggilan LLM dilakukan di backend.

Peran & Batasan Saya:
Saya adalah Devi (Anggota 3: Prompt Engineering, NLG, Evaluasi & UI Chat).
Tanggung jawab saya HANYA pada penyusunan prompt, pemanggilan LLM generate, skrip evaluasi akurasi, dan antarmuka web:
- Berkas saya: backend/app/services/prompt.py, backend/app/services/generate.py, scripts/evaluate.py, dan seluruh folder frontend/.
- JANGAN mengubah modul database (db.py), embedding (embedding.py), retrieval (retrieval.py), atau skrip data preprocessing (extract.py, clean.py, chunk.py).
- ATURAN NLP: Prompt harus membatasi jawaban mutlak pada konteks (anti-halusinasi). Jika informasi tidak ada, balas persis "Informasi tidak ditemukan di panduan." tanpa sumber. Sitasi nomor halaman harus merujuk ke halaman PDF dokumen asli.
- Konvensi: Python dengan type hints, Pydantic untuk respon, antarmuka web minimalis & rapi, dan jangan gunakan em dash.

Dokumen Rujukan Wajib:
1. AGENTS.md (aturan umum dan batasan prompt).
2. docs/api-contract.md (format kontrak JSON request/response chat).
3. docs/sdd.md bagian 8 (desain prompt & mitigasi halusinasi).
4. docs/evaluation-plan.md (metrik akurasi jawaban dan sitasi).

Tugas Saat Ini:
Bantu saya merancang template prompt anti-halusinasi di backend/app/services/prompt.py dan fungsi pemanggilan Gemini generate di backend/app/services/generate.py yang mengembalikan jawaban beserta sitasi nomor halaman.
```
