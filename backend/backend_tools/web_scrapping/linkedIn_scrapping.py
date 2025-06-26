from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
import undetected_chromedriver as uc
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import sys
import os

# Add the project root (one level up) to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from web_scrapping.driver import Driver

class linkedInDriver(Driver):

    def __init__(self,url="https://www.linkedin.com/feed/"):

        super().__init__()
        super().getURL(url)
        time.sleep(2)


    def insertJobTitle(self,title):
        f=0

        while f==0:
            try:
                self.driver.find_element(By.CSS_SELECTOR, 'input.search-global-typeahead__input')
                print("yes")
                f=1
            except Exception as e:
                print("Search input not found:", e)

        # Wait and then close
        element=self.driver.find_element(By.CSS_SELECTOR, 'input.search-global-typeahead__input')
        element.send_keys(title)
        element.send_keys(Keys.RETURN)

    def getJobsPage(self):

    
        jobButton= WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//a[contains(text(), "See all job results")]'))
        )
        jobButton.click()   

    def getJobtitles(self):

        # Wait for jobs to load
        WebDriverWait(self.driver, 15).until(
        EC.presence_of_element_located((By.TAG_NAME, "strong"))
        )

        # Scroll to load more results if needed
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

        # Extract all job titles from <strong> tags
        strong_tags = self.driver.find_elements(By.TAG_NAME, "strong")
        titles = [tag.text.strip() for tag in strong_tags if tag.text.strip()]

        return titles
    def getHTML(self):
        html_content = self.driver.page_source
        return str(html_content)
    def getCompanyURLs(self):

        time.sleep(2)
        # Find all <a> tags where class contains 'job-card-list__title--link'
        elements = self.driver.find_elements(By.XPATH, "//a[contains(@class, 'job-card-list__title--link')]")

        # Extract hrefs
        hrefs = [elem.get_attribute('href') for elem in elements]


        #NEED TO BE Extended to get urls of all pages

        return hrefs
    def getJobInfo(self,urls):
        jobsInfo={}
        for url in urls:
            self.getURL(url)

            # Locate the company name element
            company_element = self.driver.find_element(By.CLASS_NAME, "job-details-jobs-unified-top-card__company-name")

            # Extract company name text
            company_name = company_element.text.strip()

            #######################
            # Find all <p> tags inside <div id="job-details">
            p_tags = self.driver.find_elements(By.XPATH, "//div[@id='job-details']//p")

            # Extract text content
            #for p in p_tags:
            jobsInfo[company_name]=''.join(p.get_attribute("outerHTML") for p in p_tags)
            #for p in p_tags:
              #  print(p.get_attribute("outerHTML"))
            print(jobsInfo)
        return jobsInfo









"""driver=linkedInDriver()
driver.getURL("https://www.linkedin.com/feed/")
driver.insertJobTitle("python developer")
driver.getJobsPage()
time.sleep(2)
titles=driver.getJobtitles()
print(titles)
urls=driver.getCompanyURLs()
print(urls)
jobsInfo=driver.getJobInfo(urls)
print(jobsInfo)
time.sleep(60)
driver.quit()
"""