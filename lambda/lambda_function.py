# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import ask_sdk_core.utils as ask_utils
import webbrowser
import os
import boto3
import requests 
import pytz
import sintomologia_functions
import tratamiento_functions

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

from datetime import datetime, date, timezone

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
NOTIFY_MISSING_PERMISSIONS = ("Porfavor, habilita los permisos necesarios en la app de Alexa.")

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

        return sintomologia_functions.sintomologia_cansancio_apatia_uno(handler_input)


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
        return sintomologia_functions.yesIntentHandler_sint_1(handler_input)


class Sintomologia_Cansancio_Apatia_Uno_Ocio_IntentHandler(AbstractRequestHandler):
    """Handler for Sintomologia_Cansancio_Apatia_Uno."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("Sintomologia_Cansancio_Apatia_Uno_Ocio")(
            handler_input
        )

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        return sintomologia_functions.sintomologia_cansancio_apatia_uno_ocio(handler_input)


class Sintomologia_Cansancio_Apatia_Uno_Trabajo_IntentHandler(AbstractRequestHandler):
    """Handler for Sintomologia_Cansancio_Apatia_Uno."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("Sintomologia_Cansancio_Apatia_Uno_Trabajo")(
            handler_input
        )

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        return sintomologia_functions.sintomologia_cansancio_apatia_uno_trabajo(handler_input)


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
        return sintomologia_functions.carteleraIntentHandler_Sint_1(handler_input)


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
        return sintomologia_functions.yesIntentHandler_cartelera_sint_1(handler_input)


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

        return sintomologia_functions.museoIntentHandler_Sint_1(handler_input)


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

        return sintomologia_functions.yesIntentHandler_Museo_Sint_1(handler_input)


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
        return sintomologia_functions.localidad_Museo_Sint_1_IntentHandler(handler_input)


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

        return sintomologia_functions.noIntentHandler_Museo_Sint_1(handler_input)

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

        return sintomologia_functions.noIntentHandler_Llamada_Sint_1(handler_input)


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
        return sintomologia_functions.noIntentHandler_Trabajo_Sint_1(handler_input)

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

        return sintomologia_functions.yesIntentHandler_Llamada_Sint_1(handler_input)


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

        return sintomologia_functions.sintomologia_cansancio_apatia_dos(handler_input)


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
        return sintomologia_functions.sintomologia_cansancio_apatia_tres(handler_input)


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
        return sintomologia_functions.sintomologia_cansancio_apatia_cuatro(handler_input)

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
        return sintomologia_functions.sintomologia_cansancio_apatia_cuatro_YesIntentHandler(handler_input)
    

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

        return sintomologia_functions.sintomologia_cansancio_apatia_cuatro_NoIntentHandler(handler_input)


class Sintomologia_Cansancio_Apatia_Cinco_IntentHandler(AbstractRequestHandler):
    """Handler for Sintomologia_Cansancio_Apatia_Cuatro."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("Sintomologia_Cansancio_Apatia_Cinco")(
            handler_input
        )

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        return sintomologia_functions.sintomologia_cansancio_apatia_cinco(handler_input)


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
        sintomologia_functions.yesIntentHandler_Sint_4_and_5_launch_screen(self, handler_input)
            
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
        return sintomologia_functions.noIntentHandler_sint_4_and_5(handler_input)


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
        return sintomologia_functions.yesIntentHandler_sint_4_and_5_part2(handler_input)


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
        return sintomologia_functions.noIntentHandler_Sint_4_and_5_part2(handler_input) 


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
        return tratamiento_functions.tratamiento_uno(handler_input)


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
        return tratamiento_functions.tratamiento_uno_mindfulnes(self, handler_input)

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
        return tratamiento_functions.tratamiento_uno_relajacion(self, handler_input)

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
        return tratamiento_functions.tratamiento_uno_musica(self, handler_input)

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
        return tratamiento_functions.tratamiento_dos(handler_input)


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
        return tratamiento_functions.yes_tratamiento_dos_part1(handler_input)


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
        return tratamiento_functions.tratamiento_dos_llamadaTelefonica(handler_input)

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
        return tratamiento_functions.no_tratamiento_dos_part1(handler_input)


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
        return tratamiento_functions.yes_tratamiento_dos_part2(handler_input)


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
        return tratamiento_functions.yes_tratamiento_dos_part3(handler_input)


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
        return tratamiento_functions.tratamiento_dos_recordatorio(handler_input)

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
        return tratamiento_functions.no_tratamiento_dos_part3(handler_input)

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
        return tratamiento_functions.tratamiento_tres(handler_input)


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
        return tratamiento_functions.no_tratamiento_tres(handler_input)


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
        return tratamiento_functions.tratamiento_cuatro(handler_input)


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
        return tratamiento_functions.tratamiento_cuatro_fijarDia(handler_input)


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
        return tratamiento_functions.tratamiento_cuatro_fijarHora(handler_input)        


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
        return tratamiento_functions.tratamiento_cinco(handler_input)


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
        return tratamiento_functions.yes_tratamiento_cuatro_part1(handler_input)

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
        return tratamiento_functions.yes_tratamiento_cuatro_part2(handler_input)


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
        return tratamiento_functions.no_tratamiento_cuatro_part1(handler_input)


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
        return tratamiento_functions.no_tratamiento_cuatro_part3(handler_input)


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
        return tratamiento_functions.yes_tratamiento_cuatro_part3_contador(handler_input)


class Tratamiento_Cinco_IntentHandler_VueltaContador(AbstractRequestHandler):
    """Handler for Tratamiento_Tres."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return(
            ask_utils.is_intent_name("Tratamiento_Cinco_VueltaContador")(handler_input)
        )
        
        
    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        return tratamiento_functions.tratamiento_cinco_vueltaContador(handler_input)


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

        return tratamiento_functions.tratamiento_cinco_mejorEstado(handler_input)     


#########################################################
#                                                       #
#                 HANDLERS AUXILIARES                   #
#                                                       #
#########################################################


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Puedes decirme lo que te pasa y asi poder aconsejarte"

        return (
            handler_input.response_builder.speak(speak_output).set_should_end_session(
            False)
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

        return handler_input.response_builder.speak(speech).set_should_end_session(
        False).ask(reprompt).response


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
            handler_input.response_builder.speak(speak_output).set_should_end_session(
            False)
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
            handler_input.response_builder.speak(speak_output).set_should_end_session(
        False)
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
