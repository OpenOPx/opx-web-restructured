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

PROYECTISTA = '53ad3141-56bb-4ee2-adcf-5664ba03ad65'
# VOLUNTARIO =

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
            query = "SELECT p.*, r.role_name from opx.person p \
                    INNER JOIN opx.role r ON r.role_id = p.role_id " \
                    "WHERE p.pers_id = '{}'".format(userid)
            cursor.execute(query)
            queryResult = dictfetchall(cursor)

        if(len(queryResult) > 0):

            usuario = queryResult[0]

            # Puntaje esperado para llegar a rol proximo
            # Voluntario
            if str(usuario['role_id']) == '0be58d4e-6735-481a-8740-739a73c3be86':
                usuario['promocion'] = {
                    'rol': "Validador",
                    'puntaje': 22  # int(settings['umbral-validador'])
                }

            # Proyectista
            elif str(usuario['role_id']) == '53ad3141-56bb-4ee2-adcf-5664ba03ad65':
                usuario['promocion'] = {
                    'rol': "Proyectista",
                    'puntaje': 22  # int(settings['umbral-proyectista'])
                }

            # Remover la información que no se desea mostrar
            #del usuario['password']
            #del usuario['usertoken']

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

##
# @brief Recurso de almacenamiento de usuarios
# @param request Instancia HttpRequest
# @return cadena JSON
#


@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def almacenarUsuario(request):

    useremail = request.POST.get('useremail')
    fcm_token = request.POST.get('fcm_token')
    #userfullname = request.POST.get('userfullname')
    pers_name = request.POST.get('pers_name')
    pers_lastname = request.POST.get('pers_lastname')
    password = request.POST.get('password')
    role_id = request.POST.get('role_id')
    #userleveltype = 1
    #userestado = 1
    pers_birthdate = request.POST.get('pers_birthdate')
    gender_id = request.POST.get('gender_id')
    neighborhood_id = request.POST.get('neighborhood_id')
    education_level_id = request.POST.get('education_level_id')
    pers_telephone = request.POST.get('pers_telephone')
    #fechaCreacion = datetime.today()
    isemployee = request.POST.get('isemployee')

    try:
        with transaction.atomic():
            user = models.User(useremail=useremail, password=password)
            # Contexto Passlib
            pwd_context = CryptContext(
                schemes=["pbkdf2_sha256"],
                default="pbkdf2_sha256",
                pbkdf2_sha256__default_rounds=30000
            )
            user.password = pwd_context.encrypt(user.password)
            user.save()
            role = models.Role.objects.get(pk = role_id)
            gender = models.Gender.objects.get(pk = gender_id)
            neighborhood = models.Neighborhood.objects.get(pk = neighborhood_id)
            education_level = models.EducationLevel.objects.get(pk = education_level_id)

            person = models.Person(pers_name=pers_name, pers_lastname=pers_lastname, fcm_token=fcm_token,
                                role=role, pers_birthdate=pers_birthdate, pers_telephone=pers_telephone,
                                gender=gender, neighborhood=neighborhood, education_level=education_level,
                                user = user)
            # Asignación de estado "empleado" a usuario en caso tal sea enviado
            if isemployee is not None:
                if isemployee == "true":
                    person.isemployee = 1
                # else:
                #    usuario.empleado = 0

            # Validación de campos
            person.full_clean()
            person.save()

            data = {
                'code': 201,
                'usuario': serializers.serialize('python', [user])[0],#mando user o person?
                'status': 'success'
            }

    except ValidationError as e:

        data = {
            'code': 400,
            'errors': dict(e),
            'status': 'error'
        }

    except IntegrityError as e:

        data = {
            'code': 500,
            'errors': str(e),
            'status': 'error'
        }

    return JsonResponse(data, safe=False, status=data['code'])
