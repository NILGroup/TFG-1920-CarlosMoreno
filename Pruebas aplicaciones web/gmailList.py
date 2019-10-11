from __future__ import print_function

def get_gmail_list(self, service):
    threads = self.service.users().threads().list(userId='me').execute().get('threads', [])
    i = 0
    gmail_list = {}

    for thread in threads:
        tdata = self.service.users().threads().get(userId='me', id=thread['id']).execute()

        for header in tdata['messages'][0]['payload']['headers']:
            if header['name'] == 'Subject':
                subject = header['value']
            elif header['name'] == 'From' :
                sender = header['value']

        gmail_list[str(i)] = {'Subject' : subject, 'From' : sender, 'Snippet' : tdata['snippet']}
        ++i
    gmail_list['length'] = i
    return gmail_list