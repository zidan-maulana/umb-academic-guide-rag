# Kontrak API (docs/api-contract.md)

Kesepakatan antara backend (FastAPI) dan frontend web. Versi 1 (draf).
Tujuan: frontend bisa mulai dibangun tanpa menunggu backend selesai, dan backend tahu persis bentuk data yang harus dikembalikan.

Label status:
- **Final**: sudah diputuskan.
- **Usulan**: belum diputuskan tim.
- **Terbuka**: keputusan belum ada, jangan diasumsikan.

Konvensi penamaan: kunci struktur API memakai bahasa Inggris (`question`, `answer`, `sources`, `status`). Kunci metadata dokumen memakai nama yang sama dengan `docs/data-spec.md` (`halaman`, `bagian`, `fakultas`, `program_studi`, `jenjang`, `jenis_konten`, `topik`).

## 1. Umum

- Format: JSON, UTF-8, header `Content-Type: application/json`. (Usulan)
- Prefiks rute: `/api/v1`. (Usulan)
- Tanpa login dan tanpa akun pengguna. (Final, sesuai scope proyek)
- Semua panggilan LLM dilakukan di backend. Frontend tidak pernah memegang API key. (Final)
- Setiap request berdiri sendiri (stateless, satu pertanyaan satu jawaban). Riwayat percakapan tidak dikirim dan tidak dipakai. (Usulan, lihat bagian 8)
- Nomor halaman pada sitasi adalah nomor halaman PDF. (Final)

## 2. Endpoint

| Metode | Rute | Fungsi | Status |
|---|---|---|---|
| POST | `/api/v1/chat` | Kirim pertanyaan, terima jawaban dan sumber | Final |
| GET | `/api/v1/health` | Cek layanan hidup (berguna untuk cold start Railway) | Usulan |
| GET | `/api/v1/filters` | Daftar nilai filter yang valid (fakultas, prodi, jenjang) | Usulan |

## 3. POST /api/v1/chat

### Request

```json
{
  "question": "Apa akreditasi Teknik Informatika?",
  "filters": {
    "bagian": null,
    "fakultas": null,
    "program_studi": null,
    "jenjang": null
  }
}
```

| Field | Tipe | Wajib | Keterangan |
|---|---|---|---|
| `question` | string | Ya | Pertanyaan pengguna. Dipangkas spasi di tepi, tidak boleh kosong, maksimal 500 karakter (Usulan) |
| `filters` | object | Tidak | Batasan pencarian. Boleh dihilangkan |
| `filters.bagian` | string atau null | Tidak | `Regulasi`, `Kurikulum`, `Profil`, `Akreditasi` |
| `filters.fakultas` | string atau null | Tidak | `FDSK`, `FT`, `Fasilkom`, `FEB`, `Fikom`, `FPsi` |
| `filters.program_studi` | string atau null | Tidak | Nama prodi persis seperti di data |
| `filters.jenjang` | string atau null | Tidak | `Diploma Tiga`, `Sarjana`, dst. (lihat data-spec) |

Nilai filter harus berasal dari daftar valid di data-spec. Nilai di luar daftar ditolak (lihat bagian 5).

### Response 200

```json
{
  "status": "answered",
  "answer": "Program Studi Teknik Informatika (Program Sarjana) berstatus Terakreditasi dengan peringkat Unggul.",
  "sources": [
    {
      "halaman": 11,
      "kutipan": "Program Studi Teknik Informatika (Program Sarjana) berstatus Terakreditasi dengan peringkat Unggul, menurut Panduan Akademik 2025/2026.",
      "bagian": "Akreditasi",
      "jenis_konten": "akreditasi",
      "topik": null,
      "fakultas": "Fasilkom",
      "program_studi": "Teknik Informatika"
    }
  ],
  "mode": {
    "bagian": "Akreditasi",
    "fakultas": null,
    "program_studi": "Teknik Informatika",
    "jenjang": null
  },
  "clarification": null
}
```

| Field | Tipe | Keterangan |
|---|---|---|
| `status` | string | `answered`, `not_found`, atau `needs_clarification` |
| `answer` | string | Teks jawaban atau pesan penolakan. Tidak pernah kosong |
| `sources` | array | Daftar sumber. Urut dari yang paling relevan. Kosong jika status bukan `answered` |
| `sources[].halaman` | integer | Nomor halaman PDF |
| `sources[].kutipan` | string | Isi chunk asli, dipotong maksimal 300 karakter (Usulan) |
| `sources[].bagian`, `jenis_konten`, `topik`, `fakultas`, `program_studi` | string atau null | Metadata chunk, sama dengan data-spec |
| `mode` | object | Filter yang benar-benar dipakai backend pada pencarian ini. Dipakai frontend untuk label seperti "Mode: Regulasi" |
| `clarification` | object atau null | Hanya terisi bila status `needs_clarification` |

Aturan:
- Jika `status` adalah `not_found`, `answer` berisi persis: "Informasi tidak ditemukan di panduan." dan `sources` kosong. (Final)
- Satu halaman yang sama bisa muncul sekali saja di `sources`. Frontend menampilkan satu badge per halaman. (Usulan)
- Skor kemiripan tidak dikirim ke frontend. Skor dicatat di log backend untuk evaluasi. (Usulan)

### Contoh status `not_found`

```json
{
  "status": "not_found",
  "answer": "Informasi tidak ditemukan di panduan.",
  "sources": [],
  "mode": { "bagian": null, "fakultas": null, "program_studi": null, "jenjang": null },
  "clarification": null
}
```

### Contoh status `needs_clarification` (Usulan)

Dipakai bila pertanyaan ambigu antar prodi, misalnya "Apa mata kuliah NLP?" tanpa menyebut prodi dan hasilnya banyak.

```json
{
  "status": "needs_clarification",
  "answer": "Mata kuliah ini ada di lebih dari satu program studi. Pilih salah satu.",
  "sources": [],
  "mode": { "bagian": "Kurikulum", "fakultas": null, "program_studi": null, "jenjang": null },
  "clarification": {
    "message": "Pilih program studi",
    "field": "program_studi",
    "options": ["Teknik Informatika", "Sistem Informasi"]
  }
}
```

Frontend menampilkan `options` sebagai tombol. Pilihan pengguna dikirim ulang sebagai request baru dengan `filters.program_studi` terisi. Contoh nilai di atas hanya ilustrasi.

## 4. Endpoint tambahan (Usulan)

### GET /api/v1/health

```json
{ "status": "ok" }
```

Cukup mengembalikan 200 tanpa memanggil LLM atau database. Dipakai untuk membangunkan layanan sebelum demo.

### GET /api/v1/filters

```json
{
  "bagian": ["Regulasi", "Kurikulum", "Profil", "Akreditasi"],
  "fakultas": ["FDSK", "FT", "Fasilkom", "FEB", "Fikom", "FPsi"],
  "jenjang": ["Diploma Tiga", "Sarjana", "Magister", "Doktor", "Profesi"],
  "program_studi": [{ "nama": "Teknik Informatika", "fakultas": "Fasilkom", "jenjang": "Sarjana" }]
}
```

Daftar prodi lengkap menunggu verifikasi dari halaman kurikulum (lihat data-spec).

## 5. Format error

Semua error memakai bentuk yang sama:

```json
{
  "error": {
    "code": "invalid_request",
    "message": "Pertanyaan tidak boleh kosong."
  }
}
```

| HTTP | `code` | Kapan |
|---|---|---|
| 422 | `invalid_request` | Pertanyaan kosong atau terlalu panjang, nilai filter tidak valid |
| 429 | `rate_limited` | Terlalu banyak request. Sertakan header `Retry-After` |
| 502 | `llm_error` | Panggilan ke LLM atau embedding gagal |
| 504 | `timeout` | Proses melebihi batas waktu backend |
| 500 | `internal_error` | Kesalahan tak terduga. Pesan tidak membocorkan detail internal |

Pesan error ditulis untuk pengguna dalam bahasa Indonesia. Jawaban "tidak ditemukan" BUKAN error dan dikembalikan sebagai 200.

## 6. Catatan integrasi frontend

- URL dasar backend dibaca dari variabel environment frontend, bukan ditulis permanen di kode.
- Panggilan LLM bisa memakan 5 sampai 15 detik. Tampilkan indikator "mengetik". Timeout klien harus lebih panjang dari timeout backend (usulan: backend 25 detik, klien 30 detik).
- Request pertama setelah layanan tidur bisa lambat. Panggil `/health` saat halaman dibuka (jika endpoint ini disetujui).
- Tampilkan satu badge "Sumber: Hal. X" per entri `sources`. Klik badge menampilkan `kutipan`.
- Jangan tampilkan badge jika `sources` kosong.
- Tampilkan label mode dari `mode` bila ada filter aktif.
- Tangani ketiga nilai `status` dan semua kode error di bagian 5.
- Backend mengatur CORS dengan origin eksplisit (domain frontend), bukan `*` saat deploy. Frontend wajib memberi tahu domainnya ke pemilik backend.
- Batas laju (Usulan): 20 request per menit per alamat IP. Angka final menunggu uji.

## 7. Aturan perubahan kontrak

- Perubahan bentuk request atau response harus diumumkan ke seluruh tim sebelum dikerjakan.
- Penambahan field baru yang opsional boleh dilakukan tanpa menaikkan versi. Penghapusan atau perubahan arti field wajib menaikkan versi rute (`/api/v2`).
- Backend memvalidasi request dan response dengan model Pydantic yang mengikuti dokumen ini. Jika kode dan dokumen berbeda, dokumen diperbaiki lebih dulu lalu kode disesuaikan.

## 8. Keputusan yang masih terbuka

- **Siapa yang menentukan filter**: pengguna memilih lewat UI (filter dikirim frontend), atau backend menebak dari isi pertanyaan. Kontrak ini mendukung keduanya karena `filters` opsional dan `mode` selalu dikembalikan.
- **Percakapan multi-giliran**: apakah pertanyaan lanjutan ("kalau semester 5?") harus dipahami. Usulan saat ini: tidak, setiap pertanyaan berdiri sendiri.
- **Status `needs_clarification`**: dipakai atau pertanyaan ambigu langsung menampilkan semua prodi yang cocok.
- **Endpoint `/health` dan `/filters`**: diterima atau tidak.
- **Panjang `kutipan`** dan batas panjang pertanyaan.
- **Streaming jawaban** (SSE): di luar kontrak ini. Jika dipakai nanti, dibuat sebagai endpoint terpisah.

## Riwayat perubahan

- v1: draf awal, mengikuti data-spec v2.