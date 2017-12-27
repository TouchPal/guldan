from app import app, init


def create_wsgi_app():
    init()
    return app

uwsgi_app = create_wsgi_app()
