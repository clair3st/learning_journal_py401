import os
import sys
import transaction
import datetime

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
]


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)

    engine = get_engine(settings)
    Base.metadata.create_all(engine)

    session_factory = get_session_factory(engine)

    with transaction.manager:
        dbsession = get_tm_session(session_factory, transaction.manager)

        for entry in ENTRIES:
           row = MyModel(title=entry['title'],
                         body=entry['body'],
                         creation_date=datetime.datetime.strptime(entry['creation_date'], '%b %d, %Y')
                         )
           dbsession.add(row)
