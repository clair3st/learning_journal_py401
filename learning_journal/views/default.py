"""Views for learning journal web page."""

from pyramid.response import Response
from pyramid.view import view_config

from ..models import MyModel
import datetime
from pyramid.httpexceptions import HTTPFound
from learning_journal.security import check_credentials
from pyramid.security import remember, forget

import json


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


@view_config(route_name='edit',
             renderer='../templates/edit.jinja2',
             permission='add')
def edit_page(request):
    """Edit page for one entry."""
    data = request.dbsession.query(MyModel).get(request.matchdict['id'])
    if request.method == "POST":

        data.title = request.POST["title"]
        data.body = request.POST["body"]
        request.dbsession.flush()
        return HTTPFound(location=request.route_url('home'))
    return {'entries': data}


@view_config(route_name='new',
             renderer='../templates/new.jinja2',
             permission='add')
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


@view_config(route_name='post_by_title', renderer='json')
def entry_title(request):
    """Get and entry by the title from the db."""
    try:
        title = request.matchdict['title']
        entry = request.dbsession.query(MyModel).filter_by(title=title).first()
        return json.dumps({"title": entry.title, "id": entry.id})
    except AttributeError:
        return {}


@view_config(route_name='login',
             renderer='../templates/login.jinja2',
             require_csrf=False)
def login_view(request):
    """Login page for user authentication."""
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']
        if check_credentials(username, password):
            auth_head = remember(request, username)
            return HTTPFound(location=request.route_url('home'),
                             headers=auth_head)
        else:
            return {'login': 'failed'}
    return {}


@view_config(route_name='logout')
def logout_view(request):
    """Logout return to home."""
    auth_head = forget(request)
    return HTTPFound(location=request.route_url('home'), headers=auth_head)


@view_config(route_name="delete", permission="add")
def delete_view(request):
    """To delete individual items."""
    entry = request.dbsession.query(MyModel).get(request.matchdict["id"])
    request.dbsession.delete(entry)
    return HTTPFound(request.route_url("home"))


@view_config(route_name="api_list", renderer="string")
def api_list_view(request):
    """Return API list of journal entries."""
    entries = request.dbsession.query(MyModel).all()
    json_data = [entry.to_json() for entry in entries]
    return json_data
