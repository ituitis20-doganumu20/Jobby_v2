from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import os
from backend.backend_tools.web_scrapping.driver import Driver  # Adjust import to your structure

class ResumeDriver(Driver):
    def __init__(self, download_dir):
        options = Options()
        options.add_experimental_option("prefs", {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "safebrowsing.enabled": True
        })
        options.add_argument("--log-level=3")
        super().__init__(options=options)

    def uploadJSONAndDownloadCV(self, json_path):
        self.getURL("https://resumake.io/")

        wait = WebDriverWait(self.driver, 20)

        # Wait for the upload input
        upload_input = wait.until(EC.presence_of_element_located((By.ID, "import-json")))
        
        # Use the absolute path and ensure proper escaping
        abs_json_path = os.path.abspath(json_path)
        upload_input.send_keys(abs_json_path)

        # Click “Download PDF” button
        generate_btn = wait.until(EC.element_to_be_clickable((
            By.XPATH, '//*[@id="app"]/div/main/div/div[1]/div[1]/a[1]'
        )))
        generate_btn.click()

        # Wait for download to finish
        # self._wait_for_download("resume.pdf", self.download_dir)
        time.sleep(10)
        print("✅ CV download completed.")

    # def _wait_for_download(self, filename_prefix, download_dir, timeout=30):
    #     """Waits until a .crdownload file disappears (indicating the file is done downloading)."""
    #     end_time = time.time() + timeout
    #     while time.time() < end_time:
    #         files = os.listdir(download_dir)
    #         if any(f.startswith(filename_prefix) and not f.endswith(".crdownload") for f in files):
    #             return
    #         time.sleep(10)
    #     raise TimeoutError("Download timed out.")
