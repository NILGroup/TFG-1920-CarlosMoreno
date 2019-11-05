from extractor import Extractor
import quotaunits as qu

class MessageExtractor(Extractor):
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
        Constructed MessageExtractor class.

        """
        super().__init__(service, quota)

    def min_qu(self):
        """
        Returns the minimum quota units needed to make a request of a message.

        Returns
        -------
        int: minimum quota units needed to continue with extraction.

        """
        return qu.MIN_QUNITS_MSG

    def get_list_key(self):
        """
        Returns the key of the dictionary given by the list request for
        accessing to the messages list.

        Returns
        -------
        str: key of the dictionary.

        """
        return 'messages'

    def get_list(self, nextPage):
        """
        Obtains a dictionary which includes a list of messages.

        Parameters
        ----------
        nextPage : str
            Page token to retrieve a specific page of results in the list.

        Returns
        -------
        If successful, this method returns a response body with the following 
        structure:
        {
            'messages' : [
                Gmail API messages resource
            ],
            "nextPageToken": string,
            "resultSizeEstimate": unsigned integer
        }

        """
        self.wait_for_request(qu.MSG_LIST)
        m = self.service.user().messages()
        l = m.list(userId = 'me', labelIds = ['SENT'], pageToken = nextPage).execute()
        self.update_attributes(qu.MSG_LIST)
        return l

    def get_resource(self, resId):
        """
        Obtains the Gmail API messages resource.

        Parameters
        ----------
        resId : str
            Message resource's identifier that we want to retrieve.

        Returns
        -------
        Gmail API messages resource.

        """
        self.wait_for_request(qu.MSG_GET)
        m = self.service.user().messages().get(id = resId, userId = 'me').execute()
        self.update_attributes(qu.MSG_GET)
        return m

    def extract_msgs_from_resource(self, res):
        """
        Obtains a list with the information of the given messages.

        Parameters
        ----------
        res : Gmail API messages resource
            Gmail API messages resource.

        Returns
        -------
        A list of messages (with an only element) with the following structure:
        {
            'id' : string,
            'threadId' : string,
            'to' : [ string ]
            'depth' : int,               # How many messages precede it
            'date' : long,               # Epoch ms
            'subject' : string,
            'body' : string,
            'bodyBase64' : string,
            'charLength' : int
        }

        """
        