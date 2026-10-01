from src.discovery import discover_influencers
from src.filtering import main as run_filtering
from src.enrichment import main as run_enrichment
from src.email_enrichment import main as run_email_enrichment
from src.outreach import populate_database


def main():
    print("\n=== AUTOMATED MICRO-INFLUENCER OUTREACH SYSTEM ===\n")

    print("1. Discovering influencers...")
    discover_influencers()

    print("\n2. Filtering influencers...")
    run_filtering()

    print("\n3. Enriching influencer data...")
    run_enrichment()

    print("\n4. Finding public contact emails...")
    run_email_enrichment()

    print("\n5. Updating outreach database...")
    populate_database()

    print("\n=== PIPELINE COMPLETED ===")


if __name__ == "__main__":
    main()