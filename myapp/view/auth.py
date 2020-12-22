from datetime import datetime
import json
import os
import http.client
from passlib.context import CryptContext
import string
import random

from myapp import models

from django.conf import settings
from django.core import serializers
from django.core.mail import send_mail
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import connection
from django.http import HttpResponse, HttpResponseBadRequest
from django.http.response import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated
)

##
# @brief Plantilla de solicitud de Recuperación de Contraseña
# @param request Instancia HttpRequest
# @return plantilla HTML
#
def passwordReset(request):

    return render(request, "auth/password-reset.html")

##
# @brief Envio de Notificación de Correo para recuperación de contraseña
# @param request instancia HttpRequest
# @return Diccionario
#
@api_view(["POST"])
@permission_classes((AllowAny,))
def passwordResetVerification(request):

    try:

        email = request.POST.get('email')

        if email is None:

            data = {
                'code': 400,
                'status': 'error',
                'message': 'No has proporcionado una cuenta de correo'
            }

        else:

            # Consulta de Usuario
            usuario = models.Usuario.objects.get(useremail__exact = email)

            # Asunto
            subject = "Recuperación de contraseña"

            # Generación de Token
            token = ''.join(random.choices(string.ascii_uppercase + string.digits, k=30))

            # Estableciendo token a usuario
            usuario.usertoken = token
            usuario.save()

            # Mensaje del correo
            message = "<p> Cambia tu clave <a href='" + settings.URL_APP + "auth/password-reset/" + token + "'> Aquí </a> </p>"

            # Envío de correo electrónico
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
                html_message=message
            )

            data = {
                'code': 200,
                'status': 'success'
            }

    except ObjectDoesNotExist:

        data = {
            'code': 404,
            'status': 'error',
            'message': 'No se encontro una cuenta con el correo proporcionado'
        }

    return JsonResponse(data, status = data['code'])

##
# @brief Plantilla de Cambio de Contraseña
# @param request instancia HttpRequest
# @param token Token de Cambio de Contraseña
# @return plantilla HTML
#
def passwordResetConfirmation(request, token):

    try:
        usuario = models.Usuario.objects.get(usertoken__exact = token)

        status = True

    except ObjectDoesNotExist:

        status = False

    data = {
        'status': status,
        'token': token
    }

    return render(request, "auth/password-reset-confirmation.html", context = data)

##
# @brief Plantilla para cambio de contraseña
# @param request instancia HttpRequest
# @return Diccionario
#
@api_view(["POST"])
@permission_classes((AllowAny,))
def passwordResetDone(request):

    try:

        token = request.POST.get('token')
        password = request.POST.get('password')

        if token is None or password is None:

            data = {
                'code': 400,
                'message': 'La contraseña y/o el token no fueron proveidos',
                'status': 'error'
            }

        else:

            # Eliminación de token y modificación de contraseña
            usuario = models.Usuario.objects.get(usertoken__exact=token)

            # Contexto Passlib
            pwd_context = CryptContext(
                schemes=["pbkdf2_sha256"],
                default="pbkdf2_sha256",
                pbkdf2_sha256__default_rounds=30000
            )

            usuario.password = pwd_context.encrypt(password)
            usuario.usertoken = None
            usuario.save()

            data = {
                'code': 200,
                'status': 'success'
            }

    except ObjectDoesNotExist:

        data = {
            'code': 404,
            'status': 'error'
        }

    return JsonResponse(data, status = data['code'])