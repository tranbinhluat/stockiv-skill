import sqlite3
import os


def init_db():
    db_path = "/home/luattranb/Documents/projects/stock-agent/data/stockiv.db"

    # Ensure the directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create approvals table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS approvals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT NOT NULL,
        status TEXT DEFAULT 'PENDING',
        feedback TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()
    print(f"Successfully initialized 'approvals' table in {db_path}")


if __name__ == "__main__":
    init_db()
