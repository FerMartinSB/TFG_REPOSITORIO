########################################################
#                                                      #
#               FUNCIONES DE SINTOMOLOGIA              #
#                                                      #
########################################################

from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import json

from ask_sdk_model.interfaces.alexa.presentation.apl import RenderDocumentDirective


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


#########################################################
#                                                       #
#               SINTOMOLOGIA Y APATIA 1                 #
#                                                       #
#########################################################


def sintomologia_cansancio_apatia_uno(handler_input):
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


def yesIntentHandler_sint_1(handler_input):
    
    speak_output = "¿Tienes que ir a trabajar o era una actividad de ocio?"
    handler_input.attributes_manager.session_attributes["last_id"] = 17

    return (
        handler_input.response_builder.speak(speak_output).set_should_end_session(
        False)
        .ask(speak_output)
        .response
    )



def sintomologia_cansancio_apatia_uno_ocio(handler_input): 
    
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



def sintomologia_cansancio_apatia_uno_trabajo(handler_input):
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

def carteleraIntentHandler_Sint_1(handler_input):
    
    try:
        user_name = handler_input.attributes_manager.session_attributes["user_name"]
        handler_input.attributes_manager.session_attributes["last_id"] = 2
    except:
        user_name = False

    if user_name:

        speak_output = str(user_name) + ", seguramente haya actividades que puedan cambiar esa sensación. Quizá sea buena idea contactar con X (persona que haya establecido de su agenda) para hacer alguna actividad. Podríais salir a tomar un café, ir al cine o ver una exposición. ¿Quieres que te diga la cartelera?"

    else:
        reprompt = "Porfavor, digame su nombre. "
        handler_input.response_builder.ask(reprompt)


    return (
        handler_input.response_builder.speak(speak_output).set_should_end_session(
        False)
        .ask(speak_output)
        .response
    )



def yesIntentHandler_cartelera_sint_1(handler_input):
    
    url = "https://www.sensacine.com/peliculas/en-cartelera/cines/"

    request_site = Request(url, headers={"User-Agent": "Mozilla/5.0"})

    datos = urlopen(request_site).read()

    soup = BeautifulSoup(datos, "html.parser")

    tags = soup.find_all("a", {"meta-title-link"})
    
    speak_output = "Hay varias peliculas disponibles, algunas de ellas son: "

    for tag in tags[:5]:

        speak_output = str(speak_output) + str(tag.getText()) + ", "



    speak_output = (
        speak_output
        + "o "
        + str(tags[5].getText())
        + ", ¿Quieres que llame a X (persona que haya establecido de su agenda)?"
    )
    
    speak_output = speak_output.replace("&", "and")
    

    handler_input.attributes_manager.session_attributes["last_id"] = 18

    return (
        handler_input.response_builder.speak(speak_output)
        .ask(speak_output)
        .response
    )


def museoIntentHandler_Sint_1(handler_input):
    
    speak_output = "¿Quieres que te proponga alguna exposición disponible en tu localidad?"
    handler_input.attributes_manager.session_attributes["last_id"] = 3

    return (
        handler_input.response_builder.speak(speak_output).set_should_end_session(
        False)
        .ask(speak_output)
        .response
    )


def yesIntentHandler_Museo_Sint_1(handler_input):
    
    handler_input.attributes_manager.session_attributes["last_id"] = 3
    speak_output = "¿Cual es tu localidad?"

    return (
        handler_input.response_builder.speak(speak_output).set_should_end_session(
        False)
        .ask(speak_output)
        .response
    )


def localidad_Museo_Sint_1_IntentHandler(handler_input):
    
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

            speak_output = speak_output + "y " + ciudad["museos"][-1] + ". ¿Quieres que llame a X (persona que haya establecido de su agenda)?"
            

    return (
        handler_input.response_builder.speak(speak_output).set_should_end_session(
        False)
        .ask(speak_output)
        .response
    )



def noIntentHandler_Museo_Sint_1(handler_input):
    
    user_name = handler_input.attributes_manager.session_attributes["user_name"]
    speak_output = (
        "¿Quieres que llame a X (persona que haya establecido de su agenda)?"
    )
    handler_input.attributes_manager.session_attributes["last_id"] = 16

    return (
        handler_input.response_builder.speak(speak_output).set_should_end_session(
        False)
        .ask(speak_output)
        .response
    )



def noIntentHandler_Llamada_Sint_1(handler_input):
    
    user_name = handler_input.attributes_manager.session_attributes["user_name"]
    speak_output = (
        "No te preocupes "
        + str(user_name)
        + ",Todos en algún momento sentimos que el día a día nos supera. Tómate un tiempo de descanso mientras lees un libro o algo que te interesa, escuchas música relajante, o realizas un mándala."
    )
    handler_input.attributes_manager.session_attributes["last_id"] = 0

    return (
        handler_input.response_builder.speak(speak_output).set_should_end_session(
        False)
        .ask(speak_output)
        .response
    )


def noIntentHandler_Trabajo_Sint_1(handler_input):
    
    user_name = handler_input.attributes_manager.session_attributes["user_name"]
    speak_output = (
        "Bien "
        + str(user_name)
        + ". Espero haberte ayudado. Si me necesitas en otro momento, vuelve a pedirme ayuda. \
            Que tengas un buen día."
    )
    handler_input.attributes_manager.session_attributes["last_id"] = 0

    return (
        handler_input.response_builder.speak(speak_output).set_should_end_session(
        False)
        .ask(speak_output)
        .response
    )


def yesIntentHandler_Llamada_Sint_1(handler_input):
    
    user_name = handler_input.attributes_manager.session_attributes["user_name"]
    speak_output = (
        "Llamar a X (persona que haya establecido de su agenda)"
    )
    handler_input.attributes_manager.session_attributes["last_id"] = 0

    return (
        handler_input.response_builder.speak(speak_output).set_should_end_session(
        False)
        .ask(speak_output)
        .response
    )


#########################################################
#                                                       #
#               SINTOMOLOGIA Y APATIA 2                 #
#                                                       #
#########################################################


def sintomologia_cansancio_apatia_dos(handler_input):
    
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
        handler_input.response_builder.speak(speak_output).set_should_end_session(
        False)
        # .ask(speak_output)
        .response
    )


#########################################################
#                                                       #
#               SINTOMOLOGIA Y APATIA 3                 #
#                                                       #
#########################################################



def sintomologia_cansancio_apatia_tres(handler_input):
    
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
        handler_input.response_builder.speak(speak_output).set_should_end_session(
        False)
        # .ask(speak_output)
        .response
    )



#########################################################
#                                                       #
#               SINTOMOLOGIA Y APATIA 4 y 5             #
#                                                       #
#########################################################



def sintomologia_cansancio_apatia_cuatro(handler_input):
    
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
        handler_input.response_builder.speak(speak_output).set_should_end_session(
        False)
        .ask(speak_output)
        .response
    )


def sintomologia_cansancio_apatia_cuatro_YesIntentHandler(handler_input):
    
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
        handler_input.response_builder.speak(speak_output).set_should_end_session(
        False)
        .ask(speak_output)
        .response
    )


def sintomologia_cansancio_apatia_cuatro_NoIntentHandler(handler_input):
    
    handler_input.attributes_manager.session_attributes["last_id"] = 21

    speak_output = ("Puedes hacer entonces algún ejercicio de relajación ¿quieres que te recomiende alguno?")

    return (
        handler_input.response_builder.speak(speak_output).set_should_end_session(
        False)
        .ask(speak_output)
        .response
    )


def sintomologia_cansancio_apatia_cinco(handler_input):
    
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
        handler_input.response_builder.speak(speak_output).set_should_end_session(
        False)
        .ask(speak_output)
        .response
    )


def yesIntentHandler_Sint_4_and_5_launch_screen(skill, handler_input):
    
    speak_output = "Error al cargar el video"
    handler_input.attributes_manager.session_attributes["last_id"] = 0
    
    if skill.supports_apl(handler_input):
        
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
    
    handler_input.response_builder.speak(speak_output).set_should_end_session(
        False)


def noIntentHandler_sint_4_and_5(handler_input):
    
    speak_output = "También Puedes llamar a alguna persona de tu lista de contactos favoritos para tener un rato de conversación agradable, eso puede hacer que te sientas mejor. ¿Quieres que llame a X? "
    handler_input.attributes_manager.session_attributes["last_id"] = 5

    return (
        handler_input.response_builder.speak(speak_output).set_should_end_session(
        False)
        .ask(speak_output)
        .response
    )



def yesIntentHandler_sint_4_and_5_part2(handler_input):
    
    speak_output = "Llamar a X"
    handler_input.attributes_manager.session_attributes["last_id"] = 0

    return (
        handler_input.response_builder.speak(speak_output).set_should_end_session(
        False)
        .ask(speak_output)
        .response
    )


def noIntentHandler_Sint_4_and_5_part2(handler_input):
    
    user_name = handler_input.attributes_manager.session_attributes["user_name"]

    speak_output = (
        "Tranquilo "
        + str(user_name)
        + ". todos en algún momento sentimos que el día a día nos supera y estamos agotados. Puedes tomarte un tiempo de descanso mientras lees un libro interesante"
    )
    handler_input.attributes_manager.session_attributes["last_id"] = 0

    return (
        handler_input.response_builder.speak(speak_output).set_should_end_session(
        False)
        .ask(speak_output)
        .response
    )
    
    
    