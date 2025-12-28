# Arquitectura de AI Goals Tracker

## Visión General

Server
Nuestro server es un sistema que cuenta con langraph para resolver retos de codigo
nodo 1. Cuenta con un sistema de autenticacion para validar que el usuario tenga permiso para resolver retos de codigo este sistema esta anclado a uno o muchos cursos.
Nodo 2. es un agente que permite la creación de retos de codigo para los usuarios llamados goals tracker.
Nodo 3. es un agente que permite la creación de cursos para los usuarios que documentan estos retos de codigo.
Nodo 4. es un agente que genera constantemente feedback corto al usuario sobre su progreso en los retos de codigo.
Nodo 5. es un agente que genera constantemente evaluación de desempeñol del usuario y lo envia a un data lake como evento.
Nodo 6. es un agente que genera constantemente revivisión de los estados fundamentales del proceso y los cambia según sea necesario.
Nodo 7 el agente se encarga de organizar al usuario bajo el contexto global del usuario cual es la necesidad de codigo que requiere
Nodo 8 un agente se encarga de verificar el estado de animo del usuario y generar constantemente feedback corto al usuario sobre su progreso en los retos de codigo motivandolo constantemente.
Nodo 9 un agente se encarga de verificar el estado del contrato para ver si las condiciones del mismo cambian o se mantienen
el sistema emite todo el tiempo eventos a los servicios que esten interconectados
el sistema se encarga de garantizar que el proceso sea persistente y cumpla con los objetivos globales educar al usuario 

Extensión
AI Goals Tracker es una extensión de VS Code que ayuda a los desarrolladores a resolver objetivos de código de manera estructurada y validar su progreso usando inteligencia artificial (ChatGPT), esto permite que el desarrollador pueda resolver objetivos de manera masiva y eficiente ya que constantemente nuestro sistema ofrece retos de codigo para ellos cada día.
cada interacción será enviada al server en tiempo real para que pueda generar un evento y que pueda ser procesado por los agentes.
las interacciones emocionales seran preguntas que se harán con modales de alerta con respuesta desde vscode para que el usuario pueda ser motivado constantemente.
hay una extensión de pruebas en ../v1extension cumple con los objetivos de resolver un reto de codigo y dar feedback pero no es muy bueno en entregar documentación precisa y dirigida al usuario
tampoco es bueno en organizar una estructura sistematica para aprender
tampoco es bueno para manejar varios tipos de goals al mismo tiempo
no maneja nada de ejecuciones en tiempo real 
no tiene persistencia de datos 

aplicacion electron ya hay un diseño previo no trabajar aún en esta capa. 
se encarga de obtener en primera mano estadisticas del usuario y enviarlas al server para que pueda generar un evento y que pueda ser procesado por los agentes leyendo directamente los parkets que persisten en el disco duro del usuario y hay una copia de los mismos en MinIO
se encarga de llamar cada día al server para que pueda obtener los retos de cada día y pueda gestionar los objetivos del usuario


tecnologías
Backend: Python, fastapi, fastmcp, LangGraph, OpenAI + redis + states machines docker online 
eventos Rabitmq
Jenkins CI/CD
arqutectura event sourcing + websockets
Frontend: VSCODE extension, TypeScript, md, tailwindcss
Frontend Electron: React, TypeScript, tailwindcss ya realizado
Database: postgresql + vector
DataLake: parket + MinIO
Authentication: JWT

