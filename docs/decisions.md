# Catatan Keputusan (docs/decisions.md)

Daftar keputusan proyek beserta alasannya, supaya anggota tim yang melanjutkan pekerjaan tidak perlu menebak "kenapa begini".
Versi 1 (draf).

Cara memakai:
- Tambahkan baris baru setiap ada keputusan penting. Isi kolom Tanggal saat mencatat.
- Jangan menghapus keputusan lama. Jika berubah, tambahkan baris baru dan tandai yang lama sebagai "Diganti oleh D-xx".
- Hal yang belum diputuskan TIDAK dicatat di tabel utama. Letakkan di bagian "Belum diputuskan".

## Keputusan

| ID | Keputusan | Alasan | Alternatif yang dipertimbangkan | Tanggal |
|---|---|---|---|---|
| D-01 | Sistem berupa tanya jawab berbasis dokumen dengan pendekatan RAG. Inti pipeline ditulis native (chunking, embedding, pencarian, prompt). | Tujuan belajar, kode kecil dan mudah dipahami, jawaban terikat pada dokumen resmi. | Fine-tuning (butuh GPU dan data besar, di luar kebutuhan). | - |
| D-02 | LLM dan embedding memakai Google Gemini lewat API. | Keputusan tim. Dosen mengizinkan API LLM. | ChatGPT (OpenAI). | - |
| D-03 | Database PostgreSQL dengan ekstensi pgvector. Docker untuk lokal, Railway untuk deploy. | Satu database untuk data, metadata, dan vektor. Anggota sudah akrab dengan PostgreSQL. | Database vektor terpisah (lebih rumit tanpa manfaat besar pada skala ini). | - |
| D-04 | Backend memakai Python dan FastAPI. | Ringan, cocok untuk pipeline NLP berbasis Python, mudah dihubungkan ke frontend. | Backend Node.js. | - |
| D-05 | Antarmuka berupa frontend web kustom. Telegram Bot ditinggalkan. | Kontrol penuh atas tampilan, sitasi halaman tampil rapi, kesan produk nyata saat presentasi. | Telegram Bot (lebih cepat dibuat, tetapi kontrol UI rendah). | - |
| D-06 | Scope dokumen: halaman 14 sampai 98 Panduan Akademik, ditambah tabel akreditasi di halaman 11. Halaman 1 sampai 10, 12 sampai 13, dan 99 sampai 105 dikecualikan. | Mencakup aturan akademik dan kurikulum, tetapi mengecualikan bagian yang tidak relevan untuk tanya jawab mahasiswa aktif. Tabel akreditasi penting bagi mahasiswa. | Seluruh 105 halaman, atau hanya Regulasi. | - |
| D-07 | Tabel akreditasi diekstrak khusus dan dipecah per baris (satu program studi satu chunk). | Pertanyaan akreditasi bersifat spesifik per prodi. Ekstraksi otomatis pdfplumber terbukti memecah tabel ini, jadi hasilnya wajib diverifikasi. | Menyimpan tabel sebagai satu blok. | - |
| D-08 | Acuan nomor halaman untuk data, sitasi, dan evaluasi adalah nomor halaman PDF. | Pada halaman yang disampel, nomor cetak sama dengan nomor PDF, jadi tidak ada konversi yang perlu dikelola. Validasi tetap mengecek seluruh halaman scope. | Nomor cetak di dokumen. | - |
| D-09 | Preprocessing untuk RAG membersihkan tanpa mengubah makna. Tidak memakai stopword removal, stemming, atau lowercase total sebelum embedding. | Model embedding butuh kalimat utuh. Langkah klasik merusak makna dan bisa mengubah angka atau istilah resmi. | Pipeline NLP klasik penuh (boleh dijalankan pada salinan terpisah untuk bahan laporan). | - |
| D-10 | Pembatasan jawaban memakai tiga lapis: filter database, prompt LLM yang membatasi pada konteks, dan label mode di antarmuka. | Filter database paling kuat mencegah jawaban keluar dari scope. Prompt dan UI melengkapi. | Hanya mengandalkan prompt. | - |
| D-11 | Tidak dibuat: login, aplikasi mobile terpisah, dashboard admin, tool calling, fine-tuning. Analisis sentimen dilarang dosen. | Menjaga kompleksitas rendah dan fokus pada pembelajaran. | - | - |
| D-12 | Satu repositori utama (publik) untuk seluruh proyek: `backend/`, `frontend/`, `data/`, `scripts/`, `docs/`. Anggota lain melanjutkan setelah backend selesai. | Semua pekerjaan terkumpul di satu tempat. Vercel dan Netlify dapat deploy dari subfolder. | Repo terpisah per komponen. | - |
| D-13 | Repo publik tidak memuat API key, kredensial, atau PDF mentah. | Repo dapat dibaca siapa saja. | - | - |
| D-14 | Agent coding Antigravity dipakai untuk implementasi, dengan konteks proyek di `AGENTS.md`. Verifikasi hasil tetap oleh manusia. | Mempercepat penulisan kode dan skrip. Agent tidak bisa menilai kebenaran data. | Menulis semua kode manual. | - |
| D-15 | Kerja bertahap: pipeline Regulasi dulu, lalu Fasilkom, lalu fakultas lain dan tabel akreditasi. | Pipeline yang sudah terbukti pada satu bagian bisa diperluas tanpa mengulang. Mengendalikan risiko waktu pelabelan. | Langsung membangun untuk seluruh scope. | - |
| D-16 | Struktur backend memakai api/, schemas/, services/ (bukan rag/); skrip preprocessing dipecah menjadi extract.py, clean.py, chunk.py. | Pola FastAPI yang umum, dan preprocessing dikerjakan beberapa orang sehingga tahapnya perlu bisa diuji terpisah. | Struktur rag/ dan satu preprocess.py. | - |

## Belum diputuskan

Jangan menganggap usulan di bawah sebagai keputusan sampai tim sepakat lalu dipindahkan ke tabel di atas.

| Topik | Usulan saat ini | Dokumen terkait |
|---|---|---|
| Model embedding dan dimensi vektor | `gemini-embedding-2`, 768 dimensi | SDD bagian 7 |
| Model LLM penyusun jawaban | Flash-Lite atau Flash generasi 3.5, dibandingkan saat evaluasi | SDD bagian 7 |
| Library akses database dan versi Python | Belum ada | SDD bagian 12 |
| Filter ditentukan UI atau ditebak backend | Belum ada | api-contract bagian 8 |
| Data kurikulum disimpan di tabel SQL terpisah | Usulan: ya | SDD bagian 6 |
| Endpoint `/health` dan `/filters`, status `needs_clarification` | Usulan: dipakai | api-contract bagian 2 dan 3 |
| Cakupan baris tabel akreditasi (semua jenjang atau D3 dan Sarjana) | Belum ada | data-spec bagian 9 |
| Jumlah dan daftar program studi (16 atau 18, prodi Fikom satu atau empat) | Menunggu verifikasi halaman kurikulum | data-spec bagian 6 |
| Format file chunk | JSON Lines | data-spec bagian 5 |
| Rancangan eksperimen evaluasi (E0 sampai E5) dan pembagian dev/test | Sesuai evaluation-plan | evaluation-plan bagian 4 dan 6 |
| Dukungan pgvector di PostgreSQL Railway | Perlu dicek di dokumentasi Railway | SDD bagian 12 |
| Versi PostgreSQL dan tag Docker (sementara pg16 dari agent) | Sementara pg16 | docker-compose.yml |

## Hal yang menunggu konfirmasi dosen

- Apakah RAG diterima secara eksplisit sebagai proyek NLP.
- Metode wajib, bobot penilaian, format deliverable, dan tenggat.
- Jumlah anggota dan apakah ada kelompok lain dengan tema sama.
- Apakah tampilan antarmuka ikut dinilai.

## Riwayat perubahan

- v1: draf awal berisi D-01 sampai D-15.