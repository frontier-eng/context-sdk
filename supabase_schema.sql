-- Context API Database Schema for Supabase

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- users table
CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email TEXT UNIQUE NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

-- api_keys table
CREATE TABLE IF NOT EXISTS api_keys (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  key_hash TEXT NOT NULL,
  key_prefix TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Create index on key_hash for faster lookups
CREATE INDEX IF NOT EXISTS idx_api_keys_key_hash ON api_keys(key_hash);
CREATE INDEX IF NOT EXISTS idx_api_keys_user_id ON api_keys(user_id);

-- trace_metadata table
CREATE TABLE IF NOT EXISTS trace_metadata (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  trace_id TEXT NOT NULL,
  provider TEXT,
  model TEXT,
  success BOOLEAN,
  tokens_used INTEGER,
  latency_ms INTEGER,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for trace_metadata
CREATE INDEX IF NOT EXISTS idx_trace_metadata_user_id ON trace_metadata(user_id);
CREATE INDEX IF NOT EXISTS idx_trace_metadata_trace_id ON trace_metadata(trace_id);
CREATE INDEX IF NOT EXISTS idx_trace_metadata_created_at ON trace_metadata(created_at);

