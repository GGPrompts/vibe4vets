-- SQL to sync employment resource fixes to production
-- Run against Railway Postgres
-- Generated: 2026-02-01

BEGIN;

-- Updated URLs (3 resources)
UPDATE resources SET website = 'https://jobs.apple.com/en-us/search?team=Apple+Veterans', updated_at = NOW() WHERE id = '8dc9cc7c-e02c-4654-9b95-73b9d71f4501';
-- Apple - Veteran Hiring Program

UPDATE resources SET website = 'https://www.google.com/about/careers/applications/programs/veterans/', updated_at = NOW() WHERE id = '9dfc0bdd-bf39-4af3-a726-d71f1020bd7e';
-- Google - Veteran Hiring Program

UPDATE resources SET website = 'https://careers.starbucks.com', updated_at = NOW() WHERE id = 'c1833e9d-70a0-499a-a1f7-ae0a3923a9e0';
-- Starbucks - Veteran Hiring Program

-- Marked INACTIVE (8 resources)
UPDATE resources SET status = 'inactive', updated_at = NOW() WHERE id = '7a95444c-925c-4f31-b659-1d4b46d8cb2e';
-- Hilton - Veteran Hiring Program

UPDATE resources SET status = 'inactive', updated_at = NOW() WHERE id = '573e7b16-84a2-4df6-b2f7-4b19a7f20f5a';
-- Boeing - Veteran Hiring Program

UPDATE resources SET status = 'inactive', updated_at = NOW() WHERE id = '6a4dd0e1-77dd-4fd2-b55d-7d6f53f6272d';
-- Target - Veteran Hiring Program

UPDATE resources SET status = 'inactive', updated_at = NOW() WHERE id = 'be30d1a8-46df-43ea-885e-17ab631d6de3';
-- Wells Fargo - Veteran Hiring Program

UPDATE resources SET status = 'inactive', updated_at = NOW() WHERE id = '7d9cdcb1-05af-40f0-8f8f-368305c9617e';
-- Cisco - Veteran Hiring Program

UPDATE resources SET status = 'inactive', updated_at = NOW() WHERE id = 'c307b6c3-75db-4ae4-82d7-20f1f27afe12';
-- Accenture - Veteran Hiring Program

UPDATE resources SET status = 'inactive', updated_at = NOW() WHERE id = 'f17fe01d-7879-4834-8572-4ba5a73d62af';
-- Deloitte - Veteran Hiring Program

UPDATE resources SET status = 'inactive', updated_at = NOW() WHERE id = '92956395-2963-482b-9aeb-3f0d617031df';
-- Bank of America - Veteran Hiring Program

COMMIT;
