from django.views.decorators.csrf import csrf_exempt


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated
)
# ======================== Contextos ===============================

##
# @brief Recurso de listado de contextos
# @param request Instancia HttpRequest
# @return cadena JSON
#
@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def listadoContextos(request):

    contextos = models.Context.objects.all().values()

    return JsonResponse(list(contextos), safe = False)

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def listadoContextosProyecto(request, proyid):

    try:
        models.Project.objects.get(pk=proyid)

        # Listado de IDS de contexto
        contextos = []
        contextosID = models \
                    .ProjectContext \
                    .objects \
                    .filter(proj_id=proyid)

        # Inserción de IDs en lista para consulta posterior
        for contexto in contextosID:
            contextos.append(str(contexto.context_id))

        # Consulta de contextos
        contextos = models.Context.objects.filter(pk__in=contextos).values()

        response = {
            'code':         200,
            'contextos':    list(contextos),
            'status':       'success'
        }

    except ObjectDoesNotExist:
        response = {
            'code':     404,
            'status':   'error'
        }

    except ValidationError:
        response = {
            'code':     400,
            'status':   'error'
        }

    return JsonResponse(response, safe=False, status=response['code'])

##
# @brief Recurso de almacenamiento de contextos
# @param request Instancia HttpRequest
# @return cadena JSON
#
@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def almacenamientoContexto(request):

    descripcion = request.POST.get('descripcion');

    contexto = models.Context(description=descripcion)

    try:
        contexto.full_clean()

        contexto.save()

        data = {
            'status': 'success',
            'contexto': serializers.serialize('python', [contexto])[0],
            'code': 201
        }
    except ValidationError as e:
        data = {
            'status': 'error',
            'errors': dict(e),
            'code': 400
        }

    return JsonResponse(data, safe = False, status = data['code'])

##
# @brief Recurso de eliminación de contextos
# @param request Instancia HttpRequest
# @param contextoid Identificación del contexto
# @return cadena JSON
#
@api_view(["DELETE"])
@permission_classes((IsAuthenticated,))
def eliminarContexto(request, contextoid):

    try:
        contexto = models.Context.objects.get(pk = contextoid)

        contexto.delete()

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
            'message': 'Información inválida',
            'code': 400
        }

    return JsonResponse(data, status = data['code'])

##
# @brief Recurso de actualización de contextos
# @param request Instancia HttpRequest
# @param contextoid Identificación del Contexto
# @return cadena JSON
#
@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def actualizarContexto(request, contextoid):

    descripcion = request.POST.get('descripcion')

    try:
        contexto = models.Contexto.objects.get(pk = contextoid)

        contexto.description = descripcion

        contexto.full_clean()

        contexto.save()

        data = {
            'status': 'success',
            'contexto': serializers.serialize('python', [contexto])[0],
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
            'message': 'Información inválida',
            'code': 400
        }

    return JsonResponse(data, status = data['code'])

##
# @brief Plantilla HTML de contextos
# @param request Instancia HttpRequest
# @return plantilla HTML
#
def listadoContextosView(request):

    return render(request, "contextos/listado.html")

# ======================== Datos de Contexto =======================

##
# @brief Convierte feature de Mapa a GeoJSON
# @param geometry Feature de Mapa - Puede ser Punto o Poligono
# @return GeoJSON
#
def geopandaGeojson(geometry):

    try:

        # shape = 'POINT (-76.5459307779999 3.4440059623)'.capitalize().split()
        # shape = 'POLYGON ([(0, 0), (0, 1), (1, 0)])'
        #geometry = 'POLYGON ((1059603.6619 869938.2576, 1059613.8392 869969.4889999999, 1059643.2931 869960.2558, 1059637.8753 869943.791, 1059633.082 869929.2239, 1059603.6619 869938.2576))'
        shape = geometry.capitalize().split()

        if shape[0] == 'Point':
            command = eval("shapely.geometry." + shape[0] + shape[1] + "," + shape[2])
            geojson = geopandas.GeoSeries(command).to_json()

        elif shape[0] == 'Polygon':

            coordenadas = []
            search = geometry.split('((', 1)[1].split('))')[0]
            puntos = search.split(', ')

            for p in puntos:
                coords = p.split()
                data = (float(coords[0]), float(coords[1]))
                coordenadas.append(data)

            print(coordenadas)
            polygon = shapely.geometry.Polygon(coordenadas)
            geojson = geopandas.GeoSeries(polygon).to_json()

        else:
            raise ValidationError({'csv': 'Formato de archivo no valido'})

    except ValueError as e:
        raise ValidationError({'csv': e})

    return geojson


##
# @brief Recurso de listado de datos de contexto
# @param request Instancia HttpRequest
# @return cadena JSON
#
@api_view(["GET"])
@permission_classes((AllowAny,))
def listadoDatosContextoCompleto(request):

    contextosList = []

    contextos = models.Contexto.objects.all()

    if contextos:

        for c in contextos:

            datosContexto = models.DatosContexto.objects.filter(contextoid__exact = c.contextoid)

            if datosContexto:

                contextosList.append({
                    'contextoid': c.contextoid,
                    'contexto': c.descripcion,
                    'datos': list(datosContexto.values())
                })

    data = {
        'code': 200,
        'contextos': contextosList,
        'status': 'success'
    }

    return JsonResponse(data, safe = False, status = data['code'])

##
# @brief Recurso de listado de datos de contexto por contexto
# @param request Instancia HttpRequest
# @param contextoid Identificación del Contexto
# @return cadena JSON
#
@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def listadoDatosContexto(request, contextoid):

    datosContexto = models.DatosContexto.objects.filter(contextoid__exact = contextoid).values()

    data = {
        'status': 'success',
        'datosContexto': list(datosContexto),
        'code': 200
    }

    return JsonResponse(data, safe = False, status = data['code'])

##
# @brief Recurso de almacenamiento de datos de contexto
# @param request Instancia HttpRequest
# @return cadena JSON
#
@csrf_exempt
@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def almacenarDatoContexto(request):

    # hdxtag = request.POST.get('hdxtag')
    # datavalor = " "
    # datatipe = 1
    # datosContexto = models.DatosContexto(hdxtag = hdxtag, datavalor = datavalor, datatipe = datatipe, contextoid = contextoid)

    # with open('/home/vagrant/code/opc-webpack/myapp/static/uploads/datoscontexto/' + str(datosContexto.dataid) + '.csv', 'wb+') as destination:
    #     for chunk in file.chunks():
    #         destination.write(chunk)

    try:

        if "file" in request.FILES.keys():
            file = request.FILES['file']

            if file.content_type == "text/csv" or file.content_type == "application/vnd.ms-excel":

                datosContexto = []

                # Obteniendo contentido del archivo
                fileData = str(file.read(), "utf-8")

                #Obtener lineas del archivo
                lines = fileData.splitlines()

                #leer cada linea
                for line in lines[1:]:

                   # Almacenando información en un diccionario
                   data = line.split(';')

                   #Asignación de fecha/hora en caso tal esten definidos en el archivo plano
                   try:
                    fecha = data[5]
                    hora = data[6]

                   except IndexError:
                       fecha = None
                       hora = None

                   datosContexto.append({
                    'hdxtag': data[0],
                    'descripcion': data[1],
                    'valor': data[2],
                    'metrica': data[3],
                    'geojson': geopandaGeojson(data[4]),
                    'fecha': fecha,
                    'hora': hora
                   })

                try:
                    with transaction.atomic():

                      contextoid = request.POST.get('contextoid')

                      for dt in datosContexto:
                         datosContexto = models.DatosContexto(hdxtag=dt['hdxtag'], datavalor=dt['valor'], datatipe= dt['metrica'], contextoid=contextoid, descripcion = dt['descripcion'], geojson = dt['geojson'], fecha=dt['fecha'], hora=dt['hora'])
                         datosContexto.full_clean()
                         datosContexto.save()

                    data = {
                       'code': 200,
                        'status': 'success'
                    }

                except ValidationError as e:

                   data = {
                       'code': 400,
                       'errors': dict(e)
                   }

            else:

                data = {
                    'status': 'error',
                    'errors': 'El tipo de archivo no es permitido',
                    'code': 400
                }

        else:

            data = {
                'status': 'error',
                'errors': 'No se encontro ningun archivo',
                'code': 400
            }


    except ValidationError as e:

        data = {
            'status': 'error',
            'errors': dict(e),
            'code': 400
        }

    return JsonResponse(data, safe = False, status = data['code'])

##
# @brief Recurso de eliminación de datos de contexto
# @param request Instancia HttpRequest
# @param dataid Identificación de dato de contexto
# @return cadena JSON
#
@csrf_exempt
@api_view(["DELETE"])
@permission_classes((IsAuthenticated,))
def eliminarDatoContexto(request, dataid):

    try:
        datoContexto = models.DatosContexto.objects.get(pk = dataid)

        datoContexto.delete()

        #os.remove("/home/vagrant/code/opc-webpack/myapp/static/uploads/datoscontexto/" + dataid + ".csv")

        return JsonResponse({'status': 'success'})

    except ObjectDoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'El usuario no existe'}, safe = True, status = 404)

    except ValidationError:
        return JsonResponse({'status': 'error', 'message': 'Información inválida'}, safe = True, status = 400)

##
# @brief Recurso de actualización de datos de contexto
# @param request Instancia HttpRequest
# @param dataid Identificación de dato de contexto
# @return cadena JSON
#
@csrf_exempt
@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def actualizarDatoContexto(request, dataid):
    try:
        datoContexto = models.DatosContexto.objects.get(pk=dataid)

        datoContexto.hdxtag = request.POST.get('hdxtag')
        datoContexto.descripcion = request.POST.get('descripcion')
        datoContexto.datavalor = request.POST.get('datavalor')
        datoContexto.datatipe = request.POST.get('datatipe')

        datoContexto.full_clean()

        # if "file" in request.FILES.keys():
        #
        #     file = request.FILES['file']
        #
        #     if file.content_type != "text/csv" and file.content_type != "application/vnd.ms-excel":
        #
        #         data = {
        #             'status': 'error',
        #             'errors': 'El tipo de archivo no es permitido',
        #             'code': 400
        #         }
        #         raise ValidationError(data)
        #
        #     with open('/home/vagrant/code/opc-webpack/myapp/static/uploads/datoscontexto/' + str(
        #             datoContexto.dataid) + '.csv', 'wb+') as destination:
        #         for chunk in file.chunks():
        #             destination.write(chunk)

        datoContexto.save()

        data = {
            'code': 200,
            'datoContexto': serializers.serialize('python', [datoContexto])[0],
            'status': 'success'
        }

    except ObjectDoesNotExist:

        data = {
            'code': 404,
            'status': 'error'
        }

    except ValidationError as e:

        data = {
            'code': 400,
            'errors': dict(e),
            'status': 'error'
        }

    return JsonResponse(data, safe = False, status = data['code'])

##
# @brief Plantilla de datos de contexto
# @param request Instancia HttpRequest
# @param contextoid Identificación del contexto
# @return Plantilla HTML
#
def listadoDatosContextoView(request, contextoid):

    try:
        contexto = models.Context.objects.get(pk = contextoid)

        return render(request, "contextos/datos-contexto.html", {'contexto': contexto})

    except ObjectDoesNotExist:
        code = 404

    except ValidationError:
        code = 400

    return HttpResponse("", status = code)
