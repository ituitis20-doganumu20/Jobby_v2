from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
import undetected_chromedriver as uc
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

class Driver:

    def __init__(self):

        self.driver = uc.Chrome()

    def getURL(self,url):
        
        self.driver.get(url)

