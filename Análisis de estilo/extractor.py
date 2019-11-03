import time
import quotaunits

class Extractor:
    def __init__(self, service, quota):
        self.service = service
        self.quota = quota
        self.quota_sec = quotaunits.QUOTA_UNITS_PER_SECOND
        self.init_time = time.time()

    def __wait_for_request(req_quota):
        # If we are going to exceed the quota units per second in this last second
        if (time.time() - self.init_time < 1 and req_quota > self.quota_sec):
            time.sleep(1.1)
            self.quota_sec = quotaunits.QUOTA_UNITS_PER_SECOND
            self.init_time = time.time()

    def extract_sent_threads(cond_var, num_thrd, msgs)

    def extract_sent_msg(cond_var, num_msg, msgs):
        extracted = 0

        #Utilizar variables de condición
        #https://docs.python.org/3.5/library/threading.html#threading.Condition