import sqlite3
import os

DATABASE_FILE = "data/processed/outreach.db"


def get_connection():
    os.makedirs("data/processed", exist_ok=True)
    return sqlite3.connect(DATABASE_FILE)


def create_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS outreach (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            influencer_name TEXT NOT NULL,
            platform TEXT,
            profile_url TEXT UNIQUE,
            contact_email TEXT,
            email_subject TEXT,
            personalized_email TEXT,
            personalized_dm TEXT,
            status TEXT DEFAULT 'Not Sent',
            sent_at TEXT
        )
    """)

    # Add new columns if the database was created with an older schema
    existing_columns = {
        row[1]
        for row in cursor.execute("PRAGMA table_info(outreach)")
    }

    new_columns = {
        "email_subject": "TEXT",
        "personalized_email": "TEXT",
        "personalized_dm": "TEXT"
    }

    for column, data_type in new_columns.items():
        if column not in existing_columns:
            cursor.execute(
                f"ALTER TABLE outreach ADD COLUMN {column} {data_type}"
            )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_table()
    print("Outreach database created/updated successfully.")