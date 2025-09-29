from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from bs4 import BeautifulSoup


class JobScraper:
    def __init__(self):
        self.driver = webdriver.Chrome()

    def get_text_from_url(self, url):
        headers = {'User-Agent': 'Mozilla/5.0'}
        try:
            res = requests.get(url, headers=headers)
            soup = BeautifulSoup(res.text, 'html.parser')
            return soup.body.get_text().replace('\n', '')
        except Exception as e:
            return f"Failed to fetch and parse external URL: {e}"

    def scrape(self, url):
        try:
            self.driver.get(url)
            wait = WebDriverWait(self.driver, 10)

            # Check if the "View job" button is present
            if self.driver.find_elements(
                By.XPATH,
                '//a[.//span[text()="View job" and contains(@class, "button-styles__Text-sc-56105adf-5")]]'
            ):
                # Re-locate the element fresh to avoid stale reference
                view_job_link = self.driver.find_element(
                    By.XPATH,
                    '//a[.//span[text()="View job" and contains(@class, "button-styles__Text-sc-56105adf-5")]]'
                )
                job_url = view_job_link.get_attribute("href")
                print(f"Found external job URL: {job_url}")
                return self.get_text_from_url(job_url)
            else:
                print("No 'View job' button found — reading inline job description.")
                wait.until(EC.presence_of_element_located((
                    By.CSS_SELECTOR, "div.description-module__BlurWrapper-sc-6acfc168-1.fLJwRE"
                )))
                element = self.driver.find_element(
                    By.CSS_SELECTOR, "div.description-module__BlurWrapper-sc-6acfc168-1.fLJwRE"
                )
                return element.text

        except Exception as e:
            return f"Failed during scraping: {e}"

        finally:
            self.driver.quit()

# --- Example usage ---
if __name__ == "__main__":
    input_url = input("Enter the job post URL: ")
    scraper = JobScraper()
    result = scraper.scrape(input_url)
    print("\nExtracted Text:\n", result)
