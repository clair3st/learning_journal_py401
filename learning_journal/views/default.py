from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

from ..models import MyModel
import os

HERE = os.path.dirname(__file__)


@view_config(route_name='home', renderer='../templates/list.jinja2')
def my_view(request):
    """View for home page."""
    try:
        query = request.dbsession.query(MyModel)
        all_entries = query.all()
    except DBAPIError:
        return Response(db_err_msg, content_type='text/plain', status=500)
    return {'entries': all_entries}


@view_config(route_name='detail', renderer='../templates/detail.jinja2')
def detail(request):
    """Send individual entry for detail view."""
    query = request.dbsession.query(MyModel)
    data = query.filter_by(id=request.matchdict['id']).one()
    return {'entries': data}






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
