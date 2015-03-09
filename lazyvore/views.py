import cgi
import re
from docutils.core import publish_parts

import colander

from deform import (
        Form,
        ValidationFailure,
        )

from pyramid.httpexceptions import (
        HTTPFound,
        HTTPNotFound,
        )

from pyramid.view import (
        view_config,
        forbidden_view_config,
        )

from pyramid.renderers import render

from .models import (
    DBSession,
    Page,
    User,
    )

from colanderalchemy import SQLAlchemySchemaNode

from pyramid.security import (
        remember,
        forget,
        )

from .security import USERS

# regular expression used to find WikiWords
wikiwords = re.compile(r"\b([A-Z]\w+[A-Z]+\w+)")

@view_config(route_name='view_wiki', permission='view')
def view_wiki(request):
    return HTTPFound(location = request.route_url('view_page',
                                                  pagename='FrontPage'))

@view_config(route_name='view_page', renderer='templates/view.pt',
             permission='view')
def view_page(request):
    pagename = request.matchdict['pagename']
    page = DBSession.query(Page).filter_by(name=pagename).first()
    if page is None:
        return HTTPNotFound('No such page')

    def check(match):
        word = match.group(1)
        exists = DBSession.query(Page).filter_by(name=word).all()
        if exists:
            view_url = request.route_url('view_page', pagename=word)
            return '<a href="%s">%s</a>' % (view_url, cgi.escape(word))
        else:
            add_url = request.route_url('add_page', pagename=word)
            return '<a href="%s">%s</a>' % (add_url, cgi.escape(word))

    content = publish_parts(page.data, writer_name='html')['html_body']
    content = wikiwords.sub(check, content)
    edit_url = request.route_url('edit_page', pagename=pagename)

    login_form = login_form_view(request)

    return dict(
            page=page,
            content=content,
            edit_url=edit_url,
            login_form = login_form,
            )

@view_config(route_name='add_page', renderer='templates/edit.pt',
             permission='edit')
def add_page(request):
    pagename = request.matchdict['pagename']
    if 'form.submitted' in request.params:
        body = request.params['body']
        page = Page(name=pagename, data=body)
        DBSession.add(page)
        return HTTPFound(location = request.route_url('view_page',
                                                      pagename=pagename))
    save_url = request.route_url('add_page', pagename=pagename)
    page = Page(name='', data='')

    login_form = login_form_view(request)

    return dict(
            page=page,
            save_url=save_url,
            login_form = login_form,
            )

@view_config(route_name='edit_page', renderer='templates/edit.pt',
             permission='edit')
def edit_page(request):
    pagename = request.matchdict['pagename']
    page = DBSession.query(Page).filter_by(name=pagename).one()
    if 'form.submitted' in request.params:
        page.data = request.params['body']
        DBSession.add(page)
        return HTTPFound(location = request.route_url('view_page',
                                                      pagename=pagename))

    login_form = login_form_view(request)

    return dict(
            page=page,
            save_url = request.route_url('edit_page', pagename=pagename),
            login_form = login_form,
            )


@view_config(route_name='login', renderer='templates/login.pt')
@forbidden_view_config(renderer='templates/login.pt')
def login(request):
    main_view = request.route_url('view_wiki')
    came_from = request.params.get('came_from', main_view)
    gplus_id = request.params['gplus_id']
    if gplus_id:
        if not User.get_by_gplus_id(gplus_id):
            user = User(gplus_id=gplus_id)
            DBSession.add(user)

        user_id = User.get_by_gplus_id(gplus_id).id
        headers = remember(request, user_id)
        request.session.flash('Logged in via GPlus')
        return HTTPFound(location = came_from,
                         headers = headers)

    if 'form.submitted' in request.params:
        login = request.params['login']
        password = request.params['password']

        if User.check_password(login, password):
            user_id = User.get_by_username(login).id
            headers = remember(request, user_id)
            request.session.flash('Logged in with password')
            return HTTPFound(location = came_from,
                             headers = headers)

    request.session.flash('Failed login')
    return HTTPFound(location = came_from)


@view_config(route_name='logout')
def logout(request):
    headers = forget(request)
    request.session.invalidate()
    request.session.flash('Logged out successfully')
    return HTTPFound(location = request.route_url('view_wiki'),
                     headers = headers)

def login_form_view(request):
    login_url = request.route_url('login')
    referrer = request.url
    if referrer == login_url:
        referrer = '/' # never use the login form itself as came_from
    came_from = request.params.get('came_from', referrer)
    response = dict(
            message = '',
            login = '',
            password = '',
            logged_in = request.authenticated_userid,
            url = request.route_url('login'),
            came_from = came_from,
            )
    return render('templates/login.pt', response, request)

schema = SQLAlchemySchemaNode(User,
                              includes=['username', '_password'],
                              )
signupForm = Form(schema, buttons=('submit',))

@view_config(route_name='signup', renderer='templates/signup.pt')
def signup(request):
    login_url = request.route_url('login')
    referrer = request.url
    if referrer == login_url:
        referrer = '/' # never use the login form itself as came_from
    came_from = request.params.get('came_from', referrer)
    message = 'test'
    
    if 'submit' in request.POST:
        controls = request.POST.items()

        try:
            appstruct = signupForm.validate(controls)
        except ValidationFailure as e:
            return dict(
                    form = e.render(),
                    came_from = came_from,
                    message = message,
                    css_links = signupForm.get_widget_resources()['css'],
                    js_links = signupForm.get_widget_resources()['js'],
                    )
        username = appstruct['username']
        password = appstruct['_password']
        if not User.get_by_username(username):
            user = User(username=username, password=password)
            DBSession.add(user)
            headers = remember(request, username)

            return HTTPFound(
                    location = request.route_url('view_wiki'),
                    headers = headers,
                    )
        message = 'The user "{}" already exists.'.format(username)

    return dict(
            message = message,
            url = request.application_url + '/signup',
            came_from = came_from,
            form = signupForm.render(),
            css_links = signupForm.get_widget_resources()['css'],
            js_links = signupForm.get_widget_resources()['js'],
            )
