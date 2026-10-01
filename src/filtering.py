import pandas as pd


INPUT_FILE = "data/raw/discovered_influencers.csv"
OUTPUT_FILE = "data/processed/filtered_influencers.csv"


MIN_SUBSCRIBERS = 5_000
MAX_SUBSCRIBERS = 100_000


def filter_influencers(df):
    """
    Filter creators based on the micro-influencer
    subscriber range.
    """

    results = []

    for _, creator in df.iterrows():

        subscribers = creator["subscriber_count"]

        if MIN_SUBSCRIBERS <= subscribers <= MAX_SUBSCRIBERS:

            status = "PASS"
            reason = (
                "Subscriber count is within "
                "the micro-influencer range"
            )

        elif subscribers < MIN_SUBSCRIBERS:

            status = "FAIL"
            reason = (
                "Subscriber count is below "
                "5,000"
            )

        else:

            status = "FAIL"
            reason = (
                "Subscriber count is above "
                "100,000"
            )

        creator["filter_status"] = status
        creator["filter_reason"] = reason

        results.append(creator)

    return pd.DataFrame(results)


def main():

    # Load discovered influencers
    df = pd.read_csv(INPUT_FILE)

    print(f"Total influencers discovered: {len(df)}")

    # Apply filtering
    filtered_df = filter_influencers(df)

    # Create processed directory if needed
    import os
    os.makedirs("data/processed", exist_ok=True)

    # Save results
    filtered_df.to_csv(OUTPUT_FILE, index=False)

    # Display summary
    passed = (filtered_df["filter_status"] == "PASS").sum()
    failed = (filtered_df["filter_status"] == "FAIL").sum()

    print(f"\nPassed: {passed}")
    print(f"Failed: {failed}")

    print("\nFiltering completed.")

    print(f"\nSaved results to:")
    print(OUTPUT_FILE)

    print("\nSample results:")
    print(
        filtered_df[
            [
                "name",
                "subscriber_count",
                "filter_status",
                "filter_reason"
            ]
        ].head(10).to_string(index=False)
    )


if __name__ == "__main__":
    main()