from datetime import datetime
import json
import os
import http.client
from passlib.context import CryptContext

from myapp import models

from django.conf import settings
from django.core import serializers
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.mail import send_mail
from django.core.paginator import(
    Paginator,
    EmptyPage
)
from django.db import (connection, transaction)
from django.forms.models import model_to_dict
from django.db.utils import IntegrityError
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

from myapp.view import koboclient
from myapp.view.utilidades import dictfetchall, obtenerParametroSistema, obtenerEmailsEquipo, usuarioAutenticado
from myapp.view.notificaciones import gestionCambios

# =========================== Tareas ==============================

##
# @brief recurso que provee el listado de tareas
# @param request Instancia HttpRequest
# @return cadena JSON
#
@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def listadoTareas(request):

    try:
        # Obtener usuario autenticado
        usuario = usuarioAutenticado(request)
        person = models.Person.objects.get(user__userid = usuario.userid)
        tareasUsuario = []
        proyectosUsuario = []
        n = ""
        # Superadministrador
        if str(person.role_id) == '8945979e-8ca5-481e-92a2-219dd42ae9fc':
            tareasUsuario = []
            n = "SELECT tk.* FROM opx.task as tk;"
            #proyectosUsuario = []
        # Consulta de proyectos para un usuario proyectista
        elif str(person.role_id) == '628acd70-f86f-4449-af06-ab36144d9d6a':
            n = "SELECT tk.* FROM opx.person AS person INNER JOIN opx.project AS pj ON person.pers_id = pj.proj_owner_id INNER JOIN opx.task as tk ON pj.proj_id = tk.project_id where person.pers_id = '"+ str(person.pers_id)+"';"
            
            #proyectosUsuario = list(models.Project.objects.filter(proj_owner__pers_id=person.pers_id).values())

        # Consulta de proyectos para un usuario voluntario o validador
        elif str(person.role_id) == '0be58d4e-6735-481a-8740-739a73c3be86' or str(person.pers_id) == '53ad3141-56bb-4ee2-adcf-5664ba03ad65':
            n = "SELECT DISTINCT tk.* FROM opx.person AS person INNER JOIN opx.team_person AS tp ON person.pers_id =tp.person_id INNER JOIN opx.project_team AS pt ON tp.team_id = pt.team_id INNER JOIN opx.task AS tk ON tk.project_id = pt.project_id WHERE person.pers_id = '"+str(person.pers_id)+"';"

            #for t in z:
            #    proyectosUsuario[i] = models.Task.objects.filter(task_id = tasksid[i]).values('projectproject_id') #QUEDA FALTANDO A QUE LEO ANEXE LA COLUMNA DEL PROJECT ID
            #proyectosUsuario = list(models.Equipo.objects.filter(userid = usuario.userid).values('proj_owner'))


      # ================ Obtener página validación de la misma ========================
        page = request.GET.get('page')

        if (page is None):
            page = 1

        all = request.GET.get('all')

        # Obtener Búsqueda y validación de la misma
        search = request.GET.get('search')
        if search is not  None:
            if len(tareasUsuario) > 0:
                query += " and"
            query += " (t.task_name ~* '" + search + "');"        

        with connection.cursor() as cursor:
            cursor.execute(n)

            # formatear respuesta de base de datos
            tareas = dictfetchall(cursor)
        
            print(tareas[0]['task_priority_id'])

       

        # Progreso de las Tareas
        for t in tareas:
            t['task_type_name'] = (models.TaskType.objects.get(pk = t['task_type_id'])).task_type_name
            t['instrument_name']= (models.Instrument.objects.get(pk = t['instrument_id'])).instrument_name
            t['proj_name']= (models.Project.objects.get(pk = t['project_id'])).proj_name
            t['task_priority_name']= (models.TaskPriority.objects.get(pk = t['task_priority_id'])).priority_name


            # Tipo encuesta
            if t['task_type_id'] == 1:
                encuestas = models.Survery.objects.filter(task_id__exact=t['task_id']) #Me quedé varado en el survey
                progreso = (len(encuestas) * 100) / t['completness']
                t['task_quantity'] = progreso

                # instrumento = models.Instrumento.objects.get(pk=t['instrid'])
                # detalleFormulario = detalleFormularioKoboToolbox(instrumento.instridexterno)
                #
                # if(detalleFormulario):
                #     progreso = (detalleFormulario['deployment__submission_count'] * 100) / t['tarerestriccant']
                #     t['progreso'] = progreso
        print(tareas)
        if all is not None and all == "1":
            data = {
                'code': 200,
                'tareas': tareas,
                'status': 'success'
            }
        else:
            # Obtener Página
            paginator = Paginator(tareas, 10)
            # Obtener lista de tareas
            tareas = paginator.page(page).object_list
            data = {
                'code': 200,
                'paginator': {
                    'currentPage': page,
                    'perPage': paginator.per_page,
                    'lastPage': paginator.num_pages,
                    'total': paginator.count
                },
                'tareas': tareas,
                'status': 'success'
            }

    except EmptyPage:

        data = {
            'code': 400,
            'message': 'Página inexistente',
            'status': 'error'
        }

    return JsonResponse(data, safe = False, status = data['code'])

##
# @brief recurso que provee las tareas asociadas a las dimensiónes geograficas del sistema
# @param request Instancia HttpRequest
# @return cadena JSON
#
@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def listadoTareasMapa(request):

    areasMedicion = []

    #Consultando dimensiones territoriales de proyectos
    dimensionesTerritoriales = models.DelimitacionGeografica.objects.all()

    for dimension in dimensionesTerritoriales:

        tareas = models.Tarea.objects.filter(dimensionid__exact = dimension.dimensionid).values();

        data = {
            'areaMedicion': model_to_dict(dimension),
            'tareas': list(tareas)
        }

        areasMedicion.append(data)

    instrumentos = models.Instrumento.objects.filter(instrtipo__exact = 2)

    for instrumento in instrumentos:

        tareas = models.Tarea.objects.filter(instrid__exact = instrumento.instrid).values()

        areaMedicion = model_to_dict(instrumento)
        areaMedicion['nombre'] = areaMedicion['instrnombre']
        del areaMedicion['instrnombre']

        data = {
            'areaMedicion': areaMedicion,
            'tareas': list(tareas)
        }

        areasMedicion.append(data)

    data = {
        'code': 200,
        'areasMedicion': areasMedicion,
        'status': 'success'
    }

    return JsonResponse(data, status=data['code'], safe=False)

##
# @brief recurso que provee el detalle de una tarea
# @param request Instancia HttpRequest
# @param tareid Identificación de una tarea
# @return cadena JSON
#
@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def detalleTarea(request, tareid):

    try:
        tarea = models.Tarea.objects.get(pk = tareid)

        tareaDict = model_to_dict(tarea)
        
        # Tipo encuesta
        if tareaDict['task_type_id'] == 1:

            encuestas = models.Encuesta.objects.filter(tareid__exact=tarea.tareid)
            progreso = (len(encuestas) * 100) / tareaDict['tarerestriccant']
            tareaDict['progreso'] = progreso

            # instrumento = models.Instrumento.objects.get(pk=tareaDict['instrid'])
            # detalleFormulario = detalleFormularioKoboToolbox(instrumento.instridexterno)
            #
            # if detalleFormulario:
            #     progreso = (detalleFormulario['deployment__submission_count'] * 100) / tareaDict['tarerestriccant']
            #     tareaDict['progreso'] = progreso

        data = {
            'code': 200,
            'status': 'success',
            'tarea': tareaDict
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

    return JsonResponse(data, status = data['code'], safe = False)

##
# @brief recurso de almacenamiento de Tareas
# @param request Instancia HttpRequest
# @return cadena JSON
#
@csrf_exempt
@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def almacenamientoTarea(request): #Por aquí iba

    tareNombre = request.POST.get('tarenombre')
    tareTipo = request.POST.get('taretipo')
    tareRestricGeo = "{}"
    tareRestricCant = request.POST.get('tarerestriccant')
    tareRestricTime = "{}"
    instrID = request.POST.get('instrid')
    proyID = request.POST.get('proj_id')
    dimensionid = request.POST.get('dimensionid')
    geojson_subconjunto = request.POST.get('geojsonsubconjunto')
    taredescripcion = request.POST.get('taredescripcion')
    tareprioridad = request.POST.get('tareprioridad')
    isactive = request.POST.get('isactive')

    restriccion = models.TaskRestriction()
    restriccion.full_clean()
    restriccion.save()

    territoriodentroproyecto = models.TerritorialDimension()
    territoriodentroproyecto.full_clean()
    territoriodentroproyecto.save(geojson_subconjunto)

    instrumento = models.object.get(instrument_id = instrID)



    tarea = models.Task(task_name = tareNombre, task_type_id = tareTipo, task_restriction = restriccion,
                         instrument= instrID, project = proyID, territorial_dimension = dimensionid,  task_description = taredescripcion, isactive = isactive,
                         task_priority=tareprioridad)

    try:
        tarea.full_clean()

        tarea.save()
        data = serializers.serialize('python', [tarea])

        response = {
            'code':     201,
            'tarea':    data,
            'status':   'success'
        }

    except ValidationError as e:
        response = {
            'code':     400,
            'errors':   dict(e),
            'status':   'error'
        }

    except IntegrityError as e:
        response = {
            'code':     400,
            'message':  str(e),
            'status':   'success'
        }

    return JsonResponse(response, safe=False, status=response['code'])

##
# @brief recurso de eliminación de tareas
# @param request Instancia HttpRequest
# @param tareid Identificación de una tarea
# @return cadena JSON
#
@csrf_exempt
@api_view(["DELETE"])
@permission_classes((IsAuthenticated,))
def eliminarTarea(request, tareid):

    try:
        tarea = models.Tarea.objects.get(pk = tareid)
        task_type 
        tarea.delete()

        return JsonResponse({'status': 'success'})

    except ObjectDoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'El usuario no existe'}, safe = True, status = 404)

    except ValidationError:
        return JsonResponse({'status': 'error', 'message': 'Información inválida'}, safe = True, status = 400)

##
# @brief recurso de actualización de tareas
# @param request Instancia HttpRequest
# @param tareid Identificación de una tarea
# @return cadena JSON
#
@csrf_exempt
@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def actualizarTarea(request, tareid):
    try:
        tarea = models.Tarea.objects.get(pk=tareid)

        estado = int(request.POST.get('tareestado'))

        tarea.tarenombre = request.POST.get('tarenombre')
        #tarea.taretipo = request.POST.get('taretipo')
        tarea.tarerestriccant = request.POST.get('tarerestriccant')
        tarea.proyid = request.POST.get('proj_id')
        tarea.taredescripcion = request.POST.get('taredescripcion')
        tarea.tareprioridad = request.POST.get('tareprioridad');

        tarea.full_clean()

        if estado == 2 and tarea.tareestado != 2:

            if validarTarea(tarea):

                tarea.tareestado = estado
                tarea.save()

        else:

            tarea.tareestado = estado
            tarea.save()

        # Verificando que el recurso haya sido llamado desde Gestión de Cambios
        if request.POST.get('gestionCambio', None) is not None:

            # Obtener los usuarios que hacen del proyecto
            usuarios = obtenerEmailsEquipo(tarea.proyid)

            # Detalle del Cambio
            detalle = "Encuestas Objetivo: {}".format(tarea.tarerestriccant)

            # Enviar Notificaciones
            gestionCambios(usuarios, 'tarea', tarea.task_name, 1, detalle)

        response = {
            'code': 200,
            'tarea': serializers.serialize('python', [tarea])[0],
            'status': 'success'
        }

    except ObjectDoesNotExist as e:
        response = {
            'code': 404,
            'message': str(e),
            'status': 'error'
        }

    except ValidationError as e:

        try:
            errors = dict(e)
        except ValueError:
            errors = list(e)[0]

        response = {
            'code': 400,
            'errors': errors,
            'status': 'error'
        }

    except IntegrityError as e:
        response = {
            'code': 500,
            'message': str(e),
            'status': 'error'
        }

    return JsonResponse(response, safe=False, status=response['code'])

##
# @brief Función que se encarga de validar una tarea especifica
# @param tarea Instancia del modelo Tarea
# @return Booleano
#
def validarTarea(tarea):

    if ((tarea.tareestado == 1 and tarea.task_type_id == 1) or (tarea.tareestado != 2 and tarea.taretipo == 2)):

        if tarea.task_type_id == 1:

            encuestasSinValidar = models.Encuesta.objects.filter(instrid__exact=tarea.instrid) \
                                                         .filter(estado__exact=0)

            if len(encuestasSinValidar) == 0:

                aportePositivo = int(obtenerParametroSistema('aporte-positivo-encuesta'))
                aporteNegativo = int(obtenerParametroSistema('aporte-negativo-encuesta'))

                encuestas = models.Encuesta.objects.filter(instrid__exact=tarea.instrid)

                with transaction.atomic():
                    for encuesta in encuestas:

                        if encuesta.estado == 1:
                            puntaje = aporteNegativo

                        elif encuesta.estado == 2:
                            puntaje = aportePositivo

                        asignacionPuntaje(encuesta.userid, tarea.tareid, puntaje)

                response = True

            else:
                raise ValidationError(['Todas las encuestas deben ser validadas'])

        elif tarea.task_type_id == 2:

            cartografias = models.Cartografia.objects.filter(instrid__exact=tarea.instrid)

            if len(cartografias) > 0:

                aportePositivo = int(obtenerParametroSistema('aporte-positivo-cartografia'))
                aporteNegativo = int(obtenerParametroSistema('aporte-negativo-cartografia'))

                with transaction.atomic():

                    for cartografia in cartografias:

                        # Si las cartografias no fueron marcadas como malas se marcan como buenas
                        if cartografia.estado == 0:
                            cartografia.estado = 2
                            cartografia.save()
                            puntaje = aportePositivo

                        if cartografia.estado == 1:
                            puntaje = aporteNegativo

                        if cartografia.estado == 2:
                            puntaje = aportePositivo

                        asignacionPuntaje(cartografia.userid, tarea.tareid, puntaje)

                response = True

            else:
                raise ValidationError(['No hay cartografias'])
    else:
        raise ValidationError(['La tarea no esta terminada o ya fue validada'])

    return response

##
# @brief Funcion que se encarga de aumentar el puntaje actual de un usuario
# @param userid Identificación del usuario
# @param tareid Identificación de una tarea
# @param puntaje puntaje a sumar o restar para un usuario
#
def asignacionPuntaje(userid, tareid, puntaje):

    # Almacenar historial de asignación
    asignacion = models.AsignacionPuntaje(userid=userid, tareid=tareid, puntaje=puntaje)
    asignacion.save()

    #Asignacion de puntos correspondientes
    usuario = models.Usuario.objects.get(pk=userid)
    usuario.puntaje = usuario.puntaje + puntaje
    usuario.save()

    promoverUsuario(usuario)

##
# @brief Función que promueve un usuario de rol en caso tal cumpla con el puntaje requerido
# @param user Instancia del modelo Usuario
#
def promoverUsuario(user):

    puntajeValidador = int(obtenerParametroSistema('umbral-validador'))
    puntajeProyectista = obtenerParametroSistema('umbral-proyectista')

    # Promoción de voluntario a validador
    if user.rolid == '0be58d4e-6735-481a-8740-739a73c3be86' and user.puntaje >= puntajeValidador:
        user.rolid = '53ad3141-56bb-4ee2-adcf-5664ba03ad65'
        user.save()

        notificacionPromocionUsuario(user, 'Validador')

    # Promocion de Validador a Proyectista
    if user.rolid == '53ad3141-56bb-4ee2-adcf-5664ba03ad65' and user.puntaje >= puntajeProyectista:
        user.rolid = '628acd70-f86f-4449-af06-ab36144d9d6a'
        user.save()

        notificacionPromocionUsuario(user, 'Proyectista')

##
# @brief Función que envía una notificación via correo a un usuario cuando es promovido de Rol
# @param user Instancia del modelo Usuario
# @param rol Nombre del nuevo rol del usuario
#
def notificacionPromocionUsuario(user, rol):

    subject = "Notificación OPC"
    message = "<p>Felicitaciones. Ahora eres " + rol

    # Envío de correo electrónico
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [user.useremail],
        fail_silently=False,
        html_message=message
    )

##
# @brief Recurso que provee las tareas que hacen parte de una dimensión geográfica
# @param request Instancia HttpRequest
# @param dimensionid Identificación de la dimensión geográfica
#
def tareasXDimensionTerritorial(request, dimensionid):

    try:
        dimensionTerritorial = models.DelimitacionGeografica.objects.get(pk=dimensionid)

        tareas = models.Tarea.objects.filter(dimensionid__exact=dimensionid).values()

        response = {
            'code': 200,
            'data': list(tareas),
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
# @brief Función que provee la plantilla HTML para la gestión de tareas
# @param request Instancia HttpRequest
# @return plantilla HTML
#
def listadoTareasView(request):

    return render(request, 'tareas/listado.html')