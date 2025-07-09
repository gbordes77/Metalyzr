import os
import logging
from psycopg2 import pool
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# This file will contain the database client and schema definitions.
# For now, it contains the DDL for the PostgreSQL database.

DB_SCHEMA = """
CREATE TABLE IF NOT EXISTS sources (
    source_id SERIAL PRIMARY KEY,
    source_name VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS formats (
    format_id SERIAL PRIMARY KEY,
    format_name VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS archetypes (
    archetype_id SERIAL PRIMARY KEY,
    archetype_name VARCHAR(255) UNIQUE NOT NULL,
    defined_by_user BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS tournaments (
    tournament_id SERIAL PRIMARY KEY,
    tournament_uuid VARCHAR(255) UNIQUE NOT NULL, -- From the scraper
    tournament_name TEXT NOT NULL,
    tournament_date TIMESTAM bờp NOT NULL,
    source_id INT REFERENCES sources(source_id),
    format_id INT REFERENCES formats(format_id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS decks (
    deck_id SERIAL PRIMARY KEY,
    tournament_id INT REFERENCES tournaments(tournament_id),
    player_name VARCHAR(255),
    archetype_id INT REFERENCES archetypes(archetype_id),
    -- Data from the classification engine
    classified_archetype_name VARCHAR(255),
    base_archetype_name VARCHAR(255),
    archetype_confidence FLOAT,
    -- Store original decklist for reference
    decklist_json JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS cards (
    card_id SERIAL PRIMARY KEY,
    card_name VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS deck_cards (
    deck_id INT REFERENCES decks(deck_id),
    card_id INT REFERENCES cards(card_id),
    quantity INT NOT NULL,
    is_sideboard BOOLEAN NOT NULL,
    PRIMARY KEY (deck_id, card_id, is_sideboard)
);

CREATE TABLE IF NOT EXISTS matches (
    match_id SERIAL PRIMARY KEY,
    tournament_id INT REFERENCES tournaments(tournament_id),
    round_number INT,
    deck1_id INT REFERENCES decks(deck_id),
    deck2_id INT REFERENCES decks(deck_id),
    winner_deck_id INT REFERENCES decks(deck_id),
    is_draw BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_tournaments_date ON tournaments(tournament_date);
CREATE INDEX IF NOT EXISTS idx_decks_archetype ON decks(archetype_id);
CREATE INDEX IF NOT EXISTS idx_deck_cards_deck ON deck_cards(deck_id);
"""

class DatabaseClient:
    """A PostgreSQL database client with connection pooling."""
    
    def __init__(self, db_url=None):
        if db_url is None:
            db_url = os.getenv("DATABASE_URL")
            if not db_url:
                raise ValueError("Database URL not found. Set the DATABASE_URL environment variable.")
        
        self.db_url = db_url
        # minconn=1, maxconn=10
        self.pool = pool.SimpleConnectionPool(1, 10, dsn=self.db_url)
        logger.info("Database connection pool created.")

    @contextmanager
    def get_connection(self):
        """Context manager to get a connection from the pool."""
        conn = self.pool.getconn()
        try:
            yield conn
        finally:
            self.pool.putconn(conn)

    def execute_query(self, query, params=None, fetch=None):
        """
        Execute a SQL query.
        
        :param query: The SQL query string.
        :param params: A tuple or dictionary of parameters to pass to the query.
        :param fetch: Type of fetch ('one', 'all').
        :return: Result of the query if fetch is specified.
        """
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                conn.commit()
                
                if fetch == 'one':
                    return cursor.fetchone()
                if fetch == 'all':
                    return cursor.fetchall()
    
    def execute_many(self, query, params_list):
        """Execute a query for a list of parameters."""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.executemany(query, params_list)
                conn.commit()

    def init_db(self):
        """Initialize the database by creating tables from the schema."""
        logger.info("Initializing database schema...")
        try:
            self.execute_query(DB_SCHEMA)
            logger.info("Database schema initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize database schema: {e}")
            raise

    def close(self):
        """Close all connections in the pool."""
        if self.pool:
            self.pool.closeall()
            logger.info("Database connection pool closed.")

# A single instance to be used across the application
# This will be properly managed by the application lifecycle later
db_client = DatabaseClient() 