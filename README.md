# Smart-WorkLife Backend API

Backend API untuk aplikasi **Smart-WorkLife** — asisten produktivitas dan kesehatan terpadu yang dirancang khusus untuk pekerja kantoran guna mengatasi burnout dan menjaga gaya hidup sehat.

## 🚀 Fitur Utama

- **Smart Dashboard**: Ringkasan performa harian, metrik produktivitas, dan keseimbangan kerja-istirahat (*Today's Balance*).
- **Smart Pomodoro**: Manajemen waktu dengan berbagai mode (Classic, Deep Work, Extend) untuk meningkatkan fokus.
- **Smart To-Do List**: Pengelolaan tugas dengan prioritas (Penting, Hari Ini, Besok) dan sistem deadline.
- **Smart Health**:
  - **BMI Calculator**: Perhitungan indeks massa tubuh dan kategori kesehatan.
  - **Hydration Tracker**: Pemantauan asupan air harian berdasarkan profil fisik.
- **Smart Stretching**: Penyimpanan data aktivitas peregangan untuk mendukung kesehatan fisik di tempat kerja.
- **Smart Notulen**:
  - **Real-time Transcription**: Mengubah rekaman audio rapat menjadi teks secara langsung.
  - **AI Summarization**: Ringkasan otomatis poin-poin penting rapat menggunakan kecerdasan buatan.

## 🛠️ Stack Teknologi

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Asynchronous)
- **Database**: [PostgreSQL](https://www.postgresql.org/) (Hosted on [Neon](https://neon.tech/))
- **ORM**: [SQLAlchemy](https://www.sqlalchemy.org/) 2.0 (Async)
- **Migrations**: [Alembic](https://alembic.sqlalchemy.org/)
- **AI Integration**: [OpenAI API](https://openai.com/api/) & [Google Gemini API](https://ai.google.dev/)
- **Validation**: [Pydantic v2](https://docs.pydantic.dev/)

## 📋 Prasyarat

- Python 3.10+
- PostgreSQL (atau akun Neon)
- API Key untuk OpenAI/Gemini (opsional, untuk fitur Smart Notulen)

## 🔧 Instalasi & Setup

1. **Clone repositori:**
   ```bash
   git clone <repository-url>
   cd smartworklife_web_backend
   ```

2. **Buat dan aktifkan virtual environment:**
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Linux/macOS:
   source venv/bin/activate
   ```

3. **Install dependensi:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Konfigurasi Environment Variables:**
   Buat file `.env` di direktori root dan sesuaikan nilainya (lihat contoh di `.env.example` jika tersedia atau gunakan referensi di bawah):
   ```env
   DATABASE_URL=postgresql+asyncpg://user:password@localhost/dbname
   OPENAI_API_KEY=your_openai_key
   GEMINI_API_KEY=your_gemini_key
   ```

5. **Jalankan Migrasi Database:**
   ```bash
   alembic upgrade head
   ```

6. **(Opsional) Seed Data Awal:**
   ```bash
   python seed.py
   ```

## 🏃 Menjalankan Aplikasi

Jalankan server pengembangan menggunakan Uvicorn:

```bash
fastapi dev main.py
```

API akan tersedia di `http://127.0.0.1:8000`.
Dokumentasi interaktif (Swagger UI) dapat diakses di `http://127.0.0.1:8000/docs`.

## 📂 Struktur Proyek

```text
.
├── alembic/            # Migrasi database
├── app/
│   ├── core/           # Konfigurasi global & security
│   ├── crud/           # Logika database (Create, Read, Update, Delete)
│   ├── models/         # Definisi tabel SQLAlchemy
│   ├── routers/        # Endpoint API FastAPI
│   ├── schemas/        # Pydantic models (Data validation)
│   ├── services/       # Integrasi pihak ketiga (AI, STT, dll)
│   └── database.py     # Koneksi & session database
├── main.py             # Entry point aplikasi
├── requirements.txt    # Daftar dependensi
└── .env                # Konfigurasi environment
```

## 🔐 Autentikasi

Saat ini aplikasi menggunakan sistem autentikasi sederhana. Setiap request yang membutuhkan data spesifik pengguna harus menyertakan header berikut:
`X-User-Id: <UUID_PENGGUNA>`

---
**Smart-WorkLife** — *Work Smarter, Live Healthier.*
