import json
import requests
import time

#Ensure the correct port is set for your environment
#The default port for TLS enabled systems is 443
#The default port for non-TLS enable systems is 80
urlPrefix = "https://HOST:PORT"
projectId = "d6cb1483-b0e9-44c1-8c68-429780173e37"
dataUri = "/dataTables/dataSources/cas~fs~cas-shared-default~fs~Public/tables/DRY_BEAN_DATASET"
oauthToken = "TOKEN"

#Perform Batch Retrain
retrainingUrl = urlPrefix + "/dataMiningProjectResources/projects/" + projectId + "/retrainJobs"
dmprRetrainingUrl = urlPrefix + "/dataMiningProjectResources/projects/" + projectId + "/retrainJobs"
querystring = {"action":"batch", "dataUri":dataUri}
payload = ""
headers = {
    "authorization": oauthToken,
    "accept": "application/vnd.sas.job.execution.job+json",
}
response = requests.request("POST", retrainingUrl, data=payload, headers=headers, params=querystring)
print(response.text)

#Wait before starting to look for the job
time.sleep(10)

#Get Current Retraining Job
currentRetrainingJobUrl = retrainingUrl + "/@currentJob"
payload = ""
headers = {
    "authorization": oauthToken,
    "accept": "application/vnd.sas.job.execution.job+json",
}
response = requests.request("GET", currentRetrainingJobUrl, data=payload, headers=headers)
response_txt = response.text
job = json.loads(response_txt)

jobLinks = job["links"]

for link in jobLinks:
    if link["rel"] == "self":
        selfLink = link
    break;

attempts = 0
maxAttempts = 300

while True:
    attempts = attempts + 1
    selfLinkUrl = urlPrefix + selfLink["uri"]
    payload = ""
    headers = {
        "accept": "application/vnd.sas.job.execution.job+json",
        "authorization": oauthToken
    }
    response = requests.request("GET", selfLinkUrl, data=payload, headers=headers)

    response_txt = response.text
    job = json.loads(response_txt)

    jobState = job["state"]
    print("Retraining job state is "+ jobState)

    if jobState == "completed" or jobState == "canceled" or jobState == "failed" or jobState == "timedOut" or attempts > maxAttempts:
        break;
    #Wait for 10 seconds before polling the job again
    time.sleep(10)

print("Final retraining job state is " + jobState)

#Get Champion
if jobState == "completed":
    championUri = dmprRetrainingUrl + "/@lastJob/champion"
    payload = ""
    headers = {
        "authorization": oauthToken,
        "accept": "application/vnd.sas.analytics.data.mining.model+json",
    }
    response = requests.request("GET", championUri, data=payload, headers=headers, params=querystring)
    #If the project has a champion model, it will be printed
    if response.status_code == requests.codes.ok:
        response_txt = response.text
        model = json.loads(response_txt)
        projectChampion = model["name"]
        print("Project champion model is " + projectChampion)

# 
# This project was not created with a data plan.