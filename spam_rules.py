import re


FAKE_DOMAINS = ["mailinator", "trashmail", "guerrillamail", "tempmail"]
SPAM_KEYWORDS = ["casino", "viagra", "free money", "click here", "winner"]


def is_all_caps(text):
    letters = [ch for ch in text if ch.isalpha()]
    if not letters:
        return False
    upper_count = sum(1 for ch in letters if ch.isupper())
    return (upper_count / len(letters)) > 0.6


def has_character_repetition(text):
    return bool(re.search(r"(.)\1{5,}", text))


def has_url(text):
    text = text.lower()
    return "http://" in text or "https://" in text or "www." in text


def has_spam_keywords(text):
    text = text.lower()
    return any(keyword in text for keyword in SPAM_KEYWORDS)


def is_fake_email(email):
    email = email.lower()
    return any(domain in email for domain in FAKE_DOMAINS)


def is_invalid_mobile(mobile):
    return not (mobile.isdigit() and len(mobile) == 10)


def evaluate_submission(first_name, last_name, email, mobile, address,
                        time_on_page=5, honeypot_filled=False):
    score = 0.0
    rules_triggered = []

    full_name = f"{first_name} {last_name}".strip()

    if has_spam_keywords(address):
        score += 3.0
        rules_triggered.append("Keyword match (+3.0)")

    if has_url(address):
        score += 2.5
        rules_triggered.append("URL in address (+2.5)")

    if is_all_caps(full_name):
        score += 1.5
        rules_triggered.append("ALL CAPS name (+1.5)")

    if has_character_repetition(full_name) or has_character_repetition(address):
        score += 1.0
        rules_triggered.append("Character repetition (+1.0)")

    if len(first_name.strip()) < 2 or len(last_name.strip()) < 2:
        score += 2.0   # pehle 0.5 tha
        rules_triggered.append("Too short name (+2.0)")

    if len(address) > 500:
        score += 1.0
        rules_triggered.append("Very long address (+1.0)")

    if time_on_page < 2:
        score += 3.0
        rules_triggered.append("Fast submission (+3.0)")

    if is_fake_email(email):
        score += 2.5
        rules_triggered.append("Fake email domain (+2.5)")

    if is_invalid_mobile(mobile):
        score += 2.0
        rules_triggered.append("Invalid mobile (+2.0)")

    if honeypot_filled:
        score += 10.0
        rules_triggered.append("Honeypot triggered (+10.0)")

    if score < 1:
        verdict = "ham"
    elif score < 3:
        verdict = "suspect"
    else:
        verdict = "spam"

    return {
        "score": score,
        "verdict": verdict,
        "rules_triggered": rules_triggered
    }