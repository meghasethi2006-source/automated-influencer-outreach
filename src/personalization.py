import os
import json
import pandas as pd
import sqlite3
from dotenv import load_dotenv
from google import genai
from validation import validate_messages

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

INPUT_FILE = "data/processed/email_enriched_influencers.csv"
OUTPUT_FILE = "data/processed/personalized_outreach.csv"
DATABASE_FILE = "data/processed/outreach.db"

MODEL = "gemini-3.8-flash"

client = genai.Client(
    api_key=API_KEY,
    http_options={"timeout": 120000}
)


def generate_personalized_message(creator):
    prompt = f"""
You are an influencer outreach specialist.

Create a personalized outreach message for this beauty/skincare
micro-influencer.

CREATOR INFORMATION:
Name: {creator["name"]}
Platform: {creator["platform"]}
Subscribers: {creator["subscriber_count"]}
Estimated engagement rate: {creator["engagement_rate"]}%
Content themes: {creator["content_themes"]}
Recent video titles: {creator["recent_video_titles"]}
Channel description: {creator["description"]}

IMPORTANT RULES:
1. Do not invent facts about the creator.
2. Use recent video titles only as evidence of the creator's content topics.
3. Never claim that you personally watched, followed, liked, or discovered their content.
4. Do not fabricate personal familiarity with the creator.
5. Make the message genuinely personalized.
6. Mention their beauty/skincare content naturally.
7. If referencing a recent topic, say "Your recent content on..." rather than "I watched..." or "I've been following..."
8. The email, including greeting and sign-off, must be between 60 and 90 words.
9. The Instagram DM must be between 15 and 30 words.
10. Keep the tone friendly, professional and natural.
11. Do not mention subscriber count or engagement rate directly.
12. Present the collaboration as a potential brand collaboration.
13. Before returning the JSON, count the words and revise the messages if necessary.
14. Return ONLY valid JSON.

Return exactly:

{{
    "email_subject": "...",
    "email": "...",
    "instagram_dm": "..."
}}
"""

    import time

    response = None

    for attempt in range(3):
        try:
            response = client.interactions.create(
                model=MODEL,
                input=prompt
            )
            break

        except Exception as e:
            print(f"Gemini attempt {attempt + 1} failed: {e}")

            if attempt < 2:
                wait_time = 5 * (attempt + 1)
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                raise

    text = response.output_text.strip()

    if text.startswith("```"):
        text = text.replace("```json", "").replace("```", "").strip()
    messages = json.loads(text)

    validation = validate_messages(
        messages["email"],
        messages["instagram_dm"]
    )

    print("\nMessage validation:")
    print(validation)

    if not validation["overall_valid"]:
        print("WARNING: Generated messages do not meet the required word limits.")

    return messages
  
def save_to_database(creator, messages):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE outreach
        SET email_subject = ?,
            personalized_email = ?,
            personalized_dm = ?
        WHERE profile_url = ?
    """, (
        messages["email_subject"],
        messages["email"],
        messages["instagram_dm"],
        creator["profile_url"]
    ))

    conn.commit()
    conn.close()

    if cursor.rowcount == 1:
        print("Personalized messages saved to database.")
    else:
        print("Warning: creator was not found in database.")
def main():

    df = pd.read_csv(INPUT_FILE)

    print(f"Total creators available: {len(df)}")

    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    processed = 0

    for _, row in df.iterrows():

        creator = row.to_dict()

        print(f"\nProcessing: {creator['name']}")

        cursor.execute("""
            UPDATE outreach
            SET status = 'AI Generation Pending'
            WHERE profile_url = ?
        """, (creator["profile_url"],))

        processed += 1

    conn.commit()
    conn.close()

    print("\n================================")
    print(f"Creators processed: {processed}")
    print("AI generation status: Pending")
    print("================================")


if __name__ == "__main__":
    main()

    