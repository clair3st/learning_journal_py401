"""Testing our journal app."""

from pyramid.config import Configurator

import pytest
import transaction

from pyramid import testing

from .models import MyModel, get_tm_session
from .models.meta import Base
from .scripts.initializedb import ENTRIES
import datetime

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
    config.include('.models')

    def teardown():
        testing.tearDown()

    request.addfinalizer(teardown)
    return config


@pytest.fixture()
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


# ======== UNIT TESTS ==========

def test_new_entries_are_added(db_session):
    """New entries get added to the database."""
    db_session.add_all(MODEL_ENTRIES)
    query = db_session.query(MyModel).all()
    assert len(query) == len(MODEL_ENTRIES)


def test_list_view_returns_length_with_entries(dummy_request, add_models):
    """Test that the home page returns no objects in the iterable."""
    from .views.default import home_page
    result = home_page(dummy_request)
    assert len(result['entries']) == 4


# ======== FUNCTIONAL TESTS ===========

@pytest.fixture
def testapp():
    """Create a test db for functional tests."""
    from webtest import TestApp
    # from  import main

    def main(global_config, **settings):
        """The function returns a Pyramid WSGI application."""
        config = Configurator(settings=settings)
        config.include('pyramid_jinja2')
        config.include('.models')
        config.include('.routes')
        config.scan()
        return config.make_wsgi_app()

    app = main({}, **{
        'sqlalchemy.url': 'postgres://clairegatenby@localhost:5432/test_lj'
    })
    testapp = TestApp(app)

    session_factory = app.registry["dbsession_factory"]
    engine = session_factory().bind
    Base.metadata.create_all(bind=engine)

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
                creation_date=datetime.datetime.strptime(entry['creation_date'],
                                                         '%b %d, %Y')
            )

            dbsession.add(row)


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


def test_new_route_has_form(testapp):
    """The new entry page has no form."""
    response = testapp.get('/journal/new-entry', status=200)
    html = response.html
    assert len(html.find_all('form')) == 1


def test_detail_page_loads_correct_entry(testapp, fill_the_db):
    """Test that the detail route loads the proper entry."""
    response = testapp.get('/journal/1', status=200)
    title = response.html.find_all(class_='entrytitle')[0].contents[0]
    assert title == ENTRIES[0]['title']


def test_create_view_post_redirects(testapp):
    """Test that a post request redirects to home.

    reference:
    http://stackoverflow.com/questions/10773404/how-to-follow-pyramid-redirect-on-tests
    """
    post_params = {
        'title': 'Learning Journal Title',
        'body': 'So many things learned today.'
    }

    response = testapp.post('/journal/new-entry', post_params, status=302)
    full_response = response.follow()

    assert len(full_response.html.find_all(id="journal-entry")) == 1


def test_new_entry_adds_to_list(testapp):
    """Test that new entry page adds to the list view."""
    post_params = {
        'title': 'Learning Journal Title',
        'body': 'So many things learned today.'
    }

    response = testapp.post('/journal/new-entry', post_params, status=302)
    full_response = response.follow()
    assert full_response.html.find(id='journal-entry').a.text == post_params['title']


def test_edit_page_redirects_to_home(testapp, fill_the_db):
    """Test the edit page redirects to home after submit."""
    post_params = {
        'id': 1,
        'title': 'Learning Journal Title',
        'body': 'So many things learned today.'
    }
    response = testapp.post('/journal/1/edit-entry', post_params, status=302)
    full_response = response.follow()

    assert full_response.html.find_all(class_='entrytitle')[0].text[1:-1] == post_params['title']


def test_edit_has_populated_form(testapp, fill_the_db):
    """Test edit page has a pre-populated form."""
    response = testapp.get('/journal/1/edit-entry', status=200)
    title = response.html.form.input["value"]
    body = response.html.form.textarea.contents[0]
    print(body)
    assert title == ENTRIES[0]["title"]
    assert body == ENTRIES[0]["body"]
