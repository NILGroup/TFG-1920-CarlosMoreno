# TFG-1920-CarlosMoreno
Repositorio para el Trabajo de Fin de Grado de Carlos Moreno Morera

## Estructura y archivos
Este repositorio consta de varios directorios que se enumeran y explican a continuaci�n:

1. **Memoria** : directorio donde se encuentra el documento LaTeX donde se desarrolla toda la documentaci�n del proyecto IRIS como Trabajo de Fin del Grado en Ingenier�a en Inform�tica de Carlos Moreno Morera.
2. **Pruebas API Gmail** : este directorio contiene diversos scripts .py escritos en python que recopilan las funciones m�s b�sicas para trabajar con la API de Gmail. Los archivos que en �l se encuentran son los siguientes:

	+ credentials.json: credenciales obtenidas de la [Consola de desarrollo de Google](https://console.developers.google.com) para poder acceder a la API con el proyecto creado previamente en la misma plataforma.
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
