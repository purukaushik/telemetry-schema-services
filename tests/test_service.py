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
        namespace = self.config['namespace'] + "/"

        for docTypes, versions in self.config['docType_versions'].items():

            for version in versions:
                filename = docTypes + "." + version +".schema.json"
                filepath = namespace + filename
                resp = self.service_app.get("/file/"+filepath)

                # check if resp object is not None
                self.assertIsNotNone(resp)

                # check if resp is of type Response
                self.assertIsInstance(resp, flask.Response)

                # check status=200
                self.assertEqual(resp.status_code,200)
                # check mimetype=application/json
                self.assertEquals(resp.mimetype,'application/json')

                # check if resp.response, ie the json is not empty
                self.assertIsNotNone(resp.response.file)
                json_file = json.loads(resp.response.file.read())
                # FIXME: add these back after all schema.json files have ids where they will be hosted
                # check for id field in response json
                #self.assertIn('id', json_file, msg="id not in file " + filename)
                #self.assertIn(filename, json_file['id'])
