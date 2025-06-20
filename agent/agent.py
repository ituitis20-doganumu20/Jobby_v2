import sys
import os

# Add the project root (one level up) to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import llm.gemini_client as llm
import backend_tools.web_scrapping.linkedIn_scrapping as linkedInScraper

class Agent:

    def __init__(self,url):

        self.driver= linkedInScraper.Driver(url)
        self.llm=llm.Llm()

    def retreive(self):

        response=self.llm.generate_gemini_response("Hi")
        print(response)
        
agent=Agent()
agent.retreive()


