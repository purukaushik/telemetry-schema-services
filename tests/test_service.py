import json
import os
import mozschemas_service
import unittest
import flask


class TestServiceApp(unittest.TestCase):
    def setUp(self):
        self.service_app = mozschemas_service.app.test_client()
        self.config = json.load(open('test_config.json'))

    def test_file_end_point(self):
        self.is_endpoint_good('/file/', 'application/json')

    def test_schema_docTypes_versions_end_point(self):
        self.is_endpoint_good('/schema/', 'application/json')

    def test_schema_docTypes_end_point(self):
        namespace = self.config['namespace']
        for docType in self.config['docTypes']:
            endpoint = '/schema/' + namespace + "/" + docType
            resp = self.service_app.get(endpoint)

            self.is_response_good(resp, 200, 'text/html')

    def is_endpoint_good(self, endpoint_prefix, mimetype):
        namespace = self.config['namespace'] + "/"

        for docTypes, versions in self.config['docType_versions'].items():

            for version in versions:
                filepath = "/"
                if endpoint_prefix == '/file/' :
                    filename = docTypes + "." + version + ".schema.json"
                    filepath = namespace + filename
                elif endpoint_prefix == '/schema/' :
                    filename = docTypes + "/" + version
                    filepath = namespace + filename
                resp = self.service_app.get(endpoint_prefix + filepath)
                self.is_response_good(resp, 200, mimetype)

    def is_response_good(self, resp, status_code, mimetype):
        # check if resp object is not None
        self.assertIsNotNone(resp)
        # check if resp is of type Response
        self.assertIsInstance(resp, flask.Response)
        # check status=200
        self.assertEquals(resp.status_code, status_code)
        # check mimetype=application/json
        self.assertEquals(resp.mimetype, mimetype)