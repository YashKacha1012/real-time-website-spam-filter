import random
from datetime import datetime
from db import insert_submission
from spam_rules import evaluate_submission

names = ["Rahul", "Amit", "Neha", "Pooja", "Karan"]
states = ["Gujarat", "Maharashtra", "Delhi"]
cities = ["Ahmedabad", "Surat", "Mumbai"]

spam_keywords = ["free money", "casino", "click here"]

def random_email(name):
    domains = ["gmail.com", "yahoo.com", "mailinator.com"]
    return f"{name.lower()}@{random.choice(domains)}"

def random_mobile():
    return "".join([str(random.randint(0,9)) for _ in range(10)])

def generate():
    for _ in range(200):   # 🔥 rows change kar sakta hai
        name = random.choice(names)

        address = random.choice([
            "Normal address",
            "Visit www.spam.com",
            random.choice(spam_keywords)
        ])

        email = random_email(name)

        score_data = evaluate_submission(
            name, "Test", email, random_mobile(), address,
            time_on_page=random.randint(1,5),
            honeypot_filled=random.choice([False, True, False])
        )

        insert_submission(
            name,
            "Test",
            email,
            random_mobile(),
            "2000-01-01",
            "Male",
            "Maths",
            "Sports",
            address,
            random.choice(states),
            random.choice(cities),
            score_data["score"],
            score_data["verdict"],
            ", ".join(score_data["rules_triggered"]),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

    print("🔥 200 rows inserted")

generate()