"""Views for learning journal web page."""

from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

from ..models import MyModel
from datetime import datetime
import os

HERE = os.path.dirname(__file__)


@view_config(route_name='home', renderer='../templates/list.jinja2')
def home_page(request):
    """View for home page."""
    try:
        query = request.dbsession.query(MyModel)
        all_entries = query.all()
        return {'entries': all_entries}
    except DBAPIError:
        return Response(db_err_msg, content_type='text/plain', status=500)


@view_config(route_name='detail', renderer='../templates/detail.jinja2')
def detail_page(request):
    """One entry for detail veiw."""
    try:
        query = request.dbsession.query(MyModel)
        data = query.filter_by(id=request.matchdict['id']).one()
        return {'entries': data}
    except DBAPIError:
        return Response(db_err_msg, content_type='text/plain', status=500)


@view_config(route_name='edit', renderer='../templates/edit.jinja2')
def edit_page(request):
    """Edit page for one entry."""
    try:
        query = request.dbsession.query(MyModel)
        data = query.filter_by(id=request.matchdict['id']).one()
        # if request.method == "POST":

        #     new_title = request.POST["title"]
        #     new_body = request.POST["body"]
        #     new_model = MyModel(title=new_title, value=new_body)

        #     request.dbsession.add(new_model)
        return {'entries': data}
    except DBAPIError:
        return Response(db_err_msg, content_type='text/plain', status=500)


@view_config(route_name='new', renderer='../templates/new.jinja2')
def new_entry(request):
    """View the new entry page."""
    try:
        query = request.dbsession.query(MyModel)
        all_entries = query.all()
        if request.method == "POST":
            date = datetime.now()
            new_model = MyModel(title=request.POST['title'],
                                body=request.POST['body'],
                                creation_date="{}/{}/{}".format(date.month, date.day, date.year)
                                )
            request.dbsession.add(new_model)
        return {'entries': all_entries}
    except DBAPIError:
        return Response(db_err_msg, content_type='text/plain', status=500)



db_err_msg = """\
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to run the "initialize_learning_journal_db" script
    to initialize your database tables.  Check your virtual
    environment's "bin" directory for this script and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.

After you fix the problem, please restart the Pyramid application to
try it again.
"""
