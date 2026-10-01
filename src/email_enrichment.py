import re
import pandas as pd

INPUT_FILE = "data/processed/enriched_influencers.csv"
OUTPUT_FILE = "data/processed/email_enriched_influencers.csv"


def extract_email(text):
    if pd.isna(text):
        return None

    text = str(text)

    pattern = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"

    matches = re.findall(pattern, text)

    if matches:
        return matches[0]

    return None


def main():

    df = pd.read_csv(INPUT_FILE)

    print(f"Total creators: {len(df)}")

    emails_found = 0

    for index, row in df.iterrows():

        description = row.get("description", "")

        email = extract_email(description)

        if email:
            df.at[index, "contact_email"] = email
            emails_found += 1

    df.to_csv(OUTPUT_FILE, index=False)

    print(f"\nPublic emails found: {emails_found}")
    print(f"Emails still not found: {len(df) - emails_found}")

    print("\nSample email results:")

    print(
        df[
            [
                "name",
                "contact_email",
                "profile_url"
            ]
        ].head(15).to_string(index=False)
    )

    print("\nSaved to:")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()