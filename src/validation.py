def count_words(text):
    if not text:
        return 0

    return len(text.split())


def validate_email(email):
    word_count = count_words(email)

    return {
        "valid": 60 <= word_count <= 90,
        "word_count": word_count
    }


def validate_dm(dm):
    word_count = count_words(dm)

    return {
        "valid": 15 <= word_count <= 30,
        "word_count": word_count
    }


def validate_messages(email, dm):
    email_result = validate_email(email)
    dm_result = validate_dm(dm)

    return {
        "email": email_result,
        "dm": dm_result,
        "overall_valid": (
            email_result["valid"]
            and dm_result["valid"]
        )
    }


if __name__ == "__main__":
    test_email = """
    Hi there, we really appreciate your beauty and skincare content.
    We would love to explore a potential collaboration with you for
    an upcoming campaign. Your focus on skincare routines and beauty
    education aligns well with the type of content we are looking for.
    Please let us know if you would be interested in discussing the
    campaign and we can share more details.
    """

    test_dm = """
    Hi! We love your skincare content and would love to explore
    a potential beauty brand collaboration with you.
    """

    print(validate_messages(test_email, test_dm))