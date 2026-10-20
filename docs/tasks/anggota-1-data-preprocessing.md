# Panduan Kerja & Context Prompt: Anggota 1 - Nauval (Pra-pengolahan Data & Korpus Teks)

Dokumen ini memuat batasan tugas & alur kerja Anggota 1 (Nauval).

---

## 1. Profil & Tanggung Jawab

- **Nama**: Nauval
- **Peran**: Data Preprocessing & Corpus Engineer
- **Fokus NLP**: Normalisasi Teks (*Text Normalization*), Ekstraksi Tata Letak (*Layout Extraction*), Segmentasi Dokumen (*Logical Chunking*), dan Pelabelan Metadata Korpus.
- **Kepemilikan Berkas & Folder**:
  - `scripts/extract.py`
  - `scripts/clean.py`
  - `scripts/chunk.py`
  - `data/raw/` (PDF dan teks mentah hasil ekstraksi)
  - `data/clean/` (teks per halaman setelah pembersihan)
  - `data/chunks/` (chunk JSON Lines siap embedding)

---

## 2. Rincian Scope Kerja

1. **Ekstraksi PDF (`scripts/extract.py`)**:
   - Mengekstrak teks dari `data/raw/3_-Buku-Panduan-Program-Sarjana-Reguler-1-Ganjil-2025-2026.pdf`.
   - Scope halaman: 14 sampai 98, ditambah tabel akreditasi di halaman 11.
   - Lewati halaman pembatas: 13, 26, dan 99.
   - Mengatasi layout 2 kolom (contoh hal. 17): jangan gunakan `pdftotext -layout` karena baris antar kolom akan teracak. Ekstrak tanpa `-layout` atau potong kolom kiri lalu kanan.
   - Tabel akreditasi (hal. 11): diekstrak khusus (via layout rapi atau input manual ke CSV).
   - Menyimpan teks mentah per nomor halaman PDF asli di `data/raw/`.
2. **Pembersihan Teks (`scripts/clean.py`)**:
   - Membuang header, footer, dan nomor halaman cetak yang berulang.
   - Menyambung kata yang terpotong tanda hubung di akhir baris dan baris yang patah di tengah kalimat.
   - **ATURAN KERAS NLP**:
     - DILARANG melakukan *stopword removal*, *stemming*, atau *lowercase* total sebelum embedding.
     - DILARANG mengubah angka, semester, SKS, kode mata kuliah, atau istilah resmi.
     - DILARANG membetulkan salah ketik sumber (misal kata "PRINGKAT"), cukup catat saja.
   - Menyimpan hasil teks bersih per halaman di `data/clean/`.
3. **Chunking & Anotasi Metadata (`scripts/chunk.py`)**:
   - Memotong teks bersih menjadi unit logis:
     - 1 pasal atau 1 topik regulasi per chunk.
     - 1 mata kuliah per chunk kurikulum.
     - 1 visi misi fakultas per chunk.
     - 1 baris tabel akreditasi per chunk.
   - Memberi label metadata lengkap sesuai skema di `docs/data-spec.md` bagian 5:
     `{"id": "...", "konten": "...", "halaman": 14, "bagian": "Regulasi", "jenis_konten": "aturan", ...}`.
   - Menyimpan hasil akhir dalam format **JSON Lines (UTF-8)** di `data/chunks/`.

---

## 3. Context Prompt

```markdown
Konteks Proyek:
Anda adalah asisten coding untuk proyek "umb-academic-guide-rag", sebuah chatbot RAG Panduan Akademik Universitas Mercu Buana (UMB).
Repo ini publik: JANGAN PERNAH menaruh API key, password, kredensial, atau rahasia ke dalam berkas apa pun. File PDF asli di data/raw/ diabaikan oleh git.

Peran & Batasan Saya:
Saya adalah Nauval (Anggota 1: Data Preprocessing & Chunking).
Tanggung jawab saya HANYA pada ekstraksi teks PDF, pembersihan teks, dan pembuatan chunk JSON Lines:
- Berkas saya: scripts/extract.py, scripts/clean.py, scripts/chunk.py, serta folder data/raw/, data/clean/, dan data/chunks/.
- JANGAN menyentuh folder backend/ atau frontend/.
- JANGAN menyentuh skrip ingest.py atau evaluate.py.
- ATURAN NLP: Jangan lakukan stopword removal, stemming, atau lowercase total. Jangan ubah angka, SKS, kode MK, atau membetulkan typo sumber. Kalimat harus utuh untuk keperluan embedding.
- Konvensi: Python dengan type hints, fungsi pendek, idempotent (dapat dijalankan ulang tanpa merusak data), dan jangan gunakan em dash.

Dokumen Rujukan Wajib:
1. AGENTS.md (aturan umum dan batasan data).
2. docs/data-spec.md (acuan mutlak: scope halaman, aturan ekstraksi 2 kolom, skema JSON Lines, dan nilai valid).

Tugas Saat Ini:
Bantu saya mengimplementasikan dan menguji scripts/extract.py pada satu halaman sampel regulasi (halaman 17) dan tabel akreditasi (halaman 11) secara bertahap dan terverifikasi.
```
