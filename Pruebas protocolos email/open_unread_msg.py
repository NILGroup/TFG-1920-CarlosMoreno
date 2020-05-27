import email
import imaplib
import getpass

def main():
    mail = imaplib.IMAP4_SSL('imap.googlemail.com', 993)
    unm = input('Please enter your mail id: ')
    pwd = getpass.getpass('Please input your password: ')
    #Solo hace login si activas la seguridad para apps no seguras
    mail.login(unm, pwd)

    mail.select('INBOX')
    n = 0
    (retcode, messages) = mail.search(None, '(UNSEEN)')
    if retcode == 'OK':
        for num in messages[0].split():
            n = n + 1
            print(n)
            typ, data = mail.fetch(num, '(RFC822)')
            for response_part in data:
                if isinstance(response_part, tuple):
                    original  = email.message_from_string(response_part[1].decode())
                    print(original['From'])
                    data = original['Subject']
                    print(data)
                    typ, data = mail.store(num, '+FLAGS', '\\Seen')
    print(n)

if __name__ == '__main__':
    main()