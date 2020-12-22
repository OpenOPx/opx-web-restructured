from django.conf import settings
from django.core.mail import send_mail

##
# @brief Envio de notifificaciones correspondiente a la gestión de cambios de un proyecto especifico
# @param usuarios lista de correos electrónicos destinatarios de la notificación
# @param tipoReceptor define el tipo de entidad que sufrio cambios (proyecto o tarea)
# @param nombreReceptor define el nombre del proyecto/tarea que sufrio cambios
# @param tipoCambio Define el tipo de cambio que sufrio el proyecto/tarea.
# @param detalle información adicional del cambio efectuado
# @return cadena JSON
#
def gestionCambios(usuarios, tipoReceptor, nombreReceptor, tipoCambio, detalle = ""):

    # Definición de tipos de cambio
    tiposCambio = {
        1:  'Cambio de Objetivo',
        2: 'Cambio de Tiempo',
        3: 'Cambio de Equipo',
        4: 'Cambio de Territorio'
    }

    # Asunto de la notificación via correo
    subject = "Notificacion de Cambio"

    # Verificacion de la existencia de tipo de cambio recibido
    cambio = tiposCambio.get(tipoCambio, None)

    if cambio is not None:
        message = "Hola. Ha habido un {} en {} {}." \
                  "<br /> {}" \
                  .format(cambio, tipoReceptor, nombreReceptor, detalle)

        # Envío de Notificación de Correo
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            usuarios,
            fail_silently = False,
            html_message = message
        )

        response = True

    else:
        response = False

    return response



