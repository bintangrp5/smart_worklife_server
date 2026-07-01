# 📅 API Implementation Plan — Smart-WorkLife

Tech Stack: **FastAPI** + **PostgreSQL (Neon)** + **SQLAlchemy Async**

> Asumsi: 1 Sprint = 1–2 minggu  
> Seluruh endpoint menggunakan prefix `/api/v1`  
> **Status: SPRINT 5 IN PROGRESS 🚧** — Server berjalan di `http://127.0.0.1:8000`  
> **Swagger UI:** `http://127.0.0.1:8000/docs`

---

## 🚧 Sprint 5: User Authentication & Security — IN PROGRESS

### Checklist Tugas
- [ ] Update `app/models/user.py` (is_verified, otp, google_id)
- [ ] `app/core/security.py` (JWT & Password Hashing)
- [ ] `app/schemas/auth.py` (Register, Login, OTP, Forgot Password)
- [ ] `app/services/email_service.py` (Send OTP/Reset Link)
- [ ] `app/services/auth_service.py` (Business logic)
- [ ] `app/routers/auth.py`
- [ ] Middleware/Dependency: Update `get_current_user` dari header ke JWT Token

### Endpoints — Authentication 🚧

| Method | Endpoint | Status |
|--------|----------|--------|
| `POST` | `/api/v1/auth/register` | 🚧 |
| `POST` | `/api/v1/auth/verify-otp` | 🚧 |
| `POST` | `/api/v1/auth/resend-otp` | 🚧 |
| `POST` | `/api/v1/auth/login` | 🚧 |
| `POST` | `/api/v1/auth/google` | 🚧 |
| `POST` | `/api/v1/auth/forgot-password` | 🚧 |
| `POST` | `/api/v1/auth/reset-password` | 🚧 |
| `GET`  | `/api/v1/auth/me` | 🚧 |

---

## 📁 Struktur Folder Final (Terealisasi)

```
smartworklife_web_backend/
├── app/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py          ✅
│   │   ├── security.py        🚧
│   │   └── dependencies.py    ✅
│   ├── models/
│   │   ├── __init__.py        ✅
│   │   ├── user.py            ✅ (Update: verified, otp, google)
│   │   ├── pomodoro.py        ✅
│   │   ├── stretching.py      ✅
│   │   ├── health.py          ✅
│   │   ├── todo.py            ✅
│   │   └── notulen.py         ✅
│   ├── schemas/
│   │   ├── __init__.py        ✅
│   │   ├── auth.py            🚧
│   │   ├── todo.py            ✅
│   │   ├── pomodoro.py        ✅
│   │   ├── health.py          ✅
│   │   ├── stretching.py      ✅
│   │   └── notulen.py         ✅
│   ├── crud/
│   │   ├── __init__.py        ✅
│   │   ├── todo.py            ✅
│   │   ├── pomodoro.py        ✅
│   │   ├── health.py          ✅
│   │   ├── stretching.py      ✅
│   │   ├── notulen.py         ✅
│   │   └── dashboard.py       ✅
│   ├── routers/
│   │   ├── __init__.py        ✅
│   │   ├── auth.py            🚧
│   │   ├── todo.py            ✅
│   │   ├── pomodoro.py        ✅
│   │   ├── health.py          ✅
│   │   ├── stretching.py      ✅
│   │   ├── notulen.py         ✅
│   │   └── dashboard.py       ✅
│   ├── services/
│   │   ├── __init__.py        ✅
│   │   ├── email_service.py   🚧
│   │   ├── auth_service.py    🚧
│   │   ├── stt_service.py     ✅ (OpenAI Whisper)
│   │   └── ai_service.py      ✅ (Gemini 2.0 Flash)
│   ├── database.py            ✅
│   └── __init__.py            ✅
├── alembic/                   ✅ (migrations)
├── main.py                    ✅
├── requirements.txt           ✅
├── schema.sql                 ✅ (raw SQL referensi)
├── seed.py                    ✅ (seed stretching exercises)
├── plan.md                    ✅ (file ini)
└── .env                       ✅ (Neon DB URL)
```

---

## 🔑 Konfigurasi `.env` Lengkap

```env
# Database (Neon PostgreSQL - sudah terkonfigurasi)
DATABASE_URL=postgresql+asyncpg://...

# JWT
SECRET_KEY=your-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440 # 24 hours

# Email (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=Smart-WorkLife <noreply@smartworklife.com>

# Google Auth
GOOGLE_CLIENT_ID=your-google-client-id

# AI Services (isi untuk mengaktifkan Sprint 3)
OPENAI_API_KEY=sk-...        # untuk Speech-to-Text (Whisper)
GEMINI_API_KEY=AIza...       # untuk AI Summary (Gemini 2.0 Flash)
```

---

## ⏱️ Ringkasan Eksekusi

| Sprint | Modul | Status |
|--------|-------|--------|
| Sprint 1 | Core Setup + Smart To-Do List | ✅ SELESAI |
| Sprint 2 | Smart Pomodoro + Smart Health | ✅ SELESAI |
| Sprint 3 | Smart Stretching + Smart Notulen (AI) | ✅ SELESAI |
| Sprint 4 | Dashboard Aggregation + Finalisasi | ✅ SELESAI |
| Sprint 5 | User Authentication & Security | 🚧 IN PROGRESS |
| **Total endpoint** | **41 endpoint aktif** | **🚧 BUILDING** |
