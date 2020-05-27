# TFG-1920-CarlosMoreno
Repositorio para el Trabajo de Fin de Grado de Carlos Moreno Morera

## Estructura y archivos
Este repositorio consta de varios directorios que se enumeran y explican a continuación:

1. **Memoria** : directorio donde se encuentra el documento LaTeX donde se desarrolla toda la documentación del proyecto IRIS como Trabajo de Fin del Grado en Ingeniería en Informática de Carlos Moreno Morera.
2. **Pruebas API Gmail** : este directorio contiene diversos scripts .py escritos en python que recopilan las funciones más básicas para trabajar con la API de Gmail. Los archivos que en él se encuentran son los siguientes:
	+ showLabels.py: script que inicia una sesión de usuario y muestra las etiquetas que este usuario posee en su cuenta de correo
	+ auth.py: implementa la clase _auth_ la cual obtiene credenciales válidas gracias al método _get_credentials_ para poder acceder a la cuenta de gmail del usuario. Este script generará un archivo token.pickle que permite mantener la sesión iniciada.
	+ SendGmail.py: implementa la clase _sendGmail_ la cual permite crear mensajes simples y con archivos adjuntos con sus métodos _create_message_ y _create_message_with_attachment_ , respectivamente. Además, una vez se obtiene un objeto mensaje, se puede enviar gracias a _send_message_ .
	+ send_email_main.py: utilizando las dos clases anteriores, inicia una sesión de usuario y manda un mensaje con una foto adjunta prestablecido por defecto.
	+ drafts.py: implementa la clase _drafts_ la cual permite crear un borrador una vez tengamos un objeto mensaje con el método _create_draft_ . Además también permite obtener una lista de los borradores del usuario con _list_drafts_ , obtener un borrador identificado por su identificador único con _get_draft_ y modificar un borrador ya creado con _update_draft_ .
	+ drafts_main.py: utilizando las clases _drafts_ y _auth_ , inicia una sesión y crea dos borradores prestablecidos por defecto. Después lista los borradores del usuario para comprobar que la operación se ha realizado con éxito.
	+ messages.py: Implementa la clase _email_messages_ que lista todos los mensajes de la bandeja de entrada del usuario con el método _get_message_list_ y permite responder a un mensaje de la bandeja de entrada dado su identificador creando un hilo de correos. Esto último está implementado en el método _reply_message_ .
	+ response_main.py: utilizando la clase anterior y la clase _auth_ , inicia una sesión de usuario, lista los mensajes de su bandeja de entrada, selecciona uno y lo responde con un mensaje prestablecido por defecto.
	+ threads.py: implementa la clase _email_threads_ la cual posee un único método público ( _show_chatty_threads_ ) el cual muestra todos los hilos que está conformados por más de dos mensajes y posean un asunto.
	+ threads_main.py: utilizando las clases _email_threads_ y _auth_, inicia una sesión de usuario y muestra todos los hilos de correos electrónicos.
3. **Pruebas protocolos email**: este directorio contiene diversos scripts .py escritos en python que recopilan distintas formas de acceder a una cuenta de Gmail sin utilizar su API (usando las librerías imaplib, smtplib y poplib):
	+ open_unread_msg.py: implementa el acceso y lectura de los mensajes no leídos con imaplib, es decir, utilizando el protocolo IMAP.
	+ send_email_smtp.py: implementa el acceso y envío de mensajes con smtplib, es decir, utilizando el protocolo SMTP.
	+ read_msg_pop.py: implementa el acceso y lectura de los mensajes con poplib, es decir, utilizando el protocolo POP.
	+ config.py: declara las constantes utilizadas en los dos scripts anteriores.
4. **Pruebas aplicacciones web**: este directorio contiene diversos ficheros (.html, .php y .py) que al ejecutarlos en un servidor levantan una aplicación web que muestra al usuarios los mensajes de su bandeja de entrada.
5. **AnalisisEstilo** : este directorio contiene toda la implementación de la arquitectura necesaria para llevar a cabo la extracción, el preprocesado, la corrección tipográfica y el cálculo de métricas del estilo de los correos electrónicos enviados por un usuario. Además, también alberga varios scripts que llevan a cabo un análisis de los resultados obtenidos. Los directorios que en el se encuentran son los siguientes:
	+ extraction: contiene la implementación del módulo de extracción de correos electrónicos de un usuario de Gmail.
	+ preprocess: contiene la implementación del módulo de preprocesado de los mensajes extraídos previamente por el módulo de extración.
	+ typocorrection: contiene la implementación del módulo de corrección tipográfica de los mensajes preprocesados.
	+ stylemeasuring: contiene la implementación del módulo de cálculo de las métricas de los correos corregidos.
	+ contactclassification: contiene varios scripts que permiten clasificar los contactos a los que se les ha enviado mensajes en diversas categorías.
	+ analysis: contiene varios scripts que utilizan diversas técnicas de aprendizaje automático para obtener conclusiones de las métricas utilizadas sobre los mensajes del usuario.
6. **GeneracionEmail** : este directorio contiene varios scripts que implementan el algoritmo Latent Semantic Indexing (LSI) para encontrar los documentos que más se asemejan a una consulta dada con palabras clave.