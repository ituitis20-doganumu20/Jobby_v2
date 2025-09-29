from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
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
            return f"Failed to fetch and parse URL: {e}"

    def scrape(self, url):
        try:
            self.driver.get(url)
            wait = WebDriverWait(self.driver, 10)

            try:
                # Wait until the link exists
                wait.until(EC.presence_of_element_located((
                    By.XPATH,
                    '//a[.//span[text()="View job" and contains(@class, "button-styles__Text-sc-56105adf-5")]]'
                )))

                # Locate it again freshly (avoid stale reference)
                view_job_link = self.driver.find_element(
                    By.XPATH,
                    '//a[.//span[text()="View job" and contains(@class, "button-styles__Text-sc-56105adf-5")]]'
                )

                job_url = view_job_link.get_attribute("href")
                print(f"Found job URL: {job_url}")
                return self.get_text_from_url(job_url)


            except (TimeoutException, NoSuchElementException):
                print("No View Job button found, falling back to inline div.")

            # Fallback to scraping in-page div
            wait.until(EC.presence_of_element_located((
                By.CSS_SELECTOR,
                "div.description-module__BlurWrapper-sc-6acfc168-1.fLJwRE"
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
