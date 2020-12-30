
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

##
# @brief Recurso de listado de plantillas de equipo
# @param request Instancia HttpRequest
# @return cadena JSON
#
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def listadoComentarios(request):
    comentarios = models.Comment.objects.filter(project__proj_id__exact = request.POST.get('pjId'))
    comentarios = list(comentarios.values())
    return JsonResponse(list(comentarios), safe = False)

##
# @brief Recurso de creación de plantilla de equipo
# @param request Instancia HttpRequest
# @return cadena JSON
#
@csrf_exempt
@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def crearComentario(request):
    user = usuarioAutenticado(request)
    comentario = models.Comment(
        comment_title = request.POST.get('tituloComentario'), 
        comment_description = request.POST.get('descripcionComentario'),
        project = models.Project.objects.get(pk = (request.POST.get('idPj')))
    )

    try:

        comentario.full_clean()
        comentario.save()

        response = {
            'code': 201,
            'data': model_to_dict(comentario),
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
# @brief Recurso de eliminación de plantilla de equipo
# @param request Instancia HttpRequest
# @param planid Identificación de Plantilla de Equipo
# @return cadena JSON
#
@api_view(['DELETE'])
@permission_classes((IsAuthenticated,))
def eliminarComentario(request):
    try:
        comentario = models.Comment.objects.get(pk=request.POST.get('commentid'))
        
        comentario.delete()

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
# @brief Recurso de edición de plantilla de equipo
# @param request Instancia HttpRequest
# @param planid Identificación de plantilla de Equipo
# @return cadena JSON
#
@api_view(['PUT'])
@permission_classes((IsAuthenticated,))
def actualizarComentario(request):
    try:
        comentario = models.Comment.objects.get(pk=request.POST.get('commentid'))
        
        comentario.comment_title = request.POST.get('titulo')
        comentario.comment_description = request.POST.get('descripcion')

        response = {
            'code': 200,
            'data': model_to_dict(comentario),
            'status': 'success'
        }

        comentario.full_clean()
        comentario.save()

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