from __future__ import print_function
from extractor import Extractor
import quotaunits as qu

class ThreadExtractor(Extractor):
    """
    Implements Extractor class
    """
    def __init__(self, service, quota):
        """
        Class constructor.

        Parameters
        ----------
        service: Gmail resource
            Gmail API resource with an Gmail user session opened.
        quota: int
            Gmail API quota units available for message extraction.

        Returns
        -------
        Constructed ThreadExtractor class.

        """
        super().__init__(service, quota)
        self.min_qu = qu.MIN_QUNITS_THRD
        self.list_key = 'threads'

    def get_list(self, nextPage):
        """
        Obtains a dictionary which includes a list of threads.

        Parameters
        ----------
        nextPage : str
            Page token to retrieve a specific page of results in the list.

        Returns
        -------
        If successful, this method returns a response body with the following 
        structure:
        {
            'threads' : [
                Gmail API users.threads resource
            ],
            "nextPageToken": string,
            "resultSizeEstimate": unsigned integer
        }

        """
        self.wait_for_request(qu.THREADS_LIST)
        t = self.service.user().threads()
        l = t.list(userId = 'me', labelIds = ['SENT'], pageToken = nextPage).execute()
        self.update_attributes(qu.THREADS_LIST)
        return l

    def get_resource(self, resId):
        """
        Obtains the Gmail API threads resource.

        Parameters
        ----------
        resId : str
            Thread resource's identifier that we want to retrieve.

        Returns
        -------
        Gmail API users.threads resource.

        """
        self.wait_for_request(qu.THREADS_GET)
        t = self.service.user().threads().get(id = resId, userId = 'me').execute()
        self.update_attributes(qu.THREADS_GET)
        return t