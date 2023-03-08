# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import ask_sdk_core.utils as ask_utils
import webbrowser
import json
import os
import boto3
import requests 


from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.skill_builder import CustomSkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.dispatch_components import AbstractRequestInterceptor
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_dynamodb.adapter import DynamoDbAdapter
from ask_sdk_core.api_client import DefaultApiClient
from ask_sdk_model.ui import AskForPermissionsConsentCard
from ask_sdk_model.interfaces.connections import SendRequestDirective
from ask_sdk_model.interfaces.tasks import CompleteTaskDirective
from ask_sdk_core.utils import is_intent_name, get_supported_interfaces

from ask_sdk_model.interfaces.alexa.presentation.apl import RenderDocumentDirective

from ask_sdk_model.services.reminder_management import Trigger, TriggerType, AlertInfo, SpokenInfo, SpokenText, \
    PushNotification, PushNotificationStatus, ReminderRequest

from ask_sdk_model.services import ServiceException

from ask_sdk_model.ui import SimpleCard, AskForPermissionsConsentCard
from ask_sdk_model import Response

from bs4 import BeautifulSoup
from datetime import datetime, date

from urllib.request import Request, urlopen
from pytz import timezone

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

ddb_region = os.environ.get("DYNAMODB_PERSISTENCE_REGION")
ddb_table_name = os.environ.get("DYNAMODB_PERSISTENCE_TABLE_NAME")

ddb_resource = boto3.resource("dynamodb", region_name=ddb_region)
dynamodb_adapter = DynamoDbAdapter(
    table_name=ddb_table_name, create_table=False, dynamodb_resource=ddb_resource
)


sb = CustomSkillBuilder(api_client=DefaultApiClient(), persistence_adapter=dynamodb_adapter)

permissions = ["alexa::alerts:reminders:skill:readwrite"]
NOTIFY_MISSING_PERMISSIONS = ("Please enable Reminders permissions in "
                              "the Amazon Alexa app.")

# Datos relacionados con el cronometro de Tratamiento 4

new_timer_request = {
    "duration": "PT15S",
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

# Datos relacionados con el lenguaje APL necesario para la carga de videos 


APL_DOCUMENT_ID_VIDEO_1 = "Video_Sintomologia_4_5"

APL_DOCUMENT_TOKEN = "documentToken"

DATASOURCE_VIDEO_1 = {
    "videoPlayerTemplateData": {
        "type": "object",
        "properties": {
            "backgroundImage": "https://d2o906d8ln7ui1.cloudfront.net/images/response_builder/background-green.png",
            "displayFullscreen": True,
            "headerTitle": "VIDEO DE RELAJACION",
            "headerSubtitle": "",
            "logoUrl": "https://d2o906d8ln7ui1.cloudfront.net/images/response_builder/logo-world-of-plants-2.png",
            "videoControlType": "skip",
            "videoSources": [
                "https://bucketfernando.s3.eu-west-1.amazonaws.com/video_prueba.mov",
                "https://bucketfernando.s3.eu-west-1.amazonaws.com/Video_prueba2.mov"
            ],
            "sliderType": "determinate"
        }
    }
}

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



# Clases que dirigen las conversaciones

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        # Verifica si el usuario ha proporcionado permisos para acceder al perfil del cliente

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response


        persistent_attributes = handler_input.attributes_manager.persistent_attributes

        session_attributes = handler_input.attributes_manager.session_attributes
        
        handler_input.attributes_manager.delete_persistent_attributes()
        
        
        if "timer_flag" not in persistent_attributes:
            
            persistent_attributes["timer_flag"] = False

        if "user_name" not in persistent_attributes:
            
            speak_output = "Bienvenido al asistente de salud, cual es su nombre?"
        
        else:
            
            
            if persistent_attributes["timer_flag"] is False:

                nombre = persistent_attributes["user_name"] 
                
                session_attributes["user_name"] = nombre
                
                speak_output = "Bienvenido al asistente de salud " + str(nombre) + ", como te encuentras?"
            
            else: 
                nombre = persistent_attributes["user_name"] 
                
                session_attributes["user_name"] = nombre
                    
                speak_output = "Hola de nuevo " + str(nombre) + ", ¿cómo te encuentras?"
                
                handler_input.attributes_manager.persistent_attributes["timer_flag"] = False

                handler_input.attributes_manager.save_persistent_attributes()
                
                handler_input.attributes_manager.session_attributes["last_id"] = 15
            
        return (
            handler_input.response_builder.speak(speak_output).set_should_end_session(
            False)
            # .ask(speak_output)
            .response
        )

class Get_Nombre_IntentHandler(AbstractRequestHandler):
    """Handler for Get_Nombre."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("Get_Nombre")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
            
        session_attributes = handler_input.attributes_manager.session_attributes    
        
        user_name = handler_input.request_envelope.request.intent.slots["nombre"].value

        handler_input.attributes_manager.persistent_attributes["user_name"] = user_name
        
        handler_input.attributes_manager.save_persistent_attributes()
        
        session_attributes["user_name"] = user_name
        
        speak_output = "Hola " + str(user_name) + ", que es lo que deseas?"
        
        
        return (
            handler_input.response_builder.speak(speak_output).set_should_end_session(
            False)
            # .ask(speak_output)
            .response
        )

#########################################################
#                                                       #
#               SINTOMOLOGIA Y APATIA 1                 #
#                                                       #
#########################################################


class Sintomologia_Cansancio_Apatia_Uno_IntentHandler(AbstractRequestHandler):
    """Handler for Sintomologia_Cansancio_Apatia_Uno."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("Sintomologia_Cansancio_Apatia_Uno")(
            handler_input
        )

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        speak_output = ""

        try:
            user_name = handler_input.attributes_manager.session_attributes["user_name"]
            handler_input.attributes_manager.session_attributes["last_id"] = 1
        except:
            user_name = False

        if user_name:
            speak_output = (
                "Hola "
                + str(user_name)
                + " ,¿Tenías algo planificado para hacer hoy?"
            )

        else:
            reprompt = "Porfavor, digame su nombre. "
            handler_input.response_builder.ask(reprompt)

        return (
            handler_input.response_builder.speak(speak_output).set_should_end_session(
            False)
            # .ask(speak_output)
            .response
        )


# HANDLERS DE SI Y NO PARA PRIMERA PREGUNTA DE SINTOMOLOGIA 1


class YesIntentHandler_Sint_1(AbstractRequestHandler):
    """Handler for Yes Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (
            ask_utils.is_intent_name("AMAZON.YesIntent")(handler_input)
            and handler_input.attributes_manager.session_attributes["last_id"] == 1
        )

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        speak_output = "¿Tienes que ir a trabajar o era una actividad de ocio?"
        handler_input.attributes_manager.session_attributes["last_id"] = 17

        return (
            handler_input.response_builder.speak(speak_output).set_should_end_session(
            False)
            .ask(speak_output)
            .response
        )



class Sintomologia_Cansancio_Apatia_Uno_Ocio_IntentHandler(AbstractRequestHandler):
    """Handler for Sintomologia_Cansancio_Apatia_Uno."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("Sintomologia_Cansancio_Apatia_Uno_Ocio")(
            handler_input
        )

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        speak_output = "Piensa que las actividades de ocio son una buena alternativa cuando sentimos que el día a día nos supera ya que nos conectan con el mundo y los demás. \
                        Intenta pensar en ocasiones anteriores que has realizado dicha actividad y rememora los sentimientos positivos que viviste. \
                        Con estos sentimientos llénate de fuerza para salir a realizar tus planes y una vez lo hayas comenzado y finalizado verás que merece la pena"
        handler_input.attributes_manager.session_attributes["last_id"] = 0

        return (
            handler_input.response_builder.speak(speak_output).set_should_end_session(
            False)
            .ask(speak_output)
            .response
        )

class Sintomologia_Cansancio_Apatia_Uno_Trabajo_IntentHandler(AbstractRequestHandler):
    """Handler for Sintomologia_Cansancio_Apatia_Uno."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("Sintomologia_Cansancio_Apatia_Uno_Trabajo")(
            handler_input
        )

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        speak_output = ""

        try:
            user_name = handler_input.attributes_manager.session_attributes["user_name"]
            handler_input.attributes_manager.session_attributes["last_id"] = 20
        except:
            user_name = False

        if user_name:
            speak_output = (
                "No te preocupes "
                + str(user_name)
                + "Todos en algún momento sentimos que las responsabilidades nos superan, de todas formas, ten en cuenta que las rutinas que llevamos a cabo día a día nos ayudan a conectarnos con el mundo y los demás. \
                   Aunque en ocasiones es difícil comenzarlas, una vez puedas tomar fuerza y comenzar a llevarlas a cabo podrá sentirte mejor al ver que has conseguido superarlas una vez más. \
                   De todas formas, si sientes que hoy no puedes llevarlo a cabo, puedo ayudarte a comunicarlo a X (persona que haya establecido de su agenda)."
            )

        else:
            reprompt = "Porfavor, digame su nombre. "
            handler_input.response_builder.ask(reprompt)

        return (
            handler_input.response_builder.speak(speak_output).set_should_end_session(
            False)
            # .ask(speak_output)
            .response
        )





class CarteleraIntentHandler_Sint_1(AbstractRequestHandler):
    """Handler for No Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (
            ask_utils.is_intent_name("AMAZON.NoIntent")(handler_input)
            and handler_input.attributes_manager.session_attributes["last_id"] == 1
        )

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response


        try:
            user_name = handler_input.attributes_manager.session_attributes["user_name"]
            handler_input.attributes_manager.session_attributes["last_id"] = 2
        except:
            user_name = False

        if user_name:

            speak_output = str(user_name) + ", seguramente haya actividades que puedan cambiar esa sensación. \
                            Quizá sea buena idea contactar con X (persona que haya establecido de su agenda) para hacer alguna actividad. \
                            Podríais salir a tomar un café, ir al cine o ver una exposición. \
                            ¿Quieres que te diga la cartelera?"

        else:
            reprompt = "Porfavor, digame su nombre. "
            handler_input.response_builder.ask(reprompt)


        return (
            handler_input.response_builder.speak(speak_output).set_should_end_session(
            False)
            .ask(speak_output)
            .response
        )


##HANDLERS DE SI Y NO PARA PREGUNTA DE CARTELERA DE SINTOMOLOGIA 1


class YesIntentHandler_Cartelera_Sint_1(AbstractRequestHandler):
    """Handler for Yes Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (
            ask_utils.is_intent_name("AMAZON.YesIntent")(handler_input)
            and handler_input.attributes_manager.session_attributes["last_id"] == 2
        )

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        url = "https://www.abc.es/play/cine/cartelera/madrid/?ref=https%3A%2F%2Fwww.google.com%2F"

        request_site = Request(url, headers={"User-Agent": "Mozilla/5.0"})

        datos = urlopen(request_site).read()

        soup = BeautifulSoup(datos, "html.parser")

        tags = soup.find_all("span", {"titular xs"})

        speak_output = "Hay varias peliculas disponibles, algunas de ellas son: "

        for tag in tags[:9]:
            speak_output = speak_output + str(tag.getText()) + ", "

        speak_output = (
            speak_output
            + "o "
            + str(tags[10].getText())
            + ", ¿Quieres que llame a X (persona que haya establecido de su agenda)?"
        )

        handler_input.attributes_manager.session_attributes["last_id"] = 18
        # speak_output = 'Falta configuracion de cartelera'

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


class MuseoIntentHandler_Sint_1(AbstractRequestHandler):
    """Handler for Yes Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (
            ask_utils.is_intent_name("AMAZON.NoIntent")(handler_input)
            and (handler_input.attributes_manager.session_attributes["last_id"] == 2 or handler_input.attributes_manager.session_attributes["last_id"] == 18) 
        )

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        speak_output = "¿Quieres que te proponga alguna exposición disponible en tu localidad?"
        handler_input.attributes_manager.session_attributes["last_id"] = 3

        return (
            handler_input.response_builder.speak(speak_output).set_should_end_session(
            False)
            .ask(speak_output)
            .response
        )


##HANDLERS DE SI Y NO PARA PREGUNTA DE MUSEOS DE SINTOMOLOGIA 1


class YesIntentHandler_Museo_Sint_1(AbstractRequestHandler):
    """Handler for Yes Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (
            ask_utils.is_intent_name("AMAZON.YesIntent")(handler_input)
            and handler_input.attributes_manager.session_attributes["last_id"] == 3
        )

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        handler_input.attributes_manager.session_attributes["last_id"] = 3
        speak_output = "¿Cual es tu localidad?"

        return (
            handler_input.response_builder.speak(speak_output).set_should_end_session(
            False)
            .ask(speak_output)
            .response
        )


class Localidad_Museo_Sint_1_IntentHandler(AbstractRequestHandler):
    """Handler for Yes Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (
            ask_utils.is_intent_name("Localidad_Museo_Sint_Uno")(handler_input)
            and handler_input.attributes_manager.session_attributes["last_id"] == 3
        )

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        handler_input.attributes_manager.session_attributes["last_id"] = 19

        speak_output = "No se han encontrado museos en su localidad"

        file = open("museos.json")

        datos_JSON = json.load(file)
        try:
            localidad = handler_input.request_envelope.request.intent.slots[
                "Localidad"
            ].value

        except:
            speak_output = "fallo"

        for ciudad in datos_JSON["ciudad"]:
            if ciudad["nombre"] == str(localidad):

                speak_output = "En tu localidad se encuentran los siguientes museos: "

                for museo in ciudad["museos"][:-1]:

                    speak_output = speak_output + museo + ", "

                speak_output = speak_output + "y " + ciudad["museos"][-1] + ". \
                ¿Quieres que llame a X (persona que haya establecido de su agenda)?"
                

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


class NoIntentHandler_Museo_Sint_1(AbstractRequestHandler):
    """Handler for Yes Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (
            ask_utils.is_intent_name("AMAZON.NoIntent")(handler_input)
            and handler_input.attributes_manager.session_attributes["last_id"] == 3
        )

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        user_name = handler_input.attributes_manager.session_attributes["user_name"]
        speak_output = (
            "¿Quieres que llame a X (persona que haya establecido de su agenda)?"
        )
        handler_input.attributes_manager.session_attributes["last_id"] = 16

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )

class NoIntentHandler_Llamada_Sint_1(AbstractRequestHandler):
    """Handler for Yes Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (
            ask_utils.is_intent_name("AMAZON.NoIntent")(handler_input)
            and (handler_input.attributes_manager.session_attributes["last_id"] == 16 \
            or handler_input.attributes_manager.session_attributes["last_id"] == 19)
        )

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        user_name = handler_input.attributes_manager.session_attributes["user_name"]
        speak_output = (
            "No te preocupes "
            + str(user_name)
            + ",Todos en algún momento sentimos que el día a día nos supera. Tómate un tiempo de descanso mientras lees un libro o algo que te interesa, \
                escuchas música relajante, o realizas un mándala."
        )
        handler_input.attributes_manager.session_attributes["last_id"] = 0

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


class NoIntentHandler_Trabajo_Sint_1(AbstractRequestHandler):
    """Handler for Yes Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (
            ask_utils.is_intent_name("AMAZON.NoIntent")(handler_input)
            and handler_input.attributes_manager.session_attributes["last_id"] == 20
        )

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        user_name = handler_input.attributes_manager.session_attributes["user_name"]
        speak_output = (
            "Bien "
            + str(user_name)
            + ". Espero haberte ayudado. Si me necesitas en otro momento, vuelve a pedirme ayuda. \
                Que tengas un buen día."
        )
        handler_input.attributes_manager.session_attributes["last_id"] = 0

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )

# FALTA IMPLEMENTACION DE LLAMADA TELEFONICA #

class YesIntentHandler_Llamada_Sint_1(AbstractRequestHandler):

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (
            ask_utils.is_intent_name("AMAZON.YesIntent")(handler_input)
            and (handler_input.attributes_manager.session_attributes["last_id"] == 20 \
            or handler_input.attributes_manager.session_attributes["last_id"] == 16 \
            or handler_input.attributes_manager.session_attributes["last_id"] == 18 \
            or handler_input.attributes_manager.session_attributes["last_id"] == 19)
        )

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        user_name = handler_input.attributes_manager.session_attributes["user_name"]
        speak_output = (
            "Llamar a X (persona que haya establecido de su agenda)"
        )
        handler_input.attributes_manager.session_attributes["last_id"] = 0

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


#########################################################
#                                                       #
#               SINTOMOLOGIA Y APATIA 2                 #
#                                                       #
#########################################################


class Sintomologia_Cansancio_Apatia_Dos_IntentHandler(AbstractRequestHandler):
    """Handler for Sintomologia_Cansancio_Apatia_Dos."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("Sintomologia_Cansancio_Apatia_Dos")(
            handler_input
        )

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        speak_output = ""
        try:
            user_name = handler_input.attributes_manager.session_attributes["user_name"]

        except:
            user_name = False

        if user_name:
            speak_output = (
                "Hola "
                + str(user_name)
                + " , todos en algún momento sentimos que el día a día nos supera y estamos agotados. Tómate un tiempo de descanso mientras lees un libro interesante"
            )

        else:
            reprompt = "Porfavor, digame su nombre. "
            handler_input.response_builder.ask(reprompt)

        return (
            handler_input.response_builder.speak(speak_output)
            # .ask(speak_output)
            .response
        )


#########################################################
#                                                       #
#               SINTOMOLOGIA Y APATIA 3                 #
#                                                       #
#########################################################


class Sintomologia_Cansancio_Apatia_Tres_IntentHandler(AbstractRequestHandler):
    """Handler for Sintomologia_Cansancio_Apatia_Tres."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("Sintomologia_Cansancio_Apatia_Tres")(
            handler_input
        )

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        speak_output = ""
        try:
            user_name = handler_input.attributes_manager.session_attributes["user_name"]

        except:
            user_name = False

        if user_name:

            speak_output = "Un consejo: aunque no tengas ganas ni fuerzas, intenta pasear un rato por casa. Si ves que no estás demasiado cansado, sal un rato a la calle a dar un paseo corto, seguro que después te encuentras mucho mejor. La falta de movimiento hace que te sientas más cansado, intenta moverte un poquito, por ejemplo, da un paseo corto alrededor de casa y después descansa si ves que lo necesitas. Si haces una rutina de paseo todos los días, irás recuperando fuerzas. Comienza con un paseo corto y a ritmo suave, y aumenta poco a poco el tiempo y el ritmo."

        else:
            reprompt = "Porfavor, digame su nombre. "
            handler_input.response_builder.ask(reprompt)

        return (
            handler_input.response_builder.speak(speak_output)
            # .ask(speak_output)
            .response
        )


#########################################################
#                                                       #
#               SINTOMOLOGIA Y APATIA 4 y 5             #
#                                                       #
#########################################################


class Sintomologia_Cansancio_Apatia_Cuatro_IntentHandler(AbstractRequestHandler):
    """Handler for Sintomologia_Cansancio_Apatia_Cuatro."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("Sintomologia_Cansancio_Apatia_Cuatro")(
            handler_input
        )

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = ""
        try:
            user_name = handler_input.attributes_manager.session_attributes["user_name"]
            handler_input.attributes_manager.session_attributes["last_id"] = 4
        except:
            user_name = False

        if user_name:
            speak_output = (
                "Hola "
                + str(user_name)
                + ", te propongo que salgas a pasear. Quizá esa sensación disminuya al hacer algo de ejercicio."
            )

        else:
            reprompt = "Porfavor, digame su nombre. "
            handler_input.response_builder.ask(reprompt)

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )

class Sintomologia_Cansancio_Apatia_Cuatro_YesIntentHandler(AbstractRequestHandler):
    """Handler for Sintomologia_Cansancio_Apatia_Cuatro."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (
            ask_utils.is_intent_name("AMAZON.YesIntent")(handler_input)
            and handler_input.attributes_manager.session_attributes["last_id"] == 4
        )

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = ""
        try:
            user_name = handler_input.attributes_manager.session_attributes["user_name"]
            handler_input.attributes_manager.session_attributes["last_id"] = 0
        except:
            user_name = False

        if user_name:
            speak_output = (
                str(user_name) + ", ¡fenomenal!, espero que vaya muy bien"
                )

        else:
            reprompt = "Porfavor, digame su nombre. "
            handler_input.response_builder.ask(reprompt)

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )
    

class Sintomologia_Cansancio_Apatia_Cuatro_NoIntentHandler(AbstractRequestHandler):
    """Handler for Sintomologia_Cansancio_Apatia_Cuatro."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (
            ask_utils.is_intent_name("AMAZON.NoIntent")(handler_input)
            and handler_input.attributes_manager.session_attributes["last_id"] == 4
        )

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        handler_input.attributes_manager.session_attributes["last_id"] = 21

        speak_output = ("Puedes hacer entonces algún ejercicio de relajación ¿quieres que te recomiende alguno?")

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


class Sintomologia_Cansancio_Apatia_Cinco_IntentHandler(AbstractRequestHandler):
    """Handler for Sintomologia_Cansancio_Apatia_Cuatro."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("Sintomologia_Cansancio_Apatia_Cinco")(
            handler_input
        )

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = ""
        try:
            user_name = handler_input.attributes_manager.session_attributes["user_name"]
            handler_input.attributes_manager.session_attributes["last_id"] = 21
        except:
            user_name = False

        if user_name:
            speak_output = (
                "Hola "
                + str(user_name)
                + ", no te preocupes, es normal que te sientas muy cansado/a por tu enfermedad. Para ir almacenando energía te aconsejo que te des un rato de descanso sentado en un sillón cómodo e intentes hacer algún ejercicio de relajación ¿quieres que te recomiende alguno?"
            )
        else:
            reprompt = "Porfavor, digame su nombre. "
            handler_input.response_builder.ask(reprompt)

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


class YesIntentHandler_Sint_4_and_5(AbstractRequestHandler):
    """Handler for Yes Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (
            ask_utils.is_intent_name("AMAZON.YesIntent")(handler_input)
            and handler_input.attributes_manager.session_attributes["last_id"] == 21
        )

    def supports_apl(self, handler_input):
        # Checks whether APL is supported by the User's device
        supported_interfaces = get_supported_interfaces(
            handler_input)

        return supported_interfaces.alexa_presentation_apl != None

    def launch_screen(self, handler_input):
        # Only add APL directive if User's device supports APL
        
        speak_output = "Error al cargar el video"
        handler_input.attributes_manager.session_attributes["last_id"] = 0
        
        if self.supports_apl(handler_input):
            
            handler_input.response_builder.add_directive(
                RenderDocumentDirective(
                    token=APL_DOCUMENT_TOKEN,
                    document={
                        "type": "Link",
                        "src": f"doc://alexa/apl/documents/{APL_DOCUMENT_ID_VIDEO_1}"
                    },
                    datasources=DATASOURCE_VIDEO_1
                )
            )
            
            speak_output = "Abriendo video"
        
        handler_input.response_builder.speak(speak_output)
            
    def handle(self, handler_input):
        # Add APL Template if device is compatible
        self.launch_screen(handler_input)
        # Generate JSON Response
        return handler_input.response_builder.response


class NoIntentHandler_Sint_4_and_5(AbstractRequestHandler):
    """Handler for No Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (
            ask_utils.is_intent_name("AMAZON.NoIntent")(handler_input)
            and handler_input.attributes_manager.session_attributes["last_id"] == 21
        )

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        speak_output = "También Puedes llamar a alguna persona de tu lista de contactos favoritos para tener un rato de conversación agradable, eso puede hacer que te sientas mejor. ¿Quieres que llame a X? "
        handler_input.attributes_manager.session_attributes["last_id"] = 5

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


# -------- FALTA IMPLEMENTACION--------#


class YesIntentHandler_Sint_4_and_5_part2(AbstractRequestHandler):
    """Handler for Yes Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (
            ask_utils.is_intent_name("AMAZON.YesIntent")(handler_input)
            and handler_input.attributes_manager.session_attributes["last_id"] == 5
        )

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        speak_output = "Llamar a X"
        handler_input.attributes_manager.session_attributes["last_id"] = 0

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


class NoIntentHandler_Sint_4_and_5_part2(AbstractRequestHandler):
    """Handler for No Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (
            ask_utils.is_intent_name("AMAZON.NoIntent")(handler_input)
            and handler_input.attributes_manager.session_attributes["last_id"] == 5
        )

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        user_name = handler_input.attributes_manager.session_attributes["user_name"]

        speak_output = (
            "Tranquilo "
            + str(user_name)
            + ". Todos en algún momento sentimos que el día a día nos supera y estamos agotados. Puedes tomarte un tiempo de descanso mientras lees un libro interesante"
        )
        handler_input.attributes_manager.session_attributes["last_id"] = 0

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


#########################################################
#                                                       #
#                   TRATAMIENTO 1                       #
#                                                       #
#########################################################


class Tratamiento_Uno_IntentHandler(AbstractRequestHandler):
    """Handler for Tratamiento_Uno."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("Tratamiento_Uno")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
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
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


class Tratamiento_Uno_Mindfulness_IntentHandler(AbstractRequestHandler):
    """Handler for No Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (
            ask_utils.is_intent_name("Tratamiento_Uno_Mindfulness")(handler_input)
            and handler_input.attributes_manager.session_attributes["last_id"] == 6
        )

    def supports_apl(self, handler_input):
        # Checks whether APL is supported by the User's device
        supported_interfaces = get_supported_interfaces(
            handler_input)
        return supported_interfaces.alexa_presentation_apl != None

    def launch_screen(self, handler_input):
        # Only add APL directive if User's device supports APL
        if self.supports_apl(handler_input):
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
        handler_input.response_builder.speak(speak_output)

    def handle(self, handler_input):
        # Add APL Template if device is compatible
        self.launch_screen(handler_input)
        # Generate JSON Response
        return handler_input.response_builder.response



class Tratamiento_Uno_Relajacion_IntentHandler(AbstractRequestHandler):
    """Handler for No Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (
            ask_utils.is_intent_name("Tratamiento_Uno_Relajacion")(handler_input)
            and handler_input.attributes_manager.session_attributes["last_id"] == 6
        )

    def supports_apl(self, handler_input):
        # Checks whether APL is supported by the User's device
        supported_interfaces = get_supported_interfaces(
            handler_input)
        return supported_interfaces.alexa_presentation_apl != None

    def launch_screen(self, handler_input):
        # Only add APL directive if User's device supports APL
        if self.supports_apl(handler_input):
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
        handler_input.response_builder.speak(speak_output)

    def handle(self, handler_input):
        # Add APL Template if device is compatible
        self.launch_screen(handler_input)
        # Generate JSON Response
        return handler_input.response_builder.response


class Tratamiento_Uno_Musica_IntentHandler(AbstractRequestHandler):
    """Handler for No Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (
            ask_utils.is_intent_name("Tratamiento_Uno_Musica")(handler_input)
            and handler_input.attributes_manager.session_attributes["last_id"] == 6
        )

    def supports_apl(self, handler_input):
        # Checks whether APL is supported by the User's device
        supported_interfaces = get_supported_interfaces(handler_input)
        
        return supported_interfaces.alexa_presentation_apl != None
        
    def launch_screen(self, handler_input):
        # Only add APL directive if User's device supports APL
        if self.supports_apl(handler_input):
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
        handler_input.response_builder.speak(speak_output)

    def handle(self, handler_input):
        # Add APL Template if device is compatible
        self.launch_screen(handler_input)
        # Generate JSON Response
        return handler_input.response_builder.response



#########################################################
#                                                       #
#                   TRATAMIENTO 2                       #
#                                                       #
#########################################################


class Tratamiento_Dos_IntentHandler(AbstractRequestHandler):
    """Handler for Tratamiento_Uno."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("Tratamiento_Dos")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
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
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


class Yes_IntentHandler_Tratamiento_Dos_Part1(AbstractRequestHandler):
    """Handler for Yes Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (
            ask_utils.is_intent_name("AMAZON.YesIntent")(handler_input)
            and handler_input.attributes_manager.session_attributes["last_id"] == 7
        ) or (
            ask_utils.is_intent_name("AMAZON.NoIntent")(handler_input)
            and handler_input.attributes_manager.session_attributes["last_id"] == 9
        )

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        speak_output = "¿Con quién quieres que contacte?"

        handler_input.attributes_manager.session_attributes["last_id"] = 8

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


# -------- FALTA IMPLEMENTACION--------#


class Tratamiento_Dos_LlamadaTelefonica_IntentHandler(AbstractRequestHandler):
    """Handler for Tratamiento_Dos_LlamadaTelefonica."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (
            ask_utils.is_intent_name("Tratamiento_Dos_LlamadaTelefonica")(handler_input)
            and handler_input.attributes_manager.session_attributes["last_id"] == 8
        )

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        call_name = handler_input.request_envelope.request.intent.slots[
            "contacto"
        ].value

        speak_output = (
            "Quieres llamar a "
            + str(call_name)
            + " , pero falta implementacion de la llamada telefonica"
        )

        handler_input.attributes_manager.session_attributes["last_id"] = 0

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


class No_IntentHandler_Tratamiento_Dos_Part1(AbstractRequestHandler):
    """Handler for No Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (
            ask_utils.is_intent_name("AMAZON.NoIntent")(handler_input)
            and handler_input.attributes_manager.session_attributes["last_id"] == 7
        )

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        speak_output = "Recuerda que la toma de medicación de manera adecuada es esencial para tu mejora. ¿Estás seguro de que no quieres que contacte con alguien que pueda ayudarte?"
        handler_input.attributes_manager.session_attributes["last_id"] = 9

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


class Yes_IntentHandler_Tratamiento_Dos_Part2(AbstractRequestHandler):
    """Handler for Yes Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (
            ask_utils.is_intent_name("AMAZON.YesIntent")(handler_input)
            and handler_input.attributes_manager.session_attributes["last_id"] == 9
        )

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        speak_output = "¿Quieres que vuelva a preguntarte más tarde?"

        handler_input.attributes_manager.session_attributes["last_id"] = 22

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


class Yes_IntentHandler_Tratamiento_Dos_Part3(AbstractRequestHandler):
    """Handler for Yes Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (
            ask_utils.is_intent_name("AMAZON.YesIntent")(handler_input)
            and handler_input.attributes_manager.session_attributes["last_id"] == 22
        )

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        speak_output = "¿Cuándo quieres que te pregunte?"

        handler_input.attributes_manager.session_attributes["last_id"] = 23

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


#######################################################################################################################>REVISAR ESTE INTENT

class Tratamiento_Dos_Recordatorio_IntentHandler(AbstractRequestHandler):
    """Handler for Yes Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (
            ask_utils.is_intent_name("Tratamiento_Dos_Recordatorio")(handler_input)
            and handler_input.attributes_manager.session_attributes["last_id"] == 23
        )

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        
        req_envelope = handler_input.request_envelope
        response_builder = handler_input.response_builder
        
        # Check if user gave permissions to create reminders.
        # If not, request to provide permissions to the skill.
        
        logger.info("PERMISOS REMINDER: " + str(req_envelope.context.system.user.permissions))
        
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
        
        logger.info("FECHA: " + str(arg_date) + ", HORA: " + str(time))
        
        time_list = str(time).split(':')
        
        date_list = str(arg_date).split('-')
        
        logger.info("FECHA: " + str(date_list) + ", HORA: " + str(time_list))

        handler_input.attributes_manager.session_attributes["last_id"] = 0
        
        try:
            
            logger.info("1")
            
            reminder_date = datetime(int(date_list[0]), int(date_list[1]), int(date_list[2]), int(time_list[0]), int(time_list[1]))

            logger.info("2")

            notification_time = reminder_date.strftime("%Y-%m-%dT%H:%M:%S")
            
            logger.info("3")
            
            
            response = reminders_api.create_reminder(
                RequestTime=notification_time,
                TriggerType='SCHEDULED_RELATIVE',
                AlertInfo={
                    'spokenInfo': {
                        'content': [{
                            'locale': 'es-ES',
                            'text': "Habra asistente virtual"
                        }]
                    }
                },
                PushNotification={
                    'status': 'ENABLED'
                }
            )
            
            reminder_request=ReminderRequest(
                    request_time=notification_time,
                    trigger=Trigger(
                        object_type=TriggerType.SCHEDULED_ABSOLUTE,
                        scheduled_time=notification_time,
                        offset_in_seconds=60),
                    alert_info=AlertInfo(
                        spoken_info=SpokenInfo(
                            content=[SpokenText(locale="es-ES", text="Habra asistente virtual")])),
                    push_notification=PushNotification(
                        status=PushNotificationStatus.ENABLED))
            logger.info("4")   
            
            reminder_response = reminder_client.create_reminder(reminder_request) # type: ReminderResponse

            logger.info("5")          
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

class No_IntentHandler_Tratamiento_Dos_Part3(AbstractRequestHandler):
    """Handler for Yes Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (
            ask_utils.is_intent_name("AMAZON.YesIntent")(handler_input)
            and handler_input.attributes_manager.session_attributes["last_id"] == 22
        )

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        speak_output = "Intenta entonces comprarla más tarde."

        handler_input.attributes_manager.session_attributes["last_id"] = 0

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )

#########################################################
#                                                       #
#                   TRATAMIENTO 3 y 4                   #
#                                                       #
#########################################################


class Tratamiento_Tres_IntentHandler(AbstractRequestHandler):
    """Handler for Tratamiento_Tres."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("Tratamiento_Tres")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
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
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


class No_IntentHandler_Tratamiento_Tres(AbstractRequestHandler):
    """Handler for No Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (
            ask_utils.is_intent_name("AMAZON.NoIntent")(handler_input)
            and handler_input.attributes_manager.session_attributes["last_id"] == 10
        )

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        speak_output = "De acuerdo. Si en otro momento quieres hacer un recordatorio de toma de medicación indica “recordatorio de medicación” y lo podrás establecer para los días y horas que necesites"
        handler_input.attributes_manager.session_attributes["last_id"] = 0

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


class Tratamiento_Cuatro_IntentHandler(AbstractRequestHandler):
    """Handler for Tratamiento_Tres."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("Tratamiento_Cuatro")(handler_input) or (
            ask_utils.is_intent_name("AMAZON.YesIntent")(handler_input)
            and handler_input.attributes_manager.session_attributes["last_id"] == 10
        )

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        handler_input.attributes_manager.session_attributes["last_id"] = 11

        speak_output = "¿Para qué días quieres establecer el recordatorio?"

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


class Tratamiento_Cuatro_FijarDia_IntentHandler(AbstractRequestHandler):
    """Handler for Tratamiento_Tres."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (
            ask_utils.is_intent_name("Tratamiento_Cuatro_FijarDia")(handler_input)
            and handler_input.attributes_manager.session_attributes["last_id"] == 11
        )

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        date = handler_input.request_envelope.request.intent.slots[
            "dia_recordatorio"
        ].value

        handler_input.attributes_manager.session_attributes["dia_recordatorio"] = date

        speak_output = "¿A qué hora debo recordarte la toma de medicación?"

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


class Tratamiento_Cuatro_FijarHora_IntentHandler(AbstractRequestHandler):
    """Handler for Tratamiento_Tres."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (
            ask_utils.is_intent_name("Tratamiento_Cuatro_FijarHora")(handler_input)
            and handler_input.attributes_manager.session_attributes["last_id"] == 11
        )

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        req_envelope = handler_input.request_envelope
        response_builder = handler_input.response_builder
        
        # Check if user gave permissions to create reminders.
        # If not, request to provide permissions to the skill.
        
        logger.info("PERMISOS REMINDER: " + str(req_envelope.context.system.user.permissions))
        
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
            "hora_recordatorio"
        ].value

        date = None

        if "dia_recordatorio" in handler_input.attributes_manager.session_attributes:

            date = handler_input.attributes_manager.session_attributes["dia_recordatorio"]
        
        logger.info("FECHA: " + str(date) + ", HORA: " + str(time))
        
        time_list = str(time).split(':')
        
        date_list = str(date).split('-')
        
        logger.info("FECHA: " + str(date_list) + ", HORA: " + str(time_list))


        try:
            
            logger.info("1")
            '''
            reminder_date = datetime(int(date_list[0]), int(date_list[1]), int(date_list[2]), int(time_list[0]), int(time_list[1]))

            logger.info("2")

            notification_time = reminder_date.strftime("%Y-%m-%dT%H:%M:%S")
            '''
            reminder_date = datetime(int(date_list[0]), int(date_list[1]), int(date_list[2]), int(time_list[0]), int(time_list[1]))
            reminder_date_with_tz = timezone('Europe/Madrid').localize(reminder_date) 
            notification_time = reminder_date_with_tz.strftime("%Y-%m-%dT%H:%M:%S%z")
            
            logger.info("HORA: " + str(notification_time))
            logger.info("TIPO: " + str(type(notification_time)))
            
            logger.info("3")
            
            
            reminder_request=ReminderRequest(
                request_time=notification_time,
                trigger=Trigger(
                    object_type=TriggerType.SCHEDULED_ABSOLUTE,
                    offset_in_seconds=60),
                alert_info=AlertInfo(
                    spoken_info=SpokenInfo(
                        content=[SpokenText(locale="es-ES", text="Recordatorio medicacion")])),
                push_notification=PushNotification(
                    status=PushNotificationStatus.ENABLED))
            logger.info("4")   
            
            reminder_response = reminder_client.create_reminder(reminder_request) # type: ReminderResponse

            logger.info("5")          
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


class Tratamiento_Cinco_IntentHandler(AbstractRequestHandler):
    """Handler for Tratamiento_Tres."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("Tratamiento_Cinco")(handler_input)
        
    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        handler_input.attributes_manager.session_attributes["last_id"] = 12

        user_name = handler_input.attributes_manager.session_attributes["user_name"]

        speak_output = "Hola " + str(user_name) + ", ¿te encuentras muy mal?"

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


class Yes_IntentHandler_Tratamiento_Cuatro_Part1(AbstractRequestHandler):
    """Handler for No Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (
            (ask_utils.is_intent_name("AMAZON.YesIntent")(handler_input) or ask_utils.is_intent_name("Tratamiento_Cinco_PeorEstado")(handler_input))
            and (handler_input.attributes_manager.session_attributes["last_id"] == 12 or handler_input.attributes_manager.session_attributes["last_id"] == 15)
        )

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        speak_output = "Te aconsejo que llames al doctor para consultar ¿quieres que llame?"
        handler_input.attributes_manager.session_attributes["last_id"] = 13

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )

#################################################################################
#                                                                               #
# IMPORTANTE: IMPLEMENTAR AQUI LLAMADA AL DOCTOR DE ITERACCION DE TRATAMIENTO 5 #
#                                                                               #
#################################################################################


class Yes_IntentHandler_Tratamiento_Cuatro_Part2(AbstractRequestHandler):
    """Handler for No Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (
            ask_utils.is_intent_name("AMAZON.YesIntent")(handler_input)
            and handler_input.attributes_manager.session_attributes["last_id"] == 13
        )

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        speak_output = "Llamando a su Doctor/a"
        handler_input.attributes_manager.session_attributes["last_id"] = 0

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


class No_IntentHandler_Tratamiento_Cuatro_Part1(AbstractRequestHandler):
    """Handler for No Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (
            ask_utils.is_intent_name("AMAZON.NoIntent")(handler_input)
            and (handler_input.attributes_manager.session_attributes["last_id"] == 12 or handler_input.attributes_manager.session_attributes["last_id"] == 13)
        )

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        speak_output = "Vamos a esperar un rato a ver si se te pasa, si no se te pasa y te encuentras peor, deberíamos llamar al doctor. ¿Quieres que volvamos a comprobar cómo te encuentras dentro de media hora?"
        handler_input.attributes_manager.session_attributes["last_id"] = 14

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )

# PREGUNTAR SI FALTA ITERACCION AQUI DE REALIZAR UNA LLAMADA #

class No_IntentHandler_Tratamiento_Cuatro_Part3(AbstractRequestHandler):
    """Handler for No Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (
            ask_utils.is_intent_name("AMAZON.NoIntent")(handler_input)
            and handler_input.attributes_manager.session_attributes["last_id"] == 14
        )

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        speak_output = "También puedo contactar con alguien de tu lista de contactos, ¿Quieres que llame a alguien? "
        handler_input.attributes_manager.session_attributes["last_id"] = 0

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )

# IMPLEMENTACION DEL CONTADOR #

class Yes_IntentHandler_Tratamiento_Cuatro_Part3_Contador(AbstractRequestHandler):
    """Handler for No Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (
            ask_utils.is_intent_name("AMAZON.YesIntent")(handler_input)
            and handler_input.attributes_manager.session_attributes["last_id"] == 14
        )

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        
        '''

        speak_output = "Fijado recordatorio para dentro de media hora"
        handler_input.attributes_manager.session_attributes["last_id"] = 15
        
        

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )

        '''
        
        
        req_envelope = handler_input.request_envelope
        response_builder = handler_input.response_builder
        
        logger.info("PERMISOS: " + str(req_envelope.context.system.user.permissions))
        
        
        if not (req_envelope.context.system.user.permissions and
                req_envelope.context.system.user.permissions.consent_token):
            logger.info("ENTRA EN IF TIMER")
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
            
        else: 
            logger.info("NO ENTRA EN IF TIMER")
        logger.info("Voice permission provided")
        timer_service = handler_input.service_client_factory.get_timer_management_service()
        timer_response = timer_service.create_timer(new_timer_request)
        logger.info("Timer created")
        
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
            .speak(speech_text)
            .response
        )

class Tratamiento_Cinco_IntentHandler_VueltaContador(AbstractRequestHandler):
    """Handler for Tratamiento_Tres."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return(
            ask_utils.is_intent_name("Tratamiento_Cinco_VueltaContador")(handler_input)
        )
        
        
    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        handler_input.attributes_manager.session_attributes["last_id"] = 15
        
        user_name = handler_input.attributes_manager.session_attributes["user_name"]

        speak_output = "Hola de nuevo " + str(user_name) + ", ¿como te encuentras?"

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )  


class Tratamiento_Cinco_IntentHandler_MejorEstado(AbstractRequestHandler):
    """Handler for Tratamiento_Tres."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return(
            ask_utils.is_intent_name("Tratamiento_Cinco_MejorEstado")(handler_input)
            and handler_input.attributes_manager.session_attributes["last_id"] == 15
        )
        
        
    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        handler_input.attributes_manager.session_attributes["last_id"] = 0
        
        user_name = handler_input.attributes_manager.session_attributes["user_name"]

        speak_output = "Estupendo " + str(user_name) + ", que tengas un buen día"

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )        


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Puedes decirme lo que te pasa y asi poder aconsejarte"

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.CancelIntent")(
            handler_input
        ) or ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Adios!"

        return handler_input.response_builder.speak(speak_output).response


class FallbackIntentHandler(AbstractRequestHandler):
    """Single handler for Fallback Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")
        speech = "No te he entendido, hay algo en lo que pueda ayudarte?"
        reprompt = "I didn't catch that. What can I help you with?"

        return handler_input.response_builder.speak(speech).ask(reprompt).response


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)

        handler_input.attributes_manager.session_attributes["last_id"] = 0
        # speak_output = "You just triggered " + intent_name + "."
        speak_output = "No te he entendido, necesitas ayuda con algo?"

        return (
            handler_input.response_builder.speak(speak_output)
            # .ask("add a reprompt if you want to keep the session open for the user to respond")
            .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """

    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)
        '''
        speak_output = (
            "Sorry, I had trouble doing what you asked. Please try again. "
            + str(exception)
        )
        '''
        
        speak_output = "A ocurrido un error, porfavor vuelve a intentar decirme que te ocurre"

        return (
            handler_input.response_builder.speak(speak_output)
            .ask(speak_output)
            .response
        )

class LogRequestInterceptor(AbstractRequestInterceptor):
    def process(self, handler_input):
        logger.info(f"Request type: {handler_input.request_envelope.request.object_type}")

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


# sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_global_request_interceptor(LogRequestInterceptor())

# SINTOMOLOGIA 1
sb.add_request_handler(Sintomologia_Cansancio_Apatia_Uno_IntentHandler())
sb.add_request_handler(Get_Nombre_IntentHandler())
sb.add_request_handler(YesIntentHandler_Sint_1())
sb.add_request_handler(Sintomologia_Cansancio_Apatia_Uno_Ocio_IntentHandler())
sb.add_request_handler(Sintomologia_Cansancio_Apatia_Uno_Trabajo_IntentHandler())
sb.add_request_handler(CarteleraIntentHandler_Sint_1())
sb.add_request_handler(YesIntentHandler_Cartelera_Sint_1())
sb.add_request_handler(MuseoIntentHandler_Sint_1())
sb.add_request_handler(YesIntentHandler_Museo_Sint_1())
sb.add_request_handler(Localidad_Museo_Sint_1_IntentHandler())
sb.add_request_handler(NoIntentHandler_Museo_Sint_1())
sb.add_request_handler(NoIntentHandler_Llamada_Sint_1())
sb.add_request_handler(NoIntentHandler_Trabajo_Sint_1())
sb.add_request_handler(YesIntentHandler_Llamada_Sint_1())


# SINTOMOLOGIA 2
sb.add_request_handler(Sintomologia_Cansancio_Apatia_Dos_IntentHandler())

# SINTOMOLOGIA 3

sb.add_request_handler(Sintomologia_Cansancio_Apatia_Tres_IntentHandler())

# SINTOMOLOGIA 4 y 5

sb.add_request_handler(Sintomologia_Cansancio_Apatia_Cuatro_IntentHandler())
sb.add_request_handler(Sintomologia_Cansancio_Apatia_Cuatro_YesIntentHandler())
sb.add_request_handler(Sintomologia_Cansancio_Apatia_Cuatro_NoIntentHandler())
sb.add_request_handler(Sintomologia_Cansancio_Apatia_Cinco_IntentHandler())
sb.add_request_handler(YesIntentHandler_Sint_4_and_5())
sb.add_request_handler(NoIntentHandler_Sint_4_and_5())
sb.add_request_handler(YesIntentHandler_Sint_4_and_5_part2())
sb.add_request_handler(NoIntentHandler_Sint_4_and_5_part2())

# TRATAMIENTO 1

sb.add_request_handler(Tratamiento_Uno_IntentHandler())
sb.add_request_handler(Tratamiento_Uno_Mindfulness_IntentHandler())
sb.add_request_handler(Tratamiento_Uno_Relajacion_IntentHandler())
sb.add_request_handler(Tratamiento_Uno_Musica_IntentHandler())

# TRATAMIENTO 2

sb.add_request_handler(Tratamiento_Dos_IntentHandler())
sb.add_request_handler(Yes_IntentHandler_Tratamiento_Dos_Part1())
sb.add_request_handler(No_IntentHandler_Tratamiento_Dos_Part1())
sb.add_request_handler(Tratamiento_Dos_LlamadaTelefonica_IntentHandler())
sb.add_request_handler(Yes_IntentHandler_Tratamiento_Dos_Part2())
sb.add_request_handler(Yes_IntentHandler_Tratamiento_Dos_Part3())
sb.add_request_handler(Tratamiento_Dos_Recordatorio_IntentHandler())
sb.add_request_handler(No_IntentHandler_Tratamiento_Dos_Part3())

# TRATAMIENTO 3 y 4

sb.add_request_handler(Tratamiento_Tres_IntentHandler())
sb.add_request_handler(No_IntentHandler_Tratamiento_Tres())
sb.add_request_handler(Tratamiento_Cuatro_IntentHandler())
sb.add_request_handler(Tratamiento_Cuatro_FijarDia_IntentHandler())
sb.add_request_handler(Tratamiento_Cuatro_FijarHora_IntentHandler())

# TRATAMIENTO 5

sb.add_request_handler(Tratamiento_Cinco_IntentHandler())
sb.add_request_handler(Yes_IntentHandler_Tratamiento_Cuatro_Part1())
sb.add_request_handler(Yes_IntentHandler_Tratamiento_Cuatro_Part2())
sb.add_request_handler(No_IntentHandler_Tratamiento_Cuatro_Part1())
sb.add_request_handler(No_IntentHandler_Tratamiento_Cuatro_Part3())
sb.add_request_handler(Yes_IntentHandler_Tratamiento_Cuatro_Part3_Contador())
sb.add_request_handler(Tratamiento_Cinco_IntentHandler_MejorEstado())
sb.add_request_handler(Tratamiento_Cinco_IntentHandler_VueltaContador())


#sb.add_exception_handler(GetAddressExceptionHandler())

sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(
    IntentReflectorHandler()
)  # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers


sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
