--
-- Wedding Plan Master Schema
-- Combined and Cleaned - Always in sync with Tasos' latest updates
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;



CREATE SCHEMA weddingplan;
ALTER SCHEMA weddingplan OWNER TO postgres;

-- Re-setup extension
CREATE EXTENSION IF NOT EXISTS pgcrypto SCHEMA weddingplan;

-- Search path configuration
ALTER DATABASE postgres SET search_path TO postgres,public,weddingplan;

-- Permissions
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'readaccess') THEN
        CREATE ROLE readaccess;
    END IF;
END
$$;

GRANT USAGE ON SCHEMA public TO readaccess;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readaccess;
GRANT USAGE ON SCHEMA weddingplan TO readaccess;
GRANT SELECT ON ALL TABLES IN SCHEMA weddingplan TO readaccess;

ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO readaccess;
ALTER DEFAULT PRIVILEGES IN SCHEMA weddingplan GRANT SELECT ON TABLES TO readaccess;

-- 1. USERS (Authentication & Roles)
CREATE TABLE weddingplan.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role VARCHAR(50) DEFAULT 'COUPLE', -- 'COUPLE' or 'PARTNER'
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE weddingplan.users OWNER TO postgres;

-- 2. PARTNER PROFILES
CREATE TABLE weddingplan.partner_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE REFERENCES weddingplan.users(id) ON DELETE CASCADE,
    business_name VARCHAR(255) NOT NULL,
    category VARCHAR(100), -- e.g., 'Venue', 'Catering', 'Photography'
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE weddingplan.partner_profiles OWNER TO postgres;

-- 3. RESERVATIONS & REQUESTS
CREATE TABLE weddingplan.reservations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    partner_id UUID NOT NULL REFERENCES weddingplan.users(id) ON DELETE CASCADE,
    couple_id UUID REFERENCES weddingplan.users(id) ON DELETE CASCADE,
    guest_first_name VARCHAR(100),
    guest_last_name VARCHAR(100),
    guest_email VARCHAR(255),
    guest_phone VARCHAR(50),
    status VARCHAR(50) DEFAULT 'PENDING', -- 'PENDING', 'ACCEPTED', 'DENIED'
    event_date TIMESTAMPTZ,
    details TEXT,
    budget_per_reservation DECIMAL(12, 2) DEFAULT 0.00,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE weddingplan.reservations OWNER TO postgres;

-- 4. NOTES
CREATE TABLE weddingplan.notes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    author_id UUID NOT NULL REFERENCES weddingplan.users(id) ON DELETE CASCADE,
    reservation_id UUID REFERENCES weddingplan.reservations(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE weddingplan.notes OWNER TO postgres;

-- 5. TASKS
CREATE TABLE weddingplan.tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES weddingplan.users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    notes TEXT,
    is_completed BOOLEAN DEFAULT FALSE,
    due_date TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE weddingplan.tasks OWNER TO postgres;

-- 6. GIFTS
CREATE TABLE weddingplan.gifts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES weddingplan.users(id) ON DELETE CASCADE,
    item_name VARCHAR(255) NOT NULL,
    short_description VARCHAR(255),
    long_description TEXT,
    category VARCHAR(100),
    main_image_url TEXT,
    gallery_image_urls TEXT[],
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE weddingplan.gifts OWNER TO postgres;

-- 7. BUDGETS
CREATE TABLE weddingplan.budgets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE REFERENCES weddingplan.users(id) ON DELETE CASCADE,
    total_budget DECIMAL(12, 2) DEFAULT 0.00,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE weddingplan.budgets OWNER TO postgres;

-- 8. GUESTS
CREATE TABLE weddingplan.guests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES weddingplan.users(id) ON DELETE CASCADE,
    reservation_id UUID REFERENCES weddingplan.reservations(id) ON DELETE SET NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255),
    phone_number VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE weddingplan.guests OWNER TO postgres;


-- 9. PARTNER EXPENSES
CREATE TABLE weddingplan.partner_expenses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    partner_id UUID NOT NULL REFERENCES weddingplan.users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,        -- e.g., "Facebook Ads", "Camera Repair"
    amount DECIMAL(12, 2) NOT NULL,
    category VARCHAR(100),              -- e.g., "Marketing", "Equipment", "Travel"
    expense_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE weddingplan.partner_expenses  OWNER TO postgres