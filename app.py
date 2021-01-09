from flask import Flask, render_template
import requests
from util import getStories, storeStories
import json
from apscheduler.schedulers.background import BackgroundScheduler


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/<grade>/<subjectivity>/<sentimentality>')
def newsStory(grade, subjectivity, sentimentality):
    articles = getStories(int(grade), int(subjectivity), int(sentimentality))
    json_object = json.dumps(articles)
    if articles is None:
        return ["No results"]
    else:
        return json_object


if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    job = scheduler.add_job(storeStories, 'interval', minutes=30)
    scheduler.start()
    app.run(debug=True)