from django.conf import settings
from django.http.response import JsonResponse
from django.shortcuts import render

from myapp import models

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated
)

from rest_framework_simplejwt.backends import TokenBackend

#========================== Utilidades =============================

##
# @brief Función que formatea el resultado de una consulta de base de datos
# @param cursor Cursor que contiene el resultado de la consulta
# @return lista de diccionarios
#
def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

##
# @brief Recurso que provee el listado de los géneros del sistema
# @param request Instancia HttpRequest
# @return cadena JSON
#
@api_view(['GET'])
@permission_classes((AllowAny,))
def listadoGeneros(request):

    generos = models.Genero.objects.all().values()

    data = {
        'code': 200,
        'generos': list(generos),
        'status': 'success'
    }

    return JsonResponse(data, status=data['code'], safe=False)

##
# @brief Recurso que provee el listado de niveles educativos del sistema
# @param request Instancia HttpRequest
# @return cadena JSON
#
@api_view(['GET'])
@permission_classes((AllowAny,))
def listadoNivelesEducativos(request):

    nivelesEducativos = models.NivelEducativo.objects.all().values()

    data = {
        'code': 200,
        'nivelesEducativos': list(nivelesEducativos),
        'status': 'success'
    }

    return JsonResponse(data, status=data['code'], safe=False)

##
# @brief Recurso que provee el listado de barrios de Santiago de Cali
# @param request Instancia HttpRequest
# @return cadena JSON
#
@api_view(['GET'])
@permission_classes((AllowAny,))
def listadoBarrios(request):

    barrios = models.Barrio.objects.all().values()

    data = {
        'code': 200,
        'barrios': list(barrios),
        'status': 'success'
    }

    return JsonResponse(data, status=data['code'], safe=False)

##
# @brief Función que provee la instancia del modelo usuario en base al Token de sesión
# @param request Instancia HttpRequest
# @return instancia del modelo Usuario
#
def usuarioAutenticado(request):

    # Decodificando el access token
    tokenBackend = TokenBackend(settings.SIMPLE_JWT['ALGORITHM'], settings.SIMPLE_JWT['SIGNING_KEY'],
                                settings.SIMPLE_JWT['VERIFYING_KEY'])
    tokenDecoded = tokenBackend.decode(request.META['HTTP_AUTHORIZATION'].split()[1], verify=True)
    # consultando el usuario
    user = models.Usuario.objects.get(pk=tokenDecoded['user_id'])

    return user

##
# @brief Función que provee un parametro del sistema
# @param parametro Identificación del parametro
# @return cadena con el valor de parámetro del sistema
#
def obtenerParametroSistema(parametro):

    parametro = models.Parametro.objects.get(pk=parametro)

    if parametro is not None:
        response = parametro.paramvalor
    else:
        response = None

    return response

##
# @brief Función que provee el listado de correos electrónicos de los integrantes de un proyecto
# @param proyid Identificación de un proyecto
# @return Lista
#
def obtenerEmailsEquipo(proyid):

    usuarios = models.Equipo.objects.filter(proyid__exact = proyid)
    emails = []

    for u in usuarios:
        email = models.Usuario.objects.get(pk = u.userid).useremail
        emails.append(email)

    return emails

##
# @brief Recurso que provee el correo electrónico de un usuario
# @param userid Identificación de un usuario
# @return cadena que contiene el correo electrónico del usuario
#
def obtenerEmailUsuario(userid):

    usuario = models.Usuario.objects.get(pk = userid)

    email = [usuario.useremail]

    return email

##
# @brief Función que retorna una plantilla HTML cuando no se encuentra un recurso en el sistema
# @param request Instancia HttpRequest
# @param exception excepción opcional
# @return plantilla HTML
#
def notFoundPage(request, exception=None):
    return render(request, "error/404.html")

##
# @brief Función que retorna una plantilla HTML cuando ocurre un error en el sistema
# @param request Instancia HttpRequest
# @param exception excepcion opcional
# @return plantilla HTML
#
def serverErrorPage(request, exception=None):
    return render(request, "error/500.html")

##
# @brief Función que calcula el estado actual de un proyecto. provee datos como:
# Avance de la ejecución
# Avance de la validación
# Cantidad de integrantes
# @param proyid Identificación del proyecto
# @return Diccionario
#
def reporteEstadoProyecto(proyid):
    progresoProyecto = 0
    tareas = models.Tarea.objects.filter(proyid__exact = proyid)
    tareasValidadas = 0

    for tarea in tareas:

        if tarea.taretipo == 1:
            encuestas = models.Encuesta.objects.filter(tareid__exact=tarea.tareid)
            progreso = (len(encuestas) * 100) / tarea.tarerestriccant

            progresoProyecto = progresoProyecto + progreso

        if tarea.tareestado == 2:
            tareasValidadas += 1

    if progresoProyecto > 0:
        progresoProyecto = (progresoProyecto * 100) / (len(tareas) * 100)

    if (len(tareas) > 0):
        estadoValidacion = (tareasValidadas * 100) / len(tareas)
    else:
        estadoValidacion = 0

    return {
        'progreso-proyecto':    progresoProyecto,
        'estado-validacion':    estadoValidacion,
        'cantidad-integrantes': len(models.Equipo.objects.filter(proyid__exact=proyid))
    }

def reporteEstadoTarea(tarea):

    if tarea['taretipo'] == 1:
        encuestas = models.Encuesta.objects.filter(tareid__exact=tarea['tareid'])
        progreso = (len(encuestas) * 100) / tarea['tarerestriccant']

    return progreso