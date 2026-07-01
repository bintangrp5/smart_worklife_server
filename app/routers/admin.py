"""Admin Dashboard Router — Smart-WorkLife Developer Portal."""
import os
from datetime import datetime, timedelta, timezone, date
import asyncio

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from jose import jwt, JWTError
from sqlalchemy import text

from app.core.config import settings
from app.database import async_session

router = APIRouter(prefix="/admin", tags=["Admin Dashboard"])
templates = Jinja2Templates(directory="templates")

ADMIN_EMAIL    = os.getenv("ADMIN_EMAIL", "admin@smartworklife.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "AdminSmartWorkLife2025!")
COOKIE_NAME    = "swl_admin_token"
ADMIN_SECRET   = settings.SECRET_KEY + "_admin"


# ── Auth Helpers ───────────────────────────────────────────────────────

def _create_token() -> str:
    exp = datetime.now(timezone.utc) + timedelta(hours=8)
    return jwt.encode({"sub": "admin", "role": "admin", "exp": exp},
                      ADMIN_SECRET, algorithm=settings.ALGORITHM)


def _is_valid(token: str) -> bool:
    try:
        p = jwt.decode(token, ADMIN_SECRET, algorithms=[settings.ALGORITHM])
        return p.get("role") == "admin"
    except JWTError:
        return False


def _check(request: Request) -> bool:
    t = request.cookies.get(COOKIE_NAME)
    return bool(t and _is_valid(t))


# ── DB Helper ──────────────────────────────────────────────────────────

async def _q(sql: str, params: dict = None):
    async with async_session() as session:
        r = await session.execute(text(sql), params or {})
        keys = list(r.keys())
        return [dict(zip(keys, row)) for row in r.fetchall()]


# ── Pages ──────────────────────────────────────────────────────────────

@router.get("/", response_class=HTMLResponse)
async def root():
    return RedirectResponse("/admin/login")


def get_react_app():
    try:
        with open("admin_dist/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Admin Frontend is building...</h1>")


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    if _check(request):
        return RedirectResponse("/admin/dashboard")
    return get_react_app()


@router.post("/login")
async def do_login(request: Request):
    form = await request.form()
    if form.get("email") == ADMIN_EMAIL and form.get("password") == ADMIN_PASSWORD:
        token = _create_token()
        resp = JSONResponse({"ok": True})
        resp.set_cookie(COOKIE_NAME, token, httponly=True,
                        secure=True, samesite="lax", max_age=28800)
        return resp
    raise HTTPException(401, "Email atau password salah")


@router.get("/logout")
async def logout():
    resp = RedirectResponse("/admin/login", status_code=302)
    resp.delete_cookie(COOKIE_NAME)
    return resp


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    if not _check(request):
        return RedirectResponse("/admin/login", status_code=302)
    return get_react_app()


# ── JSON API (dipanggil oleh JS di dashboard.html) ─────────────────────

@router.get("/api/stats")
async def api_stats(request: Request):
    if not _check(request):
        raise HTTPException(401)
    today       = date.today()
    yesterday   = date.today() - timedelta(days=1)
    month_start = date.today().replace(day=1)
    try:
        total    = await _q("SELECT COUNT(*) as v FROM users WHERE is_active=TRUE")
        dau_t    = await _q("SELECT COUNT(DISTINCT user_id) as v FROM pomodoro_sessions WHERE session_date=:d", {"d": today})
        dau_y    = await _q("SELECT COUNT(DISTINCT user_id) as v FROM pomodoro_sessions WHERE session_date=:d", {"d": yesterday})
        mau      = await _q("SELECT COUNT(DISTINCT user_id) as v FROM pomodoro_sessions WHERE session_date>=:ms", {"ms": month_start})
        new_u    = await _q("SELECT COUNT(*) as v FROM users WHERE created_at >= NOW()-INTERVAL '7 days'")
        return {
            "total_users":    int(total[0]["v"]) if total else 0,
            "dau":            int(dau_t[0]["v"]) if dau_t else 0,
            "dau_delta":      int(dau_t[0]["v"] if dau_t else 0) - int(dau_y[0]["v"] if dau_y else 0),
            "mau":            int(mau[0]["v"]) if mau else 0,
            "new_users_week": int(new_u[0]["v"]) if new_u else 0,
        }
    except Exception as e:
        return {"error": str(e)}


@router.get("/api/chart/new-users")
async def api_chart_new_users(request: Request):
    if not _check(request): raise HTTPException(401)
    try:
        rows = await _q("""
            SELECT DATE(created_at AT TIME ZONE 'Asia/Jakarta') as d, COUNT(*) as v
            FROM users WHERE created_at >= NOW()-INTERVAL '7 days'
            GROUP BY d ORDER BY d""")
        return {"labels": [str(r["d"]) for r in rows], "values": [int(r["v"]) for r in rows]}
    except Exception as e:
        return {"error": str(e), "labels": [], "values": []}


@router.get("/api/chart/pomodoro")
async def api_chart_pomodoro(request: Request):
    if not _check(request): raise HTTPException(401)
    try:
        rows = await _q("""
            SELECT session_date as d, COUNT(*) as v FROM pomodoro_sessions
            WHERE session_date >= CURRENT_DATE-INTERVAL '14 days' AND status='completed'
            GROUP BY d ORDER BY d""")
        return {"labels": [str(r["d"]) for r in rows], "values": [int(r["v"]) for r in rows]}
    except Exception as e:
        return {"error": str(e), "labels": [], "values": []}


@router.get("/api/features")
async def api_features(request: Request):
    if not _check(request): raise HTTPException(401)
    ms = date.today().replace(day=1)
    qs = {
        "🍅 Pomodoro":          ("SELECT COUNT(*) as v FROM pomodoro_sessions WHERE session_date>=:ms AND status='completed'", {"ms": ms}),
        "✅ Smart Todo":        ("SELECT COUNT(*) as v FROM todos WHERE completed_at>=:ms AND status='done'", {"ms": ms}),
        "💧 Smart Health":      ("SELECT COUNT(*) as v FROM hydration_logs WHERE log_date>=:ms", {"ms": ms}),
        "🎙️ Smart Notulen":    ("SELECT COUNT(*) as v FROM notulens WHERE created_at>=NOW()-INTERVAL '30 days'", {}),
        "🧘 Smart Stretching":  ("SELECT COUNT(*) as v FROM stretching_sessions WHERE started_at>=NOW()-INTERVAL '30 days'", {}),
    }
    
    async def fetch_feature(name, q, p):
        try:
            r = await _q(q, p)
            return name, int(r[0]["v"]) if r else 0
        except Exception:
            return name, 0

    tasks = [fetch_feature(name, q, p) for name, (q, p) in qs.items()]
    results = await asyncio.gather(*tasks)
    
    return dict(results)


@router.get("/api/users")
async def api_users(request: Request):
    if not _check(request): raise HTTPException(401)
    try:
        return await _q("""
            SELECT COALESCE(full_name,'Belum diisi') as full_name, email,
                   COALESCE(gender,'-') as gender, COALESCE(industry,'-') as industry,
                   TO_CHAR(created_at AT TIME ZONE 'Asia/Jakarta','DD Mon YYYY HH24:MI') as joined,
                   is_verified
            FROM users ORDER BY created_at DESC LIMIT 15""")
    except Exception as e:
        return {"error": str(e)}


@router.get("/api/ratings")
async def api_ratings(request: Request):
    if not _check(request): raise HTTPException(401)
    try:
        return await _q("""
            SELECT feature_name as feature,
                   ROUND(AVG(rating)::numeric,1) as avg_rating,
                   COUNT(*) as total
            FROM app_ratings GROUP BY feature_name ORDER BY avg_rating DESC""")
    except:
        return []


@router.get("/api/health")
async def api_health(request: Request):
    if not _check(request): raise HTTPException(401)
    pg_ok = False
    try:
        await _q("SELECT 1")
        pg_ok = True
    except:
        pass
    return {"postgresql": pg_ok, "backend": True, "cloudinary": True}
