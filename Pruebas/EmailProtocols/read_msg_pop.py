import poplib
import config

def main():
    #http://chuwiki.chuidiang.org/index.php?title=Enviar_y_leer_email_con_python_y_gmail
    m = poplib.POP3_SSL('pop.gmail.com',995)
    #Es necesario habilitar el acceso no seguro
    m.user(config.EMAIL_ADDRESS)
    m.pass_(config.PASSWORD)
    numero = len(m.list()[1])
    for i in range (numero):
       print("Message number"+str(i+1))
       print("--------------------")
       # read message
       response, headerLines, bytes = m.retr(i+1)

if __name__ == '__main__':
    main()