"""Testing our journal app."""

from pyramid.config import Configurator

import pytest
import transaction

from pyramid import testing

from learning_journal.models import MyModel, get_tm_session
from learning_journal.models.meta import Base
from learning_journal.scripts.initializedb import ENTRIES
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
    config.include('learning_journal.models')

    def teardown():
        testing.tearDown()

    request.addfinalizer(teardown)
    return config


@pytest.fixture()
def db_session(configuration, request):
    """Create a session for interacting with the test database."""
    SessionFactory = configuration.registry['dbsession_factory']
    session = SessionFactory()
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
    from learning_journal.views.default import home_page
    result = home_page(dummy_request)
    assert len(result['entries']) == 4


# ======== FUNCTIONAL TESTS ===========

@pytest.fixture
def testapp():
    """Create a test db for functional tests."""
    from webtest import TestApp
    # from learning_journal import main

    def main(global_config, **settings):
        """The function returns a Pyramid WSGI application."""
        config = Configurator(settings=settings)
        config.include('pyramid_jinja2')
        config.include('learning_journal.models')
        config.include('learning_journal.routes')
        config.scan()
        return config.make_wsgi_app()

    app = main({}, **{
        'sqlalchemy.url': 'postgres://clairegatenby@localhost:5432/test_lj'
    })
    testapp = TestApp(app)

    SessionFactory = app.registry["dbsession_factory"]
    engine = SessionFactory().bind
    Base.metadata.create_all(bind=engine)

    return testapp


@pytest.fixture
def fill_the_db(testapp):
    """Test fixture for a full db."""
    SessionFactory = testapp.app.registry["dbsession_factory"]
    with transaction.manager:
        dbsession = get_tm_session(SessionFactory, transaction.manager)
        dbsession.add_all(MODEL_ENTRIES)


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
