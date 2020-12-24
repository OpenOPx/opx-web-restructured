
from datetime import datetime
import json
import os
import http.client
from passlib.context import CryptContext

from django.forms.models import model_to_dict

from django.conf import settings
from django.core import serializers
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.paginator import(
    Paginator,
    EmptyPage
)
from django.db import (connection, transaction)
from django.db.utils import IntegrityError, DataError
from django.http import HttpResponse, HttpResponseBadRequest
from django.http.response import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from rest_framework_simplejwt.backends import TokenBackend
from rest_framework_simplejwt.exceptions import TokenBackendError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated
)

from myapp import models
from myapp.view.utilidades import usuarioAutenticado


    
    #rol = str(person.role.role_id)
    #print(rol)
    #if(rol == '628acd70-f86f-4449-af06-ab36144d9d6a' or rol == '8945979e-8ca5-481e-92a2-219dd42ae9fc'):

        #plantillas = models.Team.objects.filter(user__userid = user.userid).values()

       # response = {
        #    'code': 200,
        #    'data': list(plantillas),
        #    'status': 'success'
       # }

    #else:
     #   response = {
      #      'code': 403,
       #     'message': 'Usuario no permitido',
        #    'status': 'error'
        #}

   # return JsonResponse(response, safe=False, status=response['code'])

##
# @brief Recurso de listado de equipo persona
# @param request Instancia HttpRequest
# @return cadena JSON
#
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def listadoEquiposPersona(request):

    user = usuarioAutenticado(request)
    person = models.Person.objects.get(user__userid = user.userid)

    equiposPersona = models.TeamPerson.objects.filter(person__pers_id__exact = person.pers_id)
    equiposPersona = list(equiposPersona.values())

    return JsonResponse(equiposPersona, safe = False)


##
# @brief Recurso de eliminación de equipo persona
# @param request Instancia HttpRequest
# @param planid Identificación de Plantilla de Equipo
# @return cadena JSON
#
@api_view(['DELETE'])
@permission_classes((IsAuthenticated,))
def eliminarEquipoPersona(request, teamPersonId):

    try:
        equipoPersona = models.TeamPerson.objects.get(pk=teamPersonId)
        equipoPersona.delete()

        response = {
            'code': 200,
            'status': 'success'
        }

    except ObjectDoesNotExist:

        response = {
            'code': 404,
            'status': 'error'
        }

    except ValidationError:
        response = {
            'code': 400,
            'status': 'error'
        }

    return JsonResponse(response, safe=False, status=response['code'])

##
# @brief Recurso de creación de equipo persona
# @param request Instancia HttpRequest
# @return cadena JSON
#
@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def crearEquipoPersona(request):

    try:
        equipoPersona = models.TeamPerson(
            person = request.POST.get('personaId'), 
            team = request.POST.get('equipoId'),
        )

        equipoPersona.full_clean()
        equipoPersona.save()

        response = {
            'code': 201,
            'data': model_to_dict(equipoPersona),
            'status': 'success'
        }

    except ValidationError as e:

        response = {
            'code': 400,
            'errors': dict(e),
            'status': 'success'
        }

    return JsonResponse(response, safe=False, status=response['code'])

    ##


# @brief Recurso de edición de equipo persona
# @param request Instancia HttpRequest
# @param planid Identificación de plantilla de Equipo
# @return cadena JSON
#
@api_view(['PUT'])
@permission_classes((IsAuthenticated,))
def actualizarEquipoPersona(request, teamPersonId):
    try:

        equipoPersona = models.TeamPerson.objects.get(pk=teamPersonId)

        equipoPersona.participation = request.POST.get('newParticipacion')

        response = {
            'code': 200,
            'data': model_to_dict(equipoPersona),
            'status': 'success'
        }

        equipoPersona.full_clean()
        equipoPersona.save()

    except ObjectDoesNotExist:
        response = {
            'code': 404,
            'status': 'error'
        }

    except ValidationError as e:
        response = {
            'code': 400,
            'errors': dict(e),
            'status': 'error'
        }

    return JsonResponse(response, safe=False, status=response['code'])