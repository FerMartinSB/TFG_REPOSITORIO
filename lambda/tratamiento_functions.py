########################################################
#                                                      #
#               FUNCIONES DE TRATAMIENTO               #
#                                                      #
########################################################

import logging

from ask_sdk_model.interfaces.alexa.presentation.apl import RenderDocumentDirective
from ask_sdk_model.ui import AskForPermissionsConsentCard
from ask_sdk_model.interfaces.connections import SendRequestDirective
from ask_sdk_model.interfaces.tasks import CompleteTaskDirective
from ask_sdk_model.ui import SimpleCard, AskForPermissionsConsentCard
from ask_sdk_model.services.reminder_management import Trigger, TriggerType, AlertInfo, SpokenInfo, SpokenText, \
    PushNotification, PushNotificationStatus, ReminderRequest

from ask_sdk_model import Response
from datetime import datetime, date, timezone

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

#########################################################
#                                                       #
#                         APL                           #
#                                                       #
#########################################################

APL_DOCUMENT_ID_MUSICA = "Tratamiento_Uno_Musica"

APL_DOCUMENT_TOKEN = "documentToken"

DATASOURCE_MUSICA = {
    "audioPlayerTemplateData": {
        "type": "object",
        "properties": {
            "audioControlType": "skip",
            "audioSources": [
                "https://bucketfernando.s3.eu-west-1.amazonaws.com/relaxed-vlog-131746.mp3",
                "https://bucketfernando.s3.eu-west-1.amazonaws.com/a-small-miracle-132333.mp3",
                "https://bucketfernando.s3.eu-west-1.amazonaws.com/something-about-you-marilyn-ford-135781.mp3"
            ],
            "backgroundImage": "https://d2o906d8ln7ui1.cloudfront.net/images/response_builder/background-rose.png",
            "coverImageSource": "https://d2o906d8ln7ui1.cloudfront.net/images/response_builder/card-rose.jpeg",
            "headerTitle": "My favorite songs",
            "primaryText": "Relaxing Songs",
            "secondaryText": "Relaxing playlist",
            "sliderType": "determinate"
        }
    }
}

APL_DOCUMENT_ID_VIDEO_2 = "Video_Tratamiento1_Mindfullness"

APL_DOCUMENT_TOKEN = "documentToken"

DATASOURCE_VIDEO_2 = {
    "videoPlayerTemplateData": {
        "type": "object",
        "properties": {
            "backgroundImage": "https://d2o906d8ln7ui1.cloudfront.net/images/response_builder/background-green.png",
            "displayFullscreen": True,
            "headerTitle": "Mindfulness Video Playlist",
            "headerSubtitle": "",
            "videoControlType": "skip",
            "videoSources": [
                "https://bucketfernando.s3.eu-west-1.amazonaws.com/Pexels+Videos+2308576.mp4",
                "https://bucketfernando.s3.eu-west-1.amazonaws.com/pexels-karolina-grabowska-8136927.mp4"
            ],
            "sliderType": "determinate"
        }
    }
}


APL_DOCUMENT_ID_VIDEO_3 = "Video_Tratamiento_Uno_Relajacion"

APL_DOCUMENT_TOKEN = "documentToken"

DATASOURCE_VIDEO_3 = {
    "videoPlayerTemplateData": {
        "type": "object",
        "properties": {
            "backgroundImage": "https://d2o906d8ln7ui1.cloudfront.net/images/response_builder/background-green.png",
            "displayFullscreen": True,
            "headerTitle": "Relaxing Video Playlist",
            "headerSubtitle": "",
            "videoControlType": "jump10",
            "videoSources": [
                "https://bucketfernando.s3.eu-west-1.amazonaws.com/pexels-koolshooters-6981596.mp4",
                "https://s3.console.aws.amazon.com/s3/object/bucketfernando?region=eu-west-1&prefix=pexels-koolshooters-6981596.mp4"
            ],
            "sliderType": "determinate"
        }
    }
}

NOTIFY_MISSING_PERMISSIONS = ("Porfavor, habilita los permisos necesarios en la app de Alexa.")




#########################################################
#                                                       #
#                    CRONOMETROS                        #
#                                                       #
#########################################################

new_timer_request = {
    "duration": "PT30M",
    "timerLabel": "recordatorio",
    "creationBehavior": {
        "displayExperience": {
            "visibility": "VISIBLE"
        }
    },
    "triggeringBehavior": {
        "operation": {
            "type": "ANNOUNCE",
            "textToAnnounce": [{
                "locale": "es-ES",
                "text": "Ya han pasado 30 minutos, porfavor, abra el asistente de salud."
            }]
        },
        "notificationConfig": {
            "playAudible": True
        }
    }
}

#########################################################
#                                                       #
#                   TRATAMIENTO 1                       #
#                                                       #
#########################################################


def tratamiento_uno(handler_input):
    
    speak_output = ""
    try:
        user_name = handler_input.attributes_manager.session_attributes["user_name"]
        handler_input.attributes_manager.session_attributes["last_id"] = 6
    except:
        user_name = False

    if user_name:
        speak_output = (
            "Hola "
            + str(user_name)
            + ", deja que te aconseje música relajante o prefieres otras opciones: puedes escoger entre una sesión de mindfulness, una sesión de relajación o la reproducción de la lista de música"
        )
    else:
        reprompt = "Porfavor, digame su nombre. "
        handler_input.response_builder.ask(reprompt)

    return (
        handler_input.response_builder.speak(speak_output).set_should_end_session(
        False)
        .ask(speak_output)
        .response
    )


def tratamiento_uno_mindfulnes(skill, handler_input):
    
    if skill.supports_apl(handler_input):
        handler_input.response_builder.add_directive(
            RenderDocumentDirective(
                token=APL_DOCUMENT_TOKEN,
                document={
                    "type": "Link",
                    "src": f"doc://alexa/apl/documents/{APL_DOCUMENT_ID_VIDEO_2}"
                },
                datasources=DATASOURCE_VIDEO_2
            )
        )
    
    speak_output = "Reproduciendo..."
    handler_input.attributes_manager.session_attributes["last_id"] = 0
    handler_input.response_builder.speak(speak_output).set_should_end_session(
        False)



def tratamiento_uno_relajacion(skill, handler_input):
    
    if skill.supports_apl(handler_input):
        handler_input.response_builder.add_directive(
            RenderDocumentDirective(
                token=APL_DOCUMENT_TOKEN,
                document={
                    "type": "Link",
                    "src": f"doc://alexa/apl/documents/{APL_DOCUMENT_ID_VIDEO_3}"
                },
                datasources=DATASOURCE_VIDEO_3
            )
        )
    
    speak_output = "Reproduciendo..."
    handler_input.attributes_manager.session_attributes["last_id"] = 0
    handler_input.response_builder.speak(speak_output).set_should_end_session(
        False)


def tratamiento_uno_musica(skill, handler_input):
    
    if skill.supports_apl(handler_input):
        handler_input.response_builder.add_directive(
            RenderDocumentDirective(
                token=APL_DOCUMENT_TOKEN,
                document={
                    "type": "Link",
                    "src": f"doc://alexa/apl/documents/{APL_DOCUMENT_ID_MUSICA}"
                },
                datasources=DATASOURCE_MUSICA
            )
        )
    
    speak_output = "Reproduciendo..."
    handler_input.attributes_manager.session_attributes["last_id"] = 0
    handler_input.response_builder.speak(speak_output).set_should_end_session(
        False)



#########################################################
#                                                       #
#                   TRATAMIENTO 2                       #
#                                                       #
#########################################################



def tratamiento_dos(handler_input):
    
    speak_output = ""
    try:
        user_name = handler_input.attributes_manager.session_attributes["user_name"]
        handler_input.attributes_manager.session_attributes["last_id"] = 7
    except:
        user_name = False

    if user_name:
        speak_output = (
            "No te preocupes  "
            + str(user_name)
            + ",¿quieres que avise a algún contacto de tu lista para que te ayude?"
        )
    else:
        reprompt = "Porfavor, digame su nombre. "
        handler_input.response_builder.ask(reprompt)

    return (
        handler_input.response_builder.speak(speak_output).set_should_end_session(
        False)
        .ask(speak_output)
        .response
    )


def yes_tratamiento_dos_part1(handler_input):
    
    speak_output = "¿Con quién quieres que contacte?"

    handler_input.attributes_manager.session_attributes["last_id"] = 8

    return (
        handler_input.response_builder.speak(speak_output).set_should_end_session(
        False)
        .ask(speak_output)
        .response
    )


def tratamiento_dos_llamadaTelefonica(handler_input):
    
    call_name = handler_input.request_envelope.request.intent.slots["contacto"].value

    speak_output = (
        "Quieres llamar a "
        + str(call_name)
        + " , pero falta implementacion de la llamada telefonica"
    )

    handler_input.attributes_manager.session_attributes["last_id"] = 0

    return (
        handler_input.response_builder.speak(speak_output).set_should_end_session(
        False)
        .ask(speak_output)
        .response
    )


def no_tratamiento_dos_part1(handler_input):
    
    speak_output = "Recuerda que la toma de medicación de manera adecuada es esencial para tu mejora. ¿Estás seguro de que no quieres que contacte con alguien que pueda ayudarte?"
    handler_input.attributes_manager.session_attributes["last_id"] = 9

    return (
        handler_input.response_builder.speak(speak_output).set_should_end_session(
        False)
        .ask(speak_output)
        .response
    )


def yes_tratamiento_dos_part2(handler_input):
    
    speak_output = "¿Quieres que vuelva a preguntarte más tarde?"

    handler_input.attributes_manager.session_attributes["last_id"] = 22

    return (
        handler_input.response_builder.speak(speak_output).set_should_end_session(
        False)
        .ask(speak_output)
        .response
    )



def yes_tratamiento_dos_part3(handler_input):
    
    speak_output = "¿Cuándo quieres que te pregunte?"

    handler_input.attributes_manager.session_attributes["last_id"] = 23

    return (
        handler_input.response_builder.speak(speak_output).set_should_end_session(
        False)
        .ask(speak_output)
        .response
    )


def tratamiento_dos_recordatorio(handler_input):
    
    req_envelope = handler_input.request_envelope
    response_builder = handler_input.response_builder
    
    # Check if user gave permissions to create reminders.
    # If not, request to provide permissions to the skill.
    
    if not (req_envelope.context.system.user.permissions and
            req_envelope.context.system.user.permissions.consent_token):
        response_builder.speak(NOTIFY_MISSING_PERMISSIONS)
        response_builder.add_directive(
            SendRequestDirective(
                name="AskFor",
                payload= {
                    "@type": "AskForPermissionsConsentRequest",
                    "@version": "1",
                    "permissionScope": "alexa::alerts:reminders:skill:readwrite"
                },
                token= "correlationToken"
            )
        )
        return response_builder.response
    
    reminder_client = handler_input.service_client_factory.get_reminder_management_service()
    
    time = handler_input.request_envelope.request.intent.slots[
        "hora_tratamiento_dos"
    ].value

    arg_date = None
    
    if "fecha_tratamiento_dos" in handler_input.attributes_manager.session_attributes:

        arg_date = handler_input.attributes_manager.session_attributes["fecha_tratamiento_dos"]
    
    else:
        
        arg_date = date.today()

    
    time_list = str(time).split(':')
    
    date_list = str(arg_date).split('-')

    handler_input.attributes_manager.session_attributes["last_id"] = 0
    
    try:
        
        reminder_date = datetime(int(date_list[0]), int(date_list[1]), int(date_list[2]), int(time_list[0]), int(time_list[1]))
        notification_time = reminder_date.strftime("%Y-%m-%dT%H:%M:%S")
        
        reminder_request=ReminderRequest(
                request_time=notification_time,
                trigger=Trigger(
                    object_type=TriggerType.SCHEDULED_ABSOLUTE,
                    scheduled_time=notification_time,
                    offset_in_seconds=60),
                alert_info=AlertInfo(
                    spoken_info=SpokenInfo(
                        content=[SpokenText(locale="es-ES", text="Abra el asistente de salud")])),
                push_notification=PushNotification(
                    status=PushNotificationStatus.ENABLED))
        reminder_response = reminder_client.create_reminder(reminder_request) # type: ReminderResponse

        speech_text = "El recordatorio se ha fijado para el  " + str(arg_date) + " a las " + str(time) + " . Si en algún momento necesitas cambiar el recordatorio indica “recordatorio de medicación” y podrás establecer un nuevo recordatorio"
        
        

        
        return handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard(
                "Recordatorio fijado para el dia " + str(arg_date) + " a las " + str(time))).response

    except ServiceException as e:
        logger.info("Exception encountered : {}".format(e.body))
        logger.info(str(e))
        speech_text = "Ups. Parece que algo ha ido mal. Vuelve a intentarlo mas tarde"
        return handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard(
                "Recordatorio no creado",str(e.body))).response  


def no_tratamiento_dos_part3(handler_input):
    
    speak_output = "Intenta entonces comprarla más tarde."

    handler_input.attributes_manager.session_attributes["last_id"] = 0

    return (
        handler_input.response_builder.speak(speak_output).set_should_end_session(
        False)
        .ask(speak_output)
        .response
    )


#########################################################
#                                                       #
#                   TRATAMIENTO 3 y 4                   #
#                                                       #
#########################################################


def tratamiento_tres(handler_input):
    
    speak_output = ""
    try:
        user_name = handler_input.attributes_manager.session_attributes["user_name"]
        handler_input.attributes_manager.session_attributes["last_id"] = 10
    except:
        user_name = False

    if user_name:
        speak_output = (
            "Hola "
            + str(user_name)
            + ",si no estás seguro/a, no debes tomar una dosis ahora. ¿Quieres que te recuerde todos los días las horas a las que debes tomar la medicación?"
        )
    else:
        reprompt = "Porfavor, digame su nombre. "
        handler_input.response_builder.ask(reprompt)

    return (
        handler_input.response_builder.speak(speak_output).set_should_end_session(
        False)
        .ask(speak_output)
        .response
    ) 


def no_tratamiento_tres(handler_input):
    
    speak_output = "De acuerdo. Si en otro momento quieres hacer un recordatorio de toma de medicación indica “recordatorio de medicación” y lo podrás establecer para los días y horas que necesites"
    handler_input.attributes_manager.session_attributes["last_id"] = 0

    return (
        handler_input.response_builder.speak(speak_output).set_should_end_session(
        False)
        .ask(speak_output)
        .response
    )


def tratamiento_cuatro(handler_input):
    
    handler_input.attributes_manager.session_attributes["last_id"] = 11

    speak_output = "¿Para qué días quieres establecer el recordatorio?"

    return (
        handler_input.response_builder.speak(speak_output).set_should_end_session(
        False)
        .ask(speak_output)
        .response
    )


def tratamiento_cuatro_fijarDia(handler_input):
    
    date = handler_input.request_envelope.request.intent.slots["dia_recordatorio"].value

    handler_input.attributes_manager.session_attributes["dia_recordatorio"] = date

    speak_output = "¿A qué hora debo recordarte la toma de medicación?"

    return (
        handler_input.response_builder.speak(speak_output).set_should_end_session(
        False)
        .ask(speak_output)
        .response
    )


def tratamiento_cuatro_fijarHora(handler_input):
    
    req_envelope = handler_input.request_envelope
    response_builder = handler_input.response_builder
    
    # Check if user gave permissions to create reminders.
    # If not, request to provide permissions to the skill.
    
    if not (req_envelope.context.system.user.permissions and
            req_envelope.context.system.user.permissions.consent_token):
        response_builder.speak(NOTIFY_MISSING_PERMISSIONS)
        response_builder.add_directive(
            SendRequestDirective(
                name="AskFor",
                payload= {
                    "@type": "AskForPermissionsConsentRequest",
                    "@version": "1",
                    "permissionScope": "alexa::alerts:reminders:skill:readwrite"
                },
                token= "correlationToken"
            )
        )
        return response_builder.response

    reminder_client = handler_input.service_client_factory.get_reminder_management_service()
    
    time = handler_input.request_envelope.request.intent.slots["hora_recordatorio"].value

    date = None

    if "dia_recordatorio" in handler_input.attributes_manager.session_attributes:

        date = handler_input.attributes_manager.session_attributes["dia_recordatorio"]
    
    time_list = str(time).split(':')
    
    date_list = str(date).split('-')


    try:

        reminder_date = datetime(int(date_list[0]), int(date_list[1]), int(date_list[2]), int(time_list[0]), int(time_list[1]))
        notification_time = reminder_date.strftime("%Y-%m-%dT%H:%M:%S")
        
        trigger = Trigger(object_type = TriggerType.SCHEDULED_ABSOLUTE , scheduled_time = notification_time ,time_zone_id = "Europe/Madrid")
        text = SpokenText(locale='es-ES', ssml = "<speak> Recordatorio de medicación</speak>", text= 'Recordatorio de medicación, porfavor toma tu medicina.')
        alert_info = AlertInfo(SpokenInfo([text]))
        push_notification = PushNotification(PushNotificationStatus.ENABLED)
        reminder_request = ReminderRequest(notification_time, trigger, alert_info, push_notification)
        
        reminder_response = reminder_client.create_reminder(reminder_request) # type: ReminderResponse

        speech_text = "El recordatorio se ha fijado para el  " + str(date) + " a las " + str(time) + " . Si en algún momento necesitas cambiar el recordatorio indica “recordatorio de medicación” y podrás establecer un nuevo recordatorio"
        
        

        
        return handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard(
                "Recordatorio fijado para el dia " + str(date) + " a las " + str(time))).response

    except ServiceException as e:
        logger.info("Exception encountered : {}".format(e.body))
        logger.info(str(e))
        speech_text = "Ups. Parece que algo ha ido mal. Vuelve a intentarlo mas tarde"
        return handler_input.response_builder.speak(speech_text).set_card(
            SimpleCard(
                "Recordatorio no creado",str(e.body))).response



#########################################################
#                                                       #
#                   TRATAMIENTO 5                       #
#                                                       #
#########################################################



def tratamiento_cinco(handler_input):
    
    handler_input.attributes_manager.session_attributes["last_id"] = 12

    user_name = handler_input.attributes_manager.session_attributes["user_name"]

    speak_output = "Hola " + str(user_name) + ", ¿te encuentras muy mal?"

    return (
        handler_input.response_builder.speak(speak_output)
        .ask(speak_output)
        .response
    )


def yes_tratamiento_cuatro_part1(handler_input):
    
    speak_output = "Te aconsejo que llames al doctor para consultar ¿quieres que llame?"
    handler_input.attributes_manager.session_attributes["last_id"] = 13

    return (
        handler_input.response_builder.speak(speak_output).set_should_end_session(
        False)
        .ask(speak_output)
        .response
    )


def yes_tratamiento_cuatro_part2(handler_input):
    
    speak_output = "Llamando a su Doctor/a"
    handler_input.attributes_manager.session_attributes["last_id"] = 0

    return (
        handler_input.response_builder.speak(speak_output).set_should_end_session(
        False)
        .ask(speak_output)
        .response
    )


def no_tratamiento_cuatro_part1(handler_input):
    
    speak_output = "Vamos a esperar un rato a ver si se te pasa, si no se te pasa y te encuentras peor, deberíamos llamar al doctor. ¿Quieres que volvamos a comprobar cómo te encuentras dentro de media hora?"
    handler_input.attributes_manager.session_attributes["last_id"] = 14

    return (
        handler_input.response_builder.speak(speak_output).set_should_end_session(
        False)
        .ask(speak_output)
        .response
    )


def no_tratamiento_cuatro_part3(handler_input):
    
    speak_output = "También puedo contactar con alguien de tu lista de contactos, ¿Quieres que llame a alguien? "
    handler_input.attributes_manager.session_attributes["last_id"] = 0

    return (
        handler_input.response_builder.speak(speak_output).set_should_end_session(
        False)
        .ask(speak_output)
        .response
    )


def yes_tratamiento_cuatro_part3_contador(handler_input):
    
    req_envelope = handler_input.request_envelope
    response_builder = handler_input.response_builder
    
    
    if not (req_envelope.context.system.user.permissions and
            req_envelope.context.system.user.permissions.consent_token):

        return response_builder.add_directive(
            SendRequestDirective(
                name="AskFor",
                payload= {
                    "@type": "AskForPermissionsConsentRequest",
                    "@version": "1",
                    "permissionScope": "alexa::alerts:timers:skill:readwrite"
                },
                token= "correlationToken"
            )
        ).response

    timer_service = handler_input.service_client_factory.get_timer_management_service()
    timer_response = timer_service.create_timer(new_timer_request)
    
    if str(timer_response.status) == "Status.ON":
        session_attr = handler_input.attributes_manager.session_attributes
        if not session_attr:
            session_attr['lastTimerId'] = timer_response.id

        speech_text = 'De acuerdo, dentro de media hora volveré a comprobar como te encuentras .'
        handler_input.attributes_manager.persistent_attributes["timer_flag"] = True

        handler_input.attributes_manager.save_persistent_attributes()
        
    else:
        speech_text = 'Ha habido un error con el recordatorio de media hora'

    return (
        handler_input.response_builder
        .speak(speech_text).set_should_end_session(
        False)
        .response
    )


def tratamiento_cinco_vueltaContador(handler_input):
    
    handler_input.attributes_manager.session_attributes["last_id"] = 15
        
    user_name = handler_input.attributes_manager.session_attributes["user_name"]

    speak_output = "Hola de nuevo " + str(user_name) + ", ¿como te encuentras?"

    return (
        handler_input.response_builder.speak(speak_output).set_should_end_session(
        False)
        .ask(speak_output)
        .response
    )  


def tratamiento_cinco_mejorEstado(handler_input):
    
    handler_input.attributes_manager.session_attributes["last_id"] = 0
        
    user_name = handler_input.attributes_manager.session_attributes["user_name"]

    speak_output = "Estupendo " + str(user_name) + ", que tengas un buen día"

    return (
        handler_input.response_builder.speak(speak_output).set_should_end_session(
        False)
        .ask(speak_output)
        .response
    )   




