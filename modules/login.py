import json
import time
import os
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

def linkedin_login():
    # Load credentials
    with open("config/credential.json", "r") as file:
        creds = json.load(file)

    # Set Chrome options
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--incognito")
    options.add_argument("--lang=en-US")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )

    # Launch browser
    driver = uc.Chrome(options=options)

    # Open LinkedIn login page
    driver.get("https://www.linkedin.com/login")
    print("[⏸️] Waiting... Inspect if needed.")
    time.sleep(3)

    try:
        # Fill login form
        email_input = driver.find_element(By.ID, "username")
        email_input.send_keys(creds["email"])

        password_input = driver.find_element(By.ID, "password")
        password_input.send_keys(creds["password"])
        password_input.send_keys(Keys.RETURN)

        time.sleep(5)

        if "feed" in driver.current_url:
            print("[✅] Login successful.")

            # STEP 3: Scrape Jobs
            search_job = "Data Scientist"
            search_location = "India"
            job_search_url = f"https://www.linkedin.com/jobs/search/?keywords={search_job}&location={search_location}"
            driver.get(job_search_url)
            time.sleep(4)

            total_scrolls = 5
            for _ in range(total_scrolls):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)

            jobs = driver.find_elements(By.CLASS_NAME, "base-card")
            job_data = []

            for job in jobs:
                try:
                    title = job.find_element(By.CLASS_NAME, "base-search-card__title").text.strip()
                    company = job.find_element(By.CLASS_NAME, "base-search-card__subtitle").text.strip()
                    location = job.find_element(By.CLASS_NAME, "job-search-card__location").text.strip()
                    link = job.find_element(By.TAG_NAME, "a").get_attribute("href")

                    job_data.append({
                        "title": title,
                        "company": company,
                        "location": location,
                        "link": link
                    })
                except Exception as e:
                    print("[⚠️] Skipped one job due to error:", e)

            print(f"[📦] Collected {len(job_data)} jobs.")
            for job in job_data[:5]:
                print(job)

            # Save to output file
            os.makedirs("output", exist_ok=True)
            with open("output/jobs_data.json", "w", encoding="utf-8") as f:
                json.dump(job_data, f, indent=2, ensure_ascii=False)

            print("[💾] Job data saved to 'output/jobs_data.json'")

        else:
            print("[⚠️] Login may have failed. Check manually.")

    except Exception as e:
        print("[❌] Error during login or scraping:", e)

    # Keep the browser open
    input("\n[👁️] Press ENTER to close the browser manually after inspecting...")
    driver.quit()

if __name__ == "__main__":
    linkedin_login()
