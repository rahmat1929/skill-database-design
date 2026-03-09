-- =============================================================================
-- Realistic Seed Data Generator
-- Database: PostgreSQL
-- Domain: Loyalty System
-- Usage: psql -d your_database -f seed_generator.sql
-- =============================================================================

BEGIN;

-- =============================================
-- 1. Tiers (Tingkatan)
-- =============================================
INSERT INTO tiers (id, name, level, min_points, points_multiplier, benefits, is_active) VALUES
    ('a0000000-0000-0000-0000-000000000001', 'Bronze',   'bronze',   0,      1.00, '["Birthday bonus", "Member price"]', true),
    ('a0000000-0000-0000-0000-000000000002', 'Silver',   'silver',   5000,   1.25, '["Birthday bonus", "Member price", "Free shipping 2x/month"]', true),
    ('a0000000-0000-0000-0000-000000000003', 'Gold',     'gold',     20000,  1.50, '["Birthday bonus", "Member price", "Free shipping unlimited", "Priority support"]', true),
    ('a0000000-0000-0000-0000-000000000004', 'Platinum', 'platinum', 50000,  2.00, '["Birthday bonus", "Member price", "Free shipping unlimited", "Priority support", "Exclusive events", "Personal shopper"]', true),
    ('a0000000-0000-0000-0000-000000000005', 'Diamond',  'diamond',  100000, 3.00, '["All Platinum benefits", "VIP lounge access", "Concierge service", "Early access to new products"]', true)
ON CONFLICT (id) DO NOTHING;

-- =============================================
-- 2. Members (Anggota) — 20 realistic members
-- =============================================
INSERT INTO members (id, member_code, email, full_name, phone, tier_id, status, joined_at) VALUES
    ('b0000000-0000-0000-0000-000000000001', 'MBR-20240001', 'andi.pratama@gmail.com',       'Andi Pratama',        '+6281234567001', 'a0000000-0000-0000-0000-000000000003', 'active', '2024-01-15'),
    ('b0000000-0000-0000-0000-000000000002', 'MBR-20240002', 'siti.rahayu@yahoo.com',         'Siti Rahayu',         '+6281234567002', 'a0000000-0000-0000-0000-000000000001', 'active', '2024-02-20'),
    ('b0000000-0000-0000-0000-000000000003', 'MBR-20240003', 'budi.santoso@hotmail.com',      'Budi Santoso',        '+6281234567003', 'a0000000-0000-0000-0000-000000000002', 'active', '2024-01-10'),
    ('b0000000-0000-0000-0000-000000000004', 'MBR-20240004', 'dewi.lestari@gmail.com',        'Dewi Lestari',        '+6281234567004', 'a0000000-0000-0000-0000-000000000004', 'active', '2023-11-05'),
    ('b0000000-0000-0000-0000-000000000005', 'MBR-20240005', 'rizky.firmansyah@outlook.com',  'Rizky Firmansyah',    '+6281234567005', 'a0000000-0000-0000-0000-000000000001', 'active', '2024-03-01'),
    ('b0000000-0000-0000-0000-000000000006', 'MBR-20240006', 'sarah.johnson@gmail.com',       'Sarah Johnson',       '+6281234567006', 'a0000000-0000-0000-0000-000000000005', 'active', '2023-06-15'),
    ('b0000000-0000-0000-0000-000000000007', 'MBR-20240007', 'michael.chen@gmail.com',        'Michael Chen',        '+6281234567007', 'a0000000-0000-0000-0000-000000000003', 'active', '2024-01-20'),
    ('b0000000-0000-0000-0000-000000000008', 'MBR-20240008', 'nina.kusuma@yahoo.com',         'Nina Kusuma',         '+6281234567008', 'a0000000-0000-0000-0000-000000000001', 'suspended', '2024-04-10'),
    ('b0000000-0000-0000-0000-000000000009', 'MBR-20240009', 'ahmad.hidayat@gmail.com',       'Ahmad Hidayat',       '+6281234567009', 'a0000000-0000-0000-0000-000000000002', 'active', '2024-02-28'),
    ('b0000000-0000-0000-0000-000000000010', 'MBR-20240010', 'lisa.permata@hotmail.com',      'Lisa Permata',        '+6281234567010', 'a0000000-0000-0000-0000-000000000001', 'active', '2024-05-12'),
    ('b0000000-0000-0000-0000-000000000011', 'MBR-20240011', 'david.wijaya@gmail.com',        'David Wijaya',        '+6281234567011', 'a0000000-0000-0000-0000-000000000003', 'active', '2023-12-01'),
    ('b0000000-0000-0000-0000-000000000012', 'MBR-20240012', 'maya.putri@outlook.com',        'Maya Putri Sari',     '+6281234567012', 'a0000000-0000-0000-0000-000000000001', 'active', '2024-06-20'),
    ('b0000000-0000-0000-0000-000000000013', 'MBR-20240013', 'rudi.hartono@gmail.com',        'Rudi Hartono',        '+6281234567013', 'a0000000-0000-0000-0000-000000000002', 'active', '2024-03-15'),
    ('b0000000-0000-0000-0000-000000000014', 'MBR-20240014', 'anna.christina@yahoo.com',      'Anna Christina',      '+6281234567014', 'a0000000-0000-0000-0000-000000000004', 'active', '2023-09-10'),
    ('b0000000-0000-0000-0000-000000000015', 'MBR-20240015', 'tommy.susanto@gmail.com',       'Tommy Susanto',       '+6281234567015', 'a0000000-0000-0000-0000-000000000001', 'active', '2024-07-01')
ON CONFLICT (id) DO NOTHING;

-- =============================================
-- 3. Point Balances (Saldo Poin)
-- =============================================
INSERT INTO point_balances (member_id, current_balance, lifetime_earned, lifetime_redeemed) VALUES
    ('b0000000-0000-0000-0000-000000000001', 22500,  35000,  12500),
    ('b0000000-0000-0000-0000-000000000002', 1200,   1800,   600),
    ('b0000000-0000-0000-0000-000000000003', 8500,   12000,  3500),
    ('b0000000-0000-0000-0000-000000000004', 45000,  75000,  30000),
    ('b0000000-0000-0000-0000-000000000005', 300,    500,    200),
    ('b0000000-0000-0000-0000-000000000006', 95000,  150000, 55000),
    ('b0000000-0000-0000-0000-000000000007', 18000,  28000,  10000),
    ('b0000000-0000-0000-0000-000000000008', 0,      2000,   2000),
    ('b0000000-0000-0000-0000-000000000009', 6500,   9000,   2500),
    ('b0000000-0000-0000-0000-000000000010', 800,    1200,   400),
    ('b0000000-0000-0000-0000-000000000011', 25000,  40000,  15000),
    ('b0000000-0000-0000-0000-000000000012', 500,    700,    200),
    ('b0000000-0000-0000-0000-000000000013', 7200,   10500,  3300),
    ('b0000000-0000-0000-0000-000000000014', 52000,  80000,  28000),
    ('b0000000-0000-0000-0000-000000000015', 150,    250,    100)
ON CONFLICT (member_id) DO NOTHING;

-- =============================================
-- 4. Rewards (Hadiah)
-- =============================================
INSERT INTO rewards (id, name, description, points_cost, stock, min_tier, is_active) VALUES
    ('c0000000-0000-0000-0000-000000000001', 'Rp 50.000 Voucher',          'Shopping voucher worth Rp 50.000',      5000,  100, 'bronze',   true),
    ('c0000000-0000-0000-0000-000000000002', 'Rp 100.000 Voucher',         'Shopping voucher worth Rp 100.000',     9000,  50,  'bronze',   true),
    ('c0000000-0000-0000-0000-000000000003', 'Free Coffee Tumbler',        'Premium stainless steel tumbler 500ml', 3000,  200, 'bronze',   true),
    ('c0000000-0000-0000-0000-000000000004', 'Weekend Spa Package',        '2-hour spa treatment at partner hotel', 25000, 20,  'gold',     true),
    ('c0000000-0000-0000-0000-000000000005', 'Airport Lounge Pass',        'Single-use airport lounge access',      15000, 50,  'silver',   true),
    ('c0000000-0000-0000-0000-000000000006', 'Exclusive Tote Bag',         'Limited edition designer tote bag',     8000,  30,  'silver',   true),
    ('c0000000-0000-0000-0000-000000000007', 'Hotel Stay 1 Night',         'One night at partner 4-star hotel',     40000, 10,  'platinum', true),
    ('c0000000-0000-0000-0000-000000000008', 'Concert VIP Ticket',         'VIP ticket to upcoming concert event',  50000, 5,   'platinum', true),
    ('c0000000-0000-0000-0000-000000000009', 'Rp 500.000 E-Wallet Credit', 'Top up to your e-wallet',              40000, 100, 'gold',     true),
    ('c0000000-0000-0000-0000-000000000010', 'Free Shipping 1 Month',      'Unlimited free shipping for 30 days',   2000,  999, 'bronze',   true)
ON CONFLICT (id) DO NOTHING;

-- =============================================
-- 5. Transactions (Transaksi) — sample earning events
-- =============================================
INSERT INTO transactions (id, member_id, type, reference_id, amount, points_earned, multiplier_applied, notes) VALUES
    (gen_random_uuid(), 'b0000000-0000-0000-0000-000000000001', 'purchase',   'ORD-2024-00101', 500000.00,  750,  1.50, 'Gold tier 1.5x multiplier'),
    (gen_random_uuid(), 'b0000000-0000-0000-0000-000000000001', 'purchase',   'ORD-2024-00205', 1200000.00, 1800, 1.50, 'Electronics purchase'),
    (gen_random_uuid(), 'b0000000-0000-0000-0000-000000000001', 'bonus',      NULL,             0,          500,  1.00, 'Birthday bonus'),
    (gen_random_uuid(), 'b0000000-0000-0000-0000-000000000002', 'purchase',   'ORD-2024-00302', 250000.00,  250,  1.00, 'Bronze tier standard rate'),
    (gen_random_uuid(), 'b0000000-0000-0000-0000-000000000002', 'purchase',   'ORD-2024-00410', 150000.00,  150,  1.00, 'Grocery purchase'),
    (gen_random_uuid(), 'b0000000-0000-0000-0000-000000000004', 'purchase',   'ORD-2024-00512', 3000000.00, 6000, 2.00, 'Platinum tier 2x multiplier'),
    (gen_random_uuid(), 'b0000000-0000-0000-0000-000000000004', 'refund',     'RFN-2024-00101', 500000.00,  -1000, 2.00, 'Partial refund - points deducted'),
    (gen_random_uuid(), 'b0000000-0000-0000-0000-000000000006', 'purchase',   'ORD-2024-00601', 5000000.00, 15000, 3.00, 'Diamond tier 3x multiplier'),
    (gen_random_uuid(), 'b0000000-0000-0000-0000-000000000006', 'bonus',      NULL,             0,          2000, 1.00, 'Anniversary bonus'),
    (gen_random_uuid(), 'b0000000-0000-0000-0000-000000000003', 'purchase',   'ORD-2024-00715', 800000.00,  1000, 1.25, 'Silver tier 1.25x multiplier')
ON CONFLICT (id) DO NOTHING;

-- =============================================
-- 6. Redemptions (Penukaran)
-- =============================================
INSERT INTO redemptions (id, member_id, reward_id, points_spent, status, fulfilled_at) VALUES
    (gen_random_uuid(), 'b0000000-0000-0000-0000-000000000001', 'c0000000-0000-0000-0000-000000000001', 5000,  'fulfilled', NOW() - INTERVAL '30 days'),
    (gen_random_uuid(), 'b0000000-0000-0000-0000-000000000001', 'c0000000-0000-0000-0000-000000000005', 15000, 'fulfilled', NOW() - INTERVAL '15 days'),
    (gen_random_uuid(), 'b0000000-0000-0000-0000-000000000004', 'c0000000-0000-0000-0000-000000000007', 40000, 'pending',   NULL),
    (gen_random_uuid(), 'b0000000-0000-0000-0000-000000000006', 'c0000000-0000-0000-0000-000000000008', 50000, 'fulfilled', NOW() - INTERVAL '7 days'),
    (gen_random_uuid(), 'b0000000-0000-0000-0000-000000000011', 'c0000000-0000-0000-0000-000000000004', 25000, 'approved',  NULL)
ON CONFLICT (id) DO NOTHING;

-- =============================================
-- 7. Member Tier History (Riwayat Tier)
-- =============================================
INSERT INTO member_tier_history (member_id, from_tier_id, to_tier_id, reason, changed_at) VALUES
    ('b0000000-0000-0000-0000-000000000001', 'a0000000-0000-0000-0000-000000000001', 'a0000000-0000-0000-0000-000000000002', 'auto_promotion', '2024-03-01'),
    ('b0000000-0000-0000-0000-000000000001', 'a0000000-0000-0000-0000-000000000002', 'a0000000-0000-0000-0000-000000000003', 'auto_promotion', '2024-06-15'),
    ('b0000000-0000-0000-0000-000000000004', 'a0000000-0000-0000-0000-000000000001', 'a0000000-0000-0000-0000-000000000002', 'auto_promotion', '2023-12-01'),
    ('b0000000-0000-0000-0000-000000000004', 'a0000000-0000-0000-0000-000000000002', 'a0000000-0000-0000-0000-000000000003', 'auto_promotion', '2024-02-15'),
    ('b0000000-0000-0000-0000-000000000004', 'a0000000-0000-0000-0000-000000000003', 'a0000000-0000-0000-0000-000000000004', 'auto_promotion', '2024-05-01'),
    ('b0000000-0000-0000-0000-000000000006', 'a0000000-0000-0000-0000-000000000003', 'a0000000-0000-0000-0000-000000000004', 'auto_promotion', '2023-09-01'),
    ('b0000000-0000-0000-0000-000000000006', 'a0000000-0000-0000-0000-000000000004', 'a0000000-0000-0000-0000-000000000005', 'auto_promotion', '2024-01-10')
ON CONFLICT DO NOTHING;

COMMIT;

-- =============================================
-- Verification queries (kueri verifikasi)
-- =============================================

-- Check member counts per tier
SELECT t.name AS tier, COUNT(m.id) AS member_count
FROM tiers t
LEFT JOIN members m ON m.tier_id = t.id AND m.deleted_at IS NULL
GROUP BY t.name, t.min_points
ORDER BY t.min_points;

-- Check point balance distribution
SELECT t.name AS tier,
       COUNT(pb.member_id) AS members,
       AVG(pb.current_balance)::INT AS avg_balance,
       MAX(pb.current_balance) AS max_balance,
       SUM(pb.lifetime_earned) AS total_lifetime
FROM point_balances pb
JOIN members m ON m.id = pb.member_id
JOIN tiers t ON t.id = m.tier_id
GROUP BY t.name, t.min_points
ORDER BY t.min_points;

-- Check reward catalog
SELECT name, points_cost, stock, min_tier, is_active
FROM rewards ORDER BY points_cost;
