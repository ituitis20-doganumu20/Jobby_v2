import sys
import os
import json
import re

# Add the project root (one level up) to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import llm.gemini_client as llm
from backend.backend_tools.web_scrapping.linkedIn_scrapping import linkedInDriver
from backend.backend_tools.web_scrapping.driver import Driver
from backend.backend_tools.web_scrapping.xing_scrapping import xingDriver
class Agent:

    def __init__(self):

        self.driver= None
        self.llm=llm.Llm()

    def specifyWebsite(self,driver_type):
        if driver_type == "linkedIn":
            self.driver = linkedInDriver()
        elif driver_type == "xing":
            self.driver = xingDriver()

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
    
    def xingFilteredJobs(self, url, user_pref):
        jobs = self.driver.getJobContents(url)
        filtered = []

        for i in range(0, len(jobs), 10):
            batch = jobs[i:i+10]
            prompt = (
                f"User preference: '{user_pref}'. For each of the following {len(batch)} jobs, say 'yes' or 'no' and why.\n "
                f"If the content of the job is unavailable by any change, say 'yes' also, since the user need to look to themselfs.\n"
                f"Respond in this exact JSON format only:\n"
                f"[{{'job': 1, 'answer': 'yes'/'no', 'reason': '...'}}, ...]\n\n"
            )
            # Add each job's content to the prompt
            prompt += "Here are the jobs:\n\n"
            for idx, job in enumerate(batch):
                prompt += f"Job {idx+1}:\n{job['content']}\n\n"
            
            prompt += "End of jobs."
            try:
                result = self.llm.generate_gemini_response(prompt) 
                print(f"Batch {i//10 + 1} response: {result}") #for debugging
                # 1) strip any markdown fences
                clean = re.sub(r'```(?:json)?\s*', '', result)
                clean = clean.replace('```', '')

                # 2) grab the entire JSON array
                match = re.search(r'\[.*\]', clean, re.DOTALL)
                if not match:
                    continue

                # 3) parse and filter
                answers = json.loads(match.group(0))
                for idx, ans in enumerate(answers):
                    if ans["answer"].lower() == "yes":
                        filtered.append({
                            "url": batch[idx]["url"],
                            "reason": ans["reason"],
                            "body": batch[idx]["content"]
                        })

            except Exception as e:
                # you might want to log e here
                continue

        print(f"Filtered jobs: {len(filtered)}")
        return filtered

    def linkedInFilteredJobs(self,job_title,user_pref):
        
        self.driver.insertJobTitle(job_title)
        self.driver.getJobsPage()
        urls = self.driver.getCompanyURLs()
        jobInfo = self.driver.getJobInfo(urls)
        print(len(jobInfo))
        #prompt = (
        #        f"User preference: '{user_pref}'. For each of the following {jobInfo} jobs, say 'yes' or 'no' and why. "
        #        f"Respond in this exact JSON format only:\n"
        #        f"[{{'job': 1, 'answer': 'yes'/'no', 'reason': '...'}}, ...]\n\n"
         #   )
        #filtered=[]
        #try:
         #           result = self.llm.generate_gemini_response(prompt) 
        #          #print(f"Batch {i//10 + 1} response: {result}") #for debugging
        #           # 1) strip any markdown fences
        #           clean = re.sub(r'```(?:json)?\s*', '', result)
#                    clean = clean.replace('```', '')
                    #print(clean)
                    # 2) grab the entire JSON array
                    #match = re.search(r'\[.*\]', clean, re.DOTALL)


        #except Exception as e:
            #print(e)
                    # you might want to log e here'''
                    

        return jobInfo



