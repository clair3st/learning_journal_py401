# Learning Journal

###Learning Journal application for Codefellows 401 Python

Pages have been prepared using jinja2 for the following pages:

main - home page that shows a list of journal entries with just the title and date created.
detail - detail page that shows a single entry. The title, text and created date should be displayed on this page.
new - HTML form page you will use to create a new entry. The title and text of the entry are inputs of the form, empty at first.
edit - HTML form page you will use to edit an existing entry. The title and text of the entry are inputs in this form.
style.css has been prepared for the styling of each of the 4 pages using bootstrap.

The learning journal is deployed on: https://clairegatenby-learning-journal.herokuapp.com/ utilizing Pyramid and journal entries are persisted using alchemySQL.

###Testing coverage
```
---------- coverage: platform darwin, python 2.7.11-final-0 ----------
Name                                       Stmts   Miss  Cover   Missing
------------------------------------------------------------------------
learning_journal/__init__.py                   8      0   100%
learning_journal/models/__init__.py           22      0   100%
learning_journal/models/meta.py                5      0   100%
learning_journal/models/mymodel.py             9      0   100%
learning_journal/routes.py                     6      0   100%
learning_journal/scripts/__init__.py           0      0   100%
learning_journal/scripts/initializedb.py      30     18    40%   83-86, 90-113
learning_journal/views/__init__.py             0      0   100%
learning_journal/views/default.py             40      6    85%   20-21, 30-31, 47, 63
learning_journal/views/notfound.py             4      2    50%   6-7
------------------------------------------------------------------------
TOTAL                                        124     26    79%


---------- coverage: platform darwin, python 3.5.2-final-0 -----------
Name                                       Stmts   Miss  Cover   Missing
------------------------------------------------------------------------
learning_journal/__init__.py                   8      0   100%
learning_journal/models/__init__.py           22      0   100%
learning_journal/models/meta.py                5      0   100%
learning_journal/models/mymodel.py             9      0   100%
learning_journal/routes.py                     6      0   100%
learning_journal/scripts/__init__.py           0      0   100%
learning_journal/scripts/initializedb.py      30     18    40%   83-86, 90-113
learning_journal/views/__init__.py             0      0   100%
learning_journal/views/default.py             40      6    85%   20-21, 30-31, 47, 63
learning_journal/views/notfound.py             4      2    50%   6-7
------------------------------------------------------------------------
TOTAL                                        124     26    79%
========================================== 13 passed in 2.09 seconds
```

