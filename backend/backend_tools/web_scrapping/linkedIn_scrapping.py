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
from urllib.parse import urlparse, parse_qs, urlencode
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# Add the project root (one level up) to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from web_scrapping.driver import Driver

class linkedInDriver(Driver):

    def __init__(self,url="https://www.linkedin.com/login"):
        options = Options()
        options.add_argument("--log-level=3")  # only fatal errors
        super().__init__()
        super().getURL(url)
        try:
            print("Please log in to LinkedIn within 5 minutes...")
            WebDriverWait(self.driver, 300).until(
                EC.url_to_be("https://www.linkedin.com/feed/")
            )
            print("Successfully logged in.")
        except TimeoutException:
            print("Login timed out. Please run the script again.")
            self.quit()
            raise


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
    def getCompanyURLs(self, numberOfJobs):
        """
        Scrolls through the job listings page to find all job URLs up to the desired number,
        handling both infinite scroll and pagination.
        """
        print("--- Starting getCompanyURLs ---")
        urls = set()
        
        try:
            page_count = 1
            while len(urls) < numberOfJobs:
                print(f"\n--- Starting Page {page_count}. Found {len(urls)}/{numberOfJobs} URLs so far. ---")
                
                # --- Infinite Scroll Handling ---
                last_element_count = 0
                while True:
                    # Find all job link elements currently on the page
                    elements = self.driver.find_elements(By.XPATH, "//a[contains(@class, 'job-card-list__title--link')]")
                    current_element_count = len(elements)
                    print(f"Found {current_element_count} job link elements on the page.")

                    if current_element_count == last_element_count and last_element_count > 0:
                        print("No new job elements loaded via scrolling. Moving to pagination check.")
                        break # Exit the infinite scroll loop for this page

                    # Scroll the last element into view to trigger loading more
                    print(f"Scrolling last element ({current_element_count}) into view...")
                    last_element = elements[-1]
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", last_element)
                    
                    print("Waiting for new content to load after scroll...")
                    #time.sleep(3)
                    
                    # Update for the next scroll check
                    last_element_count = current_element_count

                # --- URL Collection for the current fully loaded page ---
                final_elements = self.driver.find_elements(By.XPATH, "//a[contains(@class, 'job-card-list__title--link')]")
                initial_url_count = len(urls)
                for elem in final_elements:
                    urls.add(elem.get_attribute('href'))
                print(f"Collected URLs on this page. Total unique URLs now: {len(urls)}. New URLs found on this page: {len(urls) - initial_url_count}")

                if len(urls) >= numberOfJobs:
                    print(f"Reached desired number of jobs ({len(urls)} >= {numberOfJobs}).")
                    break

                # --- Pagination Handling ---
                try:
                    print("Checking for 'Next' button...")
                    # Ensure the whole page is scrolled down to find the pagination controls
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    #time.sleep(1)
                    
                    next_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[./span[@class='artdeco-button__text' and text()='Next']]"))
                    )
                    if next_button.is_enabled():
                        print("Found and clicking 'Next' button.")
                        next_button.click()
                        #time.sleep(3) # Wait for page to load after clicking next
                        page_count += 1
                    else:
                        print("'Next' button found but not enabled. Assuming end of results.")
                        break # Exit main loop if next button is disabled
                except TimeoutException:
                    print("'Next' button not found. Assuming end of results.")
                    break # Exit main loop if no next button is found
                except NoSuchElementException:
                    print("'Next' button not found. Assuming end of results.")
                    break # Exit main loop if no next button is found

        except Exception as e:
            print(f"An unexpected error occurred in getCompanyURLs: {e}")
        
        print(f"--- Finished getCompanyURLs. Returning {len(urls)} unique URLs. ---")
        return list(urls)[:numberOfJobs]
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


    def getJobInfoWithJobId(self, user_search_url, numberOfJobs):
        """
        Scrapes job information by constructing direct URLs from job IDs based on the user's search URL.
        """
        self.getURL(user_search_url)
        job_page_urls = self.getCompanyURLs(numberOfJobs)
        direct_urls = []

        parsed_user_search_url = urlparse(user_search_url)
        base_url = parsed_user_search_url.scheme + "://" + parsed_user_search_url.netloc + parsed_user_search_url.path
        query_params = parse_qs(parsed_user_search_url.query)

        for url in job_page_urls:
            match = re.search(r"/view/(\d+)/", url)
            if match:
                job_id = match.group(1)
                
                # Update currentJobId in the original search URL's query parameters
                query_params['currentJobId'] = [job_id]
                updated_query_string = urlencode(query_params, doseq=True)
                
                # Reconstruct the URL with the updated query parameter
                new_job_url = f"{base_url}?{updated_query_string}"
                direct_urls.append(new_job_url)
        
        return self.getJobInfo(direct_urls)

    def getJobInfoFromPanel(self, numberOfJobs):
        """
        Scrapes job information by clicking on job listings and extracting data 
        from the right-hand panel, avoiding full page reloads.
        """
        results = []
        jobs_processed = 0
        
        # Wait for the initial list of jobs to be present
        WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "scaffold-layout__list-item"))
        )

        page_number = 1
        while jobs_processed < numberOfJobs:
            print(f"Processing page {page_number}...")
            # Find all job cards on the current page to know how many to iterate through
            job_cards_on_page = self.driver.find_elements(By.CLASS_NAME, "scaffold-layout__list-item")
            
            if not job_cards_on_page:
                print("No more job cards found.")
                break

            # Iterate through the indices of job cards on the current page
            for card_index in range(len(job_cards_on_page)):
                if jobs_processed >= numberOfJobs:
                    break
                
                try:
                    # Re-find all cards and select the one at the current index right before interacting with it.
                    # This is a key step to prevent StaleElementReferenceException.
                    current_card = self.driver.find_elements(By.CLASS_NAME, "scaffold-layout__list-item")[card_index]

                    # Scroll the card into view and click it
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", current_card)
                    time.sleep(1) # Brief pause to ensure it's settled
                    current_card.click()
                    
                    # Wait for the job details panel on the right to update
                    details_container_xpath = "//div[contains(@class, 'jobs-details__main-content')]"
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, details_container_xpath))
                    )
                    time.sleep(1) # Allow content to render

                    # Scrape details from the right-hand panel
                    job_title = self.driver.find_element(By.CLASS_NAME, "job-details-jobs-unified-top-card__job-title").text.strip()
                    company_name = self.driver.find_element(By.CLASS_NAME, "job-details-jobs-unified-top-card__company-name").text.strip()
                    
                    job_link_element = current_card.find_element(By.TAG_NAME, 'a')
                    job_url = job_link_element.get_attribute('href')
                    
                    p_tags = self.driver.find_elements(By.XPATH, "//div[@id='job-details']//p")
                    description_html = ''.join(p.get_attribute("outerHTML") for p in p_tags)

                    results.append({
                        "title": job_title,
                        "company": company_name,
                        "url": job_url,
                        "content": self.removeTags(description_html)
                    })
                    jobs_processed += 1
                    print(f"Successfully scraped job {jobs_processed}/{numberOfJobs}: {job_title}")

                except (NoSuchElementException, TimeoutException) as e:
                    print(f"Warning: Skipping a job card due to a timeout or missing element. {e}")
                    continue
                except Exception as e:
                    # This can happen if the page refreshes unexpectedly.
                    print(f"An unexpected error occurred: {e}. Breaking inner loop to try next page.")
                    break 

            if jobs_processed >= numberOfJobs:
                break

            # After processing all cards on the page, attempt to paginate
            try:
                next_button = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='View next page']")
                if next_button.is_enabled():
                    print("Navigating to the next page of jobs...")
                    next_button.click()
                    page_number += 1
                    # Wait for new page to load, a simple sleep is often reliable here
                    time.sleep(3) 
                else:
                    print("All pages have been processed.")
                    break
            except NoSuchElementException:
                print("No 'next page' button found. All jobs processed.")
                break

        return results



"""
# Example using the traditional URL navigation approach (kept for reference)
# driver=linkedInDriver()
# driver.getURL("https://www.linkedin.com/feed/")
# driver.insertJobTitle("python developer")
# driver.getJobsPage()
# time.sleep(2)
# titles=driver.getJobtitles()
# print(titles)
# urls=driver.getCompanyURLs(5) # Get 5 company URLs
# print(urls)
# jobsInfo=driver.getJobInfo(urls)
# print(jobsInfo)
# time.sleep(60)
# driver.quit()

# Example using the new click-and-scrape panel approach
# driver=linkedInDriver()
# # Assuming you are already logged in or handle login separately
# # For demonstration, let's say we start from the feed and search
# driver.getURL("https://www.linkedin.com/feed/")
# driver.insertJobTitle("python developer")
# driver.getJobsPage() # Navigate to job search results page
# time.sleep(2)

# jobsInfoFromPanel = driver.getJobInfoFromPanel(5) # Scrape 5 jobs using the new method
# print("Jobs scraped from panel:", jobsInfoFromPanel)
# time.sleep(60)
# driver.quit()
"""