from __future__ import print_function

def get_gmail_list(service):
    threads = service.users().threads().list(userId='me', labelIds = ['INBOX']).execute().get('threads', [])
    i = 0
    gmail_list = {}

    for thread in threads:
        tdata = service.users().threads().get(userId='me', id=thread['id']).execute()

        subject = ""
        sender = ""
        snip = ""
        for header in tdata['messages'][0]['payload']['headers']:
            if header['name'] == 'Subject':
                subject = header['value']
            elif header['name'] == 'From' :
                sender = header['value']

        if 'snippet' in tdata['messages'][len(tdata['messages']) - 1]:
            snip = tdata['messages'][len(tdata['messages']) - 1]['snippet']
        gmail_list[str(i)] = {'Id': tdata['messages'][0]['id'], 'Subject' : subject, 'From' : sender, 'Snippet' : snip}
        i = i + 1

    gmail_list['length'] = i
    return gmail_list