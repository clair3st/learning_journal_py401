"""Initialize the sql database."""

import os
import sys
import transaction
import datetime
import requests

from pyramid.paster import (
    get_appsettings,
    setup_logging,
)

from pyramid.scripts.common import parse_vars

from ..models.meta import Base
from ..models import (
    get_engine,
    get_session_factory,
    get_tm_session,
)
from ..models import MyModel

ENTRIES = [
    {"title": "Day 11",
     "id": 1,
     "body": """Today we learnt so many new things! First we
     learned about web frameworks and in particular how to use Pyramid.
     We went pretty quickly over this so I got a little lost in class but
     doing it twice for both me and my partner's learning journal was great
     practice. We also learned about deploying simple python apps to heroku.
     I had a surprsing amount of difficulty with this. after a lot of
     frustration I realized t was a problem with my file tree setup.
     Luckily I was able to get my site up and running.<br>
            I'm really enjoying the data structures at the moment.
     I feel like the more we do the easier it is for me to get
     my head around how they work and what they could be used for.
     Today was a deque which was similar to a queue and a double
     linked list.""",
     "creation_date": "Dec 19, 2016"},

    {"title": "Day 12",
     "id": 2,
     "creation_date": "Dec 20, 2016",
     "body": """I learned about the binary heap data structure. I can see that
     this would shorten the time needed to sort data compated to just looping
     through a normal list. I found it hard to get my head around not using
     nodes when we implemented it using a list in python.<br>
     We also learned about jinja2 today and using it as a templating system for
     a website. I think initially I was a little freaked out by jinja when I
     did the reading but now that I've had the chance to practise and implement
     it in this site I feel like I'm starting to get the hang of it. """},

    {"title": "Day 13",
     "id": 3,
     "creation_date": "Dec 21, 2016",
     "body": """Today felt like a huge jump forward in what we've been learning
      over the past few days. We learned about implementing a SQL database into
      a pyramid framework to hold our data. I am still deciding if I like it
      better to follow along with the coding in class or instead of typing
      concentrate on understanding what is going on. I think I finally have my
      file structure with my pyramid apps all in order, probably just in time
      too! That was one of my biggest roadblocks today, understanding how all
      the work we've been doing over the week would sit together and their
      dependencies. """},

    {"title": "Day 14",
     "id": 4,
     "creation_date": "Dec 22, 2016",
     "body": """I was very thankful for a slightly slower pace today. Yesterday
     everything felt so over my head trying to figure out the pyramid scaffold
     and how all the seemingly separate parts connected together. Going through
     it slower today and then walking through it with my partner this afternoon
     has really helped me. I'm yet to start testing through, which at the
     moment feels like a daunting task. I did manage to build on what I had
     done yesterday and add the functionality to the edit and create new pages.
     I'm looking forward to learn about postgres and how that will help with
     our app persistence. I hope this is my last learning journal post on the
     group site! """},
]


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def get_old_entries():
    """Access old entries from class site."""
    api_key = os.environ["API_KEY"]
    url = 'http://sea-python-401d5.herokuapp.com/api/export?apikey='
    response = requests.get(url + api_key)
    resp_json = response.json()
    entries = [{
        'creation_date': i['created'],
        'title': i['title'],
        'body': i['markdown']
    } for i in resp_json]
    return entries


def add_old_entries():
    """Add previous entries."""
    entries = get_old_entries()
    settings = {
        "sqlalchemy.url": os.environ.get("DATABASE_URL", "postgres:///localhost:5432/learning-journal")
    }

    engine = get_engine(settings)

    # Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    session_factory = get_session_factory(engine)

    with transaction.manager:
        dbsession = get_tm_session(session_factory, transaction.manager)

        query = dbsession.query(MyModel).all()

        titles = [q.title for q in query]

        for entry in entries:
            row = MyModel(
                title=entry['title'],
                body=entry['body'],
                creation_date=datetime.datetime.strptime(entry['creation_date'][:-3], "%Y-%m-%dT%H:%M:%S.%f")
            )
            if entry['title'] not in titles:
                dbsession.add(row)
                titles.append(entry['title'])
                print('Added entry: ' + entry['title'])


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)

    settings = get_appsettings(config_uri, options=options)
    settings["sqlalchemy.url"] = os.environ.get("DATABASE_URL", "postgres:///localhost:5432/learning-journal")

    engine = get_engine(settings)

    # Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    session_factory = get_session_factory(engine)

    with transaction.manager:
        dbsession = get_tm_session(session_factory, transaction.manager)

        for entry in ENTRIES:
            row = MyModel(
                title=entry['title'],
                body=entry['body'],
                creation_date=datetime.datetime.strptime(entry['creation_date'], '%b %d, %Y')
            )
            dbsession.add(row)
