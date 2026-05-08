-- Add columns expected by SQLAlchemy models (Reservations) when upgrading an older DB.
-- Safe to run multiple times (IF NOT EXISTS).

ALTER TABLE weddingplan.reservations
  ADD COLUMN IF NOT EXISTS interested_dates TEXT,
  ADD COLUMN IF NOT EXISTS guest_count INTEGER,
  ADD COLUMN IF NOT EXISTS event_type VARCHAR(100),
  ADD COLUMN IF NOT EXISTS other_comments TEXT;
