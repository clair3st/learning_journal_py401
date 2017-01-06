"""Views for learning journal web page."""

from pyramid.response import Response
from pyramid.view import view_config

from ..models import MyModel
import datetime
from pyramid.httpexceptions import HTTPFound


@view_config(route_name='home', renderer='../templates/list.jinja2')
def home_page(request):
    """View for home page."""
    query = request.dbsession.query(MyModel)
    all_entries = query.all()
    return {'entries': all_entries}


@view_config(route_name='detail', renderer='../templates/detail.jinja2')
def detail_page(request):
    """One entry for detail veiw."""
    data = request.dbsession.query(MyModel).get(request.matchdict['id'])
    if data is None:
        return Response("Not Found", content_type='text/plain', status=404)
    return {'entries': data}


@view_config(route_name='edit', renderer='../templates/edit.jinja2')
def edit_page(request):
    """Edit page for one entry."""
    data = request.dbsession.query(MyModel).get(request.matchdict['id'])
    if request.method == "POST":

        data.title = request.POST["title"]
        data.body = request.POST["body"]
        request.dbsession.flush()
        return HTTPFound(location=request.route_url('home'))
    return {'entries': data}


@view_config(route_name='new', renderer='../templates/new.jinja2')
def new_entry(request):
    """View the new entry page."""
    if request.method == "POST":
        new_model = MyModel(title=request.POST['title'],
                            body=request.POST['body'],
                            creation_date=datetime.date.today()
                            )
        request.dbsession.add(new_model)
        return HTTPFound(location=request.route_url('home'))
    return {}
