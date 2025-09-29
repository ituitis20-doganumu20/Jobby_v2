from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class JobScraper:
    def __init__(self):
        self.driver = webdriver.Chrome()

    def get_blur_wrapper_text(self):
        try:
            # Wait until the specific div is present in the DOM
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div.description-module__BlurWrapper-sc-6acfc168-1.fLJwRE")
                )
            )

            # Locate and return the text
            element = self.driver.find_element(
                By.CSS_SELECTOR, "div.description-module__BlurWrapper-sc-6acfc168-1.fLJwRE"
            )
            return element.text

        except Exception as e:
            return f"Failed to extract text: {e}"

    def scrape(self, url):
        try:
            self.driver.get(url)
            return self.get_blur_wrapper_text()
        finally:
            self.driver.quit()


# Example usage
if __name__ == "__main__":
    input_url = input("Enter the job post URL: ")
    scraper = JobScraper()
    content = scraper.scrape(input_url)
    print("Extracted Text:\n", content)
