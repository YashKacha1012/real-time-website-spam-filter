import os
import json
import time
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from spam_rules import evaluate_submission
from db import init_db, insert_submission


def get_local_form_url():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "form.html")
    return "file:///" + file_path.replace("\\", "/")


def main():
    init_db()

    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(options=options)

    try:
        form_url = get_local_form_url()
        driver.get(form_url)

        print("\nForm opened in browser.")
        print("Form fill karo aur submit karo.\n")

        wait = WebDriverWait(driver, 999999)

        wait.until(
            EC.visibility_of_element_located((By.ID, "successBox"))
        )

        time.sleep(1)

        latest_data_json = driver.execute_script("""
            return localStorage.getItem("latest_submission");
        """)

        if not latest_data_json:
            print("No submitted data found.")
            return

        data = json.loads(latest_data_json)

        result = evaluate_submission(
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            email=data.get("email", ""),
            mobile=data.get("mobile", ""),
            address=data.get("address", ""),
            time_on_page=data.get("time_on_page", 5),
            honeypot_filled=data.get("honeypot_filled", False)
        )

        collected_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        insert_submission(
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            email=data.get("email", ""),
            mobile=data.get("mobile", ""),
            dob=data.get("dob", ""),
            gender=data.get("gender", ""),
            subject=data.get("subject", ""),
            hobbies=data.get("hobbies", ""),
            address=data.get("address", ""),
            state=data.get("state", ""),
            city=data.get("city", ""),
            score=result["score"],
            verdict=result["verdict"],
            rules_triggered=", ".join(result["rules_triggered"]),
            collected_at=collected_at
        )

        print("Submitted data fetched by Selenium.")
        print(f"Name    : {data.get('first_name', '')} {data.get('last_name', '')}")
        print(f"Email   : {data.get('email', '')}")
        print(f"Mobile  : {data.get('mobile', '')}")
        print(f"Address : {data.get('address', '')}")
        print(f"State   : {data.get('state', '')}")
        print(f"City    : {data.get('city', '')}")
        print(f"Score   : {result['score']}")
        print(f"Verdict : {result['verdict']}")
        print("Rules   : " + ", ".join(result["rules_triggered"]))

        time.sleep(3)

    finally:
        driver.quit()


if __name__ == "__main__":
    main()