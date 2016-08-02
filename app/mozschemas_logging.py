# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import logging
import sys

from mozilla_cloud_services_logger.formatters import JsonLogFormatter


def getLogger(module):
    logger = logging.getLogger(module)
    handler = logging.StreamHandler(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)
    handler.setFormatter(JsonLogFormatter(logger_name=module))
    logger.addHandler(handler)
    return logger
