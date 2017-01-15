"""Route to configure for pyramid app."""


def includeme(config):
    """Include routes."""
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('new', '/journal/new-entry')
    config.add_route('detail', '/journal/{id:\d+}')
    config.add_route('edit', '/journal/{id:\d+}/edit-entry')
    config.add_route('login', '/journal/login')
    config.add_route('logout', '/journal/logout')
    config.add_route('post_by_title', '/journal/{title:[\w\s]+}')
    config.add_route('delete', '/delete/{id:\d+}')
    config.add_route('api_list', '/api/entries')
