/**
 * Konfigurasi dan konstanta antarmuka chat.
 */
export const API_URL = "http://localhost:8000/api/v1/chat";
export const PDF_URL = "";
export const FALLBACK_TEXT = "Informasi tidak ditemukan di panduan.";
export const HISTORY_KEY = "umb-guide-history";
export const THEME_KEY = "umb-guide-theme";
export const REQUEST_TIMEOUT_MS = 60000;
export const MAX_QUESTION = 500;

export const SUGGESTIONS = [
  { q: "Berapa SKS maksimal per semester?", icon: "sks" },
  { q: "Berikan informasi dari matakuliah Capstone Project", icon: "kurikulum" },
  { q: "Apa syarat mengambil skripsi?", icon: "skripsi" },
  { q: "Apa akreditasi Teknik Informatika?", icon: "akreditasi" },
  { q: "Berapa lama batas waktu studi program sarjana?", icon: "waktu" },
  { q: "Apa sanksi jika melanggar tata tertib ujian?", icon: "aturan" },
];

export const ICONS = {
  sks: '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path d="M7 7h4v4H7V7Zm6 0h4v4h-4V7ZM7 13h4v4H7v-4Zm6 0h4v4h-4v-4Z" fill="none" stroke="currentColor" stroke-width="1.7"/></svg>',
  kurikulum: '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path d="M12 6.5C10.5 5.3 8 4.8 4.5 5v12.5c3.5-.2 6 .3 7.5 1.5 1.5-1.2 4-1.7 7.5-1.5V5c-3.5-.2-6 .3-7.5 1.5Z" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/><path d="M12 6.5V19" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/></svg>',
  skripsi: '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path d="M7 4.5h7l4 4V19.5H7v-15Z" fill="none" stroke="currentColor" stroke-width="1.7"/><path d="M14 4.5V9h4.5M9.5 13h5M9.5 16h3.5" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/></svg>',
  akreditasi: '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path d="M12 4.5 14.2 9l4.8.6-3.5 3.3.9 4.7L12 15.7 7.6 17.6l.9-4.7L5 9.6 9.8 9 12 4.5Z" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/></svg>',
  waktu: '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><circle cx="12" cy="12" r="7.5" fill="none" stroke="currentColor" stroke-width="1.7"/><path d="M12 8v4.5l3 2" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/></svg>',
  aturan: '<svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path d="M12 4v16M6 8h12M7 16h10" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/><path d="M6 8c0 3 2.5 5 6 8 3.5-3 6-5 6-8" fill="none" stroke="currentColor" stroke-width="1.7"/></svg>',
  book: '<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><path d="M6 6.5h5.5V18H7a1 1 0 0 1-1-1V6.5Zm6.5 0H18V17a1 1 0 0 1-1 1h-4.5V6.5Z" fill="none" stroke="currentColor" stroke-width="1.6"/></svg>',
  user: '<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><circle cx="12" cy="9" r="2.6" fill="none" stroke="currentColor" stroke-width="1.7"/><path d="M7 17c.8-2 2.6-3 5-3s4.2 1 5 3" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/></svg>',
  info: '<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><circle cx="12" cy="12" r="8" fill="none" stroke="currentColor" stroke-width="1.7"/><path d="M12 11v5M12 8h.01" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>',
  warn: '<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><path d="M12 5 20 19H4L12 5Z" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/><path d="M12 10v5M12 17h.01" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>',
  copy: '<svg viewBox="0 0 24 24" width="14" height="14" aria-hidden="true"><rect x="8" y="8" width="10" height="10" rx="1.5" fill="none" stroke="currentColor" stroke-width="1.7"/><path d="M6 16V6.5A1.5 1.5 0 0 1 7.5 5H16" fill="none" stroke="currentColor" stroke-width="1.7"/></svg>',
  check: '<svg viewBox="0 0 24 24" width="14" height="14" aria-hidden="true"><path d="M6 12.5 10 16.5 18 8" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  doc: '<svg viewBox="0 0 24 24" width="14" height="14" aria-hidden="true"><path d="M7 5h7l4 4v10H7V5Z" fill="none" stroke="currentColor" stroke-width="1.7"/><path d="M14 5v4h4" stroke="currentColor" stroke-width="1.7"/></svg>',
};
