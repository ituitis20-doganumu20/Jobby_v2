from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
import undetected_chromedriver as uc
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

class Driver:

    def __init__(self, options=None):
        if options:
            self.driver = webdriver.Chrome(options=options)
        else:
            import undetected_chromedriver as uc
            self.driver = uc.Chrome()


    def getURL(self,url):
        self.driver.get(url)
        time.sleep(2)
    def quit(self):
        self.driver.quit()
        
    def get_job_body(self):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "description-module__BlurWrapper-sc-6acfc168-1"))
            )
            try:
                show_more = self.driver.find_element(By.CLASS_NAME, "show-more-styles__ToggleButton-sc-f5ed2ced-2")
                show_more.click()
                #time.sleep(1)
            except:
                pass
            body_container = self.driver.find_element(By.CLASS_NAME, "html-description__DescriptionContainer-sc-f41a8879-0")
            return body_container.text
        except Exception as e:
            return f"Failed to extract job body: {e}"

