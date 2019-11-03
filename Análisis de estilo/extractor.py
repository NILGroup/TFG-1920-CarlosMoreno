import time
import quotaunits

class Extractor:
    """
    The Extractor object performs the task of extracting sent messages from
    the user by accessing Gmail API.
    
    Parameters:
        service: Gmail API resource with an Gmail user session opened.
        quota (int): Gmail API quota units available for message extraction.

    Attributes:
        service: variable where we store service.
        quota (int): variable where we store quota. Represents the remaining
            quota units available to carry out the extraction operations.
        init_time (float): Moment in which the second of operations begins.
        last_req_time (float): Momento in which the last request was made.
        quota_sec (int): remaining Gmail API quota units per second from 
            init_time moment.
    """
    def __init__(self, service, quota):
        self.service = service
        self.quota = quota
        self.quota_sec = quotaunits.QUOTA_UNITS_PER_SECOND
        self.init_time = time.time()
        self.last_req_time = time.time()

    def __update_attributes(self, req_quota):
        """
        Update the quota, quota_sec and last_req_time attributes of this class
        after making a Gmail API request with the req_quota quota units.

        Parameters:
            req_quota (int): quota units of the Gmail API request that has just
                been made.
        """
        self.last_req_time = time.time()
        self.quota = self.quota - req_quota
        self.quota_sec = self.quota_sec - req_quota

    def __wait_for_request(self, req_quota):
        """
        Avoid exceeding Gmail API quota units per second by waiting for the time
        needed to make the request with req_quota quota units. Besides this
        method updates the init_time attribute if from init_time until now more
        than a second has passed.

        Parameters:
            req_quota (int): quota units of the Gmail API request that is going
                to be made.
        """
        slept = False
        t_now = time.time()
        # If we are going to exceed the quota units per second in this last second
        # or the init_time attribute is not updated
        if ((t_now - self.init_time <= 1 and req_quota >= self.quota_sec)
            or (t_now - self.init_time > 1 and t_now - self.last_req_time <= 1)):
            slept = True
            time.sleep(1.1 - (t_now - self.last_req_time))

        if slept or (t_now - self.init_time > 1):
            self.quota_sec = quotaunits.QUOTA_UNITS_PER_SECOND
            self.init_time = time.time()
            self.last_req_time = time.time()

    def __get_list_resource(self, msg_extract, nextPage):
        """
        Obtain the list of the resource we are extracting.

        Parameters:
            msg_extract (bool): True if we are extracting sent messages and
                False if we are extracting sent threads.
            nextPage (str): Page token to retrieve a specific page of results
                in the list.
        
        Returns:
            List resource of sent messages (if msg_extract is True) or sent 
            threads (if msg_extract is False).
        """
        msg_list = {}
        if (msg_extract):
            self.__wait_for_request(req_quota = quotaunits.MSG_LIST)
            msg_list = self.service.users().messages().list(userId = 'me',
                            labelIds = ['SENT'], pageToken = nextPage).execute()
            self.__update_attributes(req_quota = quotaunits.MSG_LIST)
        else:
            self.__wait_for_request(req_quota = quotaunits.THREADS_LIST)
            msg_list = self.service.users().threads().list(userId = 'me',
                            labelIds = ['SENT'], pageToken = nextPage).execute()
            self.__update_attributes(req_quota = quotaunits.THREADS_LIST)
        return msg_list

    def extract_sent_msg(self, cond_var, num_msg, msgs, msg_extract = True):
        extracted = 0
        nextPage = None
        self.init_time = time.time()
        while (extracted < num_msg and self.quota >= quotaunits.MIN_QUNITS_MSG):
            msg_list = self.__get_list_resource(msg_extract, nextPage)

            list_size = len(msg_list['messages'])
            if (extracted + list_size < num_msg):
                nextPage = msg_list['nextPageToken']

            msg_list = msg_list['messages']
            i = 0
            while (i < list_size and self.quota >= quotaunits.MIN_QUNITS_MSG):
                self.__wait_for_request(req_quota = quotaunits.MSG_GET)


        #Si se queda a medias guardar estado en un archivo
        #Utilizar variables de condición
        #https://docs.python.org/3.5/library/threading.html#threading.Condition