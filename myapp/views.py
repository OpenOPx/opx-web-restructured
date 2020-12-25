# from django.shortcuts import render
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


# Create your views here.

##
# Vista de Autenticación Dashboard
# @param request Instancia HttpRequest
# @return Plantilla Html
#


def loginView(request):

    return render(request, "auth/login.html")


@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def login(request):

    try:

        username = request.POST.get("username")
        password = request.POST.get("password")

        if username is None or password is None:

            data = {
                'status': 'error',
                'message': 'Por favor especifique usuario y contraseña',
                'code': 400
            }

        else:

            user = models.User.objects.get(useremail__exact=username)
            person = models.Person.objects.get(user__userid__exact=user.userid)

            # .filter(password__exact = password)
            #user = authenticate(email=username, password=password)

            # Si el correo electrónico existe
            # Contexto Passlib
            pwd_context = CryptContext(
                schemes=["pbkdf2_sha256"],
                default="pbkdf2_sha256",
                pbkdf2_sha256__default_rounds=30000
            )
            passwordVerification = pwd_context.verify(password, user.password)

            if(passwordVerification):

                # Generación de tokens
                refresh = RefreshToken.for_user(user)

                # Almacenando los permisos del usuario en la sesión
                request.session['permisos'] = []

                permisos = models.RolePermissionn.objects.filter(role__role_id__exact = person.role.role_id)
                for i in permisos:
                    request.session['permisos'].append(str(i.permissionn_id))

                # Consultando el nombre del rol del usuario autenticado
                #rol = models.Rol.objects.get(pk = user.rolid)

                data = {
                    'token': str(refresh.access_token),
                    'user': {
                        'userid':       user.userid,
                        'userfullname': 'user.userfullname',
                        'useremail':    user.useremail,
                        'rol':          'rol.rolname',
                        'puntaje':      'user.puntaje'
                    },
                    'code': 200
                }

                # Puntaje esperado para llegar a rol proximo
                # Voluntario
                # if str(rol.rolid) == '0be58d4e-6735-481a-8740-739a73c3be86':
                #    data['user']['promocion'] = {
                #        'rol': "Validador",
                #       'puntaje': int(settings['umbral-validador'])
                #   }

                # Proyectista
                # elif str(rol.rolid) == '53ad3141-56bb-4ee2-adcf-5664ba03ad65':
                #    data['user']['promocion'] = {
                #        'rol': "Proyectista",
                #        'puntaje': int(settings['umbral-proyectista'])
                #    }

            else:

                data = {
                    'status': 'error',
                    'message': 'Usuario y/o contraseña incorrecta',
                    'code': 404
                }

    except ObjectDoesNotExist:

        data = {
            'status': 'error',
            'message': 'Usuario y/o contraseña incorrecta',
            'code': 404
        }

    return JsonResponse(data, status=data['code'])


