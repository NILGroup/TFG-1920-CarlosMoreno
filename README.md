# TFG-1920-CarlosMoreno
Repositorio para el Trabajo de Fin de Grado de Carlos Moreno Morera

## Estructura y archivos
Este repositorio consta de varios directorios que se enumeran y explican a continuaci�n:

1. **Memoria** : directorio donde se encuentra el documento LaTeX donde se desarrolla toda la documentaci�n del proyecto IRIS como Trabajo de Fin del Grado en Ingenier�a en Inform�tica de Carlos Moreno Morera.
2. **Pruebas API Gmail** : este directorio contiene diversos scripts .py escritos en python que recopilan las funciones m�s b�sicas para trabajar con la API de Gmail. Los archivos que en �l se encuentran son los siguientes:
	+ showLabels.py: script que inicia una sesi�n de usuario y muestra las etiquetas que este usuario posee en su cuenta de correo
	+ auth.py: implementa la clase _auth_ la cual obtiene credenciales v�lidas gracias al m�todo _get_credentials_ para poder acceder a la cuenta de gmail del usuario. Este script generar� un archivo token.pickle que permite mantener la sesi�n iniciada.
	+ SendGmail.py: implementa la clase _sendGmail_ la cual permite crear mensajes simples y con archivos adjuntos con sus m�todos _create_message_ y _create_message_with_attachment_ , respectivamente. Adem�s, una vez se obtiene un objeto mensaje, se puede enviar gracias a _send_message_ .
	+ send_email_main.py: utilizando las dos clases anteriores, inicia una sesi�n de usuario y manda un mensaje con una foto adjunta prestablecido por defecto.
	+ drafts.py: implementa la clase _drafts_ la cual permite crear un borrador una vez tengamos un objeto mensaje con el m�todo _create_draft_ . Adem�s tambi�n permite obtener una lista de los borradores del usuario con _list_drafts_ , obtener un borrador identificado por su identificador �nico con _get_draft_ y modificar un borrador ya creado con _update_draft_ .
	+ drafts_main.py: utilizando las clases _drafts_ y _auth_ , inicia una sesi�n y crea dos borradores prestablecidos por defecto. Despu�s lista los borradores del usuario para comprobar que la operaci�n se ha realizado con �xito.
	+ messages.py: Implementa la clase _email_messages_ que lista todos los mensajes de la bandeja de entrada del usuario con el m�todo _get_message_list_ y permite responder a un mensaje de la bandeja de entrada dado su identificador creando un hilo de correos. Esto �ltimo est� implementado en el m�todo _reply_message_ .
	+ response_main.py: utilizando la clase anterior y la clase _auth_ , inicia una sesi�n de usuario, lista los mensajes de su bandeja de entrada, selecciona uno y lo responde con un mensaje prestablecido por defecto.
	+ threads.py: implementa la clase _email_threads_ la cual posee un �nico m�todo p�blico ( _show_chatty_threads_ ) el cual muestra todos los hilos que est� conformados por m�s de dos mensajes y posean un asunto.
	+ threads_main.py: utilizando las clases _email_threads_ y _auth_, inicia una sesi�n de usuario y muestra todos los hilos de correos electr�nicos.
3. **Pruebas protocolos email**: este directorio contiene diversos scripts .py escritos en python que recopilan distintas formas de acceder a una cuenta de Gmail sin utilizar su API (usando las librer�as imaplib, smtplib y poplib):
	+ open_unread_msg.py: implementa el acceso y lectura de los mensajes no le�dos con imaplib, es decir, utilizando el protocolo IMAP.
	+ send_email_smtp.py: implementa el acceso y env�o de mensajes con smtplib, es decir, utilizando el protocolo SMTP.
	+ read_msg_pop.py: implementa el acceso y lectura de los mensajes con poplib, es decir, utilizando el protocolo POP.
	+ config.py: declara las constantes utilizadas en los dos scripts anteriores.
4. **Pruebas aplicacciones web**: este directorio contiene diversos ficheros (.html, .php y .py) que al ejecutarlos en un servidor levantan una aplicaci�n web que muestra al usuarios los mensajes de su bandeja de entrada.
5. **AnalisisEstilo** : este directorio contiene toda la implementaci�n de la arquitectura necesaria para llevar a cabo la extracci�n, el preprocesado, la correcci�n tipogr�fica y el c�lculo de m�tricas del estilo de los correos electr�nicos enviados por un usuario. Adem�s, tambi�n alberga varios scripts que llevan a cabo un an�lisis de los resultados obtenidos. Los directorios que en el se encuentran son los siguientes:
	+ extraction: contiene la implementaci�n del m�dulo de extracci�n de correos electr�nicos de un usuario de Gmail.
	+ preprocess: contiene la implementaci�n del m�dulo de preprocesado de los mensajes extra�dos previamente por el m�dulo de extraci�n.
	+ typocorrection: contiene la implementaci�n del m�dulo de correcci�n tipogr�fica de los mensajes preprocesados.
	+ stylemeasuring: contiene la implementaci�n del m�dulo de c�lculo de las m�tricas de los correos corregidos.
	+ contactclassification: contiene varios scripts que permiten clasificar los contactos a los que se les ha enviado mensajes en diversas categor�as.
	+ analysis: contiene varios scripts que utilizan diversas t�cnicas de aprendizaje autom�tico para obtener conclusiones de las m�tricas utilizadas sobre los mensajes del usuario.
6. **GeneracionEmail** : este directorio contiene varios scripts que implementan el algoritmo Latent Semantic Indexing (LSI) para encontrar los documentos que m�s se asemejan a una consulta dada con palabras clave.