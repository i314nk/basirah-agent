-- basīrah Analysis Storage Schema
-- PostgreSQL 16+

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- For fuzzy text search

-- Companies table (master list)
CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL UNIQUE,
    company_name VARCHAR(255) NOT NULL,
    sector VARCHAR(100),
    industry VARCHAR(100),
    first_analyzed TIMESTAMP NOT NULL DEFAULT NOW(),
    last_analyzed TIMESTAMP NOT NULL DEFAULT NOW(),
    total_analyses INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Analyses table (main storage)
CREATE TABLE analyses (
    id SERIAL PRIMARY KEY,
    analysis_id VARCHAR(255) NOT NULL UNIQUE, -- e.g., "AAPL_2025-11-04_buy_10y"
    company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    ticker VARCHAR(10) NOT NULL,
    company_name VARCHAR(255) NOT NULL,

    -- Analysis metadata
    analysis_type VARCHAR(50) NOT NULL, -- 'quick', 'deep_dive', 'sharia'
    analysis_date DATE NOT NULL,
    analysis_datetime TIMESTAMP NOT NULL DEFAULT NOW(),
    years_analyzed INTEGER, -- For deep dive (1-10)

    -- Results
    decision VARCHAR(50) NOT NULL, -- 'BUY', 'WATCH', 'AVOID', 'INVESTIGATE', 'PASS', etc.
    conviction VARCHAR(50), -- 'HIGH', 'MODERATE', 'LOW'

    -- Financial metrics (for deep dive)
    intrinsic_value DECIMAL(12, 2),
    current_price DECIMAL(12, 2),
    margin_of_safety DECIMAL(5, 2), -- Percentage
    roic DECIMAL(5, 2), -- Percentage

    -- Sharia metrics
    sharia_status VARCHAR(50), -- 'COMPLIANT', 'DOUBTFUL', 'NON-COMPLIANT'
    purification_rate DECIMAL(5, 2), -- Percentage

    -- Cost and performance
    cost DECIMAL(6, 2) NOT NULL,
    duration_seconds INTEGER NOT NULL,
    token_usage_input INTEGER,
    token_usage_output INTEGER,

    -- Content
    thesis_preview TEXT, -- First 500 chars for quick display
    thesis_full TEXT, -- Full thesis content

    -- File storage
    file_path VARCHAR(500) NOT NULL, -- Relative path to JSON file

    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Constraints
    CHECK (analysis_type IN ('quick', 'deep_dive', 'sharia')),
    CHECK (margin_of_safety IS NULL OR (margin_of_safety >= -100 AND margin_of_safety <= 100)),
    CHECK (roic IS NULL OR roic >= 0),
    CHECK (purification_rate IS NULL OR (purification_rate >= 0 AND purification_rate <= 100))
);

-- Tags table (for custom categorization)
CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    color VARCHAR(7), -- Hex color code
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Analysis tags (many-to-many)
CREATE TABLE analysis_tags (
    analysis_id INTEGER NOT NULL REFERENCES analyses(id) ON DELETE CASCADE,
    tag_id INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    PRIMARY KEY (analysis_id, tag_id)
);

-- Saved searches
CREATE TABLE saved_searches (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    search_criteria JSONB NOT NULL, -- Store filter criteria as JSON
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    last_used TIMESTAMP
);

-- Analysis comparison history
CREATE TABLE comparisons (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    analysis_ids INTEGER[] NOT NULL, -- Array of analysis IDs
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Indexes for fast queries
CREATE INDEX idx_analyses_ticker ON analyses(ticker);
CREATE INDEX idx_analyses_date ON analyses(analysis_date DESC);
CREATE INDEX idx_analyses_type ON analyses(analysis_type);
CREATE INDEX idx_analyses_decision ON analyses(decision);
CREATE INDEX idx_analyses_conviction ON analyses(conviction);
CREATE INDEX idx_analyses_sharia ON analyses(sharia_status);
CREATE INDEX idx_analyses_company ON analyses(company_id);
CREATE INDEX idx_analyses_composite ON analyses(analysis_type, decision, analysis_date DESC);

-- Full-text search indexes
CREATE INDEX idx_companies_name_trgm ON companies USING gin(company_name gin_trgm_ops);
CREATE INDEX idx_analyses_thesis_trgm ON analyses USING gin(thesis_full gin_trgm_ops);

-- Function to update company statistics
CREATE OR REPLACE FUNCTION update_company_stats()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE companies
        SET
            last_analyzed = NEW.analysis_datetime,
            total_analyses = total_analyses + 1,
            updated_at = NOW()
        WHERE id = NEW.company_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update company stats
CREATE TRIGGER trigger_update_company_stats
AFTER INSERT ON analyses
FOR EACH ROW
EXECUTE FUNCTION update_company_stats();

-- Function to update timestamps
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for updated_at
CREATE TRIGGER trigger_companies_updated_at
BEFORE UPDATE ON companies
FOR EACH ROW
EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trigger_analyses_updated_at
BEFORE UPDATE ON analyses
FOR EACH ROW
EXECUTE FUNCTION update_updated_at();

-- Insert default tags
INSERT INTO tags (name, description, color) VALUES
    ('Portfolio', 'Companies in my portfolio', '#10B981'),
    ('Watchlist', 'Companies to monitor', '#F59E0B'),
    ('High Priority', 'Urgent analysis needed', '#EF4444'),
    ('Halal', 'Sharia compliant companies', '#8B5CF6'),
    ('Re-screen', 'Needs updated analysis', '#3B82F6'),
    ('Archived', 'Old analysis, no longer relevant', '#6B7280');

-- Create view for easy querying
CREATE VIEW v_analysis_summary AS
SELECT
    a.id,
    a.analysis_id,
    a.ticker,
    a.company_name,
    c.sector,
    c.industry,
    a.analysis_type,
    a.analysis_date,
    a.years_analyzed,
    a.decision,
    a.conviction,
    a.intrinsic_value,
    a.current_price,
    a.margin_of_safety,
    a.roic,
    a.sharia_status,
    a.purification_rate,
    a.cost,
    a.duration_seconds,
    a.thesis_preview,
    a.file_path,
    a.created_at,
    ARRAY_AGG(t.name) FILTER (WHERE t.name IS NOT NULL) as tags
FROM analyses a
LEFT JOIN companies c ON a.company_id = c.id
LEFT JOIN analysis_tags at ON a.id = at.analysis_id
LEFT JOIN tags t ON at.tag_id = t.id
GROUP BY a.id, c.sector, c.industry;

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO basirah_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO basirah_user;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO basirah_user;
