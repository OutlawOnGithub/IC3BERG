-- Create schema if not exists
CREATE SCHEMA IF NOT EXISTS iceberg;

-- Create server table
CREATE TABLE IF NOT EXISTS iceberg.server (
    guild_id BIGINT PRIMARY KEY,
    enabled BOOLEAN,
    rss_channel BIGINT
);

-- Create rss table
CREATE TABLE IF NOT EXISTS iceberg.rss (
    url TEXT PRIMARY KEY,
    last_fetched TEXT,
    description TEXT,
    guild_id BIGINT
);

-- Create schema if not exists
CREATE SCHEMA IF NOT EXISTS iceburk;

-- Create server table
CREATE TABLE IF NOT EXISTS iceburk.server (
    guild_id BIGINT PRIMARY KEY,
    enabled BOOLEAN,
    rss_channel BIGINT
);

-- Create rss table
CREATE TABLE IF NOT EXISTS iceburk.rss (
    url TEXT PRIMARY KEY,
    last_fetched TEXT,
    description TEXT,
    guild_id BIGINT
);