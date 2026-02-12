-- Add trial_ends_at column to tenants table
ALTER TABLE tenants ADD COLUMN IF NOT EXISTS trial_ends_at TIMESTAMP;

-- For existing tenants, set a default trial_ends_at to 14 days from their creation date
-- if they are on the 'free' tier.
UPDATE tenants 
SET trial_ends_at = created_at + INTERVAL '14 days' 
WHERE trial_ends_at IS NULL AND billing_tier = 'free';
