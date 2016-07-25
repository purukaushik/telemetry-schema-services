# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import json
import mozschemas_service
import unittest
import flask
import os

class TestServiceApp(unittest.TestCase):
    def setUp(self):
        self.service_app = mozschemas_service.app.test_client()
        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        self.config = json.load(open(os.path.join(__location__, "config.json")))

    def test_file_end_point(self):
        self.is_endpoint_good('/file/', 'application/json')

    def test_schema_docTypes_versions_end_point(self):
        self.is_endpoint_good('/schema/', 'application/json')

    def test_validate_version_end_point(self):
        self.is_endpoint_good('/validate/','text/html')

    def is_valid_json_in_upload(self, endpoint, valid_json):
        response = self.service_app.post(endpoint, data=dict(file=valid_json))
        self.is_response_good(response, 200, 'application/json')
        self.assertIsInstance(response, flask.Response)
        self.assertIn("valid", str(response.data))

    def is_invalid_json_in_upload(self, endpoint, invalid_json):
        response = self.service_app.post(endpoint, data=dict(file=invalid_json))
        self.is_response_good(response, 400, 'application/json')
        self.assertIsInstance(response, flask.Response)
        self.assertIn("invalid", str(response.data))

    def is_non_json_in_upload(self, endpoint, non_json):
        response = self.service_app.post(endpoint, data=dict(file=non_json))
        self.is_response_good(response, 400, 'application/json')
        self.assertIsInstance(response, flask.Response)
        self.assertIn("not a json", str(response.data))

    def test_file_upload_module(self):
        namespace = self.config['namespace']

        for docType, versions in self.config['docType_versions'].items():

            for version in versions:
                schema_tag = namespace + "/" + docType + "/" + version
                endpoint = '/validate/' + schema_tag

                if 'valid'+schema_tag in self.config:
                    valid_json = open(self.config['valid/'+ schema_tag])
                    self.is_valid_json_in_upload(endpoint, valid_json)

                if docType not in self.config['skip_invalid']:
                    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
                    invalid_json = open(os.path.join(__location__, "config.json"))
                    self.is_invalid_json_in_upload(endpoint, invalid_json=invalid_json)

                if 'non_json' in self.config:
                    non_json = open(self.config['non_json'])
                    self.is_non_json_in_upload(endpoint, non_json)

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
                elif endpoint_prefix == '/schema/' or endpoint_prefix == '/validate/' :
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
