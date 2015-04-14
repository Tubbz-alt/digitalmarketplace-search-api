from __future__ import absolute_import

import os
import json

from app import create_app


class WSGIApplicationWithEnvironment(object):
    def __init__(self, app, **kwargs):
        self.app = app
        self.kwargs = kwargs

    def __call__(self, environ, start_response):
        for key, value in self.kwargs.items():
            environ[key] = value
        return self.app(environ, start_response)


class BaseApplicationTest(object):

    def setup(self):
        self.app = create_app('test')
        self.client = self.app.test_client()
        self.default_index_name = "index-to-create"

        self.setup_authorization()

    def setup_authorization(self):
        """Set up bearer token and pass on all requests"""
        valid_token = 'valid-token'
        self.app.wsgi_app = WSGIApplicationWithEnvironment(
            self.app.wsgi_app,
            HTTP_AUTHORIZATION='Bearer {}'.format(valid_token))
        self._auth_tokens = os.environ.get('DM_SEARCH_API_AUTH_TOKENS')
        os.environ['DM_SEARCH_API_AUTH_TOKENS'] = valid_token

    def do_not_provide_access_token(self):
        self.app.wsgi_app = self.app.wsgi_app.app

    def teardown(self):
        self.teardown_authorization()
        self.client.delete('/' + self.default_index_name)

    def teardown_authorization(self):
        if self._auth_tokens is None:
            del os.environ['DM_SEARCH_API_AUTH_TOKENS']
        else:
            os.environ['DM_SEARCH_API_AUTH_TOKENS'] = self._auth_tokens


def get_json_from_response(response):
    return json.loads(response.get_data())
