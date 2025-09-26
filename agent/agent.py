import sys
import os
import json
import re
import time

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
    def prompt(self,jobsInfo,batch_size,user_pref):
        
        filtered = []
        for i in range(0, len(jobsInfo), batch_size):
            batch = jobsInfo[i:i+batch_size]

            # Build single prompt for both filtering and summarizing
            prompt = (
                f"You are an assistant helping a user find jobs based on their preference: '{user_pref}'.\n"
                f"For each of the {len(batch)} jobs below, do two things:\n"
                f"1. Say 'yes' or 'no' for whether the job matches the user's preference.\n"
                f"2. If 'yes', give a short bullet-point summary with important information like title, responsibilities, requirements, location, and language needs.\n"
                f"If your answer is no, say no summary in the summary json field, since we won't display them to the user, you dont need to write it anyways.\n"
                f"Note: If job content is unavailable or unclear, respond with 'yes' so the user can check manually. For the summary you can say check by yourself.\n\n"
                f"Respond in this exact JSON format:\n"
                f"[{{'job': 1, 'answer': 'yes'/'no', 'reason': '...', 'summary': '...'}}, ...]\n\n"
            )

            prompt += "Here are the jobs:\n\n"
            for idx, job in enumerate(batch):
                prompt += f"Job {idx+1} (Title: {job['title']}):\n{job['content']}\n\n"
            prompt += "End of jobs."

            try:
                result = self.llm.generate_gemini_response(prompt)
                print(f"Batch {i//10 + 1} response: {result}")

                # Clean markdown
                clean = re.sub(r'```(?:json)?\s*', '', result).replace('```', '')
                match = re.search(r'\[.*\]', clean, re.DOTALL)
                if not match:
                    continue

                responses = json.loads(match.group(0))
                for idx, resp in enumerate(responses):
                    if resp["answer"].lower() == "yes":
                        job = batch[idx]
                        filtered.append({
                            "title": job["title"],
                            "url": job["url"],
                            "reason": resp["reason"],
                            "body": job["content"],
                            "job_sum": resp["summary"]
                        })

            except Exception as e:
                print(f"Error in batch {i//10 + 1}: {e[:50]}")
                continue

        print(f"Filtered jobs: {len(filtered)}")
        return filtered
    
    def xingFilteredJobs(self, url, user_pref):
        jobs = self.driver.getJobContents(url)
        print(f"Total jobs scraped: {len(jobs)}")
        filtered=self.prompt_one_by_one(jobs,user_pref)
        return filtered

    def linkedInFilteredJobs(self,job_title,numberOfJobs):
        
        self.driver.insertJobTitle(job_title)
        self.driver.getJobsPage()
        urls = self.driver.getCompanyURLs(numberOfJobs)
        jobInfo = self.driver.getJobInfo(urls) 

        return jobInfo
    
    def prompt_one_by_one(self, jobsInfo, user_pref):
        print(f"Starting filtering")
        filtered = []
        for idx, job in enumerate(jobsInfo):
            while True:
                try:
                    # Get the current API key
                    current_api_key = self.llm.get_api_key()

                    prompt = (
                        f"You are an assistant helping a user find jobs based on their preference: '{user_pref}'.\n"
                        f"For the job below, do two things:\n"
                        f"1. Say 'yes' or 'no' for whether the job matches the user's preference.\n"
                        f"2. If 'yes', give a short bullet-point summary with important information like title, responsibilities, requirements, location, and language needs. This needs to be in a human readible format, bullet point list for example, it wont be json.\n"
                        f"If your answer is no, say no summary in the summary json field.\n"
                        f"Note: If job content is unavailable or unclear, respond with 'yes'. For the summary you can say check by yourself.\n\n"
                        f"Respond in this exact JSON format:\n"
                        f"[{{'job': 1, 'answer': 'yes'/'no', 'reason': '...', 'summary': '...'}}]\n\n"
                        f"Job 1 (Title: {job['title']}):\n{job['content']}\n\nEnd of job."
                    )

                    result = self.llm.generate_gemini_response(prompt, api_key=current_api_key)
                    print(f"Job {idx + 1} done")
                    clean = re.sub(r'```(?:json)?\s*','', result).replace('```', '')
                    match = re.search(r'\[.*\]', clean, re.DOTALL)
                    if not match:
                        raise ValueError("Response did not contain valid JSON list.")

                    resp = json.loads(match.group(0))[0]
                    if resp["answer"].lower() == "yes":
                        filtered.append({
                            "title": job["title"],
                            "url": job["url"],
                            "reason": resp["reason"],
                            "body": job["content"],
                            "job_sum": resp["summary"]
                        })
                    ##print the answer and reason for each job
                    print(f"Job {idx + 1} answer: \n {resp['answer']}, \n reason:\n {resp['reason']}")
                    break  # success
                except Exception as e:
                    print(f"Retrying job {idx + 1} due to error: {e}")
                    self.llm.switch_to_next_key()
                    print("Switched to the next API key.")
                    #time.sleep(5)  # optional: avoid hammering the API
                    continue

        print(f"Filtered jobs: {len(filtered)}")
        return filtered

    def linkedInPrompt(self, jobsInfo, user_pref,batch_size):        
        filtered=self.prompt(jobsInfo,batch_size,user_pref)
        return filtered