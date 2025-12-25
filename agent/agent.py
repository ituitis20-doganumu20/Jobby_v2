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

    def linkedInFilteredJobs(self, url, numberOfJobs, user_pref):
        # self.driver.getURL(url)
        # urls = self.driver.getCompanyURLs(numberOfJobs)
        # jobInfo = self.driver.getJobInfo(urls)
        # jobInfo = self.driver.getJobInfoFromPanel(numberOfJobs)
        jobInfo = self.driver.getJobInfoWithJobId(url, numberOfJobs)
        filtered_jobs = self.prompt_one_by_one(jobInfo, user_pref)
        return filtered_jobs
    
    def get_history_file_path(self):
        return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'processed_jobs.json')

    def load_processed_jobs(self):
        file_path = self.get_history_file_path()
        if not os.path.exists(file_path):
            return {}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Convert list to dict keyed by url for fast lookup
                if isinstance(data, list):
                     return {job['url']: job for job in data}
                return data
        except Exception:
            return {}

    def save_job_to_history(self, job_data):
        file_path = self.get_history_file_path()
        # Load current to ensure we don't overwrite if file changed externally (though unlikely here)
        # For performance, we could rely on in-memory dict, but safety first.
        current_data = self.load_processed_jobs()
        current_data[job_data['url']] = job_data
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(list(current_data.values()), f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Error saving job to history: {e}")

    def prompt_one_by_one(self, jobsInfo, user_pref):
        print(f"Starting filtering")
        processed_history = self.load_processed_jobs()
        
        for idx, job in enumerate(jobsInfo):
            if job['url'] in processed_history:
                print(f"Skipping already processed job: {job['title']}")
                saved_job = processed_history[job['url']]
                if saved_job.get("is_match", False):
                    yield {
                        "title": saved_job["title"],
                        "url": saved_job["url"],
                        "reason": saved_job.get("reason"),
                        "body": saved_job.get("body"),
                        "job_sum": saved_job.get("job_sum")
                    }
                continue

            while True:
                try:
                    # Get the current API key
                    current_api_key = self.llm.get_api_key()

                    prompt = (
                        f"You are an assistant helping a user find jobs based on their preference: '{user_pref}'.\n"
                        f"For the job below, do these followin things:\n"
                        f"1. Say 'yes' or 'no' for whether the job matches the user's preference.\n"
                        f"2. If 'yes', give a short bullet-point summary with important information like title, responsibilities, requirements, location, and language needs. This needs to be in a human readable format, bullet point list for example, it won't be JSON. An example summary:\n- **Job Title:** Student Trainee / Working Student in IT Operations\n- **Responsibilities:** Support operational IT procurement (licenses, hardware, SAP orders, communication), create/maintain application package data sheets, optimize device assignment in ServiceNow internationally, and assist with lifecycle management.\n- **Requirements:** Enrolled student (1+ year perspective), good knowledge of MS Office, Outlook, Teams, excellent communication skills, interest in IT, and good English skills.\n- **Location:** Leverkusen, NW, Germany (On-site).\n- **Language Needs:** Good English skills."
                        f"If your answer is no, say no summary in the summary json field.\n"
                        f"Note: If job content is unavailable or unclear, respond with 'yes'. For the summary you can say check by yourself.\n\n"
                        f"Respond in this exact JSON format:\n"
                        f"[{{'answer': 'yes'/'no', 'reason': '...', 'summary': '...'}}]\n\n"
                        f"Job (Title: {job['title']}):\n{job['content']}\n\nEnd of job."
                    )

                    result = self.llm.generate_gemini_response(prompt, api_key=current_api_key)
                    print(f"Job {idx + 1} Link: {job['url']} \n response: {result}")
                    clean = re.sub(r'```(?:json)?\s*','', result).replace('```', '')
                    match = re.search(r'\[.*\]', clean, re.DOTALL)
                    if not match:
                        raise ValueError("Response did not contain valid JSON list.")

                    resp = json.loads(match.group(0))[0]
                    is_match = resp["answer"].lower() == "yes"
                    
                    job_result_data = {
                        "title": job["title"],
                        "url": job["url"],
                        "reason": resp["reason"],
                        "body": job["content"],
                        "job_sum": resp["summary"],
                        "is_match": is_match
                    }
                    
                    self.save_job_to_history(job_result_data)

                    if is_match:
                        yield job_result_data
                    break  # success
                except Exception as e:
                    print(f"Retrying job {idx + 1} due to error: {e}")
                    if "429" in str(e):
                        # Try to find 'seconds: <number>' in the error message
                        match_wait = re.search(r'seconds:\s*(\d+)', str(e))
                        wait_time = (int(match_wait.group(1)) + 1) if match_wait else 15
                        print(f"Rate limit reached (429). Waiting for {wait_time} seconds...")
                        time.sleep(wait_time)
                    self.llm.switch_to_next_key()
                    print("Switched to the next API key.")
                    continue

        print("All jobs have been processed.")
