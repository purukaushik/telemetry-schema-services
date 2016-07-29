# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import json
import logging
import os
import unittest

from app.mozschemas_common import SchemasLocalFilesHelper, gitcheckout


class TestCommons(unittest.TestCase):

    def setUp(self):

        self.helper = SchemasLocalFilesHelper()
        self.logger = logging.getLogger(__name__)
        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        self.config = json.load(open(os.path.join(__location__, "config.json")))
        gitcheckout(self.logger)

    def test_get_doctypes(self):
        namespace = self.config["namespace"]
        docTypes = self.config["docTypes"]
        result = self.helper.get_doctypes_versions(namespace=namespace, docType=None, logger=self.logger)
        # check if result returned is a list
        self.assertIsInstance(result, list)
        # size must be 4 as we currently have 4 docTypes.
        self.assertEquals(len(result), 4)
        for item in result:
            # check if items in list returned are tuples
            self.assertIsInstance(item, tuple)
            # check if the tuples are of size 4 always!
            self.assertEquals(len(item), 4)
            # check if the 3,4th items are always None - as the request was for only docTypes
            self.assertIsNone(item[2])
            self.assertIsNone(item[3])
            # check if docType is in known types
            self.assertIn(item[0], docTypes)

    def test_get_versions(self):
        namespace = self.config["namespace"]
        docType_versions = self.config["docType_versions"]

        for docType,versions in docType_versions.items():
            result = self.helper.get_doctypes_versions(namespace=namespace, docType=docType, logger=self.logger)
            # check if result is a list
            self.assertIsInstance(result,list)
            # check if result has same length as no of versions for that docType
            self.assertEquals(len(result),len(versions))
            for item in result:
                # check if each item is a tuple in the result list
                self.assertIsInstance(item, tuple)
                # check if no of elements in tuple is 4
                self.assertEquals(len(item),4)
                # check if the last two fields are not none -> as the request was for versions there must be minify,
                # validate button endpoint uris
                self.assertIsNotNone(item[2])
                self.assertIsNotNone(item[3])
                # check if version from commons service is same as expected in the test_config file
                self.assertIn(item[0], versions, msg=item[0]+" not a version of " + docType)
