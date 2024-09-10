# title gives every event title
# link gives a link to owl life
# <description> is formatted in html, so that will need further parsing... I bet the tags could just be stripped out of it and new lines removed.
# then <start xmlns="events"> is the event date, this can be parsed into a datetime format or just left as is
# then <end xmlns="events"> is the end date

import feedparser 
import re


class event:
    title = ""
    description = ""
    startDate = "" # could be some kind of datetime?
    endDate = ""
    link = ""

    # make SURE we pass an empty string as a method param if there's something missing
    def __init__(self, params):
        self.title = params[0]
        self.description = params[1]
        self.startDate = params[2] # could be some kind of datetime?
        self.endDate = params[3]
        self.link = params[4]

    def __str__(self):
        return (f"Title: {self.title}\n"
                f"Description: {self.description}\n"
                f"Start Date: {self.startDate}\n"
                f"End Date: {self.endDate}\n"
                f"Link: {self.link}\n")

class RSSparser:
    
    events = []

    # this could be json-ified
    def to_string(self, output):
        for i in self.events:
            output = output + " " + i.__str__() + " \n"

    def dehtmlify(self, doc):
        p = re.compile('<.*?>')
        return re.sub(p, "", doc).replace("&nbsp;", " ")


    def scrape(self):
        feed_url = "https://owllife.kennesaw.edu/events.rss" 
        blog_feed = feedparser.parse(feed_url) 
        for entry in blog_feed.entries:
            self.events.append(event([entry.title, self.dehtmlify(entry.description), entry.start, entry.end, entry.link]))
         
r = RSSparser()
r.scrape()
