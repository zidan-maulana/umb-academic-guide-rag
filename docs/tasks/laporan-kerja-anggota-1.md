# Laporan Hasil Kerja: Anggota 1 (Nauval - Data Preprocessing & Korpus Teks)

Dokumen ini mendokumentasikan hasil implementasi dan verifikasi pipeline pra-pengolahan data untuk proyek **UMB Academic Guide RAG**.

---

## 1. Ringkasan Eksekutif

Pipeline pra-pengolahan data telah selesai dibangun dari hulu ke hilir secara idempotent (dapat dijalankan ulang tanpa merusak data) menggunakan skrip Python native dan terverifikasi 100% terhadap dokumen asli `3.-Buku-Panduan-Program-Sarjana-Reguler-1-Ganjil-2025-2026.pdf`.

- **Skrip Implementasi**:
  - `scripts/extract.py` (Ekstraksi teks per halaman dengan penanganan layout 2 kolom & tabel)
  - `scripts/clean.py` (Pembersihan & normalisasi teks tanpa merusak semantik/aturan NLP)
  - `scripts/chunk.py` (Logical chunking, skema Pydantic, metadata enrichment, & validasi)
- **Output Korpus Akhir**:
  - `data/chunks/academic_guide_chunks.jsonl` (Total: **1.303 chunk**, format JSON Lines UTF-8)

---

## 2. Rincian Hasil Tahapan Kerja

### Tahap 1: Ekstraksi Teks PDF (`scripts/extract.py`)
- **Total Halaman Scope**: 85 halaman (Halaman 11 + Halaman 14 s/d 98).
- **Halaman Dilewati (Skip)**: Halaman pembatas bab 13, 26, dan 99.
- **Halaman Luar Scope (Ignore)**: Halaman 1–10, 12, dan 100–105.
- **Penanganan Layout Khusus**:
  - *Regulasi (Hal. 14–25)*: Menggunakan teknik *page cropping* vertikal (`pdfplumber`) membelah koordinat halaman menjadi kolom kiri dan kanan untuk mencegah teracaknya baris horizontal.
  - *Footer Margin*: Margin bawah 45 pt dipotong otomatis untuk mengeliminasi nomor halaman cetak repetitif.
  - *Tabel Akreditasi (Hal. 11)*: Mengekstrak seluruh 31 baris tabel akreditasi lengkap.
- **Penyimpanan**: 85 berkas tersimpan di `data/raw/page_{nomor:03d}.txt`.

### Tahap 2: Pembersihan Teks (`scripts/clean.py`)
- **Aturan NLP yang Ditegakkan**:
  - Tanpa *stopword removal*, tanpa *stemming*, dan tanpa *lowercase* total (menjaga struktur sintaksis alami untuk model embedding modern).
  - Angka, semester, SKS, kode MK, dan istilah resmi dipertahankan 100%.
  - Typo sumber seperti kata `PRINGKAT` pada tabel hal. 11 dipertahankan dan dicatat dalam log sistem.
- **Normalisasi Tata Letak & Karakter**:
  - Normalisasi artefak drop-shadow font judul (misal `FFAAKKUULLTTAASS` menjadi `FAKULTAS`).
  - Normalisasi karakter bullet anomali/korup menjadi format markdown `- `.
  - Simbol akademis/matematis (`≥`, `∑`) dipertahankan.
  - *De-hyphenation* cerdas yang menyambung pemenggalan kata tanpa merusak reduplikasi bahasa Indonesia (`lain-lain`, `sekurang-kurangnya`).
  - *Line unwrapping* terkontrol khusus pada paragraf regulasi tanpa memecah daftar poin `(1)`, `(2)`, `a.`, `b.`.
- **Penyimpanan**: 85 berkas tersimpan di `data/clean/page_{nomor:03d}.txt`.

### Tahap 3: Segmentasi Logis (Chunking) & Metadata (`scripts/chunk.py`)
- **Skema Chunk**: Memenuhi 15 field standar `docs/data-spec.md` Section 5 dengan validasi Pydantic:
  `id`, `konten`, `halaman`, `bagian`, `jenis_konten`, `topik`, `fakultas`, `program_studi`, `jenjang`, `mata_kuliah`, `nama_inggris`, `kode_mk`, `semester`, `sks`, `peringkat_akreditasi`. Field yang tidak relevan diisi `null`.
- **Statistik Korpus Akhir**:
  | Jenis Konten | Bagian | Jumlah Chunk | Keterangan |
  |---|---|---|---|
  | `akreditasi` | Akreditasi | 31 chunk | 1 chunk per baris tabel akreditasi hal. 11 |
  | `aturan` | Regulasi | 15 chunk | 1 chunk per topik/pasal regulasi akademik |
  | `visi_misi` | Profil | 6 chunk | 1 chunk per fakultas (FDSK, FT, Fasilkom, FEB, Fikom, FPsi) |
  | `mata_kuliah` | Kurikulum | 1.109 chunk | 1 chunk per mata kuliah (nama ID, EN, kode MK, SKS, sem, prodi) |
  | `ringkasan_semester` | Kurikulum | 142 chunk | 1 chunk daftar mata kuliah per semester per prodi |
  | **TOTAL** | - | **1.303 chunk** | Tersimpan di `data/chunks/academic_guide_chunks.jsonl` |

---

## 3. Hasil Validasi Kualitas Data
Validasi otomatis dijalankan per aturan `docs/data-spec.md` Section 10:
1. **Unikitas ID**: 100% ID chunk (1.303) unik tanpa duplikasi.
2. **Kelengkapan Konten**: Tidak ada chunk dengan konten kosong.
3. **Format Kode MK**: Seluruh kode mata kuliah valid dengan format standar `[A-Z]\d{8,9}`.
4. **Kesesuaian Ingest**: Format baris JSON Lines valid dan kompatibel penuh dengan `scripts/ingest.py` (Anggota 2).

---

## 4. Panduan Menjalankan Ulang Pipeline (Reproducibility)

Jika sewaktu-waktu dataset perlu diekstrak dan dibuat ulang dari awal:

```bash
# 1. Ekstraksi teks dari PDF ke data/raw/
python scripts/extract.py --all

# 2. Pembersihan teks dari data/raw/ ke data/clean/
python scripts/clean.py --all

# 3. Chunking dan pembuatan korpus JSON Lines ke data/chunks/
python scripts/chunk.py
```
