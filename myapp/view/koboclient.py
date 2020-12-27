from datetime import datetime
import json
import os
import http.client
from passlib.context import CryptContext
import shapely.geometry
import geopandas

from myapp import models

from django.conf import settings
from django.core import serializers
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import (connection, transaction)
from django.db.utils import DataError, IntegrityError
from django.forms.models import model_to_dict
from django.http import HttpResponse, HttpResponseBadRequest
from django.http.response import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from rest_framework_simplejwt.backends import TokenBackend
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated
)

from myapp.view.utilidades import dictfetchall, usuarioAutenticado
from myapp.view.osm import detalleCartografia

from opc.opc_settings import settings
from myapp.view import(
    koboclient,
    tmclient,
    encuestaview,
)

# ================= Kobo Toolbox ========================

##
# @brief Obtenención de encuestas de un formulario KoboToolbox
# @param id Identificación del Formulario KoboToolbox
# @return Diccionario
#
def informacionFormularioKoboToolbox(id):

    headers = {'Authorization': settings['kobo-token']}

    client = http.client.HTTPConnection(
        settings['kobo-kpi'], int(settings['kobo-puerto']), timeout=int(settings['timeout-request']))

    client.request('GET', '/assets/' + id + '/submissions/?format=json', '{}', headers)

    response = client.getresponse()

    if(response.status == 200):

        info = json.loads(response.read())

        # ============== Obteniendo campos del formulario====================

        detalleFormulario = detalleFormularioKoboToolbox(id)

        if (detalleFormulario):

            camposFormulario = detalleFormulario['content']['survey']

            data = {
                'campos': camposFormulario,
                'info': info
            }

        else:
            data = False

    else:
        data = False

    client.close()

    return data

##
# @brief Obtención de información de detalle de un formulario de KoboToolbox
# @param id Identificación del Formulario KoboToolbox
# @return Diccionario
#
def detalleFormularioKoboToolbox(id):

    headers = {'Authorization': settings['kobo-token']}

    client = http.client.HTTPConnection(
        settings['kobo-kpi'], int(settings['kobo-puerto']), timeout=int(settings['timeout-request']))
    client.request('GET', '/assets/' + str(id) + '/?format=json', '', headers)
    response = client.getresponse()

    if (response.status == 200):

        data = json.loads(response.read())

    else:
        data = False

    return data

##
# @brief Obtención de enlace de diligenciamiento de un formulario de KoboToolbox
# @param id tareid Identificación de la tarea Tipo Encuesta
# @return cadena JSON
#
@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def enlaceFormularioKoboToolbox(request, tareid):

    KOBO_INSTR = 1

    #headers = {'Authorization': settings['kobo-token']}

    try:
        tarea = models.Task.objects.get(pk=tareid)

        instrumento = models.Instrument.objects.get(pk=tarea.task_id)

        if instrumento.instrument_type == KOBO_INSTR:

            informacion = informacionFormularioKoboToolbox(
                instrumento.external_id)

            if (isinstance(informacion, dict)):

                user = usuarioAutenticado(request)
                person = models.Person.objects.get(user__user_id__exact = user.userid)
                encuestaview.almacenarEncuestas(
                    instrumento, informacion['info'], person, tarea)

            detalleFormulario = detalleFormularioKoboToolbox(
                instrumento.external_id)

            if detalleFormulario:

                if(detalleFormulario['deployment__active']):

                    if detalleFormulario['deployment__submission_count'] < tarea.task_quantity:

                        enlace = detalleFormulario['deployment__links']['offline_url']

                        data = {
                            'code': 200,
                            'enlace': enlace,
                            'status': 'success'
                        }

                    else:

                        # La tarea ya esta completada y se marca como terminada si esta en progreso
                        if tarea.isactive == 0:
                            tarea.isactive = 1
                            tarea.save()

                        data = {
                            'code': 403,
                            'message': 'Tarea completada',
                            'status': 'error'
                        }

                else:

                    data = {
                        'code': 400,
                        'message': 'El formulario no está implementado',
                        'status': 'error'
                    }

            else:

                data = {
                    'code': 500,
                    'status': 'error'
                }

        else:

            data = {
                'code': 400,
                'message': 'El instrumento no es de tipo encuesta',
                'status': 'error'
            }

    except ObjectDoesNotExist:

        data = {
            'code': 404,
            'status': 'error'
        }

    except ValidationError:

        data = {
            'code': 400,
            'status': 'error'
        }

    return JsonResponse(data, status=data['code'], safe=False)

##
# @brief Implementación/Despliegue de un formulario de KoboToolbox
# @param id Identificación del Formulario KoboToolbox
# @return cadena JSON
#
@csrf_exempt
@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def implementarFormularioKoboToolbox(request, id):

    try:

        instrumento = models.Instrument.objects.get(pk=id)

        headers = {
            'Authorization': settings['kobo-token'],
            'Content-Type': 'application/json'
        }

        payload = {'active': True}

        client = http.client.HTTPConnection(
            settings['kobo-kpi'], int(settings['kobo-puerto']), timeout=int(settings['timeout-request']))

        client.request('POST', '/assets/' + instrumento.external_id +
                       '/deployment/', json.dumps(payload), headers)

        response = client.getresponse()

        if response.status != 200:

            data = {
                'status': 'error',
                'code': 500
            }

        else:

            data = {
                'status': 'success',
                'code': 200
            }

    except ObjectDoesNotExist:

        data = {
            'status': 'error',
            'code': 404
        }

    except ValidationError:

        data = {
            'status': 'error',
            'code': 400
        }

    return JsonResponse(data, status=data['code'])

##
# @brief Listado de formularios de KoboToolbox
# @param request Instancia HttpRequest
# @return cadena JSON
#
@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def listadoFormulariosKoboToolbox(request):

    try:

        headers = {
            'Authorization': settings['kobo-token'],
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.75 Safari/537.36'
        }

        client = http.client.HTTPConnection(
            settings['kobo-kpi'], int(settings['kobo-puerto']), timeout=int(settings['timeout-request']))
        client.request('GET', '/assets/?format=json', '', headers)
        response = client.getresponse()

        if(response.status == 200):

            formulariosKoboToolbox = json.loads(response.read())['results']

            data = {
                'code': 200,
                'formularios': formulariosKoboToolbox,
                'status': 'success'
            }

        else:
            data = {
                'code': 500,
                'status': 'error'
            }

    except:

        data = {
            'code': 500,
            'status': 'error'
        }

    return JsonResponse(data, status=data['code'], safe=False)

##
# @brief Verificación de Implementación/Despliegue de un formulario de KoboToolbox
# @param request Instancia HttpRequest
# @param id Identificación del Formulario KoboToolbox
# @return cadena JSON
#
@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def verificarImplementaciónFormulario(request, id):

    try:
        instrumento = models.Instrument.objects.get(pk=id)

        headers = {
            'Authorization': settings['kobo-token'],
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.75 Safari/537.36'
        }

        client = http.client.HTTPConnection(
            settings['kobo-kpi'], int(settings['kobo-puerto']), timeout=int(settings['timeout-request']))
        client.request('GET', '/assets/?format=json', '', headers)
        response = client.getresponse()

        if(response.status == 200):

            formulariosKoboToolbox = json.loads(response.read())['results']

            for i in formulariosKoboToolbox:

                if(i['uid'] == instrumento.external_id):

                    if(i['has_deployment']):

                        data = {
                            'code': 200,
                            'status': 'success',
                            'implementacion': True
                        }

                    else:

                        data = {
                            'code': 200,
                            'status': 'success',
                            'implementacion': False
                        }

                    break

                else:

                    data = {
                        'code': 404,
                        'status': 'error'
                    }

        else:

            data = {
                'code': 500,
                'status': 'error'
            }

    except ObjectDoesNotExist:

        data = {
            'status': 'success',
            'code': 404
        }

    except ValidationError:

        data = {
            'status': 'error',
            'code': 400
        }

    return JsonResponse(data, status=data['code'])


@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def getKoboKpiUrl(request):

    data = {
        'code': 200,
        'status': 'success',
        'kpiUrl': settings['kobo-kpi'],
    }
    return JsonResponse(data, status=data['code'])