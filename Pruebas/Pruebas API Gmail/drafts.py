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
      message['To'] = to
      message['From'] = sender
      message['Subject'] = subject
      return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

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

    def list_drafts(self, user_id):
      """Get a list of all drafts in the user's mailbox.
    
      Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
    
      Returns:
        A list of all Drafts in the user's mailbox.
      """
      try:
        response = self.service.users().drafts().list(userId=user_id).execute()
        drafts = response['drafts']
        for draft in drafts:
          print('Draft id: %s' % draft['id'])
        return drafts
      except HttpError as error:
        print('An error occurred: %s' % error)

    def get_draft(self, user_id, draft_id):
      """Get Draft with ID matching draft_id.
    
      Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        draft_id: The ID of the Draft to return.
    
      Returns:
        Draft with ID matching draft_id.
      """
      try:
        draft = self.service.users().drafts().get(user_id=user_id, id=draft_id).execute()
    
        print('Draft id: %s\nDraft message: %s' % (draft['id'], draft['message']))
    
        return draft
      except HttpError as error:
        print('An error occurred: %s' % error)

    def update_draft(self, user_id, draft_id, message_body, send):
      """Create and update a draft email.
    
      Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        draft_id: ID of the draft to Update.
        message_body: The body of the email message, including headers.
        send: Send draft if 1 otherwise don't send draft.
    
      Returns:
        Updated draft object.
      """
      try:
        message = {'message': message_body}
        draft = self.service.users().drafts().update(userId=user_id, id=draft_id,
                                                body=message, send=send).execute()
    
        print('Draft id: %s\nDraft message: %s' % (draft['id'], draft['message']))
    
        return draft
      except HttpError as error:
        print('An error occurred: %s' % error)