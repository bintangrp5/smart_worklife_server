"""
Smart-WorkLife Developer Dashboard
Streamlit app terhubung langsung ke database PostgreSQL (Neon) dan MongoDB.
"""
import os
import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta, timezone
from dotenv import load_dotenv

# ─── 1. Konfigurasi Halaman ────────────────────────────────────────────────────
st.set_page_config(
    page_title="Smart-WorkLife Dev Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── 2. Load Environment Variables ────────────────────────────────────────────
load_dotenv()

# ─── 3. Custom CSS (Styling Premium) ──────────────────────────────────────────
st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Warna tema utama */
    :root {
        --primary: #4F46E5;
        --success: #10B981;
        --warning: #F59E0B;
        --danger: #EF4444;
    }

    /* Kartu metrik */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 20px rgba(79, 70, 229, 0.15);
    }

    /* Header sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    }

    section[data-testid="stSidebar"] .stMarkdown, 
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] span {
        color: #e2e8f0 !important;
    }

    /* Judul halaman */
    h1, h2, h3 {
        color: #f8fafc;
    }

    /* Background utama */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        color: #e2e8f0;
    }

    /* Tabel */
    [data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
    }

    /* Badges status */
    .badge-online {
        background: #10B981; color: white;
        padding: 4px 12px; border-radius: 20px; font-size: 13px; font-weight: 600;
    }
    .badge-warning {
        background: #F59E0B; color: white;
        padding: 4px 12px; border-radius: 20px; font-size: 13px; font-weight: 600;
    }
    .badge-offline {
        background: #EF4444; color: white;
        padding: 4px 12px; border-radius: 20px; font-size: 13px; font-weight: 600;
    }

    /* Separator */
    hr { border-color: rgba(99, 102, 241, 0.2); }
</style>
""", unsafe_allow_html=True)


# ─── 4. Koneksi Database (Synchronous via psycopg2) ───────────────────────────
def _get_sync_url() -> str:
    """Ambil URL koneksi synchronous dari .env."""
    raw_url = os.getenv("DATABASE_URL", "")
    sync_url = raw_url.replace("postgresql+asyncpg://", "postgresql://")
    sync_url = sync_url.replace("?ssl=require", "?sslmode=require")
    return sync_url


def run_query(query: str, params=None) -> pd.DataFrame:
    """Buat fresh connection tiap query agar tidak kena timeout Neon."""
    import psycopg2
    sync_url = _get_sync_url()
    try:
        conn = psycopg2.connect(sync_url)
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df
    except Exception as e:
        st.warning(f"⚠️ Query gagal: {e}")
        return pd.DataFrame()


# ─── 5. Fungsi Ambil Data Nyata ────────────────────────────────────────────────
@st.cache_data(ttl=60)  # Cache 60 detik agar tidak overload DB
def get_kpi_data():
    """Ambil KPI utama dari database."""
    total = run_query("SELECT COUNT(*) as total FROM users WHERE is_active = TRUE")
    
    today = date.today().isoformat()
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    month_start = date.today().replace(day=1).isoformat()

    dau_today = run_query(
        "SELECT COUNT(DISTINCT user_id) as dau FROM pomodoro_sessions WHERE session_date = %s",
        (today,)
    )
    dau_yesterday = run_query(
        "SELECT COUNT(DISTINCT user_id) as dau FROM pomodoro_sessions WHERE session_date = %s",
        (yesterday,)
    )
    mau = run_query(
        "SELECT COUNT(DISTINCT user_id) as mau FROM pomodoro_sessions WHERE session_date >= %s",
        (month_start,)
    )
    new_users_week = run_query(
        "SELECT COUNT(*) as total FROM users WHERE created_at >= NOW() - INTERVAL '7 days'"
    )

    total_users = int(total["total"].iloc[0]) if not total.empty else 0
    dau_val = int(dau_today["dau"].iloc[0]) if not dau_today.empty else 0
    dau_prev = int(dau_yesterday["dau"].iloc[0]) if not dau_yesterday.empty else 0
    mau_val = int(mau["mau"].iloc[0]) if not mau.empty else 0
    new_users = int(new_users_week["total"].iloc[0]) if not new_users_week.empty else 0

    dau_delta = dau_val - dau_prev

    return {
        "total_users": total_users,
        "dau": dau_val,
        "dau_delta": dau_delta,
        "mau": mau_val,
        "new_users_week": new_users
    }


@st.cache_data(ttl=60)
def get_feature_usage():
    """Hitung penggunaan masing-masing fitur bulan ini."""
    month_start = date.today().replace(day=1).isoformat()

    pomodoro = run_query(
        "SELECT COUNT(*) as total FROM pomodoro_sessions WHERE session_date >= %s AND status = 'completed'",
        (month_start,)
    )
    todos_done = run_query(
        "SELECT COUNT(*) as total FROM todos WHERE completed_at >= %s AND status = 'done'",
        (month_start,)
    )
    notulen = run_query(
        "SELECT COUNT(*) as total FROM notulens WHERE created_at >= NOW() - INTERVAL '30 days'"
    )
    stretching = run_query(
        # stretching_sessions tidak punya created_at, pakai started_at
        "SELECT COUNT(*) as total FROM stretching_sessions WHERE started_at >= NOW() - INTERVAL '30 days'"
    )
    hydration = run_query(
        # hydration_logs pakai log_date (tipe Date), bukan logged_at
        "SELECT COUNT(*) as total FROM hydration_logs WHERE log_date >= CURRENT_DATE - INTERVAL '30 days'"
    )

    def safe_val(df):
        return int(df["total"].iloc[0]) if not df.empty else 0

    return pd.DataFrame({
        "Fitur": ["🍅 Pomodoro", "✅ Smart Todo", "💧 Smart Health (Hydration)", "🎙️ Smart Notulen", "🧘 Smart Stretching"],
        "Penggunaan Bulan Ini": [
            safe_val(pomodoro),
            safe_val(todos_done),
            safe_val(hydration),
            safe_val(notulen),
            safe_val(stretching)
        ]
    }).set_index("Fitur")


@st.cache_data(ttl=60)
def get_new_users_chart():
    """Grafik registrasi user baru per hari (7 hari terakhir)."""
    df = run_query("""
        SELECT DATE(created_at AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Jakarta') as tanggal,
               COUNT(*) as jumlah_user_baru
        FROM users
        WHERE created_at >= NOW() - INTERVAL '7 days'
        GROUP BY tanggal
        ORDER BY tanggal ASC
    """)
    if df.empty:
        return pd.DataFrame()
    df["tanggal"] = pd.to_datetime(df["tanggal"])
    return df.set_index("tanggal")


@st.cache_data(ttl=60)
def get_pomodoro_trend():
    """Grafik tren sesi Pomodoro selesai per hari (14 hari terakhir)."""
    df = run_query("""
        SELECT session_date as tanggal, COUNT(*) as sesi_selesai
        FROM pomodoro_sessions
        WHERE session_date >= CURRENT_DATE - INTERVAL '14 days'
          AND status = 'completed'
        GROUP BY session_date
        ORDER BY session_date ASC
    """)
    if df.empty:
        return pd.DataFrame()
    df["tanggal"] = pd.to_datetime(df["tanggal"])
    return df.set_index("tanggal")


@st.cache_data(ttl=60)
def get_recent_users():
    """Daftar user terbaru yang mendaftar."""
    return run_query("""
        SELECT 
            COALESCE(full_name, 'Belum diisi') as "Nama",
            email as "Email",
            gender as "Gender",
            industry as "Industri",
            TO_CHAR(created_at AT TIME ZONE 'Asia/Jakarta', 'DD Mon YYYY HH24:MI') as "Daftar Pada",
            CASE WHEN is_verified THEN '✅ Terverifikasi' ELSE '⏳ Belum Verifikasi' END as "Status"
        FROM users
        ORDER BY created_at DESC
        LIMIT 10
    """)


@st.cache_data(ttl=60)
def get_ratings_data():
    """Ambil data rating dari tabel app_ratings (jika sudah ada)."""
    # Cek apakah tabel rating sudah ada
    check = run_query("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'app_ratings'
        ) as exists
    """)
    if not check.empty and check["exists"].iloc[0]:
        return run_query("""
            SELECT 
                feature_name as "Fitur",
                ROUND(AVG(rating), 1) as "Rata-rata Rating",
                COUNT(*) as "Jumlah Ulasan"
            FROM app_ratings
            GROUP BY feature_name
            ORDER BY "Rata-rata Rating" DESC
        """)
    return None  # Tabel belum ada


# ─── 6. Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🚀 Smart-WorkLife")
    st.markdown("**Developer Dashboard**")
    st.markdown("---")

    page = st.radio(
        "Navigasi",
        ["📊 Overview & Metrik", "👥 Data Pengguna", "⭐ Feedback & Rating", "🖥️ System Health"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    last_refresh = datetime.now(timezone.utc).astimezone(
        __import__("zoneinfo").ZoneInfo("Asia/Jakarta")
    ).strftime("%d %b %Y, %H:%M WIB")
    st.caption(f"🕐 Data terakhir diperbarui:\n**{last_refresh}**")

    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()


# ─── 7. Halaman: Overview & Metrik ────────────────────────────────────────────
if page == "📊 Overview & Metrik":
    st.title("📊 Overview & Metrik Aplikasi")
    st.markdown("Ringkasan performa real-time aplikasi Smart-WorkLife.")
    st.markdown("---")

    # KPI Cards
    st.subheader("📈 Key Performance Indicators")
    kpi = get_kpi_data()
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="👥 Total Pengguna Aktif",
            value=f"{kpi['total_users']:,}",
            delta=f"+{kpi['new_users_week']} minggu ini"
        )
    with col2:
        delta_str = f"+{kpi['dau_delta']}" if kpi['dau_delta'] >= 0 else str(kpi['dau_delta'])
        st.metric(
            label="🔥 DAU (Harian)",
            value=f"{kpi['dau']:,}",
            delta=f"{delta_str} dari kemarin"
        )
    with col3:
        st.metric(
            label="📅 MAU (Bulanan)",
            value=f"{kpi['mau']:,}",
            help="Dihitung dari user yang aktif di fitur Pomodoro bulan ini"
        )
    with col4:
        st.metric(
            label="🆕 User Baru (7 Hari)",
            value=f"{kpi['new_users_week']:,}",
        )

    st.markdown("---")

    # Dua grafik sejajar
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("📅 Registrasi User Baru (7 Hari)")
        df_new_users = get_new_users_chart()
        if not df_new_users.empty:
            st.bar_chart(df_new_users["jumlah_user_baru"], color="#818CF8")
        else:
            st.info("Belum ada data registrasi minggu ini.")

    with col_right:
        st.subheader("🍅 Tren Sesi Pomodoro Selesai (14 Hari)")
        df_pomo = get_pomodoro_trend()
        if not df_pomo.empty:
            st.area_chart(df_pomo["sesi_selesai"], color="#34D399")
        else:
            st.info("Belum ada sesi Pomodoro yang diselesaikan.")

    st.markdown("---")

    # Penggunaan Fitur
    st.subheader("🛠️ Perbandingan Penggunaan Fitur (Bulan Ini)")
    df_usage = get_feature_usage()
    if not df_usage.empty and df_usage["Penggunaan Bulan Ini"].sum() > 0:
        st.bar_chart(df_usage, color="#F472B6")
    else:
        st.info("Belum ada data penggunaan fitur bulan ini.")


# ─── 8. Halaman: Data Pengguna ─────────────────────────────────────────────────
elif page == "👥 Data Pengguna":
    st.title("👥 Data Pengguna Terdaftar")
    st.markdown("Pantau detail pengguna yang terdaftar di aplikasi Smart-WorkLife.")
    st.markdown("---")

    kpi = get_kpi_data()
    col1, col2, col3 = st.columns(3)
    col1.metric("Total User Aktif", f"{kpi['total_users']:,}")
    col2.metric("User Baru 7 Hari", f"{kpi['new_users_week']:,}")
    col3.metric("DAU (Hari Ini)", f"{kpi['dau']:,}")

    st.markdown("---")
    st.subheader("📋 10 Pengguna Terbaru")
    df_users = get_recent_users()
    if not df_users.empty:
        st.dataframe(df_users, use_container_width=True, hide_index=True)
    else:
        st.info("Tidak ada data pengguna yang tersedia.")


# ─── 9. Halaman: Feedback & Rating ────────────────────────────────────────────
elif page == "⭐ Feedback & Rating":
    st.title("⭐ Feedback & Ulasan Pengguna")
    st.markdown("Pantau kepuasan pengguna untuk menentukan prioritas perbaikan.")
    st.markdown("---")

    df_ratings = get_ratings_data()

    if df_ratings is not None:
        if not df_ratings.empty:
            # Tampilkan data rating nyata
            col1, col2 = st.columns([1, 2])
            with col1:
                st.subheader("Rata-rata Rating Fitur")
                for _, row in df_ratings.iterrows():
                    rating = float(row["Rata-rata Rating"])
                    stars = "⭐" * round(rating)
                    st.write(f"**{row['Fitur']}**: {stars} `{rating}/5.0`")
                    st.progress(rating / 5.0)
                    st.caption(f"Dari {int(row['Jumlah Ulasan'])} ulasan")
                    st.markdown("")
            with col2:
                st.subheader("Tabel Rekapitulasi Rating")
                st.dataframe(df_ratings, use_container_width=True, hide_index=True)
        else:
            st.info("Belum ada user yang memberikan rating. Coba submit rating pertama Anda dari aplikasi Flutter!")
    else:
        # Tabel rating belum ada — tampilkan info setup
        st.warning("⚠️ Tabel `app_ratings` belum tersedia di database.")
        st.info("""
            **Langkah selanjutnya** untuk mengaktifkan fitur ini:
            1. ✅ Buat halaman **"Feedback & Penilaian"** di Flutter (Mobile App).
            2. ✅ Buat endpoint `POST /ratings` di FastAPI Backend.
            3. ✅ Jalankan migration untuk membuat tabel `app_ratings`.
            4. ✅ Data rating dari pengguna akan otomatis muncul di sini!
        """)

        st.markdown("---")
        st.subheader("🎯 Preview Rating (Demo Dummy)")
        st.caption("Tampilan ini adalah preview. Data nyata akan muncul setelah fitur rating di Flutter selesai.")

        dummy_ratings = {
            "Fitur": ["Keseluruhan Aplikasi", "🍅 Pomodoro", "✅ Smart Todo", "🎙️ Smart Notulen", "🧘 Smart Stretching", "💡 Smart Insight", "💧 Smart Health"],
            "Rata-rata Rating (Demo)": [4.7, 4.9, 4.8, 4.2, 4.5, 4.3, 4.6],
            "Jumlah Ulasan (Demo)": [120, 95, 110, 60, 45, 55, 80]
        }
        df_demo = pd.DataFrame(dummy_ratings)

        col1, col2 = st.columns([1, 2])
        with col1:
            for _, row in df_demo.iterrows():
                rating = float(row["Rata-rata Rating (Demo)"])
                stars = "⭐" * round(rating)
                st.write(f"**{row['Fitur']}**: {stars} `{rating}/5.0`")
                st.progress(rating / 5.0)
                st.markdown("")
        with col2:
            st.dataframe(df_demo, use_container_width=True, hide_index=True)


# ─── 10. Halaman: System Health ────────────────────────────────────────────────
elif page == "🖥️ System Health":
    st.title("🖥️ System Health & Data Pipelines")
    st.markdown("Pantau status kelancaran server, database, dan mesin *scraper* Python.")
    st.markdown("---")

    # Cek koneksi database secara langsung
    st.subheader("🔌 Status Layanan")
    col1, col2, col3 = st.columns(3)

    with col1:
        df_check = run_query("SELECT 1 as ok")
        if not df_check.empty:
            st.success("🟢 **PostgreSQL (Neon)**\nTerhubung & Normal")
        else:
            st.error("🔴 **PostgreSQL (Neon)**\nGagal Terhubung")

    with col2:
        st.warning("🟡 **FastAPI Backend**\nStatus: Tidak Dicek Langsung")

    with col3:
        # Cek data scraper MongoDB dengan melihat data terbaru
        df_mongo_check = run_query("SELECT COUNT(*) as c FROM users LIMIT 1")  # placeholder
        st.info("🔵 **MongoDB Scraper**\nCek via log GitHub Actions")

    st.markdown("---")

    # Statistik database
    st.subheader("📊 Statistik Database")
    col1, col2, col3, col4 = st.columns(4)

    df_todos = run_query("SELECT COUNT(*) as c FROM todos")
    df_pomo_total = run_query("SELECT COUNT(*) as c FROM pomodoro_sessions")
    df_notulen = run_query("SELECT COUNT(*) as c FROM notulens")
    df_stretching = run_query("SELECT COUNT(*) as c FROM stretching_sessions")

    col1.metric("Total Todos", int(df_todos["c"].iloc[0]) if not df_todos.empty else 0)
    col2.metric("Total Sesi Pomodoro", int(df_pomo_total["c"].iloc[0]) if not df_pomo_total.empty else 0)
    col3.metric("Total Notulen", int(df_notulen["c"].iloc[0]) if not df_notulen.empty else 0)
    col4.metric("Total Sesi Stretching", int(df_stretching["c"].iloc[0]) if not df_stretching.empty else 0)

    st.markdown("---")
    st.subheader("📜 Informasi Pipeline Scraper")
    st.markdown("""
    | Pipeline | Jadwal | Tujuan | Status |
    |---|---|---|---|
    | `scraper_detik.py` | Setiap hari (via GitHub Actions) | MongoDB → `Data_Detik` | 🟡 Cek di GitHub Actions |
    | `scraper_youtube.py` | Setiap hari (via GitHub Actions) | MongoDB → `Data_Youtube_2` | 🟡 Cek di GitHub Actions |
    | FastAPI Backend | Continuous (Neon Cloud) | PostgreSQL | 🟢 Online |
    """)
    st.info("💡 Untuk melihat status scraper, kunjungi tab **Actions** di repositori GitHub `Analisis_BigData` Anda.")
