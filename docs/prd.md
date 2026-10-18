# Product Requirements Document (docs/prd.md)

Chatbot RAG Panduan Akademik UMB 2025/2026. Versi 1 (draf ringkas).
Dokumen ini menjelaskan APA yang dibangun dan KENAPA. Cara membangunnya ada di `docs/sdd.md`.

Label status: **Final** (sudah diputuskan), **Usulan** (belum diputuskan), **Belum dikonfirmasi** (menunggu kepastian dosen).

## 1. Ringkasan produk

Chatbot web yang menjawab pertanyaan mahasiswa tentang Panduan Akademik UMB Tahun Akademik 2025/2026. Chatbot hanya menjawab dari isi panduan, menyertakan nomor halaman sebagai sumber, dan menolak menjawab bila informasinya tidak ada.

## 2. Latar belakang dan masalah

- Panduan akademik berupa PDF 105 halaman. Mencari satu aturan atau satu mata kuliah di dalamnya lambat.
- Pertanyaan yang sering muncul (aturan UAS, cuti, masa studi, daftar mata kuliah per semester, status akreditasi) jawabannya tersebar di banyak halaman.
- Chatbot AI umum bisa menjawab dengan percaya diri tetapi salah, karena tidak membaca panduan UMB. Mahasiswa perlu jawaban yang bisa diperiksa ke sumbernya.
- Konteks akademik: proyek kelompok mata kuliah Natural Language Processing. Tujuan utama adalah belajar dan menunjukkan pipeline NLP yang dievaluasi dengan baik.

## 3. Tujuan dan non-tujuan

Tujuan (Final):
- Menjawab pertanyaan akademik dari panduan dengan sitasi halaman yang benar.
- Menolak dengan jelas pertanyaan di luar isi panduan, tanpa mengarang.
- Membangun dan mengevaluasi pipeline RAG secara terukur (bahan laporan).

Non-tujuan (Final):
- Bukan produk komersial dan tidak melayani banyak pengguna sekaligus secara skala besar.
- Tidak memakai login, aplikasi mobile terpisah, dashboard admin, tool calling, atau fine-tuning.
- Tidak melakukan analisis sentimen (dilarang dosen).
- Tidak memberi nasihat di luar panduan (misalnya kebijakan kampus yang tidak tertulis di dokumen).

## 4. Pengguna dan skenario

Pengguna utama: mahasiswa aktif UMB. Pengguna kedua: penilai proyek (dosen) yang mengecek kualitas jawaban dan sitasi.

Contoh skenario:
- "Apa sanksi melanggar tata tertib UAS?" Jawaban dari bagian Regulasi, sitasi halaman 18 (perkiraan, harus dicek).
- "Apa saja mata kuliah semester 6 Teknik Informatika?" Jawaban dari bagian Kurikulum dengan sitasi halaman.
- "Apa akreditasi Teknik Informatika?" Jawaban dari tabel akreditasi (hal. 11).
- "Siapa presiden Indonesia?" Ditolak: "Informasi tidak ditemukan di panduan."
- "Apa mata kuliah NLP?" (tanpa prodi) Sistem meminta pengguna memilih prodi bila ambigu (Usulan).

## 5. Scope

Masuk (Final):
- Halaman 14 sampai 98 Panduan Akademik, ditambah tabel akreditasi di halaman 11.
- Bagian Regulasi, Kurikulum dan profil fakultas, dan Akreditasi.

Keluar (Final):
- Halaman 1 sampai 10, 12 sampai 13, dan 99 sampai 105 (pembuka dan penerimaan mahasiswa baru).
- Dokumen lain di luar panduan.

Pendekatan bertahap (Usulan): Regulasi dulu, lalu Fasilkom, lalu fakultas lain dan tabel akreditasi, sesuai sisa waktu. Cakupan akhir bergantung pada kecepatan pelabelan dan verifikasi data.

## 6. Kebutuhan fungsional

| ID | Kebutuhan | Prioritas |
|---|---|---|
| FR-1 | Pengguna dapat mengetik pertanyaan bahasa Indonesia dan menerima jawaban. | Wajib |
| FR-2 | Setiap jawaban menampilkan sumber berupa nomor halaman dan kutipan teks panduan. | Wajib |
| FR-3 | Jika informasi tidak ada di panduan, sistem menjawab "Informasi tidak ditemukan di panduan." tanpa menampilkan sumber. | Wajib |
| FR-4 | Sistem membatasi pencarian dengan metadata (bagian, fakultas, prodi, jenjang) sebelum pencarian kemiripan. | Wajib |
| FR-5 | Antarmuka web menampilkan indikator proses dan label filter yang aktif. | Wajib |
| FR-6 | Jika pertanyaan ambigu antar prodi, sistem meminta pengguna memilih prodi. | Usulan |
| FR-7 | Pengguna dapat memilih filter bagian atau prodi secara manual di antarmuka. | Usulan |
| FR-8 | Klik sumber menampilkan kutipan asli chunk. | Usulan |

## 7. Kebutuhan non-fungsional

- Akurasi: angka, SKS, semester, dan istilah resmi harus sama persis dengan panduan.
- Ketertelusuran: setiap jawaban dapat diperiksa ke halaman PDF yang disebut.
- Respons: waktu jawaban wajar untuk panggilan LLM (beberapa detik) dengan indikator proses. Target angka ditetapkan setelah uji.
- Keamanan: API key hanya di backend, repo publik tanpa rahasia, CORS dengan origin eksplisit, rate limit sederhana.
- Privasi: tanpa login, log tidak menyimpan identitas pengguna.
- Keterulangan: pipeline data dapat dijalankan ulang dari PDF sampai database.
- Kesederhanaan: kompleksitas teknis rendah dan tidak berlebihan.

## 8. Kriteria sukses

- Sistem lulus uji 80 sampai 120 pertanyaan (Usulan) dengan kunci jawaban dari dokumen.
- Terukur dan dilaporkan: ketepatan pencarian (hit rate di 3 teratas), ketepatan jawaban, ketepatan sitasi, dan persentase penolakan benar pada pertanyaan di luar cakupan.
- RAG terbukti lebih baik daripada LLM tanpa data pada pertanyaan yang sama.
- Target angka tiap metrik ditetapkan setelah evaluasi awal (baseline), supaya realistis.
- Demo berjalan dari URL yang dapat dibuka, dengan sitasi tampil benar.

## 9. Deliverable

Dugaan, belum dikonfirmasi ke dosen: aplikasi demo, dataset (chunk dan metadata), kode di repo, laporan, dan presentasi.

Isi laporan yang diusulkan: latar belakang, data dan pembersihan, desain chunking, arsitektur, hasil evaluasi, analisis kesalahan, dan keterbatasan.

## 10. Peran tim

- Backend dan RAG: pipeline pencarian, integrasi Gemini, API.
- Preprocessing dan data: ekstraksi, pembersihan, chunking, pelabelan, verifikasi.
- Frontend: antarmuka chat dan tampilan sitasi.
- Evaluasi dan laporan: pertanyaan uji, kunci jawaban, analisis hasil.

Pembagian nama anggota ke peran ditentukan tim. Anggota lain melanjutkan pekerjaan setelah backend selesai.

## 11. Asumsi, batasan, risiko

Asumsi:
- Panduan 2025/2026 yang dipakai adalah versi final yang dibagikan, dan seluruh tim memakai file yang sama.
- Dosen membebaskan pendekatan teknis (informasi dari anggota tim).

Batasan:
- Waktu terbatas dan tenggat belum diketahui.
- Pekerjaan pelabelan dan verifikasi data bersifat manual dan memakan waktu.

Risiko utama:
- Waktu pelabelan data terlalu lama. Mitigasi: bagi tugas, bangun bertahap, perkecil scope jika perlu.
- Ambiguitas pencarian antar prodi. Mitigasi: metadata berlapis dan tabel SQL untuk kurikulum.
- Data kurikulum salah parsing. Mitigasi: verifikasi visual dan validasi otomatis.
- Kuota atau batas laju API Gemini. Mitigasi: retry terbatas dan rate limit.
- Proyek dinilai hanya sebagai aplikasi, bukan NLP. Mitigasi: evaluasi yang kuat dan perbandingan metode.

## 12. Tahapan kerja (Usulan, tanpa tanggal karena tenggat belum diketahui)

1. Preprocessing data (pekerjaan minggu depan sesuai arahan dosen), disusul chunking dan pelabelan.
2. Pipeline RAG untuk Regulasi sampai menjawab dengan sitasi, paralel dengan langkah 2 memakai data mini.
3. API FastAPI dan antarmuka web.
4. Perluasan ke Fasilkom dan fakultas lain, serta tabel akreditasi.
5. Evaluasi lengkap dan analisis kesalahan.
6. Deploy, uji demo, laporan, dan presentasi.

## Riwayat perubahan

- v1: draf awal, mengikuti data-spec v2, api-contract v1, dan SDD v1.