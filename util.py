from classify import subjectivity_and_grade
import requests
import os
from dotenv import load_dotenv
import json
from bs4 import BeautifulSoup as bs
from article import article
from pymongo import MongoClient
from datetime import datetime
from boto.s3.connection import S3Connection

load_dotenv()


def getNYTArticle(url):
    content = requests.get(url).content
    soup = bs(content, 'html.parser')
    pTags = soup.findAll('p')
    art = ''
    count = 0
    # these lines are for the 'Advertisement', 'Supported By' and author text
    skipLines = [0, 1, 3, len(pTags) - 1]
    for tag in pTags:
        if count in skipLines:
            count += 1
            continue
        art += tag.getText() + "\n"
        count += 1
    return art


MONGO_CONNECTION = os.environ.get('MONGO_CONNECTION')
client = MongoClient(MONGO_CONNECTION)
db = client.data
news = db.news


def getStories(grade, subjectivity, sentimentality):
    if grade == 0:
        stories = list(news.find({}, {'_id': 0}))
    else:
        stories = list(news.find({"grade":grade}, {'_id': 0}))
    if subjectivity == 0 and sentimentality == 0: #sort by lowest subjectivity 
        stories = sorted(stories, key = lambda i: (i["sentimentality"], i["subjectivity"]))
    elif subjectivity == 0 and sentimentality == 1:
        stories = sorted(stories, key = lambda i: (-i["sentimentality"], i["subjectivity"]))
    elif subjectivity == 1 and sentimentality == 0:
        stories = sorted(stories, key = lambda i: (i["sentimentality"], -i["subjectivity"]))
    elif subjectivity == 1 and sentimentality == 1:
        stories = sorted(stories, key = lambda i: (-i["sentimentality"], -i["subjectivity"]))
    elif subjectivity == 0 and sentimentality == 2:
        stories = sorted(stories, key = lambda i: i["subjectivity"])
    elif subjectivity == 1 and sentimentality == 2:
        stories = sorted(stories, key = lambda i: i["subjectivity"], reverse=True)
    elif subjectivity == 2 and sentimentality == 0:
        stories = sorted(stories, key = lambda i: i["sentimentality"])
    elif subjectivity == 2 and sentimentality == 1:
        stories = sorted(stories, key = lambda i: i["sentimentality"], reverse=True)
    return stories

def storeStories():
    #print("Updating articles.")
    news.drop()
    stories = []
    year = datetime.now().year
    month = datetime.now().month
    NYT = requests.get(
        "https://api.nytimes.com/svc/archive/v1/" + str(year) + "/" + str(month) + ".json?api-key=" + os.environ.get('NYT_API')).json()
    
    for story in NYT["response"]["docs"][-1 * min(len(NYT["response"]["docs"]), 100):]:
        art = getNYTArticle(story['web_url'])
        subjectivity, grade, sentimentality = subjectivity_and_grade(art)
        datetime_obj = datetime.strptime(story["pub_date"], '%Y-%m-%dT%H:%M:%S+%f')
        date_string = str(datetime_obj.month) + "/" + str(datetime_obj.day) + "/" + str(datetime_obj.year)
        a = article(int(grade), story["web_url"], "NYT", story["headline"]["main"],
                    story["lead_paragraph"], date_string, subjectivity, sentimentality)
        stories.append(vars(a))

    news.insert_many(stories)

