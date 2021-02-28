
StartPage = "https://www.seek.com.au/jobs-in-information-communication-technology/in-All-Brisbane-QLD"
jobBaseURL = "https://www.seek.com.au/job/"

import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# SETUP WEBDRIVER WITH NORMAL UA
opts = Options()
opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36")
driver = webdriver.Chrome("./chromedriver.exe", 0, opts)

# GET FIRST WEBPAGE
driver.get(StartPage)

# initialise job stores
jobIDStore = []
jobStore = []


# GET JOB ID's
def getJobIds():
    JobListings = driver.find_elements_by_css_selector('div[data-search-sol-meta]')
    JobCount = len(JobListings)
    print("Adding " + str(JobCount) + " Job IDs to the store")
    for Job in JobListings:
        JobJSON = Job.get_attribute('data-search-sol-meta')
        JobID = json.loads(JobJSON)["jobId"]
        jobIDStore.append(JobID)

getJobIds()

def nextPage():
    NextPageItems = driver.find_elements_by_css_selector('a[data-automation="page-next"]')
    if len(NextPageItems) != 0:
        NextPageLink = NextPageItems[0].get_attribute('href')
        print("Navigating to " + NextPageLink)
        driver.get(NextPageLink)
        # time.sleep(0.5)
        getJobIds()
        nextPage()
    else:
        print("Outputing " + str(len(jobIDStore)) + " Job IDs")
        AllJobIDJSON = json.dumps(jobIDStore)
        f = open("output/allJobIds.json", "w")
        f.write(AllJobIDJSON)
        f.close()

nextPage()

# Scrape all jobs
for Job in jobIDStore:
    JobLink = jobBaseURL + Job
    print("Getting Job Data - " + JobLink)
    driver.get(JobLink)
    
    JobInfo = {}
    # time.sleep(0.5)
    JobInfo["id"] = Job
    JobInfo["link"] = JobLink
    JobInfo["title"] = driver.find_element_by_css_selector('span[data-automation="job-detail-title"]').find_element_by_xpath('.//*').get_attribute('textContent')
    JobInfo["advertiser"] = ""
    try:
        JobInfo["advertiser"] = driver.find_element_by_css_selector('span[data-automation="advertiser-name"]').find_element_by_xpath('.//*').get_attribute('textContent')
    except:
        try:
            JobInfo["advertiser"] = driver.find_element_by_css_selector('span[data-automation="job-header-company-review-title"]').find_element_by_xpath('.//*').get_attribute('textContent')
        except:
            print("no advertiser found")
    print(JobInfo)
    infoBox = driver.find_element_by_css_selector('dd[data-automation="job-detail-date"]').find_element_by_xpath('./..')
    infoBoxTitles = infoBox.find_elements_by_xpath('.//dt')
    infoBoxDescriptions = infoBox.find_elements_by_xpath('.//dd')
    for i in range(len(infoBoxTitles)):
        dt = infoBoxTitles[i].get_attribute('textContent').lower()
        dd = infoBoxDescriptions[i].get_attribute('textContent')
        JobInfo[dt] = dd

    JobInfo["description"] = driver.find_element_by_css_selector('div[data-automation="jobDescription"]').text
    
    jobStore.append(JobInfo)

# Write all jobs to json
f = open("output/allJobs.json", "w")
AllJobJSON = json.dumps(jobStore)
f.write(AllJobJSON)
f.close()


# BYE
driver.quit()