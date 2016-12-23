"""Views for learning journal web page."""

from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

from ..models import MyModel
import datetime
from pyramid.httpexceptions import HTTPFound


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
        data = request.dbsession.query(MyModel).get(request.matchdict['id'])
        return {'entries': data}
    except DBAPIError:
        return Response(db_err_msg, content_type='text/plain', status=500)


@view_config(route_name='edit', renderer='../templates/edit.jinja2')
def edit_page(request):
    """Edit page for one entry."""
    try:
        data = request.dbsession.query(MyModel).get(request.matchdict['id'])
        if request.method == "POST":

            data.title = request.POST["title"]
            data.body = request.POST["body"]
            request.dbsession.flush()
            return HTTPFound(location=request.route_url('home'))
        return {'entries': data}
    except DBAPIError:
        return Response(db_err_msg, content_type='text/plain', status=500)


@view_config(route_name='new', renderer='../templates/new.jinja2')
def new_entry(request):
    """View the new entry page."""
    try:
        if request.method == "POST":
            new_model = MyModel(title=request.POST['title'],
                                body=request.POST['body'],
                                creation_date=datetime.date.today()
                                )
            request.dbsession.add(new_model)
            return HTTPFound(location=request.route_url('home'))
        return {}
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
