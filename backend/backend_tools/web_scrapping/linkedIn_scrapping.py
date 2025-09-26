from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
import undetected_chromedriver as uc
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import sys
import os
import re
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# Add the project root (one level up) to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from web_scrapping.driver import Driver

class linkedInDriver(Driver):

    def __init__(self,url="https://www.linkedin.com/feed/"):
        options = Options()
        options.add_argument(r"--user-data-dir=C:\Users\umutc\chrome_selenium_profile")
        options.add_argument("--profile-directory=Default")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--log-level=3")  # only fatal errors
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
    def getCompanyURLs(self,numberOfJobs):

        urls=[]

        flag=False
        
        while True:

        

            try:
               

                time.sleep(4)
                # Find all <a> tags where class contains 'job-card-list__title--link'
                elements = self.driver.find_elements(By.XPATH, "//a[contains(@class, 'job-card-list__title--link')]")

                # Extract hrefs
                #hrefs = [elem.get_attribute('href') for elem in elements]
                for elem in elements:
                    print(len(urls))
                    if len(urls)==numberOfJobs:
                        flag=True
                        break
                    urls.append(elem.get_attribute('href'))
                if flag==True:
                    break
                # Wait for the "next" button to appear
                next_button = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "button[aria-label='View next page']")
                )
            )

                # Check if the button is clickable
                if next_button.is_enabled():
                    next_button.click()
                    print("Clicked next page button")
                else:
                    print("Next button not enabled. Ending loop.")
                    break

            except (NoSuchElementException, TimeoutException):
                print("No next button found. Ending loop.")
                break

        return urls
    def removeTags(self,txt):
        stk=[]


        ans=[]

        for i in txt:
    
            if i=="<":
        
                stk.append(i)
            elif i==">":
                stk.pop()
        
            else:
                if len(stk)==0:
                    ans.append(i)
        return re.sub(r'\s+', ' ', ''.join(ans).replace("\n", ""))
        
    def getJobInfo(self,urls):
       results = []
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
            txt=''.join(p.get_attribute("outerHTML") for p in p_tags)
           
            results.append({
                "title": company_name,
                "url": url,
                "content": self.removeTags(txt)
            })
           
           
       self.driver.close()
       return results









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