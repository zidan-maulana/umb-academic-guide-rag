# Rencana Evaluasi (docs/evaluation-plan.md)

Cara mengukur kualitas chatbot RAG Panduan Akademik UMB. Versi 1 (draf).
Evaluasi adalah bagian yang membedakan proyek ini sebagai proyek NLP, bukan sekadar aplikasi.

Label status: **Final** (sudah diputuskan), **Usulan** (belum diputuskan), **Terbuka** (belum ada keputusan).

## 1. Tujuan evaluasi

- Mengukur seberapa tepat sistem menemukan bagian panduan yang benar (retrieval).
- Mengukur ketepatan jawaban dan ketepatan sitasi halaman.
- Mengukur kemampuan menolak pertanyaan di luar panduan tanpa mengarang.
- Membandingkan beberapa pilihan desain dengan data, bukan perasaan.

## 2. Dokumen terkait

- `docs/data-spec.md`: nomor halaman memakai nomor halaman PDF (Final).
- `docs/api-contract.md`: nilai `status` (`answered`, `not_found`, `needs_clarification`) dan bentuk `sources`.
- `docs/sdd.md`: konfigurasi yang dapat diganti (`TOP_K`, ambang, model, strategi chunking) dan tabel `query_logs`.

## 3. Set pertanyaan uji

Jumlah: 80 sampai 120 pertanyaan (Usulan). Di bawah sekitar 60, hasil kurang meyakinkan.

Sebaran awal (Usulan, sesuaikan dengan scope yang benar-benar selesai):

| Kategori | Jumlah awal | Contoh |
|---|---|---|
| Aturan (Regulasi) | sekitar 30 | Syarat mengikuti UAS, batas masa studi, prosedur cuti |
| Kurikulum | sekitar 25 | SKS satu mata kuliah, mata kuliah satu semester |
| Profil dan visi misi | sekitar 8 | Visi sebuah fakultas |
| Akreditasi | sekitar 8 | Peringkat akreditasi sebuah prodi |
| Ambigu antar prodi | sekitar 8 | "Apa mata kuliah NLP?" tanpa menyebut prodi |
| Di luar cakupan | sekitar 15 | Topik umum, atau isi di halaman yang dikecualikan |

Aturan penyusunan:
- Sertakan variasi bahasa: formal, santai, singkatan (KRS, UAS, SKS), dan salah ketik ringan, karena begitulah mahasiswa bertanya.
- Sertakan beberapa pertanyaan yang jawabannya tersebar di dua halaman.
- Pertanyaan di luar cakupan harus jelas tidak ada di scope. Sertakan juga pertanyaan yang tampak mirip topik panduan tetapi tidak dijawab di dalamnya.
- Jangan membuat pertanyaan hanya dengan menyalin kalimat dari panduan. Ubah susunan kata agar pencarian benar-benar diuji.

### Format file (Usulan: CSV atau JSON Lines di `data/eval/`)

| Kolom | Keterangan |
|---|---|
| `id` | Unik |
| `kategori` | Dari tabel di atas |
| `pertanyaan` | Teks pertanyaan |
| `jenis` | `dalam_cakupan`, `di_luar_cakupan`, atau `ambigu` |
| `jawaban_kunci` | Jawaban ringkas yang benar, ditulis manusia dari PDF |
| `halaman_kunci` | Satu atau beberapa nomor halaman PDF |
| `filter_benar` | Filter yang ideal (opsional) |
| `catatan` | Hal yang perlu diperhatikan penilai |
| `split` | `dev` atau `test` |

### Pembuatan kunci jawaban

- Kunci jawaban dan halaman kunci dibuat manusia dari PDF asli, bukan dari keluaran chatbot.
- Setiap kunci diperiksa oleh orang kedua. Perbedaan pendapat dibahas dan dicatat.
- Boleh memakai LLM untuk membantu mengusulkan pertanyaan, tetapi kuncinya tetap diverifikasi manusia.
- Pertanyaan dapat mulai disusun sekarang karena hanya membutuhkan PDF, tidak perlu menunggu sistem jadi.

## 4. Pembagian dev dan test

- Sekitar separuh pertanyaan menjadi `dev`, sisanya `test` (Usulan).
- Set `dev` dipakai untuk menyetel prompt, `TOP_K`, dan ambang kemiripan.
- Set `test` hanya dijalankan untuk hasil akhir di laporan. Jangan menyetel sistem berdasarkan hasil `test`, karena hasilnya jadi terlalu optimistis.
- Sebaran kategori pada `dev` dan `test` dibuat seimbang.

## 5. Metrik

| Metrik | Definisi | Dihitung pada |
|---|---|---|
| Hit@3 dan Hit@5 | Persentase pertanyaan dalam cakupan yang punya minimal satu chunk dari `halaman_kunci` di 3 atau 5 hasil teratas | Retrieval |
| Ketepatan jawaban | Jawaban dinilai `benar`, `sebagian`, atau `salah` terhadap `jawaban_kunci` | Pertanyaan dalam cakupan |
| Ketepatan sitasi | Sitasi benar jika SEMUA halaman yang disebut ada di `halaman_kunci` dan minimal satu `halaman_kunci` disebut | Jawaban berstatus `answered` |
| Tingkat mengarang | Persentase jawaban yang memuat klaim yang tidak ada di konteks yang diberikan | Sampel manual |
| Penolakan benar | Persentase pertanyaan di luar cakupan yang dijawab `not_found` | Pertanyaan di luar cakupan |
| Penolakan keliru | Persentase pertanyaan dalam cakupan yang salah dijawab `not_found` | Pertanyaan dalam cakupan |
| Penanganan ambigu | Persentase pertanyaan ambigu yang menghasilkan `needs_clarification` atau jawaban yang menyebut semua prodi terkait | Pertanyaan ambigu |
| Latensi | Median dan persentil ke-95 waktu jawab | Semua |

Catatan penilaian:
- Sitasi dibandingkan dengan `halaman_kunci`, bukan hanya dengan halaman chunk yang diambil. Cara ini lebih jujur karena chunk yang diambil bisa saja salah.
- Penilaian ketepatan jawaban dilakukan manusia pada set `test`. Penilaian otomatis oleh LLM boleh dipakai untuk `dev`, tetapi harus dicocokkan dulu dengan penilaian manusia pada sampel (Usulan).
- Angka dan nama mata kuliah dinilai ketat: satu angka salah berarti jawaban `salah`.

## 6. Eksperimen

Setiap eksperimen mengubah satu variabel saja dan memakai set pertanyaan yang sama.

| ID | Eksperimen | Tujuan | Status |
|---|---|---|---|
| E0 | LLM tanpa data (hanya pertanyaan) | Pembanding utama: apa untungnya RAG | Usulan |
| E1 | RAG dengan chunking per topik atau per mata kuliah (sesuai data-spec) | Sistem utama | Usulan |
| E2 | RAG dengan chunking ukuran tetap (ukuran dan overlap ditetapkan sebelum jalan) | Membandingkan dua strategi chunking | Usulan |
| E3 | `TOP_K` = 3 lawan 5 | Pengaruh jumlah konteks | Usulan |
| E4 | Dua model LLM Gemini | Pengaruh model penyusun jawaban | Usulan, opsional |
| E5 | Kurikulum lewat SQL lawan lewat vektor | Pengaruh desain data terstruktur | Usulan, opsional |

Catatan E0: tanpa konteks, LLM tidak punya halaman untuk disitasi, jadi hanya ketepatan jawaban dan tingkat mengarang yang dibandingkan. Untuk pertanyaan di luar cakupan, perhatikan apakah LLM menjawab seolah tahu.

## 7. Prosedur

1. Bekukan konfigurasi: model embedding dan dimensi, model LLM, `TOP_K`, ambang, versi chunk, dan commit kode. Catat semuanya bersama hasil.
2. Jalankan `scripts/evaluate.py` pada set `dev`. Setel prompt, `TOP_K`, dan ambang kemiripan di sini.
3. Bekukan pengaturan, lalu jalankan semua eksperimen pada set `test`.
4. Simpan hasil per pertanyaan (status, jawaban, sumber, skor, latensi) ke `data/eval/results/`.
5. Nilai jawaban secara manual pada set `test`, lalu hitung metrik.
6. Lakukan analisis kesalahan (bagian 8).

Ambang kemiripan disetel dari data `dev` dengan melihat sebaran skor pertanyaan dalam dan di luar cakupan. Jangan memakai angka tebakan.

## 8. Analisis kesalahan

Setiap jawaban salah diberi satu penyebab utama:

| Penyebab | Arti |
|---|---|
| Data | Teks atau label di chunk salah (kesalahan ekstraksi atau pelabelan) |
| Chunking | Informasi terpotong atau tercampur di chunk yang salah |
| Retrieval | Chunk benar tidak ikut terambil |
| Filter | Filter salah atau terlalu sempit |
| Generasi | Chunk benar terambil tetapi LLM menjawab keliru |
| Ambang | Penolakan keliru atau jawaban yang seharusnya ditolak |
| Kunci | Kunci jawaban yang salah |

Hasil analisis ini adalah bahan terkuat untuk bagian pembahasan laporan.

## 9. Pelaporan

Tabel hasil utama (format usulan):

| Eksperimen | Hit@3 | Hit@5 | Jawaban benar | Sitasi benar | Penolakan benar | Penolakan keliru | Latensi median |
|---|---|---|---|---|---|---|---|
| E0 | tidak berlaku | tidak berlaku | | tidak berlaku | | | |
| E1 | | | | | | | |
| E2 | | | | | | | |

- Tampilkan jumlah mentah (misalnya 41 dari 50), bukan hanya persentase.
- Dengan sekitar 100 pertanyaan, selisih beberapa poin persentase bisa hanya kebetulan. Jangan menyimpulkan keunggulan dari selisih kecil, dan sebutkan ini di bagian keterbatasan.
- Sertakan contoh jawaban benar, salah, dan penolakan.

## 10. Pembagian tugas (Usulan)

- Penyusun pertanyaan dan kunci: seluruh anggota, dibagi per bagian panduan (sama dengan pembagian pelabelan).
- Pemeriksa kunci: anggota lain yang tidak menyusun pertanyaan tersebut.
- Skrip evaluasi dan pencatatan log: pemilik backend.
- Penilaian manual dan analisis kesalahan: seluruh anggota, dibagi agar tiap jawaban dinilai minimal satu orang.

## 11. Keputusan yang masih terbuka

- Jumlah akhir pertanyaan dan sebaran kategori (bergantung pada scope yang selesai).
- Parameter chunking ukuran tetap untuk E2.
- Apakah penilaian otomatis oleh LLM dipakai untuk `dev`.
- Apakah E4 dan E5 dikerjakan.
- Format file pertanyaan (CSV atau JSON Lines).
- Cakupan baris tabel akreditasi, yang menentukan jumlah pertanyaan akreditasi.

## Riwayat perubahan

- v1: draf awal, mengikuti data-spec v2, api-contract v1, SDD v1, dan PRD v1.