from datetime import datetime
import json
import os
import http.client
from passlib.context import CryptContext

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
from myapp.view.utilidades import usuarioAutenticado, reporteEstadoProyecto, dictfetchall
 
##
# @brief Función que provee una plantilla HTML para la gestión de proyectos
# @param request Instancia HttpRequest
# @return plantilla HTML
#
def listadoProyectosView(request):
    return render(request, 'proyectos/listado.html')

##
# @brief Función que provee una plantilla HTML para la gestión de cambios de un proyecto
# @param request Instancia HttpRequest
# @return plantilla HTML
#
def gestionProyectosView(request):
    return render(request, "proyectos/gestion-proyectos-mapa.html")

    ##

# @brief Recurso de listado de proyectos
# @param request Instancia HttpRequest
# @return cadena JSON
#
@api_view(["GET"])
@permission_classes((AllowAny,))
def listadoProyectos(request):
    search = request.GET.get('search')
    page = request.GET.get('page')
    all = request.GET.get('all')

    try:
        if 'HTTP_AUTHORIZATION' in request.META.keys() and request.META['HTTP_AUTHORIZATION'] != 'null':

            # # Decodificando el access token
            # tokenBackend = TokenBackend(settings.SIMPLE_JWT['ALGORITHM'], settings.SIMPLE_JWT['SIGNING_KEY'],
            #                             settings.SIMPLE_JWT['VERIFYING_KEY'])
            # tokenDecoded = tokenBackend.decode(request.META['HTTP_AUTHORIZATION'].split()[1], verify=True)
            # #consultando el usuario
            # user = models.Usuario.objects.get(pk = tokenDecoded['user_id'])
            user = usuarioAutenticado(request)

            # ============================ Consultando proyectos ====================================

            #Consulta de proyectos para super administrador
            person = models.Person.objects.get(user__userid = user.userid)
                
            if str(person.role.role_id) == '8945979e-8ca5-481e-92a2-219dd42ae9fc':
                proyectos = models.Project.objects.all()
                # Especificando orden
                proyectos = proyectos.order_by('-proj_creation_date')
                # convirtiendo a lista de diccionarios
                proyectos = list(proyectos.values())

            # Consulta de proyectos para proyectista
            elif str(person.role.role_id) == '628acd70-f86f-4449-af06-ab36144d9d6a':
                proyectos = models.Project.objects.filter(proj_owner__pers_id__exact = person.pers_id)
                # Especificando orden
                proyectos = proyectos.order_by('-proj_creation_date')
                # convirtiendo a lista de diccionarios
                proyectos = list(proyectos.values())

            # Consulta de proyectos para voluntarios o validadores
            elif str(person.role.role_id) == '0be58d4e-6735-481a-8740-739a73c3be86' or str(person.role.role_id) == '53ad3141-56bb-4ee2-adcf-5664ba03ad65':

                #consultar los proyectos a los que está asociado el voluntario o validador
                query = "select distinct pj.* from opx.team_person as tp inner join opx.project_team as pt on pt.team_id = tp.team_id inner join opx.project as pj on pt.project_id = pj.proj_id where tp.person_id = '"+str(person.pers_id)+"' order by pj.proj_creation_date DESC;"

                with connection.cursor() as cursor:
                    cursor.execute(query)
                    PJ = dictfetchall(cursor)
                    proyectos = list(PJ)

            #Tipo de usuario distinto
            else:
                proyectos = models.Project.objects.filter(proj_name = 'qwerty')

        # Usuario Invitado
        else:
            proyectos = models.Project.objects.all()

        # ================= Busqueda de proyectos
        if search:
            proyectos = models.Project.filter(proj_name__icontains = search)


        listadoProyectos = []
        for p in proyectos:

            #Consulta del proyectista
            persona = models.Person.objects.get(pk = p['proj_owner_id'])
            p['proyectista'] = persona.pers_name + ' ' + persona.pers_lastname 

            if 'user' in locals() and str(person.role.role_id) == '628acd70-f86f-4449-af06-ab36144d9d6a':

                p['dimensiones_territoriales'] = []

                query = "select dim.* from opx.territorial_dimension as dim inner join opx.project_dimension as pd on pd.territorial_dimension_id = dim.dimension_id where pd.project_id = '"+ str(p['proj_id']) +"';"

                with connection.cursor() as cursor:
                    cursor.execute(query)
                    territorios = dictfetchall(cursor)
                    p['dimensiones_territoriales'] = list(territorios)

                query1 = "select tarea.* from opx.task as tarea where tarea.project_id = '"+str(p['proj_id'])+"';"
                with connection.cursor() as cursor:
                    cursor.execute(query1)
                    tareas = dictfetchall(cursor)
                    p['tareas'] = list(tareas)

            #Reportes
            p['reportes'] = reporteEstadoProyecto(str(p['proj_id']))

            listadoProyectos.append(p)

        if all is not None and all == "1":

            data = {
                'code': 200,
                'proyectos': listadoProyectos,
                'status': 'success'
            }

        else:

            # Paginación
            paginator = Paginator(listadoProyectos, 10)

            # Validación de página
            if page is None:
                page = 1

            #Petición de página
            proyectos = paginator.page(page).object_list

            data = {
                'code': 200,
                'paginator': {
                    'currentPage': int(page),
                    'perPage': paginator.per_page,
                    'lastPage': paginator.num_pages,
                    'total': paginator.count
                },
                'proyectos': proyectos,
                'status': 'success',
            }

    except EmptyPage:

        data = {
            'code': 404,
            'message': 'Página inexistente',
            'status': 'error'
        }

    except IndexError:
        data = {
            'code': 400,
            'status': 'error'
        }

    except TokenBackendError as e:
        data = {
            'code': 400,
            'message': str(e),
            'status': 'error'
        }

    return JsonResponse(data, safe = False, status = data['code'])

##
# @brief Recurso de almacenamiento de proyectos
# @param request Instancia HttpRequest
# @return cadena JSON
#
@csrf_exempt
@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def almacenamientoProyecto(request):
    print(request.data)
    print("1")
    user = usuarioAutenticado(request)
    person = models.Person.objects.get(user__userid = user.userid)
    print("2")
    # Decodificando el access token
    tokenBackend = TokenBackend(settings.SIMPLE_JWT['ALGORITHM'], settings.SIMPLE_JWT['SIGNING_KEY'], settings.SIMPLE_JWT['VERIFYING_KEY'])
    tokenDecoded = tokenBackend.decode(request.META['HTTP_AUTHORIZATION'].split()[1], verify=True)

    print("3")
    decisiones = request.POST.get('decisiones')
    print("4")
    contextos = request.POST.get('contextos')
    print("5")
    equipos = request.POST.get('plantillas')
    print("6")
    delimitacionGeograficas = request.POST.get('delimitacionesGeograficas')
    print("7")
    tipoP = models.ProjectType.objects.get(projtype_id__exact = request.POST.get('tiproid'))
    
    try:
        with transaction.atomic():
            print("8")
            if((delimitacionGeograficas != "[]") and (decisiones != "[]") and (contextos != "[]") and (equipos != "[]")):
                print("9")
                proyecto = models.Project(
                    proj_name = request.POST.get('proynombre'),
                    proj_description= request.POST.get('proydescripcion'),
                    proj_external_id = 12345,
                    proj_close_date = request.POST.get('proyfechacierre'),
                    proj_start_date = request.POST.get('proyfechainicio'),
                    proj_completness = 0,
                    project_type = tipoP,
                    proj_owner = person
                )
                print("10")
                proyecto.full_clean()
                print("11")
                proyecto.save()
                print("12")

                delimitacionGeograficas = json.loads(delimitacionGeograficas)
                almacenarDelimitacionesGeograficas(proyecto, delimitacionGeograficas)

                print("13")
                decisiones = json.loads(decisiones)
                almacenarDecisionProyecto(proyecto, decisiones)

                print("14")
                contextos = json.loads(contextos)
                almacenarContextosProyecto(proyecto, contextos)

                print("15")
                equipos = json.loads(equipos)
                asignarEquipos(proyecto, equipos)

                print("16")
                data = serializers.serialize('python', [proyecto])[0]

                print("17")
                data = {
                    'code': 201,
                    'proyecto': data,
                    'status': 'success'
                }
            else:
                raise ValidationError({'Información incompleta'})

    except ValidationError as e:
        proyecto.delete()
        try:
            errors = dict(e)
        except ValueError:
            errors = list(e)[0]

        data = {
            'code': 400,
            'errors': errors,
            'message': str(e),
            'status': 'error'
        }

    except IntegrityError as e:

        data = {
            'code': 500,
            'message': str(e),
            'status': 'success'
        }

    except ObjectDoesNotExist as e:
        data = {
            'code': 404,
            'message': str(e),
            'status': 'error'
        }
    print("18")
    return JsonResponse(data, safe = False, status = data['code'])

##
# @brief Funcion que asigna decision(es) a un proyecto especifico
# @param proyecto instancia del modelo proyecto
# @param decisiones listado de identificadores de decisiones
# @return booleano
#
def almacenarDecisionProyecto(proyecto, decisiones):
    print(decisiones)
    try:
        for decisionI in decisiones:
            print("acáaaaaaaaaaaaaaaaaaa")
            print(decisionI+ "ESTO FUE")
            desicionP = None
            decisionProyecto = None

            desicionP = models.Decision.objects.get(decs_id__exact = decisionI)

            decisionProyecto = models.ProjectDecision(
                project = proyecto, 
                decision = desicionP
            )

            decisionProyecto.save()

        return True

    except ValidationError as e:
        return False


        ##
# @brief Funcion que asigna contexto(s) a un proyecto especifico
# @param proyecto instancia del modelo proyecto
# @param contextos listado de identificadores de contextos
# @return booleano
#
def almacenarContextosProyecto(proyecto, contextos):

    try:
        for contexto in contextos:
            contextoP = None
            contextoProyecto = None

            contextoP = models.Context.objects.get(context_id__exact = contexto)
            contextoProyecto = models.ProjectContext(
                project = proyecto, 
                context = contextoP
            )

            contextoProyecto.save()


        return True

    except ValidationError as e:
        return False

##
# @brief Funcion que almacena las dimensiones geograficas de un proyecto especifico
# @param proyecto instancia del modelo proyecto
# @param delimitacionesGeograficas delimitaciones geograficas generadas por el mapa
# @return Diccionario
# 
def almacenarDelimitacionesGeograficas(proyecto, delimitacionesGeograficas):
    try:

            for d in delimitacionesGeograficas:
                delimitacion = None
                delimitacion = models.TerritorialDimension(
                    dimension_name = d['nombre'], 
                    dimension_geojson = d['geojson'],
                    dimension_type = models.DimensionType.objects.get(dim_type_id__exact = '35b0b478-9675-45fe-8da5-02ea9ef88f1b')
                )
                delimitacion.save()
                delimitacionP = models.ProjectTerritorialDimension(
                    project = proyecto,
                    territorial_dimension = delimitacion
                )
                delimitacionP.save()
                delimitacionP = None
        
            return True

    except ValidationError as e:
        return False

##
# @brief Funcion que asigna integrantes a un proyecto en base a los integrantes de una plantilla de equipo
# @param proyecto instancia del modelo proyecto
# @param equipos lista de identificadores de plantillas de equipo
#
def asignarEquipos(proyecto, equipos):
    try:
            for equipo in equipos:
                equipoP = None
                proyectoEquipo = None

                equipoP = models.Team.objects.get(pk=equipo)

                proyectoEquipo = models.ProjectTeam(
                    team = equipoP,
                    project = proyecto
                )
                print(proyectoEquipo)
                proyectoEquipo.save()
    
            return True

    except ValidationError as e:
        return False

##
# @brief recurso de actualización de proyectos
# @param request Instancia HttpRequest
# @param proyid Identificación del proyecto
# @return cadena JSON
#
@csrf_exempt
@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def actualizarProyecto(request, proyid):
    try:
        proyecto = models.Project.objects.get(pk=proyid)
        decisiones = request.POST.get('decisiones')
        contextos = request.POST.get('contextos')
        equipos = request.POST.get('plantillas')
        delimitacionGeograficas = request.POST.get('delimitacionesGeograficas')

        if((delimitacionGeograficas != "[]") and (decisiones != "[]") and (contextos != "[]") and (equipos != "[]")):
            proyecto.proj_name = request.POST.get('proynombre')
            proyecto.proj_description = request.POST.get('proydescripcion')
            proyecto.project_type = models.ProjectType.objects.get(projtype_id__exact = request.POST.get('tiproid'))
            proyecto.proj_start_date = request.POST.get('proyfechainicio')
            proyecto.proj_close_date = request.POST.get('proyfechacierre')
            #Actualiza las decisiones
            decisiones = json.loads(decisiones)
            if len(decisiones)>0:
                decisionesP = models.ProjectDecision.objects.filter(project__proj_id__exact = proyecto.proj_id)
                if decisionesP.exists():
                    for decisionProj in decisionesP:
                        decisionProj.delete()

                for decision in decisiones:
                    descProj = models.ProjectDecision(project = proyecto, decision = models.Decision.objects.get(pk = decision))
                    descProj.save()

            #Actualiza los contextos
            contextos = json.loads(contextos)
            if len(contextos)>0:
                contextosP = models.ProjectContext.objects.filter(project__proj_id__exact = proyecto.proj_id)
                if contextosP.exists():
                    for contextoProj in contextosP:
                        contextoProj.delete() 
                
                for contexto in contextos:
                    contProj = models.ProjectContext(project = proyecto, context = models.Context.objects.get(pk = contexto))
                    contProj.save()

            proyecto.full_clean()
            proyecto.save()

        # ================== Notificación de Gestion de cambios ========================
#        if request.POST.get('gestionCambio', None) is not None:
    
            #obtener usuarios que hacen parte del proyecto:
#            usuarios = obtenerEmailsEquipo(proyid)

            # Detalle del Cambio
#            detalle = "<b> Fecha Inicio: </b> {} <br />" \
#                      "<b> Fecha Fin </b> {}" \
#                      .format(proyecto.proj_start_date, proyecto.proj_close_date)

            #Enviar notificaciones
#            gestionCambios(usuarios, 'proyecto', proyecto.proj_name, 2, detalle)

        return JsonResponse(serializers.serialize('python', [proyecto]), safe=False)

    except ObjectDoesNotExist:
        return JsonResponse({'status': 'error'}, status=404)

    except ValidationError as e:
        return JsonResponse({'status': 'error', 'errors': dict(e)}, status=400)

##
# @brief recurso de eliminación de proyectos
# @param request Instancia HttpRequest
# @param proyid Identificación del proyecto
# @return cadena JSON
#
@csrf_exempt
@api_view(["DELETE"])
@permission_classes((IsAuthenticated,))
def eliminarProyecto(request, proyid):

    try:
        projDeci = models.ProjectDecision.objects.filter(project__proj_id = proyid)

        for p in projDeci:
            p.delete()

        projContx = models.ProjectContext.objects.filter(project__proj_id = proyid)

        for p in projContx:
            p.delete()

        print("3")
        projTeam = models.ProjectTeam.objects.filter(project__proj_id = proyid)
        for p in projTeam:
            p.delete()

        projTerr = models.ProjectTerritorialDimension.objects.filter(project__proj_id = proyid)
        for p in projTerr:
            p.delete()

        query="select dim.* from opx.territorial_dimension as dim inner join opx.project_dimension as pd on dim.dimension_id = pd.territorial_dimension_id where pd.project_id = '"+proyid+"';"

        with connection.cursor() as cursor:
            cursor.execute(query)
            territorios = dictfetchall(cursor)
            for p in territorios:
                models.TerritorialDimension.objects.get(pk = p['dimension_id']).delete()
            
        
        projComentario = models.Comment.objects.filter(project__proj_id = proyid)
        for p in projComentario:
            p.delete()

        projTask = models.Task.objects.filter(project__proj_id = proyid)
        for p in projTask:
            p.delete()

        #borrar las tareas antes de borrar e pj al igual que
        proyecto = models.Project.objects.get(pk = proyid)
        proyecto.delete()

        return JsonResponse({'status': 'success'})

    except ObjectDoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'El usuario no existe'}, safe = True, status = 404)

    except ValidationError:
        return JsonResponse({'status': 'error', 'message': 'Información inválida'}, safe = True, status = 400)


        ##

# @brief Plantilla para la gestión del equipo de un proyecto
# @param request instancia HttpRequest
# @param proyid Identificación de un proyecto
# @return cadena JSON
#
def equipoProyectoView(request, proyid):

    try:
        models.Project.objects.get(pk = proyid)
        return render(request, "proyectos/equipo.html")

    except ObjectDoesNotExist:
        return HttpResponse("", status = 404)

    except ValidationError:
        return HttpResponse("", status = 400)

##
# @brief Recurso que provee los integrantes de un proyecto
# @param request Instancia HttpRequest
# @param proyid Identificacion del proyecto
# @return cadena JSON
#
@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def equipoProyecto(request, proyid):

    try:
        query = "select tm.team_name, tm.team_effectiveness, tm.team_leader_id, pt.proj_team_id  from opx.project as pj inner join opx.project_team as pt on pj.proj_id = pt.project_id inner join opx.team as tm on pt.team_id = tm.team_id where pj.proj_id = '"+ proyid+"' order by tm.team_name ASC"
        with connection.cursor() as cursor:
            cursor.execute(query)
            equipos = dictfetchall(cursor)

            for n in equipos:
                n['name_owner'] = (models.Person.objects.get(pk = n['team_leader_id'])).pers_name

            data = {
                'code': 200,
                'equipo': equipos,
                'status': 'success'
            }

    except ValidationError as e:

        data = {
            'code': 400,
            'equipo': list(e),
            'status': 'success'
        }

    return JsonResponse(data, safe = False, status = data['code'])


    ##
# @brief Recurso que provee los integrantes de un proyecto
# @param request Instancia HttpRequest
# @param proyid Identificacion del proyecto
# @return cadena JSON
#
@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def equiposDisponiblesProyecto(request, proyid):

    try:
        query = "select * from opx.team as team2\
            except(select team1.* from opx.project_team as pt \
            inner join opx.team as team1 on pt.team_id = team1.team_id \
            where pt.project_id = '"+proyid+"')"
            
        with connection.cursor() as cursor:
            cursor.execute(query)
            equipos = dictfetchall(cursor)

            for n in equipos:
                n['name_owner'] = (models.Person.objects.get(pk = n['team_leader_id'])).pers_name

            data = {
                'code': 200,
                'equipo': equipos,
                'status': 'success'
            }

    except ValidationError as e:
        data = {
            'code': 400,
            'equipo': list(e),
            'status': 'success'
        }

    return JsonResponse(data, safe = False, status = data['code'])

@csrf_exempt
@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def agregarEquipo(request):
    
    try:
        equipoId = request.POST.get('equipoId')
        proyectoId = request.POST.get('proyectoId')

        equipoP = models.Team.objects.get(pk=equipoId)
        proyectoP = models.Project.objects.get(pk=proyectoId)

        proyectoEquipo = models.ProjectTeam(
                team = equipoP,
                project = proyectoP
        )
    
        proyectoEquipo.save()

        data = {
            'code': 201,
            'integrante': serializers.serialize('python', [proyectoEquipo])[0],
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

    return JsonResponse(data, safe = False, status = data['code'])

@csrf_exempt
@api_view(["DELETE"])
@permission_classes((IsAuthenticated,))
def eliminarEquipo(request,equid):
        
    try:
        proyectoEquipo = models.ProjectTeam.objects.get(pk = equid)
        proyectoEquipo.delete()

        response = {
            'code': 200,
            'status': 'success'
        }

    except ValidationError as e:

        response = {
            'code': 400,
            'errors': list(e)[0],
            'status': 'error'
        }

    return JsonResponse(response, safe=False, status=response['code'])


##
# @brief recurso que provee las dimensiones geograficas de un proyecto
# @param request Instancia HttpRequest
# @param proyid Identificación del proyecto
# @return cadena JSON
#
@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def dimensionesTerritoriales(request, proyid):

    try:

        query= "select td.* from opx.territorial_dimension as td \
                inner join opx.project_dimension as pt on td.dimension_id = pt.territorial_dimension_id \
                inner join opx.project as pj on pj.proj_id = pt.project_id \
                where pj.proj_id = '"+proyid+"';"
       

        with connection.cursor() as cursor:
            cursor.execute(query)
            dimensionesTerritoriales = dictfetchall(cursor)

    
        data = {
            'code': 200,
            'dimensionesTerritoriales': list(dimensionesTerritoriales),
            'status': 'success'
        }

    except ValidationError as e:

        data = {
            'code': 400,
            'status': 'error'
        }

    except ObjectDoesNotExist:

        data = {
            'code': 404,
            'status': 'error'
        }

    return JsonResponse(data, safe = False, status = data['code'])


    ##

# @brief Función que provee una plantilla HTML para la gestión de tareas de un proyecto especifico
# @param request Instancia HttpRequest
# @param proyid Identificación de un proyecto
# @return plantilla HTML
#
def tareasProyectoView(request, proyid):

    try:
        proyecto = models.Project.objects.get(pk=proyid)
        data =  render(request, 'tareas/listado.html', {'proyecto':proyecto})
    except ObjectDoesNotExist:
        data = HttpResponse("", status=404)
    except ValidationError:
        data = HttpResponse("", status=400)

    return data

##
# @brief recurso que provee el detalle de un proyecto
# @param request Instancia HttpRequest
# @param proyid Identificación del proyecto
# @return cadena JSON
#
@api_view(['GET'])
@permission_classes((AllowAny,))
def detalleProyecto(request, proyid):

    try:
        query = "select tarea.*,tipoT.task_type_name, instrumento.instrument_name, proyecto.proj_name, prioridad.priority_name \
                from opx.project as proyecto \
                inner join opx.task as tarea on proyecto.proj_id = tarea.project_id \
                inner join opx.task_priority as prioridad on tarea.task_priority_id = prioridad.priority_id \
                inner join opx.task_type as tipoT on tarea.task_type_id = tipoT.task_type_id \
                inner join opx.instrument as instrumento on tarea.instrument_id = instrumento.instrument_id \
                where proyecto.proj_id = '"+proyid+"';"

        with connection.cursor() as cursor:
            cursor.execute(query)
            listaTareas = dictfetchall(cursor)

        data = {
            'code': 200,
            'detail':{
              #'proyecto': proyecto[0],
              'tareas': list(listaTareas)
            },
            'status': 'success'
        }

    except ObjectDoesNotExist:

        data = {
            'code': 404,
            'status': "error",
        }

    except DataError:

        data = {
            'code': 400,
            'status': 'error'
        }

    return JsonResponse(data, status = data['code'], safe = False)

    ##
# @brief recurso que provee el detalle de un proyecto
# @param request Instancia HttpRequest
# @param proyid Identificación del proyecto
# @return cadena JSON
#
@api_view(['GET'])
@permission_classes((AllowAny,))
def detalleProyectoMovil(request, proyid):

    try:
        queryProyecto= "select proyecto.*, persona.pers_name, persona.pers_lastname from opx.project as proyecto inner join opx.person as persona on persona.pers_id = proyecto.proj_owner_id where proyecto.proj_id = '"+proyid+"'"

        queryTareas = "select tarea.*,tipoT.task_type_name, instrumento.instrument_name, prioridad.priority_name, td.dimension_geojson, tr.* \
                    from opx.project as proyecto \
                    inner join opx.task as tarea on proyecto.proj_id = tarea.project_id \
                    inner join opx.task_priority as prioridad on tarea.task_priority_id = prioridad.priority_id \
                    inner join opx.task_type as tipoT on tarea.task_type_id = tipoT.task_type_id \
                    inner join opx.instrument as instrumento on tarea.instrument_id = instrumento.instrument_id \
                    inner join opx.territorial_dimension as td on td.dimension_id = tarea.territorial_dimension_id    \
                    inner join opx.task_restriction as tr on tr.restriction_id = tarea.task_restriction_id \
                    where proyecto.proj_id = '"+proyid+"';"

        with connection.cursor() as cursor:
            cursor.execute(queryProyecto)
            infoPj = dictfetchall(cursor)
            print(infoPj)      
            
        with connection.cursor() as cursor:
            cursor.execute(queryTareas)
            listaTareas = dictfetchall(cursor)   
            print(listaTareas)   

        data = {
            'code': 200,
            'detail':{
              'proyecto': infoPj[0],
              'tareas': list(listaTareas)
            },
            'status': 'success'
        }

    except ObjectDoesNotExist:

        data = {
            'code': 404,
            'status': "error",
        }

    except DataError:

        data = {
            'code': 400,
            'status': 'error'
        }

    return JsonResponse(data, status = data['code'], safe = False)