# AGENTS.md

Konteks proyek untuk agent coding. Baca seluruh file ini sebelum mengubah apa pun.
Repo ini PUBLIK. Jangan pernah menaruh API key, kredensial, atau data pribadi di file apa pun.

## 1. Ringkasan proyek

Chatbot RAG (Retrieval-Augmented Generation) untuk tanya jawab Panduan Akademik
Universitas Mercu Buana (UMB) Tahun Akademik 2025/2026. Jawaban hanya boleh berasal
dari isi panduan dan harus disertai sitasi nomor halaman.

- Konteks: proyek kelompok mata kuliah Natural Language Processing (S1 Teknik Informatika).
- Tujuan utama: belajar dan menunjukkan pipeline NLP yang dievaluasi dengan baik.
  Bukan produk komersial. Jaga kompleksitas tetap rendah, jangan overkill.
- Pemilik backend dan RAG: satu anggota tim. Anggota lain mengerjakan preprocessing data,
  frontend, dan evaluasi, lalu melanjutkan setelah backend selesai.
- Dataset: `3_-Buku-Panduan-Program-Sarjana-Reguler-1-Ganjil-2025-2026.pdf` (105 halaman,
  lapisan teks tersedia, bukan hasil scan). Semua orang memakai file yang sama persis.

## 2. Status keputusan

Jangan menganggap "Usulan" atau "Terbuka" sebagai perintah.

### Final
- Sistem: RAG, inti pipeline ditulis native (chunking, embedding, pencarian, prompt).
- LLM dan embedding: Google Gemini lewat API. Tanpa GPU, model lokal, atau fine-tuning.
- Database: PostgreSQL + pgvector (Docker lokal, Railway untuk deploy).
- Backend: Python + FastAPI.
- Antarmuka: frontend web kustom (dikerjakan anggota lain). Telegram Bot TIDAK dipakai.
- Scope dokumen: halaman 14 sampai 98, ditambah tabel akreditasi di halaman 11.
- Dikecualikan: halaman 1 sampai 10, 12 sampai 13, dan 99 sampai 105.
- Acuan nomor halaman untuk data, sitasi, dan evaluasi: NOMOR HALAMAN PDF. Nomor cetak
  sama dengan nomor PDF pada halaman yang sudah disampel. Validasi harus mengecek ini
  di seluruh halaman scope.
- Tidak dibuat: login, aplikasi mobile, dashboard admin, tool calling, analisis sentimen
  (dilarang oleh dosen), fine-tuning.

### Usulan (tanyakan sebelum menerapkan)
- Data kurikulum (mata kuliah, semester, SKS) disimpan di tabel SQL biasa dan dicari
  dengan SQL, bukan pencarian vektor.
- Ambang skor kemiripan: di bawah ambang, jawab "tidak ditemukan" tanpa memanggil LLM.
- Chunk `ringkasan_semester` per semester per prodi untuk pertanyaan "daftar mata kuliah".
- Format file chunk: JSON Lines (UTF-8).

### Terbuka (JANGAN diputuskan sendiri, tanya pemilik repo)
- Model embedding: `gemini-embedding-2` atau `gemini-embedding-001`, beserta dimensi vektor.
- Nama model LLM Gemini untuk penyusun jawaban.
- Library akses database (psycopg, SQLAlchemy, atau lainnya) dan versi Python.
- Endpoint tambahan di luar chat (misalnya cek kesehatan layanan).
- Cakupan baris tabel akreditasi: semua jenjang atau hanya D3 dan Sarjana.
- Jumlah dan daftar program studi (ringkasan lama menyebut 16, daftar awal berjumlah 18),
  termasuk apakah Fikom punya satu atau empat prodi. Belum diverifikasi ke halaman kurikulum.

## 3. Struktur folder

- `backend/` : FastAPI dan pipeline RAG (area kerja utama agent).
- `frontend/` : milik anggota lain. Jangan diubah tanpa diminta.
- `data/raw/` : PDF dan teks mentah. DI-IGNORE git. Baca saja, jangan pernah ditimpa.
- `data/clean/` : teks hasil pembersihan.
- `data/chunks/` : chunk beserta metadata.
- `scripts/` : skrip preprocessing (extract.py, clean.py, chunk.py), ingest.py, dan evaluate.py.
- `docs/` : dokumen proyek (data-spec.md, api-contract.md, sdd.md, prd.md, evaluation-plan.md, decisions.md ada di folder docs).

## 4. Alur sistem

Persiapan data (sekali jalan): ekstrak teks per halaman, bersihkan, chunk, beri label,
embedding, simpan ke pgvector.

Saat pengguna bertanya: frontend kirim JSON ke FastAPI, backend embed pertanyaan, cari
vektor dengan filter metadata, ambil 3 sampai 5 chunk terdekat, kirim ke LLM, kembalikan
jawaban beserta sumber (halaman dan kutipan chunk).

## 5. Aturan data

Sumber kebenaran skema chunk, nilai valid, dan aturan pembersihan: `docs/data-spec.md`.
Jika file ini bertentangan dengan data-spec, ikuti data-spec lalu laporkan konfliknya.

- Simpan tiga tahap terpisah: mentah, bersih, chunk. Jangan menimpa tahap sebelumnya.
- Preprocessing untuk RAG = bersihkan tanpa mengubah makna. JANGAN lakukan stopword
  removal, stemming, atau lowercase total sebelum embedding.
- Jangan mengubah angka, SKS, semester, kode mata kuliah, nama, atau istilah resmi.
  Jangan memperbaiki salah ketik di sumber (contoh: judul tabel hal. 11 tertulis
  "PRINGKAT"). Catat saja.
- Field wajib setiap chunk: `id`, `konten`, `halaman`, `bagian`, `jenis_konten`.
  Field lain (`topik`, `fakultas`, `program_studi`, `jenjang`, `mata_kuliah`,
  `nama_inggris`, `kode_mk`, `semester`, `sks`, `peringkat_akreditasi`) diisi sesuai
  jenis konten, dan bernilai `null` bila tidak relevan. Jangan menghilangkan field.
- Aturan chunking: satu pasal atau topik, satu mata kuliah, satu visi misi per fakultas,
  satu baris tabel akreditasi. Halaman multi-topik dipecah per topik.
- Validasi otomatis wajib: teks chunk ada di halaman yang tertulis di labelnya, `id` unik,
  nilai metadata ada di daftar valid, format `kode_mk` konsisten. Laporkan yang gagal,
  jangan diam-diam memperbaikinya.
- Jangan mengarang nomor halaman, isi pasal, kode, atau data tabel. Jika ragu, tandai
  untuk diperiksa manusia.

## 6. Aturan ekstraksi PDF (hasil pemeriksaan dataset)

- Lewati halaman pembatas bagian: 13, 26, dan 99.
- Halaman regulasi berkolom dua. JANGAN pakai `pdftotext -layout` untuk halaman ini
  karena baris antar kolom teracak. Pakai ekstraksi tanpa `-layout`, atau potong halaman
  jadi separuh kiri dan kanan (pdfplumber crop) lalu baca kiri dulu. Baru diuji di hal. 17,
  uji halaman lain sebelum dianggap aman.
- Tabel akreditasi (hal. 11): `pdfplumber extract_tables()` memecahnya dan kolom status
  hilang. Gunakan `pdftotext -layout` untuk halaman ini atau input manual ke CSV, lalu
  verifikasi manual. Tabel memuat sekitar 31 baris dari semua jenjang.
- Halaman kurikulum: tiap mata kuliah punya kode, nama Indonesia, nama Inggris, dan SKS,
  dengan posisi kode yang tidak konsisten. Pemasangan kode dengan mata kuliah harus dicek
  visual (rasterisasi halaman), jangan dipercaya otomatis.
- Selalu uji skrip pada satu halaman contoh dulu, bandingkan dengan PDF, baru jalankan
  ke seluruh halaman.

## 7. Aturan RAG dan Gemini

- Satu model embedding dan satu dimensi untuk seluruh data. Dimensi kolom `vector`
  harus sama dengan dimensi embedding. Ganti model atau dimensi berarti embed ulang semuanya.
- `gemini-embedding-001` memakai parameter `task_type`. `gemini-embedding-2` tidak
  mendukung `task_type`; instruksi tugas ditulis sebagai prefiks pada teks (format berbeda
  untuk query dan dokumen). Cek dokumentasi resmi Gemini sebelum menulis kode embedding.
- Prompt LLM wajib membatasi jawaban pada konteks. Jika konteks kosong atau tidak relevan,
  balas persis: "Informasi tidak ditemukan di panduan." Jangan memakai pengetahuan lain.
- Jika jawaban "tidak ditemukan", jangan kembalikan sumber.
- Filter metadata (SQL WHERE) dijalankan sebelum pencarian vektor.
- API key dibaca dari environment variable. Semua panggilan LLM lewat backend,
  tidak pernah dari frontend.

## 8. Aturan kerja agent

Lakukan:
- Kerja bertahap: buat dan uji satu halaman contoh atau satu endpoint dulu, baru perluas.
- Jelaskan singkat apa yang diubah dan kenapa, lalu sebutkan cara mengujinya.
- Jalankan ulang skrip dan tes setelah mengubah kode, dan laporkan hasil sebenarnya.
- Pakai file Python biasa (`.py`), bukan notebook (`.ipynb`).
- Tulis skrip yang dapat dijalankan ulang (idempotent) dan tidak merusak data.
- Perbarui `.env.example` jika menambah variabel environment baru (tanpa nilai rahasia).

Jangan:
- Menimpa atau menghapus isi `data/raw/`.
- Meng-commit `.env`, API key, atau PDF mentah.
- Menambah fitur di luar scope (lihat "Tidak dibuat").
- Memutuskan hal yang berstatus "Terbuka" atau "Usulan". Tanyakan dulu.
- Menambah dependensi besar (misalnya LangChain) tanpa izin. Hanya jika kode mulai
  berantakan dan pemilik repo setuju.
- Menyembunyikan error atau mengubah tes agar lolos.
- Mengubah folder `frontend/` atau kontrak API tanpa diminta.

## 9. Konvensi kode

- Python dengan type hints. Fungsi pendek dengan satu tanggung jawab.
- Validasi request dan response API dengan Pydantic.
- Konfigurasi (nama model, dimensi, ambang, jumlah chunk) di satu tempat konfigurasi,
  bukan tersebar di kode.
- Atur CORS dengan origin eksplisit (bukan `*` saat deploy), timeout klien lebih panjang
  dari timeout backend, dan gunakan connection pool untuk database.
- Catat (log) pertanyaan, chunk yang diambil, dan skor kemiripan untuk evaluasi,
  tanpa menyimpan data pribadi.
- Komentar dan docstring singkat. Nama variabel dalam bahasa Inggris.

## 10. Evaluasi (agar kode siap diuji)

Rencana: 80 sampai 120 pertanyaan uji dengan kunci jawaban (halaman PDF), termasuk
pertanyaan di luar cakupan dan beberapa pertanyaan akreditasi. Metrik: hit rate di 3
teratas, ketepatan jawaban, ketepatan sitasi, persentase penolakan benar. Pembanding:
LLM tanpa data lawan RAG, dan dua strategi chunking. Rancang kode agar pengaturan
chunking dan jumlah chunk mudah diganti untuk eksperimen.

## 11. Dokumen rujukan

Jika ada konflik antara file ini dan dokumen lain, hentikan dan tanyakan ke pemilik repo.
Ada: `docs/data-spec.md`. Ada: `docs/api-contract.md`. Ada: `docs/sdd.md`. Ada: `docs/prd.md`.
Ada: `docs/evaluation-plan.md`. Ada: `docs/decisions.md`. Ada: `README.md`.

## 12. Perintah umum

Diisi setelah setup selesai (install dependensi, jalankan Docker dan database, ingest data,
jalankan server, jalankan evaluasi).