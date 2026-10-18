# Spesifikasi Data (docs/data-spec.md)

Kesepakatan format data antara tim preprocessing dan backend RAG. Versi 2, diperbarui setelah PDF diperiksa langsung.

Label status:
- **Final**: sudah diputuskan.
- **Usulan**: belum diputuskan tim.
- **Terverifikasi**: sudah dicek langsung ke PDF (sampel halaman).
- **Cek PDF**: wajib diverifikasi ke dokumen asli sebelum dipakai.

## 1. Tujuan

- Menetapkan bentuk data di setiap tahap, dari PDF mentah sampai chunk siap embedding.
- Menjadi acuan tunggal untuk nama field, nilai metadata yang valid, dan aturan pembersihan.
- Perubahan dokumen ini harus diberitahukan ke seluruh tim, karena memengaruhi skrip ingest dan filter pencarian.

## 2. Sumber dan scope

- Dokumen: Panduan Akademik Program Diploma Tiga dan Program Sarjana UMB, Tahun Akademik 2025/2026. File: `3_-Buku-Panduan-Program-Sarjana-Reguler-1-Ganjil-2025-2026.pdf`. Seluruh tim wajib memakai file yang sama persis. (Terverifikasi: 105 halaman, ukuran A4, lapisan teks tersedia, bukan hasil scan.)
- Dalam scope (Final): halaman 14 sampai 98, ditambah tabel akreditasi di halaman 11.
- Di luar scope (Final): halaman 1 sampai 10, 12 sampai 13, dan 99 sampai 105.
- **Acuan nomor halaman (Final): nomor halaman PDF.** Terverifikasi: nomor cetak sama dengan nomor halaman PDF pada semua halaman yang disampel (11, 12, 14, 17 sampai 19, 24 sampai 27, 63 sampai 67, 94, 98, 100). Skrip validasi tetap harus mengecek ini di seluruh halaman scope.
- Halaman 13, 26, dan 99 adalah halaman pembatas bagian (hampir kosong). Lewati saat ekstraksi.

Peta halaman:

| Halaman | Isi | Status |
|---|---|---|
| 11 | Tabel status dan peringkat akreditasi | Terverifikasi |
| 13 | Pembatas "Ketentuan Pelaksanaan Pembelajaran" | Terverifikasi |
| 14 sampai 25 | Regulasi akademik | Terverifikasi (batas), isi per halaman Cek PDF |
| 26 | Pembatas "Program Diploma Tiga dan Program Sarjana" | Terverifikasi |
| 27 sampai 40 | FDSK | Cek PDF (awal halaman 27 terverifikasi) |
| 41 sampai 62 | FT | Cek PDF |
| 63 sampai 70 | Fasilkom (visi misi di hal. 64, kurikulum TI mulai sekitar hal. 66) | Terverifikasi sebagian |
| 71 sampai 83 | FEB | Cek PDF |
| 84 sampai 93 | Fikom | Cek PDF |
| 94 sampai 98 | FPsi | Terverifikasi (batas) |
| 99 | Pembatas "Penerimaan Mahasiswa Baru" | Terverifikasi |

## 3. Tahapan data (Final)

| Tahap | Folder | Isi | Git |
|---|---|---|---|
| Mentah | `data/raw/` | PDF asli dan teks hasil ekstraksi per halaman | Di-ignore |
| Bersih | `data/clean/` | Teks per halaman setelah pembersihan | Boleh di-commit bila kecil |
| Chunk | `data/chunks/` | Chunk beserta metadata, siap embedding | Boleh di-commit |

Tahap berikutnya tidak boleh menimpa tahap sebelumnya. Semua tahap dapat dibuat ulang lewat skrip.

## 4. Aturan ekstraksi dan pembersihan (Usulan, finalkan setelah uji lebih banyak halaman)

Temuan dari PDF (Terverifikasi pada halaman sampel):

- **Halaman regulasi berkolom dua** (contoh: hal. 17, 19, 25). Mode `pdftotext -layout` mengacak urutan baris antar kolom. Ekstraksi tanpa `-layout`, atau memotong halaman menjadi separuh kiri dan kanan lalu membaca kiri dulu, memberi urutan benar (diuji pada hal. 17). Jangan pakai `-layout` untuk halaman regulasi.
- **Tabel akreditasi (hal. 11)**: `pdfplumber extract_tables()` memecahnya menjadi enam potongan dan kolom status hilang. `pdftotext -layout` menghasilkan baris rapi (nama, status, peringkat). Gunakan hasil ini, atau ketik manual ke CSV, lalu verifikasi manual.
- **Halaman kurikulum**: tiap mata kuliah punya kode, nama Indonesia, nama Inggris, dan SKS. Posisi kode tidak konsisten (kadang di atas nama, kadang di antara nama Indonesia dan Inggris). Pemasangan kode dengan mata kuliah wajib dicek visual, jangan dipercaya otomatis.

Lakukan:
- Ekstrak teks per halaman dan simpan nomor halaman.
- Buang header, footer, dan nomor halaman cetak yang berulang.
- Gabungkan kata yang terpotong di akhir baris dan baris yang patah di tengah kalimat.
- Rapikan spasi ganda, karakter aneh, dan simbol bullet yang rusak.

Jangan lakukan:
- Stopword removal, stemming, atau lowercase total.
- Mengubah angka, SKS, semester, kode, nama mata kuliah, atau istilah resmi.
- Memperbaiki isi sumber yang tampak keliru, termasuk salah ketik (contoh: judul tabel hal. 11 tertulis "PRINGKAT"). Catat saja untuk dibahas.

## 5. Skema chunk

Satu chunk satu objek. Format file: JSON Lines, UTF-8 (Usulan). Field yang tidak relevan diisi `null`, bukan dihilangkan.

| Field | Tipe | Wajib | Keterangan |
|---|---|---|---|
| `id` | string | Ya | Unik. Usulan: `{jenis_konten}-{halaman}-{urut}` |
| `konten` | string | Ya | Teks yang di-embed dan ditampilkan sebagai kutipan |
| `halaman` | integer | Ya | Nomor halaman PDF |
| `bagian` | string | Ya | `Regulasi`, `Kurikulum`, `Profil`, atau `Akreditasi` |
| `jenis_konten` | string | Ya | Lihat bagian 6 |
| `topik` | string | Untuk aturan | Judul topik, misalnya "Tata Tertib UAS" |
| `fakultas` | string | Untuk kurikulum, profil, akreditasi | Kode fakultas |
| `program_studi` | string | Untuk kurikulum, akreditasi | Nama prodi persis seperti di sumber |
| `jenjang` | string | Untuk kurikulum, akreditasi | Lihat bagian 6 |
| `mata_kuliah` | string | Untuk mata kuliah | Nama Indonesia |
| `nama_inggris` | string | Untuk mata kuliah | Nama Inggris |
| `kode_mk` | string | Untuk mata kuliah | Contoh: `W152500028` |
| `semester` | integer | Untuk mata kuliah, ringkasan semester | 1 sampai 8 |
| `sks` | integer | Untuk mata kuliah | Jumlah SKS |
| `peringkat_akreditasi` | string | Untuk akreditasi | Nilai persis dari tabel |

## 6. Nilai valid

`bagian`: `Regulasi`, `Kurikulum`, `Profil`, `Akreditasi`.

`jenis_konten`:
- `aturan`: pasal atau topik regulasi.
- `mata_kuliah`: satu mata kuliah.
- `visi_misi`: visi dan misi fakultas atau prodi.
- `akreditasi`: satu baris tabel akreditasi.
- `ringkasan_semester`: daftar mata kuliah satu semester satu prodi (Usulan).

`fakultas`: `FDSK`, `FT`, `Fasilkom`, `FEB`, `Fikom`, `FPsi`.

`jenjang`: `Institusi`, `Diploma Tiga`, `Sarjana`, `Magister`, `Doktor`, `Profesi` (Terverifikasi dari tabel hal. 11).

`peringkat_akreditasi` yang muncul di tabel hal. 11 (Terverifikasi): `Unggul`, `Baik Sekali`, `Baik`, `A`, `B`, `Sementara`. Kolom status berisi "Terakreditasi" pada baris yang terbaca.

### Nama program studi

Nama di tabel akreditasi hal. 11 (Terverifikasi), untuk D3 dan Sarjana:
- FEB: Manajemen Perusahaan (D3), Akuntansi (D3), Manajemen (Sarjana), Akuntansi (Sarjana).
- Teknik: Teknik Sipil, Arsitektur, Teknik Mesin, Teknik Elektro, Teknik Industri (semua Sarjana).
- Ilmu Komunikasi: satu entri "Ilmu Komunikasi (Program Sarjana)".
- Ilmu Komputer: Teknik Informatika, Sistem Informasi (Sarjana).
- Psikologi: Psikologi (Sarjana).
- Desain dan Seni Kreatif: Desain Produk, Desain Interior, Desain Komunikasi Visual (Sarjana).

Tabel yang sama juga memuat baris Magister, Doktor, dan Profesi (sekitar 31 baris seluruhnya, termasuk institusi).

**Belum terverifikasi (Cek PDF):**
- Ringkasan proyek menyebut empat prodi Fikom (Penyiaran, Hubungan Masyarakat, Periklanan, Komunikasi Digital), sedangkan tabel akreditasi hanya menyebut satu entri Ilmu Komunikasi. Cek halaman 84 sampai 93.
- Ringkasan menyebut "16 prodi"; daftar di ringkasan berjumlah 18. Hitung ulang dari halaman kurikulum, lalu samakan di semua dokumen.
- Ejaan nama prodi di halaman kurikulum bisa berbeda dari tabel akreditasi. Pakai ejaan persis sumber di masing-masing konteks, dan buat tabel pemetaan nama bila berbeda.

## 7. Aturan chunking (Final, kecuali ditandai)

| Jenis konten | Ukuran chunk | Alasan |
|---|---|---|
| Aturan | 1 pasal atau 1 topik | Harus dibaca utuh |
| Mata kuliah | 1 mata kuliah | Unit terkecil yang bermakna |
| Visi misi | 1 bagian (satu fakultas) | Pendek, tidak perlu dipecah |
| Akreditasi | 1 baris tabel | Pertanyaan spesifik per prodi |

- Halaman multi-topik (misalnya hal. 17) dipecah per topik, bukan per halaman.
- Chunk akreditasi ditulis sebagai kalimat utuh yang menyebut prodi, jenjang, status, dan peringkat. Cantumkan bahwa data berasal dari Panduan Akademik 2025/2026 karena akreditasi punya masa berlaku.
- Hindari chunk melebihi batas input model embedding (lihat bagian 9).

## 8. Contoh chunk

Nilai pada contoh akreditasi dan kode mata kuliah diambil dari PDF. Nilai `semester` NLP belum diverifikasi.

```json
{"id": "aturan-18-01", "konten": "Peserta ujian yang melanggar tata tertib...", "halaman": 18, "bagian": "Regulasi", "jenis_konten": "aturan", "topik": "Tata Tertib UAS", "fakultas": null, "program_studi": null, "jenjang": null, "mata_kuliah": null, "nama_inggris": null, "kode_mk": null, "semester": null, "sks": null, "peringkat_akreditasi": null}
```

```json
{"id": "mata_kuliah-67-01", "konten": "Natural Language Processing (Natural Language Processing), kode W152500028, 3 SKS, Program Studi Teknik Informatika.", "halaman": 67, "bagian": "Kurikulum", "jenis_konten": "mata_kuliah", "topik": null, "fakultas": "Fasilkom", "program_studi": "Teknik Informatika", "jenjang": "Sarjana", "mata_kuliah": "Natural Language Processing", "nama_inggris": "Natural Language Processing", "kode_mk": "W152500028", "semester": null, "sks": 3, "peringkat_akreditasi": null}
```

```json
{"id": "akreditasi-11-01", "konten": "Program Studi Teknik Informatika (Program Sarjana) berstatus Terakreditasi dengan peringkat Unggul, menurut Panduan Akademik 2025/2026.", "halaman": 11, "bagian": "Akreditasi", "jenis_konten": "akreditasi", "topik": null, "fakultas": "Fasilkom", "program_studi": "Teknik Informatika", "jenjang": "Sarjana", "mata_kuliah": null, "nama_inggris": null, "kode_mk": null, "semester": null, "sks": null, "peringkat_akreditasi": "Unggul"}
```

## 9. Keputusan yang masih terbuka

- **Cakupan baris akreditasi**: semua baris (institusi, D3, Sarjana, Magister, Doktor, Profesi) atau hanya D3 dan Sarjana. Menentukan jumlah chunk dan pertanyaan uji.
- **Model embedding dan dimensi vektor**: menentukan batas panjang chunk dan kolom `vector`. Diputuskan di SDD.
- **Data kurikulum**: chunk vektor, tabel SQL biasa, atau keduanya. Catatan: kode mata kuliah tidak konsisten posisinya, jadi biaya parsing tinggi apa pun pilihannya.
- **Format file chunk**: JSON Lines (usulan) atau CSV.
- **Visi misi tingkat prodi**: apakah dipisah dari visi misi fakultas.

## 10. Validasi kualitas

Otomatis (wajib):
- Field wajib terisi dan nilainya ada di daftar nilai valid.
- `id` unik.
- Teks `konten` ada di halaman yang tertulis di `halaman`.
- Jumlah chunk akreditasi sama dengan jumlah baris tabel yang diputuskan masuk scope.
- Format `kode_mk` konsisten (huruf awalan diikuti angka) dan tidak ada kode ganda dalam satu prodi.
- Chunk tidak kosong dan tidak melebihi batas panjang.
- Laporan ringkas: jumlah halaman, jumlah chunk per jenis, dan daftar chunk yang gagal.

Manual:
- Periksa sampel acak minimal 15 sampai 20 persen chunk terhadap PDF asli.
- Verifikasi seluruh tabel akreditasi dan pemasangan kode, nama, dan SKS pada halaman kurikulum secara visual.
- Nilai chunk yang batasnya meragukan.

## Riwayat perubahan

- v2: acuan halaman ditetapkan (nomor PDF), field `jenjang`, `kode_mk`, `nama_inggris`, `peringkat_akreditasi` ditambahkan, temuan ekstraksi kolom dan tabel dicatat, daftar prodi disesuaikan dengan tabel hal. 11, contoh chunk memakai data nyata.
- v1: draf awal dari ringkasan proyek.