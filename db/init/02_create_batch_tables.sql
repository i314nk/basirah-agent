-- Batch Processing Tables for basīrah
-- Phase 8: Automated Batch Screening Protocol

-- Batch summaries table (stores batch-level metadata and results)
CREATE TABLE batch_summaries (
    id SERIAL PRIMARY KEY,
    batch_id VARCHAR(255) NOT NULL UNIQUE,
    batch_name VARCHAR(255) NOT NULL,

    -- Protocol information
    protocol_id VARCHAR(50) NOT NULL,
    protocol_name VARCHAR(100) NOT NULL,
    protocol_description TEXT,

    -- Status tracking
    status VARCHAR(50) NOT NULL, -- 'running', 'paused', 'complete', 'error'

    -- Statistics
    total_companies INTEGER NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    duration_seconds INTEGER,
    total_cost DECIMAL(8, 2),

    -- Stage results (stored as JSONB for flexibility)
    -- Example: [{"stage_name": "Quick Screen", "companies_processed": 100, "passed": 70, ...}]
    stage_stats JSONB,

    -- Top recommendations (BUY decisions from final stage)
    -- Example: [{"ticker": "AAPL", "decision": "BUY", "conviction": "HIGH", ...}]
    top_recommendations JSONB,

    -- Error tracking
    error_message TEXT,

    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Constraints
    CHECK (status IN ('idle', 'running', 'paused', 'complete', 'error'))
);

-- Junction table linking analyses to batches
-- Enables hierarchical organization: Batch → Stage → Company Analyses
CREATE TABLE batch_analyses (
    batch_id INTEGER NOT NULL REFERENCES batch_summaries(id) ON DELETE CASCADE,
    analysis_id INTEGER NOT NULL REFERENCES analyses(id) ON DELETE CASCADE,

    -- Stage information
    stage_index INTEGER NOT NULL,
    stage_name VARCHAR(100) NOT NULL,

    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    PRIMARY KEY (batch_id, analysis_id)
);

-- Add batch metadata to analyses table (nullable for non-batch analyses)
ALTER TABLE analyses
ADD COLUMN batch_id VARCHAR(255),
ADD COLUMN batch_stage_name VARCHAR(100),
ADD COLUMN batch_stage_index INTEGER;

-- Indexes for fast batch queries
CREATE INDEX idx_batch_summaries_status ON batch_summaries(status);
CREATE INDEX idx_batch_summaries_date ON batch_summaries(start_time DESC);
CREATE INDEX idx_batch_summaries_protocol ON batch_summaries(protocol_id);

CREATE INDEX idx_batch_analyses_batch ON batch_analyses(batch_id);
CREATE INDEX idx_batch_analyses_stage ON batch_analyses(batch_id, stage_index);

CREATE INDEX idx_analyses_batch_id ON analyses(batch_id) WHERE batch_id IS NOT NULL;

-- Trigger for batch_summaries updated_at
CREATE TRIGGER trigger_batch_summaries_updated_at
BEFORE UPDATE ON batch_summaries
FOR EACH ROW
EXECUTE FUNCTION update_updated_at();

-- View for easy batch querying with analysis counts
CREATE VIEW v_batch_summary AS
SELECT
    bs.id,
    bs.batch_id,
    bs.batch_name,
    bs.protocol_name,
    bs.status,
    bs.total_companies,
    bs.start_time,
    bs.end_time,
    bs.duration_seconds,
    bs.total_cost,
    bs.stage_stats,
    bs.created_at,
    COUNT(DISTINCT ba.analysis_id) as analyses_count,
    COUNT(DISTINCT CASE WHEN a.decision = 'BUY' THEN ba.analysis_id END) as buy_count
FROM batch_summaries bs
LEFT JOIN batch_analyses ba ON bs.id = ba.batch_id
LEFT JOIN analyses a ON ba.analysis_id = a.id
GROUP BY bs.id;

-- Grant permissions
GRANT ALL PRIVILEGES ON TABLE batch_summaries TO basirah_user;
GRANT ALL PRIVILEGES ON TABLE batch_analyses TO basirah_user;
GRANT ALL PRIVILEGES ON SEQUENCE batch_summaries_id_seq TO basirah_user;
