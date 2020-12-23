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


# ======================= usuarios =================================

##
# @brief plantilla de listado de usuarios
# @param request Instancia HttpRequest
# @return plantilla HTML
#


def listadoUsuariosView(request):

    return render(request, "usuarios/listado.html")


##
# @brief Recurso de listado de usuarios
# @param request Instancia HttpRequest
# @return cadena JSON
#
@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def listadoUsuarios(request):

    #users = models.Usuario.objects.all().values()
    # json_res = serializers.serialize('python', users)

    with connection.cursor() as cursor:

        query = "SELECT user_id, opx.user.useremail, pers_id, pers_name, \
                pers_lastname, opx.person.isactive, opx.person.role_id, pers_birthdate, \
                neighborhood_id, gender_id, education_level_id, pers_telephone, opx.role.role_name, \
                pers_latitude, pers_longitude, \
                hour_location, pers_creation_date, isemployee \
                FROM opx.person \
                INNER JOIN opx.role ON opx.role.role_id = opx.person.role_id \
                INNER JOIN opx.user ON opx.user.userid = opx.person.user_id"

        cursor.execute(query)
        users = dictfetchall(cursor)

        return JsonResponse(users, safe=False)

##
# @brief Recurso que provee el detalle de un usuario registrado
# @param userid identificación del usuario
# @return Cadena JSON
#
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def detalleUsuario(request, userid):

    try:
        #usuario = models.Usuario.objects.get(pk=userid)
        usuario = {}

        with connection.cursor() as cursor:
            query = "SELECT u.*, r.rolname from v1.usuarios u \
                    INNER JOIN v1.roles r ON r.rolid = u.rolid " \
                    "WHERE u.userid = '{}'".format(userid)
            cursor.execute(query)
            queryResult = dictfetchall(cursor)

        if(len(queryResult) > 0):

            usuario = queryResult[0]

            # Puntaje esperado para llegar a rol proximo
            # Voluntario
            if str(usuario['rolid']) == '0be58d4e-6735-481a-8740-739a73c3be86':
                usuario['promocion'] = {
                    'rol': "Validador",
                    'puntaje': int(settings['umbral-validador'])
                }

            # Proyectista
            elif str(usuario['rolid']) == '53ad3141-56bb-4ee2-adcf-5664ba03ad65':
                usuario['promocion'] = {
                    'rol': "Proyectista",
                    'puntaje': int(settings['umbral-proyectista'])
                }

            # Remover la información que no se desea mostrar
            del usuario['password']
            del usuario['usertoken']

            data = {
                'code': 200,
                'usuario': usuario,
                'status': 'success'
            }

        else:
            raise ObjectDoesNotExist("")

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

    except DataError:

        data = {
            'code': 400,
            'status': 'error'
        }

    return JsonResponse(data, status=data['code'])
