from backend.backend_tools.web_scrapping.driver import Driver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class xingDriver(Driver):
    def __init__(self):
        options = Options()
        #options.add_argument(r"--user-data-dir=C:\Users\umutc\chrome_selenium_profile")
        #options.add_argument("--profile-directory=Default")
        #options.add_argument("--no-sandbox")
        #options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--log-level=3")  # only fatal errors
        super().__init__(options=options)
        
    def getJobContents(self, url):
        self.getURL(url)
        wait = WebDriverWait(self.driver, 10)
        """
        # Attempt to click "Accept all" if the button is present
        try:
            accept_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-testid="uc-accept-all-button"]'))
            )
            accept_button.click()
        except:
            print("No 'Accept all' button found — continuing.")
            
        """   
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.card-styles__CardLink-sc-ecfcdbce-2.eVLJBS")))

        job_links = self.driver.find_elements(By.CSS_SELECTOR, "a.card-styles__CardLink-sc-ecfcdbce-2.eVLJBS")
        main_window = self.driver.current_window_handle

        # Open all job detail tabs
        for link in job_links:
            href = link.get_attribute("href")
            self.driver.execute_script(f"window.open('{href}', '_blank');")
            #break  # Remove this break to open all job links

        # Collect job contents
        results = []
        job_tabs = self.driver.window_handles[1:]  # exclude main window

        for tab in job_tabs:
            self.driver.switch_to.window(tab)
            body = self.get_job_body()
            results.append({"url": self.driver.current_url, "content": body})

        # Close all job tabs
        for tab in job_tabs:
            self.driver.switch_to.window(tab)
            self.driver.close()

        # Switch back to main window safely
        if main_window in self.driver.window_handles:
            self.driver.switch_to.window(main_window)
            self.driver.close()
        else:
            print("Warning: Main window not found.")

        print(results) 
        return results
