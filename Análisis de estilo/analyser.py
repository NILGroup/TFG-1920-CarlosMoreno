from __future__ import print_function
import base64
import quotaunits
import extractor

class Analyser:

    def __init__(self, service, quota = quotaunits.QUOTA_UNITS_PER_DAY):
        self.service = service
        self.quota = quota
