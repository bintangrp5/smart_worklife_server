-- ============================================================
-- Smart-WorkLife Database Schema
-- PostgreSQL 15+
-- ============================================================

-- Extension untuk UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- 1. USERS
-- ============================================================
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email           VARCHAR(255) NOT NULL UNIQUE,
    username        VARCHAR(100) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    full_name       VARCHAR(255),
    avatar_url      TEXT,
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);

-- ============================================================
-- 2. USER PREFERENCES
-- ============================================================
CREATE TABLE user_preferences (
    id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id                 UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    theme                   VARCHAR(20) DEFAULT 'light',
    notifications_enabled   BOOLEAN DEFAULT TRUE,
    language                VARCHAR(10) DEFAULT 'id',
    created_at              TIMESTAMPTZ DEFAULT NOW(),
    updated_at              TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- 3. POMODORO SETTINGS
-- ============================================================
CREATE TABLE pomodoro_settings (
    id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id                 UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    mode                    VARCHAR(20) NOT NULL, -- classic | deep_work | extend
    focus_duration_minutes  INTEGER NOT NULL,
    break_duration_minutes  INTEGER NOT NULL,
    is_active               BOOLEAN DEFAULT TRUE,
    created_at              TIMESTAMPTZ DEFAULT NOW(),
    updated_at              TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- 4. POMODORO SESSIONS
-- ============================================================
CREATE TABLE pomodoro_sessions (
    id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id                 UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    setting_id              UUID REFERENCES pomodoro_settings(id) ON DELETE SET NULL,
    mode                    VARCHAR(20) NOT NULL,
    session_type            VARCHAR(10) NOT NULL,  -- focus | break
    duration_seconds        INTEGER NOT NULL,
    actual_duration_seconds INTEGER,
    status                  VARCHAR(20) NOT NULL DEFAULT 'in_progress', -- completed | cancelled | in_progress
    started_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ended_at                TIMESTAMPTZ,
    session_date            DATE NOT NULL DEFAULT CURRENT_DATE
);

CREATE INDEX idx_pomodoro_sessions_user_date ON pomodoro_sessions(user_id, session_date);
CREATE INDEX idx_pomodoro_sessions_status ON pomodoro_sessions(user_id, status);

-- ============================================================
-- 5. STRETCHING EXERCISES (Master Data)
-- ============================================================
CREATE TABLE stretching_exercises (
    id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name                    VARCHAR(100) NOT NULL,
    description             TEXT,
    image_url               TEXT,
    animation_url           TEXT,
    default_reps            INTEGER DEFAULT 10,
    default_duration_seconds INTEGER DEFAULT 30,
    body_part               VARCHAR(50),
    sort_order              INTEGER DEFAULT 0,
    is_active               BOOLEAN DEFAULT TRUE,
    created_at              TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- 6. STRETCHING SESSIONS
-- ============================================================
CREATE TABLE stretching_sessions (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    exercise_id     UUID NOT NULL REFERENCES stretching_exercises(id) ON DELETE CASCADE,
    total_reps      INTEGER DEFAULT 0,
    correct_reps    INTEGER DEFAULT 0,
    duration_seconds INTEGER,
    accuracy_score  FLOAT,
    status          VARCHAR(20) DEFAULT 'in_progress',
    started_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ended_at        TIMESTAMPTZ
);

CREATE INDEX idx_stretching_sessions_user ON stretching_sessions(user_id, started_at);

-- ============================================================
-- 7. STRETCHING REPS
-- ============================================================
CREATE TABLE stretching_reps (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id  UUID NOT NULL REFERENCES stretching_sessions(id) ON DELETE CASCADE,
    rep_number  INTEGER NOT NULL,
    is_correct  BOOLEAN NOT NULL,
    feedback    TEXT,
    recorded_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- 8. BMI PROFILES
-- ============================================================
CREATE TABLE bmi_profiles (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    height_cm       FLOAT NOT NULL,
    weight_kg       FLOAT NOT NULL,
    bmi_value       FLOAT,
    bmi_category    VARCHAR(20), -- underweight | normal | overweight | obese
    calculated_at   TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- 9. HYDRATION SETTINGS
-- ============================================================
CREATE TABLE hydration_settings (
    id                          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id                     UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    daily_target_ml             FLOAT NOT NULL,
    reminder_interval_minutes   INTEGER DEFAULT 60,
    reminder_enabled            BOOLEAN DEFAULT TRUE,
    reminder_start_time         TIME DEFAULT '08:00:00',
    reminder_end_time           TIME DEFAULT '20:00:00',
    created_at                  TIMESTAMPTZ DEFAULT NOW(),
    updated_at                  TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- 10. HYDRATION LOGS
-- ============================================================
CREATE TABLE hydration_logs (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    amount_ml   FLOAT NOT NULL,
    log_date    DATE NOT NULL DEFAULT CURRENT_DATE,
    logged_at   TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_hydration_logs_user_date ON hydration_logs(user_id, log_date);

-- ============================================================
-- 11. TODOS
-- ============================================================
CREATE TABLE todos (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title           VARCHAR(255) NOT NULL,
    description     TEXT,
    priority        VARCHAR(20) DEFAULT 'normal',   -- important | normal
    status          VARCHAR(20) DEFAULT 'pending',  -- pending | done
    deadline        TIMESTAMPTZ,
    task_date       DATE,
    completed_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_todos_user_status ON todos(user_id, status);
CREATE INDEX idx_todos_user_date ON todos(user_id, task_date);
CREATE INDEX idx_todos_user_priority ON todos(user_id, priority);

-- ============================================================
-- 12. NOTULENS
-- ============================================================
CREATE TABLE notulens (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title               VARCHAR(255) NOT NULL,
    transcript          TEXT,
    summary             TEXT,
    action_items        JSONB,
    duration_seconds    INTEGER,
    audio_url           TEXT,
    meeting_date        TIMESTAMPTZ,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_notulens_user ON notulens(user_id, created_at);

-- ============================================================
-- SEED: Default Stretching Exercises
-- ============================================================
INSERT INTO stretching_exercises (name, description, body_part, default_reps, default_duration_seconds, sort_order) VALUES
('Neck Tilt',           'Miringkan kepala ke kiri dan kanan secara bergantian',    'neck',     10, 30, 1),
('Shoulder Shrug',      'Angkat bahu ke atas lalu lepaskan secara perlahan',       'shoulder', 10, 30, 2),
('Upper Back Stretch',  'Tarik kedua tangan ke depan dan bulatkan punggung atas',  'back',     10, 30, 3);
