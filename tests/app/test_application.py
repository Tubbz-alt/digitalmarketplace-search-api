"""
Tests for the application infrastructure
"""
import gzip

import mock
import pytest

from flask import json
from elasticsearch.exceptions import ConnectionError

from tests.helpers import BaseApplicationTest, BaseApplicationTestWithIndex


class TestApplication(BaseApplicationTest):
    def test_index(self):
        response = self.client.get('/')
        assert 200 == response.status_code
        assert 'links' in json.loads(response.get_data())

    def test_404(self):
        response = self.client.get('/index/type/search')
        assert 404 == response.status_code

    def test_bearer_token_is_required(self):
        self.do_not_provide_access_token()
        response = self.client.get('/')
        assert 401 == response.status_code
        assert 'WWW-Authenticate' in response.headers

    def test_invalid_bearer_token_is_required(self):
        self.do_not_provide_access_token()
        response = self.client.get(
            '/',
            headers={'Authorization': 'Bearer invalid-token'})
        assert 403 == response.status_code

    def test_ttl_is_not_set(self):
        response = self.client.get('/')
        assert response.cache_control.max_age is None

    @mock.patch('elasticsearch.transport.Urllib3HttpConnection.perform_request', side_effect=ConnectionError(500))
    def test_elastic_search_client_performs_retries_on_connection_error(self, perform_request):
        with pytest.raises(ConnectionError):
            self.client.get('/')

        # FlaskElasticsearch attaches the es client to the context in flask_elasticsearch.py
        from flask import _app_ctx_stack

        assert perform_request.call_count == 1 + _app_ctx_stack.top.elasticsearch.transport.max_retries
        assert perform_request.call_count == 1 + 3


class TestGzip(BaseApplicationTestWithIndex):
    def setup(self):
        super().setup()
        for c in "abcdefghijklmnopqrstuvwxyz1234567890":
            # create a bunch of indexes with quite long names so we definitely have a response from the "/" route
            # that is > the minimum gzipped size limit
            self.create_index(index_name=f"test-{c*180}")

    def test_gzip(self):
        response = self.client.get('/', headers={"Accept-Encoding": "gzip"})

        assert response.status_code == 200
        assert response.headers.get("Content-Encoding") == "gzip"
        # check the un-gzipped content can successfully be read as json
        assert json.loads(gzip.decompress(response.data))
