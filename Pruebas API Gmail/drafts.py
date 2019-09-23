from __future__ import print_function
import base64
from email.mime.text import MIMEText
from googleapiclient.errors import HttpError

class drafts:
    def __init__(self, service):
        self.service = service

    def create_message(self, sender, to, subject, message_text):
      """Create a message for an email.
    
      Args:
        sender: Email address of the sender.
        to: Email address of the receiver.
        subject: The subject of the email message.
        message_text: The text of the email message.
    
      Returns:
        An object containing a base64url encoded email object.
      """
      message = MIMEText(message_text)
      message['to'] = to
      message['from'] = sender
      message['subject'] = subject
      return {'raw': base64.urlsafe_b64encode(message.as_bytes())}

    def create_draft(self, user_id, message_body):
      """Create and insert a draft email. Print the returned draft's message and id.
    
      Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        message_body: The body of the email message, including headers.
    
      Returns:
        Draft object, including draft id and message meta data.
      """
      try:
        message = {'message': message_body}
        draft = self.service.users().drafts().create(userId=user_id, body=message).execute()
    
        print('Draft id: %s\nDraft message: %s' % (draft['id'], draft['message']))

        return draft
      except HttpError as error:
        print('An error occurred: %s' % error)
        return None