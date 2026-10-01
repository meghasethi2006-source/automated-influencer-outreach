import pandas as pd
import sqlite3
import os

INPUT_FILE = "data/processed/email_enriched_influencers.csv"
DATABASE_FILE = "data/processed/outreach.db"
OUTPUT_FILE = "data/processed/final_outreach_dataset.csv"


def create_final_dataset():

    # Load enriched influencer data
    df = pd.read_csv(INPUT_FILE)

    # Connect to outreach database
    conn = sqlite3.connect(DATABASE_FILE)

    outreach = pd.read_sql_query("""
        SELECT
            profile_url,
            email_subject,
            personalized_email,
            personalized_dm,
            status,
            sent_at
        FROM outreach
    """, conn)

    conn.close()

    # Merge influencer data with outreach tracking
    final_df = df.merge(
        outreach,
        on="profile_url",
        how="left"
    )

    # Save final dataset
    os.makedirs("data/processed", exist_ok=True)

    final_df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\n===================================")
    print("FINAL DATASET CREATED")
    print("===================================")
    print(f"Total creators: {len(final_df)}")
    print(f"Output: {OUTPUT_FILE}")
    print("\nColumns:")
    print(list(final_df.columns))


if __name__ == "__main__":
    create_final_dataset()