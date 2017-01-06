"""Testing our journal app."""

from pyramid.config import Configurator

import pytest
import transaction

from pyramid import testing

from learning_journal.models import MyModel, get_tm_session
from learning_journal.models.meta import Base
from learning_journal.scripts.initializedb import ENTRIES
import datetime

from pyramid.httpexceptions import HTTPFound

MODEL_ENTRIES = [MyModel(
    title=entry['title'],
    body=entry['body'],
    creation_date=datetime.datetime.strptime(
        entry['creation_date'], '%b %d, %Y'
    )
) for entry in ENTRIES]


@pytest.fixture(scope="session")
def configuration(request):
    """Set up a Configurator instance."""
    settings = {
        'sqlalchemy.url': 'postgres://clairegatenby@localhost:5432/test_lj'
    }
    config = testing.setUp(settings=settings)
    config.include('learning_journal.models')
    config.include('learning_journal.routes')

    def teardown():
        testing.tearDown()

    request.addfinalizer(teardown)
    return config


@pytest.fixture
def db_session(configuration, request):
    """Create a session for interacting with the test database."""
    session_factory = configuration.registry['dbsession_factory']
    session = session_factory()
    engine = session.bind
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    def teardown():
        session.transaction.rollback()

    request.addfinalizer(teardown)
    return session


@pytest.fixture
def dummy_request(db_session):
    """Instantiate a fake HTTP Request, complete with a database session."""
    return testing.DummyRequest(dbsession=db_session)


@pytest.fixture
def add_models(dummy_request):
    """Add a bunch of model instances to the database."""
    for entry in ENTRIES:
        row = MyModel(
            title=entry['title'],
            body=entry['body'],
            creation_date=datetime.datetime.strptime(entry['creation_date'],
                                                     '%b %d, %Y')
        )

        dummy_request.dbsession.add(row)


@pytest.fixture
def set_auth_credentials():
    """Make a username/password combo for testing."""
    import os
    from passlib.apps import custom_app_context as pwd_context

    os.environ["AUTH_USERNAME"] = "testme"
    os.environ["AUTH_PASSWORD"] = pwd_context.hash("foobar")


# ======== UNIT TESTS ==========
def test_list_view_returns_no_length_without_entries(dummy_request):
    """Test that the home page returns no objects in the iterable."""
    from learning_journal.views.default import home_page
    result = home_page(dummy_request)
    assert len(result['entries']) == 0


def test_list_view_returns_length_with_entries(dummy_request, add_models):
    """Test that the home page returns no objects in the iterable."""
    from learning_journal.views.default import home_page
    result = home_page(dummy_request)
    assert len(result['entries']) == 4


def test_new_entries_view_returns_empty(dummy_request):
    """Assert create view withou post returns an empty dict."""
    from learning_journal.views.default import new_entry
    assert new_entry(dummy_request) == {}


def test_new_entries_are_added(db_session):
    """New entries get added to the database."""
    db_session.add_all(MODEL_ENTRIES)
    query = db_session.query(MyModel).all()
    assert len(query) == len(MODEL_ENTRIES)


def test_new_entry_returns_empty_dict(dummy_request):
    """When I send a simple get request to new entry, I get emptiness."""
    from learning_journal.views.default import new_entry
    assert new_entry(dummy_request) == {}


def test_new_entry_creates_new(db_session, dummy_request):
    """Test when new entry is create the db is updated."""
    from learning_journal.views.default import new_entry

    dummy_request.method = "POST"
    dummy_request.POST["title"] = "Learning Journal Title"
    dummy_request.POST["body"] = "So many things learned today."

    new_entry(dummy_request)

    query = db_session.query(MyModel).all()
    assert query[0].title == "Learning Journal Title"
    assert query[0].body == "So many things learned today."


def test_detail_view_for_nonexistent_entry_is_not_found(dummy_request):
    """When I provide an id that doesn't exist, it should error."""
    from learning_journal.views.default import detail_page
    dummy_request.matchdict["id"] = "1234"
    result = detail_page(dummy_request)
    assert result.status_code == 404


def test_detail_view_returns_entry(db_session, dummy_request, add_models):
    """Test detail view returns entry."""
    from learning_journal.views.default import detail_page
    dummy_request.matchdict['id'] = 1
    detail_page(dummy_request)
    query = db_session.query(MyModel).all()
    assert query[0].title == 'Day 11'


def test_make_new_entry_then_edit(db_session, dummy_request):
    """Test make new entry and edit page updates the db."""
    from learning_journal.views.default import edit_page
    from learning_journal.views.default import new_entry

    dummy_request.method = "POST"
    dummy_request.POST["title"] = "Learning Journal Title"
    dummy_request.POST["body"] = "So many things learned today."

    new_entry(dummy_request)

    dummy_request.method = "POST"
    dummy_request.POST["title"] = "New Learning Journal Title"
    dummy_request.POST["body"] = "So many NEW things learned today."
    dummy_request.matchdict['id'] = 1

    edit_page(dummy_request)

    query = db_session.query(MyModel).all()
    assert query[0].title == "New Learning Journal Title"
    assert query[0].body == "So many NEW things learned today."


def test_edit_entry_edits_db(db_session, dummy_request, add_models):
    """Test when edit entry it updates db."""
    from learning_journal.views.default import edit_page

    dummy_request.method = "POST"
    dummy_request.POST["title"] = "New Learning Journal Title"
    dummy_request.POST["body"] = "So many NEW things learned today."
    dummy_request.matchdict['id'] = 1

    edit_page(dummy_request)
    query = dummy_request.dbsession.query(MyModel).get(1)

    assert query.title == "New Learning Journal Title"
    assert query.body == "So many NEW things learned today."


def test_check_credentials_passes_good_creds(set_auth_credentials):
    """Test check_credentials returns True when correct entries."""
    from learning_journal.security import check_credentials
    assert check_credentials("testme", "foobar")


def test_check_credentials_fails_bad_pass(set_auth_credentials):
    """Test check_credentials returns False when bad password."""
    from learning_journal.security import check_credentials
    assert not check_credentials("testme", "bad pass")


def test_check_credentials_fails_bad_user(set_auth_credentials):
    """Test check_credentials returns False when bad username."""
    from learning_journal.security import check_credentials
    assert not check_credentials("bad username", "foobar")


def test_check_credentials_fails_empty_creds(set_auth_credentials):
    """Test check_credentials returns False when nothing entered."""
    from learning_journal.security import check_credentials
    assert not check_credentials("", "")


def test_get_login_view_is_empty_dict(dummy_request):
    """Assert empty dict is returned, from Get request."""
    from learning_journal.views.default import login_view
    assert login_view(dummy_request) == {}


def test_post_login_view_is_http_found(dummy_request, set_auth_credentials):
    """Assert is instance of HTTP found, from POST request."""
    from learning_journal.views.default import login_view

    dummy_request.method = "POST"
    dummy_request.POST["username"] = "testme"
    dummy_request.POST["password"] = "foobar"

    result = login_view(dummy_request)

    assert isinstance(result, HTTPFound)


# ======== FUNCTIONAL TESTS ===========

@pytest.fixture
def testapp(request):
    """Create a test db for functional tests."""
    from webtest import TestApp

    def main(global_config, **settings):
        """The function returns a Pyramid WSGI application."""
        config = Configurator(settings=settings)
        config.include('pyramid_jinja2')
        config.include('.models')
        config.include('.routes')
        config.include('.security')
        config.scan()
        return config.make_wsgi_app()

    app = main({}, **{
        'sqlalchemy.url': 'postgres://clairegatenby@localhost:5432/test_lj'
    })
    testapp = TestApp(app)

    session_factory = app.registry["dbsession_factory"]
    engine = session_factory().bind
    Base.metadata.create_all(bind=engine)

    def tear_down():
        Base.metadata.drop_all(bind=engine)

    request.addfinalizer(tear_down)
    return testapp


@pytest.fixture
def fill_the_db(testapp):
    """Test fixture for a full db."""
    session_factory = testapp.app.registry["dbsession_factory"]
    with transaction.manager:
        dbsession = get_tm_session(session_factory, transaction.manager)
        for entry in ENTRIES:
            row = MyModel(
                title=entry['title'],
                body=entry['body'],
                creation_date=datetime.datetime.strptime(
                    entry['creation_date'], '%b %d, %Y'
                )
            )

            dbsession.add(row)

    return dbsession


@pytest.fixture
def login_testcase(testapp, set_auth_credentials):
    """Test that logging redirects."""
    response = testapp.post(
        '/journal/login',
        params={'username': 'testme', 'password': 'foobar'}
    )
    headers = response.headers
    return headers


def test_home_route_has_no_article_when_db_empty(testapp):
    """The home page has no articles."""
    response = testapp.get('/', status=200)
    html = response.html
    assert len(html.find_all('article')) == 0


def test_home_route_with_data_has_articles(testapp, fill_the_db):
    """When there's data in the database, the home page has articles."""
    response = testapp.get('/', status=200)
    html = response.html
    assert len(html.find_all("article")) == len(ENTRIES)


def test_new_entry_route_has_form(testapp, login_testcase):
    """The new entry page has no form."""
    response = testapp.get('/journal/new-entry', status=200)
    html = response.html
    assert len(html.find_all('form')) == 1


def test_detail_route_has_no_information(testapp):
    """Test when no data there is a 404 error."""
    response = testapp.get("/journal/1", status=404)
    assert response.status_code == 404


def test_detail_route_raises_404_for_incorrect_id(testapp):
    """Test when id that doesn't exist, 404 response."""
    response = testapp.get("/journal/12345", status=404)
    assert response.status_code == 404


def test_detail_page_loads_correct_entry(testapp, fill_the_db):
    """Test that the detail route loads the proper entry."""
    response = testapp.get('/journal/1', status=200)
    title = response.html.find_all(class_='entrytitle')[0].contents[0]
    assert title == ENTRIES[0]['title']


def test_new_entry_view_post_redirects(testapp,
                                       set_auth_credentials,
                                       login_testcase):
    """Test that a post request redirects to home.

    reference:
    http://stackoverflow.com/questions/10773404/how-to-follow-pyramid-redirect-on-tests
    """
    response = testapp.get("/journal/new-entry")
    csrf_token = response.html.find("input", {"name": "csrf_token"})
    csrf_token = csrf_token.attrs['value']

    post_params = {
        'title': 'Learning Journal Title',
        'body': 'So many things learned today.',
        'csrf_token': csrf_token
    }

    response = testapp.post('/journal/new-entry', post_params, status=302)
    full_response = response.follow()

    assert len(full_response.html.find_all(id="journal-entry")) == 1


def test_new_entry_adds_to_list(testapp, login_testcase):
    """Test that new entry page adds to the list view."""
    response = testapp.get("/journal/new-entry")
    csrf_token = response.html.find("input", {"name": "csrf_token"})
    csrf_token = csrf_token.attrs['value']

    post_params = {
        'title': 'Learning Journal Title',
        'body': 'So many things learned today.',
        'csrf_token': csrf_token
    }

    response = testapp.post('/journal/new-entry', post_params, status=302)
    full_response = response.follow()
    new_title = full_response.html.find(id='journal-entry').a.text
    assert new_title == post_params['title']


def test_edit_page_redirects_to_home(testapp, fill_the_db, login_testcase):
    """Test the edit page redirects to home after submit."""
    response = testapp.get("/journal/1/edit-entry")
    csrf_token = response.html.find("input", {"name": "csrf_token"})
    csrf_token = csrf_token.attrs['value']

    post_params = {
        'id': 1,
        'title': 'Learning Journal Title',
        'body': 'So many things learned today.',
        'csrf_token': csrf_token
    }

    response = testapp.post('/journal/1/edit-entry', post_params, status=302)
    full_response = response.follow()

    new_title = full_response.html.find_all(class_='entrytitle')[-1].text[1:-1]
    assert new_title == post_params['title']


# def test_new_entry_is_in_db(testapp, fill_the_db, login_testcase):
#     """Test that new entry page adds to the list view."""
#     response = testapp.get("/journal/new-entry")
#     csrf_token = response.html.find("input", {"name": "csrf_token"})
#     csrf_token = csrf_token.attrs['value']

#     post_params = {
#         'title': 'Learning Journal Title',
#         'body': 'So many things learned today.',
#         'csrf_token': csrf_token
#     }

#     response = testapp.post('/journal/new-entry', post_params, status=302)

#     query = fill_the_db.query(MyModel).all()
#     assert query[-1].title == post_params['title']


def test_edit_has_populated_form(testapp, fill_the_db, login_testcase):
    """Test edit page has a pre-populated form."""
    response = testapp.get('/journal/1/edit-entry', status=200)
    title = response.html.find_all('input')[1]['value']
    body = response.html.form.textarea.contents[0]

    assert title == ENTRIES[0]['title']
    assert body == ENTRIES[0]['body']


# def test_edited_is_in_db(testapp, fill_the_db, login_testcase):
#     """Test that edited entry is in the db."""
#     response = testapp.get("/journal/1/edit-entry")
#     csrf_token = response.html.find("input", {"name": "csrf_token"})
#     csrf_token = csrf_token.attrs['value']

#     post_params = {
#         'title': 'Learning Journal Title',
#         'body': 'So many things learned today.',
#         'csrf_token': csrf_token
#     }

#     testapp.post('/journal/1/edit-entry', post_params, status=302)
#     query = fill_the_db.query(MyModel).all()
#     assert query[0].title == post_params['title']


# def test_detail_view_only_has_one_article(testapp, fill_the_db):
#     """Test detail view only has one article."""
#     response = testapp.get("/journal/1")
#     num_items = fill_the_db.query(MyModel).filter_by(id=1).count()

#     html = response.html
#     article = html.find_all("article")
#     assert len(article) == num_items
