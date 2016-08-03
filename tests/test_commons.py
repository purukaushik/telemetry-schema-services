# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import json
import os
import unittest

from app.git_checkout import gitcheckout
from app.mozschemas_common import SchemasLocalFilesHelper


class TestCommons(unittest.TestCase):

    def setUp(self):

        self.helper = SchemasLocalFilesHelper()
        curr_dir = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        self.config = json.load(open(os.path.join(curr_dir, "config.json")))
        gitcheckout()

    def test_get_doctypes(self):
        namespace = self.config["namespace"]
        docTypes = self.config["docTypes"]
        result = self.helper.get_doctypes_versions(namespace=namespace, docType=None)
        # check if result is a list
        self.assertIsInstance(result, dict)
        # check if result has 'doc_list'
        self.assertIn('doc_list', result)
        # check if doc_list is list
        self.assertIsInstance(result['doc_list'], list)

        # size must be 4 as we currently have 4 docTypes.
        self.assertEquals(len(result['doc_list']), 4)
        for item in result['doc_list']:
            # check if items in list returned are dicts
            self.assertIsInstance(item, dict)
            # check if the tuples are of size 5 always!
            self.assertEquals(len(item), 5)
            # check if the 3, 4th, 5th items are always None - as the request was for only docTypes
            self.assertIsNone(item['validate'])
            self.assertIsNone(item['minify'])
            self.assertIsNone(item['inline'])
            # check if docType is in known types
            self.assertIn(item['document'], docTypes)

    def test_get_versions(self):
        namespace = self.config["namespace"]
        docType_versions = self.config["docType_versions"]

        for docType,versions in docType_versions.items():
            result = self.helper.get_doctypes_versions(namespace=namespace, docType=docType)
            # check if result is a list
            self.assertIsInstance(result, dict)
            # check if result has 'doc_list'
            self.assertIn('doc_list', result)
            # check if doc_list is list
            self.assertIsInstance(result['doc_list'], list)

            # check if result has same length as no of versions for that docType
            self.assertEquals(len(result),len(versions))
            for item in result['doc_list']:
                # check if each item is a tuple in the result list
                self.assertIsInstance(item, dict)
                # check if no of elements in tuple is 5 ; change for inline
                self.assertEquals(len(item), 5)
                # check if the last two fields are not none -> as the request was for versions there must be minify,
                # validate button endpoint uris
                self.assertIsNotNone(item['validate'])
                self.assertIsNotNone(item['minify'])
                self.assertIsNotNone(item['inline'])
                # check if version from commons service is same as expected in the test_config file
                self.assertIn(item['document'], versions, msg=item['document']+" not a version of " + docType)
