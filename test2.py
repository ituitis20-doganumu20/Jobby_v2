from backend.backend_tools.web_scrapping.driver import Driver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class XingDriver(Driver):
    def __init__(self):
        options = Options()
        options.add_argument("--log-level=3")
        super().__init__(options=options)

    def printFilteredLinks(self, url):
        self.getURL(url)
        wait = WebDriverWait(self.driver, 10)
        time.sleep(50)
        links = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a[aria-label][href]')))
        kept = []
        for l in links:
            href = (l.get_attribute("href") or "").strip()
            label = (l.get_attribute("aria-label") or "").strip()
            if not href:
                continue
            if "https://www.xing.com/" in href.lower() and "job" not in href.lower():
                continue
            #print(label, "->", href)
            kept.append({"label": label, "href": href})
            
        # print how many links were kept
        print(f"Kept {len(kept)} relevant job links.")
        # print which urls were removed

        self.driver.close()
        return kept

driver = XingDriver()
driver.printFilteredLinks("https://www.xing.com/jobs/search?keywords=Werkstudent&location=Bonn&id=121067bff07394a5d92ce255fa4ee3a5&cityId=2946447.b8acbb&radius=100&careerLevel=1.795d28*2.24d1f6&sort=date&discipline=1011.6cf3f7*1007.b61d22*1022.ed6b40")

