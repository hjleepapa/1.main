-- Call Center Database Schema
-- PostgreSQL SQL Script
-- 
-- This script creates the necessary tables for the call center application.
-- Tables include: cc_agents, cc_calls, cc_agent_activities
--
-- Usage:
--   psql -U username -d database_name -f generate_tables.sql

-- Drop existing tables (in reverse order of dependencies)
DROP TABLE IF EXISTS cc_agent_activities CASCADE;
DROP TABLE IF EXISTS cc_calls CASCADE;
DROP TABLE IF EXISTS cc_agents CASCADE;

-- Create cc_agents table
CREATE TABLE cc_agents (
    id SERIAL PRIMARY KEY,
    agent_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    sip_extension VARCHAR(50) UNIQUE,
    sip_username VARCHAR(100),
    sip_password VARCHAR(100),
    sip_domain VARCHAR(100),
    state VARCHAR(20) DEFAULT 'logged_out',
    state_changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create cc_calls table
CREATE TABLE cc_calls (
    id SERIAL PRIMARY KEY,
    call_id VARCHAR(100) UNIQUE NOT NULL,
    agent_id INTEGER REFERENCES cc_agents(id) ON DELETE SET NULL,
    caller_number VARCHAR(50),
    caller_name VARCHAR(100),
    called_number VARCHAR(50),
    customer_id VARCHAR(100),
    customer_data JSONB,
    state VARCHAR(20) DEFAULT 'idle',
    direction VARCHAR(10),
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    answered_at TIMESTAMP,
    ended_at TIMESTAMP,
    duration INTEGER,
    disposition VARCHAR(50),
    notes TEXT
);

-- Create cc_agent_activities table
CREATE TABLE cc_agent_activities (
    id SERIAL PRIMARY KEY,
    agent_id INTEGER REFERENCES cc_agents(id) ON DELETE CASCADE,
    activity_type VARCHAR(50),
    from_state VARCHAR(20),
    to_state VARCHAR(20),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- Create indexes for better performance

-- Indexes on cc_agents
CREATE INDEX idx_cc_agents_agent_id ON cc_agents(agent_id);
CREATE INDEX idx_cc_agents_state ON cc_agents(state);
CREATE INDEX idx_cc_agents_sip_extension ON cc_agents(sip_extension);

-- Indexes on cc_calls
CREATE INDEX idx_cc_calls_call_id ON cc_calls(call_id);
CREATE INDEX idx_cc_calls_agent_id ON cc_calls(agent_id);
CREATE INDEX idx_cc_calls_state ON cc_calls(state);
CREATE INDEX idx_cc_calls_customer_id ON cc_calls(customer_id);
CREATE INDEX idx_cc_calls_started_at ON cc_calls(started_at);
CREATE INDEX idx_cc_calls_direction ON cc_calls(direction);

-- Indexes on cc_agent_activities
CREATE INDEX idx_cc_agent_activities_agent_id ON cc_agent_activities(agent_id);
CREATE INDEX idx_cc_agent_activities_timestamp ON cc_agent_activities(timestamp);
CREATE INDEX idx_cc_agent_activities_activity_type ON cc_agent_activities(activity_type);

-- Add comments to tables
COMMENT ON TABLE cc_agents IS 'Call center agents with SIP configuration';
COMMENT ON TABLE cc_calls IS 'Call records and history';
COMMENT ON TABLE cc_agent_activities IS 'Agent activity log for tracking state changes and events';

-- Add comments to important columns
COMMENT ON COLUMN cc_agents.state IS 'Agent state: logged_out, logged_in, ready, not_ready, on_call, wrap_up';
COMMENT ON COLUMN cc_agents.sip_extension IS 'SIP extension number for agent';
COMMENT ON COLUMN cc_calls.state IS 'Call state: idle, ringing, connected, held, transferring, ended';
COMMENT ON COLUMN cc_calls.direction IS 'Call direction: inbound or outbound';
COMMENT ON COLUMN cc_calls.customer_data IS 'JSON data for customer information popup';
COMMENT ON COLUMN cc_agent_activities.activity_type IS 'Activity type: login, logout, state_change, call_start, call_end';

-- Optional: Insert a test agent for development
-- Uncomment the following lines if you want to create a test agent

-- INSERT INTO cc_agents (
--     agent_id,
--     name,
--     email,
--     sip_extension,
--     sip_username,
--     sip_password,
--     sip_domain,
--     state
-- ) VALUES (
--     'agent001',
--     'Test Agent',
--     'test@example.com',
--     '1001',
--     'agent001',
--     'test123',
--     'sip.example.com',
--     'logged_out'
-- );

-- Grant permissions (adjust as needed for your database user)
-- GRANT ALL PRIVILEGES ON cc_agents TO your_db_user;
-- GRANT ALL PRIVILEGES ON cc_calls TO your_db_user;
-- GRANT ALL PRIVILEGES ON cc_agent_activities TO your_db_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO your_db_user;

-- Display success message
DO $$
BEGIN
    RAISE NOTICE 'Call Center database tables created successfully!';
    RAISE NOTICE 'Tables created:';
    RAISE NOTICE '  - cc_agents';
    RAISE NOTICE '  - cc_calls';
    RAISE NOTICE '  - cc_agent_activities';
END $$;

