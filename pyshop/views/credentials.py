# -*- coding: utf-8 -*-
import logging

from pyramid.httpexceptions import HTTPFound, HTTPForbidden
from pyramid.url import resource_url, route_url
from pyramid.security import authenticated_userid, remember, forget
from pyramid.response import Response

from pyshop.helpers.i18n import trans as _
from pyshop.models import DBSession, User, AuthorizedIP

from .base import View


log = logging.getLogger(__name__)


class Login(View):

    def render(self, request, session):

        login_url = resource_url(request.context, request, 'login')
        referrer = request.url
        # never use the login form itself as came_from
        if referrer == login_url:
            referrer = '/'
        came_from = request.params.get('came_from', referrer)

        login = request.params.get('user.login', '')
        if 'form.submitted' in request.params:
            password = request.params.get('user.password', u'')
            if password and \
            User.by_credentials(session, login, password) is not None:
                log.info('login %r succeed' % login)
                headers = remember(request, login)
                return HTTPFound(location=came_from,
                                 headers=headers)

        return {'came_from': came_from,
                'user': User(login=login),
                }

class Logout(View):

    def render(self, request, session):

        return HTTPFound(location=route_url('index', request),
                         headers=forget(request))


def authbasic(request):
    """
    Authentification basic, Upload pyshop repository access
    """
    if len(request.environ.get('HTTP_AUTHORIZATION','')) > 0:
        auth = request.environ.get('HTTP_AUTHORIZATION')
        scheme, data = auth.split(None, 1)
        assert scheme.lower() == 'basic'
        username, password = data.decode('base64').split(':', 1)
        if User.by_credentials(DBSession(), username, password):
            headers = remember(request, username)
            return HTTPFound(location=route_url('repository', request,
                             file_id=request.matchdict['file_id'],
                             filename=request.matchdict['filename']))
    return Response(status=401,
                    headerlist=[('WWW-Authenticate', 
                                 'Basic realm="pyshop repository access"',)],
                    )