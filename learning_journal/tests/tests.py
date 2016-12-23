"""Testing our journal app."""


import pytest
# import transaction

from pyramid import testing

from learning_journal.models import MyModel, get_tm_session
from learning_journal.models.meta import Base
from learning_journal.scripts.initializedb import ENTRIES
import datetime

MODEL_ENTRIES = [MyModel(
    title=i['title'],
    body=i['body'],
    creation_date=datetime.datetime.strptime(i['creation_date'], '%b %d, %Y')
) for i in ENTRIES]


@pytest.fixture(scope="session")
def configuration(request):
    """Set up a Configurator instance."""
    settings = {'sqlalchemy.url': 'sqlite:///:memory:'}
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
            creation_date=datetime.datetime.strptime(entry['creation_date'], '%b %d, %Y')
        )

        dummy_request.dbsession.add(row)


# ======== UNIT TESTS ==========

def test_new_expenses_are_added(db_session):
    """New entries get added to the database."""
    db_session.add_all(MODEL_ENTRIES)
    query = db_session.query(MyModel).all()
    assert len(query) == len(MODEL_ENTRIES)


def test_list_view_returns_length_with_entries(dummy_request, add_models):
    """Test that the home page returns no objects in the iterable."""
    from learning_journal.views.default import home_page
    result = home_page(dummy_request)
    assert len(result['entries']) == 4


# from pyramid import testing
# import pytest


# @pytest.fixture
# def req():
#     """Fixture for a dummy request."""
#     the_request = testing.DummyRequest()
#     return the_request


# @pytest.fixture()
# def testapp():
#     """Create an instance of our app for testing."""
#     from ..scripts.initializedb import main
#     app = main({})
#     from webtest import TestApp
#     return TestApp(app)


# def test_home_view(req):
#     """Test that the home page returns what we expect."""
#     from ..views.default import home_page
#     info = home_page(req)
#     assert "entries" in info


# # functional testing here

# def test_layout_root(testapp):
#     """Test that the contents of the root page contains <article>."""
#     response = testapp.get('/', status=200)
#     html = response.html
#     assert "Claire's Learning Journal ~ Python 401" in html.find("footer").text


# def test_root_contents(testapp):
#     """Test that home contains as many <article> tags as journal entries."""
#     from ..scripts.initializedb import ENTRIES
#     response = testapp.get('/', status=200)
#     html = response.html
#     assert len(ENTRIES) == len(html.findAll("article"))


# def test_new_layout(testapp):
#     """Test that the contents of the root page contains <article>."""
#     response = testapp.get('/journal/new-entry', status=200)
#     html = response.html
#     assert "Title" in html.find("h2").text


# def test_detail_view():
#     """Test that the detail page contains 'title'."""
#     from .views import detail_page
#     request = testing.DummyRequest()
#     info = detail_page(request)
#     assert "title" in info
