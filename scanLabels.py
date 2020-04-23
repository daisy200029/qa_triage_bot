import requests
import io
import re
import sys
import os
import slack
from datetime import datetime, timedelta

HOST= "https://api.github.com/"
TOKEN=os.environ["MOZILLA_GITHUB_TOKEN"]
headers = {'Authorization': 'token ' + TOKEN}

LABEL = "need triage"
N = 10

def find_issues_without_label():
    '''
    find issues without any labels since last week.
    GET /repos/:owner/:repo/issues
    Return [issues_without_label]
    '''
    date_N_days_ago = datetime.now() - timedelta(days=N)
    print( "ISO format {} days ago : {} ".format( N, date_N_days_ago.isoformat()))
    
    issues_without_label=[]
    data = {"since": date_N_days_ago.isoformat()}
    resp = requests.get( HOST + 'repos/' + 'mozilla-tw/FirefoxLite/issues', headers=headers, json = data )
    if resp.status_code == 200 or 201:
        for issue in resp.json():
            if  ("pull_request" not in issue) and (len(issue['labels'])== 0) :
                issues_without_label.append(issue['number'])
        print ('list tickets without label : ', issues_without_label)
        return issues_without_label
    else:
        print('Unable to find tags')
        print(resp.text)

def update_issue_label(issues_without_label):
    '''
    Update issues to label "need triage" 
    PATCH /repos/:owner/:repo/issues/:issue_number
    parameter labels  = "need tirage"
    '''
    data = {"labels": [LABEL]}
    for issue_number in issues_without_label:
        resp = requests.patch( HOST + 'repos/' + 'mozilla-tw/FirefoxLite/issues/'+ str(issue_number) , headers=headers, json = data )
        if resp.status_code == 200 :
            print('label sucessfully updated : ', issue_number)
        else:
            print('Unable to find tags')
            print(resp.text)

def need_triage_issues():
    '''
    count issues with "need triage" label since last week.
    GET /repos/:owner/:repo/issues
    parameter : label name = "need triage"
    Return "count"
    '''
    need_triage_issues=[]
    resp = requests.get( HOST + 'repos/' + 'mozilla-tw/FirefoxLite/issues?labels=need triage', headers=headers )
    if resp.status_code == 200 or 201:
        for issue in resp.json():
            if  "pull_request" not in issue :
                need_triage_issues.append(issue['number'])
        print ('list {} issues : {} '.format( LABEL, need_triage_issues))
        return need_triage_issues
    else:
        print('Unable to find tags')
        print(resp.text)

def send_slack_msg_to_notify_pm(list_of_need_triage_issue):
    '''
    Send Slack notification
    '''
    count = len(list_of_need_triage_issue)
    TRIAGE_SLACK_API_TOKEN=os.environ["TRIAGE_SLACK_API_TOKEN"]
    client = slack.WebClient(token=TRIAGE_SLACK_API_TOKEN)
    CHANNEL="DE18AFX53"

    if count > 0: 
        client.chat_postMessage(
        channel=CHANNEL,
        link_names=1,
        text='Please PM help triage {} issues, refers {} cc: @wendy,@mark'.format(count,"https://github.com/mozilla-tw/FirefoxLite/issues?q=label%3A%22need+triage%22+")
        )
    else:
        client.chat_postMessage(
        channel=CHANNEL,
        text='great job, no tickets to triage today!'
        )

issues_without_label=find_issues_without_label()
update_issue_label(issues_without_label)

list_of_need_triage_issue = need_triage_issues()
send_slack_msg_to_notify_pm(list_of_need_triage_issue)
