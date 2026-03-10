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

-- ==========================================
-- DUMMY DATA INSERTS
-- ==========================================

-- 1. USERS
INSERT INTO weddingplan.users (id, role, username, email, password_hash, first_name, last_name) VALUES
-- Password --> hashed_pass_123
('c1111111-1111-1111-1111-111111111111', 'COUPLE', 'alice_and_john', 'alice@example.com', '$2b$12$mEN25JX2khEZwxDCtnPu4uH7vfEFj.G92jR51Ym9L9cGTJ/3nVVh2', 'Alice', 'Wonderland'),
-- Password --> hashed_pass_456
('b2222222-2222-2222-2222-222222222222', 'PARTNER', 'grand_venue', 'booking@grandvenue.gr', '$2b$12$vzc8P28ntepLwqpqP6e8NeDggoBeNk0DCQbatWrneTJp7Fm.yDHwi', 'Kostas', 'Pappas'),
-- Password --> hashed_pass_789
('b3333333-3333-3333-3333-333333333333', 'PARTNER', 'tasty_catering', 'info@tastycatering.gr', '$2b$12$gJKuky.8bp61W595rOZCPueX0UtfEX6rluVYTBiG5p0P4W2RayLm2', 'Maria', 'Leka');

-- 2. PARTNER PROFILES
INSERT INTO weddingplan.partner_profiles (user_id, business_name, category, description) VALUES
('b2222222-2222-2222-2222-222222222222', 'The Grand Estate', 'Venue', 'A beautiful luxury estate with a sea view.'),
('b3333333-3333-3333-3333-333333333333', 'Tasty Catering Co.', 'Catering', 'Premium Mediterranean cuisine for your special day.');

-- 3. BUDGETS
INSERT INTO weddingplan.budgets (user_id, total_budget) VALUES
('c1111111-1111-1111-1111-111111111111', 30000.00),
('b2222222-2222-2222-2222-222222222222', 150000.00);

-- 4. RESERVATIONS & REQUESTS
INSERT INTO weddingplan.reservations (id, partner_id, couple_id, status, event_date, details, budget_per_reservation) VALUES
('d1111111-1111-1111-1111-111111111111', 'b2222222-2222-2222-2222-222222222222', 'c1111111-1111-1111-1111-111111111111', 'ACCEPTED', '2024-09-15 17:00:00+00', 'Booking the main hall for 200 people.', 10000.00),
('d2222222-2222-2222-2222-222222222222', 'b3333333-3333-3333-3333-333333333333', 'c1111111-1111-1111-1111-111111111111', 'PENDING', '2024-09-15 19:00:00+00', 'Do you offer a vegan menu option?', 5000.00);

-- 5. NOTES
INSERT INTO weddingplan.notes (author_id, reservation_id, content) VALUES
('b2222222-2222-2222-2222-222222222222', 'd1111111-1111-1111-1111-111111111111', 'Alice requested round tables instead of square ones.');

-- 6. TASKS
INSERT INTO weddingplan.tasks (user_id, title, description, is_completed, due_date) VALUES
('c1111111-1111-1111-1111-111111111111', 'Finalize Guest List', 'Get addresses from both families', FALSE, '2024-04-01 10:00:00+00'),
('c1111111-1111-1111-1111-111111111111', 'Book Photographer', 'Meeting with Nikos on Friday', TRUE, '2024-02-15 14:00:00+00');

-- 7. GIFTS
INSERT INTO weddingplan.gifts (user_id, item_name, category, short_description) VALUES
('c1111111-1111-1111-1111-111111111111', 'Honeymoon Fund', 'Experiences', 'Help us travel to Italy!'),
('c1111111-1111-1111-1111-111111111111', 'Dyson Vacuum', 'Home', 'V15 Detect Absolute');

-- 8. GUESTS
INSERT INTO weddingplan.guests (user_id, reservation_id, first_name, last_name, email, phone_number) VALUES
('c1111111-1111-1111-1111-111111111111', 'd1111111-1111-1111-1111-111111111111', 'Eleni', 'Papadopoulou', 'eleni@test.gr', '6911111111'),
('c1111111-1111-1111-1111-111111111111', NULL, 'Dimitris', 'Antoniou', 'dimitris@test.gr', '6922222222');
