import pandas as pd
from database import get_connection, create_table

INPUT_FILE = "data/processed/email_enriched_influencers.csv"


def load_influencers():
    df = pd.read_csv(INPUT_FILE)
    return df[df["filter_status"] == "PASS"].copy()


def populate_database():
    create_table()

    df = load_influencers()
    conn = get_connection()
    cursor = conn.cursor()

    added = 0
    skipped = 0

    for _, row in df.iterrows():
        try:
            cursor.execute("""
                INSERT INTO outreach (
                    influencer_name,
                    platform,
                    profile_url,
                    contact_email,
                    email_subject,
                    personalized_email,
                    personalized_dm,
                    status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row["name"],
                row["platform"],
                row["profile_url"],
                row["contact_email"],
                "",
                "",
                "",
                "Not Sent"
            ))

            added += 1

        except Exception:
            skipped += 1

    conn.commit()
    conn.close()

    print(f"Influencers added: {added}")
    print(f"Duplicates skipped: {skipped}")


def simulate_outreach(profile_url):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE outreach
        SET status = 'Simulated',
            sent_at = datetime('now')
        WHERE profile_url = ?
          AND status = 'Not Sent'
    """, (profile_url,))

    if cursor.rowcount == 1:
        print("Outreach simulated successfully.")
    else:
        print("Outreach not performed. Creator may already have been contacted.")

    conn.commit()
    conn.close()


def export_tracker():
    conn = get_connection()

    query = """
        SELECT
            influencer_name,
            platform,
            profile_url,
            contact_email,
            email_subject,
            personalized_email,
            personalized_dm,
            status,
            sent_at
        FROM outreach
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    output_file = "data/processed/outreach_tracker.csv"
    df.to_csv(output_file, index=False)

    print(f"\nOutreach tracker exported: {output_file}")
    print(f"Total influencers: {len(df)}")


if __name__ == "__main__":
    populate_database()
    export_tracker()
                   

    