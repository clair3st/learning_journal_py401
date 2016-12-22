"""Testing our journal app."""

from pyramid import testing
import pytest


@pytest.fixture
def req():
    """Fixture for a dummy request."""
    the_request = testing.DummyRequest()
    return the_request


@pytest.fixture()
def testapp():
    """Create an instance of our app for testing."""
    from learning_journal_basic import main
    app = main({})
    from webtest import TestApp
    return TestApp(app)


def test_home_view(req):
    """Test that the home page returns what we expect."""
    from .views import home_page
    info = home_page(req)
    assert "entries" in info


# functional testing here

def test_layout_root(testapp):
    """Test that the contents of the root page contains <article>."""
    response = testapp.get('/', status=200)
    html = response.html
    assert "Claire's Learning Journal ~ Python 401" in html.find("footer").text


def test_root_contents(testapp):
    """Test that home contains as many <article> tags as journal entries."""
    from .views import ENTRIES
    response = testapp.get('/', status=200)
    html = response.html
    assert len(ENTRIES) == len(html.findAll("article"))


def test_new_layout(testapp):
    """Test that the contents of the root page contains <article>."""
    response = testapp.get('/journal/new-entry', status=200)
    html = response.html
    assert "Title" in html.find("h2").text


# def test_detail_view():
#     """Test that the detail page contains 'title'."""
#     from .views import detail_page
#     request = testing.DummyRequest()
#     info = detail_page(request)
#     assert "title" in info



# import unittest
# import transaction

# from pyramid import testing


# def dummy_request(dbsession):
#     return testing.DummyRequest(dbsession=dbsession)


# class BaseTest(unittest.TestCase):
#     def setUp(self):
#         self.config = testing.setUp(settings={
#             'sqlalchemy.url': 'sqlite:///:memory:'
#         })
#         self.config.include('.models')
#         settings = self.config.get_settings()

#         from .models import (
#             get_engine,
#             get_session_factory,
#             get_tm_session,
#             )

#         self.engine = get_engine(settings)
#         session_factory = get_session_factory(self.engine)

#         self.session = get_tm_session(session_factory, transaction.manager)

#     def init_database(self):
#         from .models.meta import Base
#         Base.metadata.create_all(self.engine)

#     def tearDown(self):
#         from .models.meta import Base

#         testing.tearDown()
#         transaction.abort()
#         Base.metadata.drop_all(self.engine)


# class TestMyViewSuccessCondition(BaseTest):

#     def setUp(self):
#         super(TestMyViewSuccessCondition, self).setUp()
#         self.init_database()

#         from .models import MyModel

#         model = MyModel(name='one', value=55)
#         self.session.add(model)

#     def test_passing_view(self):
#         from .views.default import my_view
#         info = my_view(dummy_request(self.session))
#         self.assertEqual(info['one'].name, 'one')
#         self.assertEqual(info['project'], 'learning_journal')


# class TestMyViewFailureCondition(BaseTest):

#     def test_failing_view(self):
#         from .views.default import my_view
#         info = my_view(dummy_request(self.session))
#         self.assertEqual(info.status_int, 500)
