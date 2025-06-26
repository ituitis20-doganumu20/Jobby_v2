import sys
import os

# Add the project root (one level up) to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import llm.gemini_client as llm
from backend.backend_tools.web_scrapping.linkedIn_scrapping import linkedInDriver
from backend.backend_tools.web_scrapping.driver import Driver
class Agent:

    def __init__(self):

        self.driver= None
        self.llm=llm.Llm()

    def specifyWebsite(self,driver_type):
         if driver_type == "linkedIn":
            self.driver = linkedInDriver()
       # elif driver_type == "xing":
           # self.driver = xingDriver()

    def linkedInGetJobTitles(self,jobTitle):
        self.driver.insertJobTitle(jobTitle)
        self.driver.getJobsPage()
        titles=self.driver.getJobtitles()

        response=self.llm.generate_gemini_response("Extract job titles from this list"+' '.join(titles))
        print(response)
        return response
    def linkedInGetCompanyNamesURL(self):
        html=self.driver.getHTML()
        response=self.llm.generate_gemini_response("Extract each company name and its url from this html code"+html)
        #print(response)
        return response

        
"""agent=Agent()
agent.specifyWebsite("linkedIn")
agent.linkedInGetJobTitles("python developer")
companyNamesURLS=agent.linkedInGetCompanyNamesURL()
"""

