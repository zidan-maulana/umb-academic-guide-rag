# Laporan Review & Audit Kualitas Korpus Preprocessing (Anggota 1 - Nauval)

Dokumen ini memuat audit teknis mendalam terhadap hasil pengerjaan pra-pengolahan data (ekstraksi, pembersihan, dan segmentasi chunk) dibandingkan dengan spesifikasi pada [docs/data-spec.md](file:///d:/NLP2/umb-academic-guide-rag/docs/data-spec.md), [AGENTS.md](file:///d:/NLP2/umb-academic-guide-rag/AGENTS.md), dan [docs/decisions.md](file:///d:/NLP2/umb-academic-guide-rag/docs/decisions.md).

Tanggal Audit: 28 Oktober 2026  
Auditor: Automated System Audit (Antigravity)  
Target Evaluasi:
- Skrip: `scripts/extract.py`, `scripts/clean.py`, `scripts/chunk.py`
- Output: `data/chunks/academic_guide_chunks.jsonl` (1.303 chunk), `data/clean/` (85 file)

---

## 1. Ringkasan Hasil Audit

| Area Evaluasi | Status | Catatan Utama |
|---|---|---|
| **Struktur Pipeline & Idempotensi** | **Lolos (100%)** | Struktur 3 tahap (`extract` -> `clean` -> `chunk`) berjalan independen dan idempotent sesuai D-16. |
| **Scope Halaman & Layout PDF** | **Lolos (100%)** | 85 halaman target (hal. 11 & 14-98) diekstrak benar, pemotongan footer 45 pt dan layout 2 kolom regulasi berjalan rapi. |
| **Kaidah NLP Pembersihan Teks** | **Lolos (100%)** | Tanpa stopword removal, tanpa stemming, tanpa lowercase total; angka, SKS, simbol (`≥`, `∑`), dan typo asli (`PRINGKAT`) dipertahankan. |
| **Skema Metadata Pydantic** | **Lolos (100%)** | 15 field standar terpenuhi, ID 100% unik, format kode MK valid (`[A-Z]\d{8,9}`). |
| **Segmentasi Regulasi (Aturan)** | **Perlu Perbaikan (Under-segmented)** | Hanya 15 chunk untuk 12 halaman; halaman multi-topik (hal. 14, 17, 18, 20) tergabung menjadi chunk terlalu besar (3.000+ karakter). |
| **Akurasi Parsing Kurikulum** | **Ditemukan Bug Parsing** | Ditemukan 16 MK dengan nama angka murni, 27 MK kehilangan SKS, dan salah pemetaan halaman 83 pada D3 Manajemen. |

---

## 2. Aspek yang Sudah Sesuai Ketentuan (Kekuatan)

1. **Kepatuhan Aturan NLP Modern untuk RAG (D-09)**:
   - Skrip `scripts/clean.py` berhasil mempertahankan integritas gramatikal teks asli tanpa menerapkan teknik NLP klasik yang merusak semantik (*stopword removal*, *stemming*, atau *lowercasing* total).
   - Simbol penting seperti tanda pertidaksamaan (`≥`) dan penjumlahan (`∑`) pada rumus masa belajar dan evaluasi studi tetap utuh.
   - Typo dokumen sumber pada tabel akreditasi hal. 11 (`PRINGKAT`) tidak diubah secara sepihak dan dicatat dalam log sistem.

2. **Ekstraksi Tata Letak Khusus (Section 4 data-spec)**:
   - Pemotongan vertikal 2 kolom (*left-right cropping*) pada halaman regulasi (14 s/d 25) sukses mencegah pencampuran baris horizontal antar kolom.
   - Pemotongan margin bawah 45 pt berhasil mengeliminasi nomor halaman cetak repetitif di footer dokumen.
   - Halaman pembatas bab (13, 26, dan 99) serta halaman di luar scope (1-10, 12, 100-105) di-skip dengan benar.

3. **Format Korpus & Kepatuhan Skema Data (Section 5 data-spec)**:
   - Output tersimpan dalam format **JSON Lines UTF-8** di `data/chunks/academic_guide_chunks.jsonl`.
   - Seluruh 1.303 objek chunk tervalidasi oleh Pydantic dengan 15 field wajib/opsional:
     `id`, `konten`, `halaman`, `bagian`, `jenis_konten`, `topik`, `fakultas`, `program_studi`, `jenjang`, `mata_kuliah`, `nama_inggris`, `kode_mk`, `semester`, `sks`, `peringkat_akreditasi`.
   - Field yang tidak relevan diisi `null` dan tidak dihapus dari JSON.

4. **Tabel Akreditasi & Visi Misi**:
   - Sebanyak 31 baris tabel akreditasi pada hal. 11 berhasil diekstrak menjadi 31 chunk kalimat naratif utuh (`akreditasi-11-01` s/d `akreditasi-11-31`).
   - Visi dan misi seluruh 6 fakultas (FDSK, FT, Fasilkom, FEB, Fikom, FPsi) berhasil dibentuk menjadi 6 chunk profil.

---

## 3. Temuan Anomali & Kekurangan Kritis

Berdasarkan audit langsung terhadap baris data pada file `data/chunks/academic_guide_chunks.jsonl`, ditemukan 4 permasalahan teknis yang membutuhkan perbaikan:

### A. Bug Nama Mata Kuliah Menjadi Angka Murni (16 Kasus)
- **Gejala**: Field `mata_kuliah` berisi angka string seperti `'3'` atau `'4'`.
- **Akar Masalah**: Pada tata letak kurikulum tertentu di PDF (khususnya Fasilkom hal. 67 dan 69), baris tepat sebelum kode mata kuliah adalah angka SKS yang berdiri sendiri dalam satu baris. Kode pada `scripts/chunk.py` baris 349:
  ```python
  nama_id = lines[i - 1]
  ```
  mengambil angka SKS tersebut sebagai nama mata kuliah bahasa Indonesia.
- **Daftar Kasus Nyata**:
  - `mata_kuliah-67-10` (Teknik Informatika, Hal 67): Kode `W152500001`, `mata_kuliah: "4"`. (Nama asli: **Metodologi Penelitian**, SKS: 4).
  - `mata_kuliah-67-11` (Teknik Informatika, Hal 67): Kode `W152500027`, `mata_kuliah: "3"`. (Nama asli: **Deep Learning**, SKS: 3).
  - `mata_kuliah-69-02` (Sistem Informasi, Hal 69): Kode `W182500006`, `mata_kuliah: "3"`. (Nama asli: **Konsep Sistem Basis Data**, SKS: 3).
  - `mata_kuliah-69-03` (Sistem Informasi, Hal 69): Kode `W182500007`, `mata_kuliah: "3"`. (Nama asli: **Arsitektur dan Organisasi**, SKS: 3).
  - `mata_kuliah-69-04` (Sistem Informasi, Hal 69): Kode `F062500001`, `mata_kuliah: "3"`. (Nama asli: **Matematika dan Statistik Dasar**, SKS: 3).
  - `mata_kuliah-69-05` (Sistem Informasi, Hal 69): Kode `U002500004`, `mata_kuliah: "2"`. (Nama asli: **Bahasa Inggris**, SKS: 2).
  - `mata_kuliah-69-06` s/d `mata_kuliah-69-14` (Sistem Informasi, Hal 69): Seluruhnya bernama angka `'3'` atau `'2'` (Matematika Bisnis, Konsep Dasar Pemrograman, Statistik dan Probabilitas, Sistem Informasi, Struktur Data, Manajemen Data, Audit SI, Pancasila, Manajemen Proses Bisnis).
  - `mata_kuliah-74-28` (Manajemen, Hal 74): Kode `U002500002`, `mata_kuliah: "3"`. (Nama asli: **Kewirausahaan**, SKS: 3).

---

### B. Bug SKS Hilang & Menempel di Nama Mata Kuliah (27 Kasus SKS None)
- **Gejala**: Field `sks: null` dan nama mata kuliah berakhiran angka SKS (misal `"Natural Language Processing 3"`).
- **Akar Masalah**: Pada hal. 67 dan 69, angka SKS tercetak di baris nama mata kuliah bahasa Indonesia, sementara baris kode MK hanya berisi kodenya saja. Pola deteksi SKS `scripts/chunk.py` hanya mencari angka di baris kode, sehingga SKS tidak terdeteksi dan angka SKS menempel pada nama.
- **Dampak Kritis**: Mata kuliah mata kuliah NLP sendiri terpengaruh langsung:
  - `mata_kuliah-67-20`: Kode `W152500028`, `mata_kuliah: "Natural Language Processing 3"`, `sks: null`.
  - Kasus lain di Hal 67: `Analitik Data 3`, `Pemrograman Web Enterprise 3`, `Pengolahan Citra 3`, `Kerja Praktek 3`, `Pemrograman Mobile 3`, `UI/UX Teknologi Digital Imersive 3`, `Sistem Informasi Geografis 3`, `Generative AI 3`.
  - Kasus lain di Hal 69: `Pendidikan Agama Islam 2`, `Pendidikan Agama Kristen 2`, `Bahasa Indonesia 2`, `Bisnis Digital 3`, `Rekayasa Perangkat Lunak 3`, `Aljabar Linier 3`, `Etika, Sosial dan Profesi 3`.

---

### C. Kesalahan Pemetaan Halaman pada `PAGE_MAPPING` Hal. 83 (Kurikulum D3)
- **Gejala**: Program studi D3 Manajemen Perusahaan hanya memiliki mata kuliah Semester 1 dan 2 (total 20 MK).
- **Akar Masalah**: Pada `scripts/chunk.py` baris 124, halaman 83 dipetakan sebagai:
  ```python
  83: ("FEB", "Akuntansi", "Diploma Tiga")
  ```
  Padahal setelah diverifikasi langsung ke berkas `data/clean/page_083.txt`, halaman 83 berisi kelanjutan **Kurikulum Manajemen Diploma Tiga Semester 3, 4, 5, dan 6** (mata kuliah: *Bahasa Mandarin, MICE Management Praktikum, Digital Marketing, PKL Magang, Tugas Akhir*).
- **Dampak**: 
  - Semester 3 s/d 6 D3 Manajemen Perusahaan hilang dan salah dilabeli sebagai Program Studi Akuntansi.
  - Program studi D3 Akuntansi di PDF sebenarnya tidak memiliki lembar kurikulum (hanya ada di tabel akreditasi hal. 11).

---

### D. Under-segmentation pada Regulasi Akademik (Hal. 14 s/d 25)
- **Gejala**: Hanya terbentuk **15 chunk regulasi** untuk 12 halaman regulasi akademik padat.
- **Akar Masalah**:
  1. `clean.py` menggabungkan baris paragraf, namun pada beberapa halaman judul topik tidak memiliki jeda double newline `\n\n`.
  2. `chunk.py` menggunakan batas ketat `len(first_line) < 50` dan daftar kata kunci regex terbatas.
- **Dampak**:
  - **Halaman 17 (3 topik besar)**: `Masa Belajar`, `KRS Online`, dan `Ujian Akhir Semester` digabung menjadi satu chunk raksasa `aturan-17-01` sepanjang **3.235 karakter**. Ini melanggar aturan spesifikasi data Section 7: *"Halaman multi-topik (misalnya hal. 17) dipecah per topik, bukan per halaman"*.
  - **Halaman 18 (2 topik)**: Topik `Pengumuman Daftar Hasil Studi Semester` terlewat dari regex dan tergabung ke dalam topik `Pelaksanaan UAS`.
  - **Halaman 20 (Typo & 2 topik)**: Heading terpotong `Penyusunan Tugas Akhi` (huruf 'r' terputus ke baris bawah akibat crop kolom) dan topik `Ujian Tugas Akhir` tergabung menjadi satu chunk.
  - **Halaman 23**: Topik menjadi default fallback `"Regulasi Akademik"` karena judul dan isi paragraf pertama menyatu sehingga panjangnya melebihi 50 karakter.
  - **Halaman 14**: Topik `Ketentuan Pelaksanaan`, `Kurikulum`, `Prinsip Pembelajaran`, `Semester`, dan `Kegiatan Akademik` tergabung dalam 1 chunk raksasa sepanjang **3.131 karakter**.

---

## 4. Klarifikasi Temuan Penting (Status Dokumen)

Berdasarkan pemeriksaan data bersih:
1. **Jumlah & Status Program Studi Fikom (Menjawab Terbuka data-spec Section 6)**:
   - Pada `page_084.txt`, tercatat struktur resmi:
     - Fakultas: **Fakultas Ilmu Komunikasi (FIKOM)**
     - Program Studi: **Ilmu Komunikasi (Program Sarjana)**
     - Bidang Studi (Peminatan): **Penyiaran**, **Hubungan Masyarakat**, **Periklanan**, **Komunikasi Digital**.
   - Kesimpulan: FIKOM hanya memiliki **1 Program Studi (Ilmu Komunikasi)** dengan 4 bidang peminatan. Hal ini sinkron 100% dengan baris tunggal akreditasi di halaman 11.
2. **Mata Kuliah Pilihan Tanpa Semester (51 Kasus)**:
   - Terdapat 51 mata kuliah (misal di FT Teknik Sipil hal. 46) yang berada di bawah blok "Mata Kuliah Pilihan" tanpa label semester. Nilai `semester: null` pada kasus ini sah dan sesuai spesifikasi data Section 5.

---

## 5. Rencana Perbaikan Kode (Action Plan)

Untuk mencapai kualitas korpus 100% bersih dan presisi tinggi sebelum proses embedding / ingest oleh Anggota 2 (Zidan), berikut perbaikan yang direkomendasikan pada `scripts/chunk.py`:

### 1. Perbaikan `PAGE_MAPPING` Halaman 83
Ubah baris 124 `scripts/chunk.py`:
```python
# SEBELUM:
83: ("FEB", "Akuntansi", "Diploma Tiga"),

# SESUDAH:
83: ("FEB", "Manajemen Perusahaan", "Diploma Tiga"),
```

### 2. Perbaikan Parsing Nama & SKS Mata Kuliah
Ubah logika ekstraksi pada `chunk_curriculum_page()` di `scripts/chunk.py`:
```python
# 1. Mundur baris jika nama_id adalah angka SKS murni
nama_id = lines[i - 1] if i > 0 else ""
if re.match(r"^[1-6]$", nama_id) and i > 1:
    sks_from_prev = int(nama_id)
    nama_id = lines[i - 2]
else:
    sks_from_prev = None

# 2. Tangani jika nama_id berakhiran angka SKS (misal "Natural Language Processing 3")
sks_match_in_name = re.search(r"^(.*?)\s+([1-6])$", nama_id)
if sks_match_in_name and not nama_id.startswith(("Matematika", "Fisika Dasar", "Praktikum")):
    nama_id = sks_match_in_name.group(1).strip()
    sks_from_name = int(sks_match_in_name.group(2))
else:
    sks_from_name = None

# 3. Tetapkan SKS final dengan prioritas
if not sks:
    sks = sks_from_prev or sks_from_name
```

### 3. Perbaikan Granularitas Chunk Regulasi
1. Pecah topik secara eksplisit pada halaman multi-topik:
   - Hal. 14: `Kurikulum`, `Prinsip Pembelajaran`, `Semester`, `Kegiatan Akademik`.
   - Hal. 17: `Masa Belajar`, `Pendaftaran KRS Online`, `Ujian Akhir Semester`.
   - Hal. 18: `Pelaksanaan UAS`, `Pengumuman KHS`.
   - Hal. 20: Rapikan typo `"Penyusunan Tugas Akhir"` dan pisahkan `"Ujian Tugas Akhir"`.
   - Hal. 23: Pastikan topik terdeteksi sebagai `"Evaluasi Keberhasilan Studi Mahasiswa"`.

---

Dokumen ini disusun untuk memastikan kesiapan korpus data sebelum dijalankan ke skrip ingest dan embedding oleh Anggota 2.
