import smtplib
import config

def main():
    try:
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.ehlo()
        server.starttls()
        #Es necesario quitarle seguridad a la cuenta
        server.login(config.EMAIL_ADDRESS, config.PASSWORD)
        message = 'Subject: {}\n\n{}'.format('Test subject', 'Hello there, how are you today?')
        server.sendmail(config.EMAIL_ADDRESS, 'ferrerromualda@gmail.com', message)
        server.quit()
        print('Success: Email sent!')
    except:
        print('Email failed to send.')

if __name__ == '__main__':
    main()