from pyramid.config import Configurator
from sqlalchemy import engine_from_config

# from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authentication import SessionAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

from beaker.session import CookieSession

from lazyvore.security import groupfinder

from .models import (
    DBSession,
    Base,
    )

from os.path import expandvars


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    db_url = expandvars(settings.get('sqlalchemy.url'))
    engine = engine_from_config(settings, 'sqlalchemy.', url=db_url)
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    authn_policy = AuthTktAuthenticationPolicy(
            'sosecret', callback=groupfinder, hashalg='sha512')
    authn_policy = SessionAuthenticationPolicy()
    authz_policy = ACLAuthorizationPolicy()
    session_factory = CookieSession()
    config = Configurator(settings=settings,
                          root_factory='lazyvore.models.RootFactory')
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)
    config.set_session_factory(session_factory)
    config.include('pyramid_chameleon')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_static_view('static_deform', 'deform:static')
    config.add_route('view_wiki', '/')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('signup', '/signup')
    config.add_route('view_page', '/{pagename}')
    config.add_route('add_page', '/add_page/{pagename}')
    config.add_route('edit_page', '/{pagename}/edit_page')
    config.scan()
    return config.make_wsgi_app()
