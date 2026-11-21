-- ==========================================
-- CAMPUS EVENT REGISTRATION SYSTEM
-- DATABASE SCHEMA
-- ==========================================

PRAGMA foreign_keys = ON;

-- ==========================================
-- TABLE 1: EVENTS
-- ==========================================

CREATE TABLE IF NOT EXISTS events (

    event_id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT NOT NULL,

    event_date TEXT NOT NULL,

    seats INTEGER NOT NULL
        CHECK (seats > 0),

    registered INTEGER NOT NULL DEFAULT 0
        CHECK (registered >= 0 AND registered <= seats)

);


-- ==========================================
-- TABLE 2: REGISTRATIONS
-- ==========================================

CREATE TABLE IF NOT EXISTS registrations (

    reg_id INTEGER PRIMARY KEY AUTOINCREMENT,

    event_id INTEGER NOT NULL,

    student_name TEXT NOT NULL,

    roll_no TEXT NOT NULL,

    registered_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    status TEXT NOT NULL DEFAULT 'ACTIVE'
        CHECK (status IN ('ACTIVE', 'CANCELLED')),

    FOREIGN KEY (event_id)
        REFERENCES events(event_id)
        ON DELETE RESTRICT,

    UNIQUE (event_id, roll_no)

);


-- ==========================================
-- TABLE 3: MANAGERS
-- ==========================================

CREATE TABLE IF NOT EXISTS managers (

    manager_id INTEGER PRIMARY KEY AUTOINCREMENT,

    username TEXT NOT NULL UNIQUE,

    password_hash TEXT NOT NULL

);

-- ==========================================
-- INDEXES FOR FASTER SEARCHING
-- ==========================================

CREATE INDEX IF NOT EXISTS idx_registrations_event
ON registrations(event_id);

CREATE INDEX IF NOT EXISTS idx_registrations_roll
ON registrations(roll_no);