-- Example partition creation for date-partitioned tables
-- Run this script to create partitions for a date range
-- Adjust date ranges as needed for your use case

-- Example: Create partitions for Q1 2026
-- Amazon listings partitions
CREATE TABLE amazon_listings_raw_2026_01 PARTITION OF amazon_listings_raw
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');

CREATE TABLE amazon_listings_raw_2026_02 PARTITION OF amazon_listings_raw
    FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');

CREATE TABLE amazon_listings_raw_2026_03 PARTITION OF amazon_listings_raw
    FOR VALUES FROM ('2026-03-01') TO ('2026-04-01');

-- Similar for other partitioned tables...
-- Note: In production, you may want to automate partition creation
-- or use a tool like pg_partman

