from __future__ import print_function
import base64
import email
import quopri

class email_threads:
    def __init__(self, service):
        self.service = service

    def _print_body_message(self, message):
        msg_str = base64.urlsafe_b64decode(message['raw'].encode('ASCII')).decode('utf-8')
        mime_msg = email.message_from_string(msg_str)
        text = None
        if (mime_msg.is_multipart()):
            print('MIME message is multipart')
            html = ""
            for part in mime_msg.get_payload():
                print ("%s, %s" % (part.get_content_type(), part.get_content_charset()))

                if text is None and part.get_content_charset() is None:
                    # We cannot know the character set, so return decoded "something"
                    text = part.get_payload()
                    if part['Content-Transfer-Encoding'] == 'quoted-printable':
                        text = quopri.decodestring(text).decode('utf-8')
                    elif part['Content-Transfer-Encoding'] == 'base64':
                        text = base64.urlsafe_b64decode(text).decode('utf-8')
                elif text is None:
                    if part.get_content_type() == 'text/plain':
                        text = part.get_payload();
                        if part['Content-Transfer-Encoding'] == 'quoted-printable':
                            text = quopri.decodestring(text).decode('utf-8')
                        elif part['Content-Transfer-Encoding'] == 'base64':
                            text = base64.urlsafe_b64decode(text).decode('utf-8')
                        text = 'Message text: ' + text
                    elif part.get_content_type() == 'text/html':
                        html = part.get_payload();
                        if part['Content-Transfer-Encoding'] == 'quoted-printable':
                            html = quopri.decodestring(html).decode('utf-8')
                        elif part['Content-Transfer-Encoding'] == 'base64':
                            html = base64.urlsafe_b64decode(html).decode('utf-8')
                        html = 'Message hmtl: ' + html
            if text is not None:
                print(text)
            else:
                print(html)
        else:
            print('Mime message is not multipart')
            text = mime_msg.get_payload()
            if mime_msg['Content-Transfer-Encoding'] == 'quoted-printable':
                text = quopri.decodestring(text).decode('utf-8')
            elif mime_msg['Content-Transfer-Encoding'] == 'base64':
                text = base64.urlsafe_b64decode(text).decode('utf-8')
            print('Message text: %s' % text)

    def _print_attachments(self, message):
        file_names = []
        for p in message['payload'].get('parts', []):
            if p['filename']:
                file_names.append(p['filename'])

        if (len(file_names) > 0):
            file = file_names[0]
            for i in range(1, len(file_names)):
                file += ', ' + file_names[i]
            print('Attachment: %s' % file)

    def show_chatty_threads(self, user_id='me'):
        threads = self.service.users().threads().list(userId=user_id).execute().get('threads', [])
        for thread in threads:
            tdata = self.service.users().threads().get(userId=user_id, id=thread['id']).execute()
            nmsgs = len(tdata['messages'])
    
            if nmsgs > 2:    # skip if <3 msgs in thread
                msg = tdata['messages'][0]['payload']
                subject = ''
                for header in msg['headers']:
                    if header['name'] == 'Subject':
                        subject = header['value']
                        break
                if subject:  # skip if no Subject line
                    print('- %s (%d msgs)' % (subject, nmsgs))
                    for i in range(0, nmsgs):
                        print('Message id: %s' % tdata['messages'][i]['id'])
                        payload_h = tdata['messages'][i]['payload']['headers']

                        #Export sections of the list headers
                        head_sect = {}
                        for j in range (0, len(payload_h)):
                            head_sect[payload_h[j]['name']] = j

                        print('Message from: %s' % payload_h[head_sect['From']]['value'])
                        print('Message to: %s' % payload_h[head_sect['To']]['value'])
                        print('Message subject: %s' % payload_h[head_sect['Subject']]['value'])
                        #It is less reliable than tdata['message'][i]['internalDate']
                        print('Message date: %s' % payload_h[head_sect['Date']]['value'])

                        head_sect.clear()

                        self._print_attachments(message = tdata['messages'][i])

                        message = self.service.users().messages().get(userId=user_id,
                                id=tdata['messages'][i]['id'], format='raw').execute()
                        self._print_body_message(message = message)
                        print('------------')
                        print('------------')

                        # Cuando respondes a un mensaje en un hilo google copia el
                            # mensaje respondido justo debajo. Este texto copiado
                            # aparece en el cuerpo del mensaje
                        # Cuando envías un mensaje google internamente asigna \n que
                            # se mantienen cuando se extrae y decodifica.
