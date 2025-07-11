#!/usr/bin/env python3
"""
Script d'initialisation de la base de données Metalyzr
Crée toutes les tables et insère des données de test
"""

import asyncio
from database import db_client

async def main():
    print("Initializing database...")
    db_client.init_db()
    print("Database initialization complete.")
    db_client.close()

if __name__ == "__main__":
    asyncio.run(main()) 