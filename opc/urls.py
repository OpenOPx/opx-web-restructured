"""opc URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import handler404, handler500

from myapp import views, proyecto, decision, equipo, comentario, decisionProyecto, equipoPersona
from myapp.view import (
    userview,
    utilidades, osm, rolesview, tiposProyecto, profileview, estadisticas, contextoview #,contextualizacion, tareas
)

urlpatterns = [

#los id's los pasan por el path y deberian pasarlos internamente

    #ANTIGUOS PATHS

    path('admin/', admin.site.urls), 

    path('', views.loginView), #OK LEO
    path('login/', views.login), #OK LEO

    #path('auth/password-reset/', auth.passwordReset),
    #path('auth/password-reset-verification/', auth.passwordResetVerification),
    #path('auth/password-reset/<str:token>', auth.passwordResetConfirmation),
    #path('auth/password-reset-done/', auth.passwordResetDone),

    path('usuarios/', userview.listadoUsuariosView), #OK LEO
    path('usuarios/list/', userview.listadoUsuarios), #OK LEO
    #path('usuarios/store/', userview.almacenarUsuario),
    path('usuarios/detail/<str:userid>', userview.detalleUsuario), #OK LEO
    #path('usuarios/delete/<str:userid>', userview.eliminarUsuario),
    #path('usuarios/<str:userid>', userview.actualizarUsuario),

    path('contextos/', contextoview.listadoContextosView), #OK S 
    path('contextos/list/', contextoview.listadoContextos), #OK S 
    path('contextos/store/', contextoview.almacenamientoContexto), #OK S 
    path('contextos/delete/<str:contextoid>', contextoview.eliminarContexto), #OK S 
    path('contextos/<str:contextoid>', contextoview.actualizarContexto), #OK S 
    path('contextos/datos/<str:contextoid>', contextoview.listadoDatosContextoView), #OK S PROBAR
    path('contextos/<str:proyid>/list/', contextoview.listadoContextosProyecto), #OK S PROBAR

    #path('datos-contexto/list/', contextoview.listadoDatosContextoCompleto), # S LO QUIERO COGER YO
    #path('datos-contexto/list/<str:contextoid>', contextoview.listadoDatosContexto), # S LO QUIERO COGER YO
    #path('datos-contexto/store/', contextoview.almacenarDatoContexto), # S LO QUIERO COGER YO
    #path('datos-contexto/delete/<str:dataid>', contextoview.eliminarDatoContexto), # S LO QUIERO COGER YO
    #path('datos-contexto/<str:dataid>', contextoview.actualizarDatoContexto), # S LO QUIERO COGER YO

    #path('decisiones/<str:proyid>/list/', views.listDecisionesProyecto),

    path('decisiones/', decision.listadoDecisionesView), #JM OK OK
    path('decisiones/list/', decision.listadoDecisiones), #JM OK OK
    path('decisiones/store/', decision.almacenarDecision), #JM OK OK
    path('decisiones/delete/<str:desiid>/', decision.eliminarDecision), #JM OK OK
    path('decisiones/<str:desiid>', decision.actualizarDecision), #JM OK OK

    path('decisiones-proyecto/<str:proyid>/', decisionProyecto.listadoDecisionesProyecto), #JM OK
    path('decisiones-proyecto/store/', decisionProyecto.almacenarDecisionProyecto), #JM ???
    path('decisiones-proyecto/delete/<str:desproid>/', decisionProyecto.eliminarDecisionProyecto), #JM OK

    #path('equipos/', plantillaEquipo.plantillasView),
    #path('equipos/<str:planid>/miembros/', plantillaEquipo.miembrosPlantillaView),
    #path('equipos/list/<str:proyid>', equipo.equipoProyecto),
    #path('equipos/<str:proyid>/usuarios-disponibles/', equipo.usuariosDisponiblesProyecto),
    #path('equipos/store/', equipo.almacenamientoEquipo),
    #path('equipos/delete/<str:equid>', equipo.eliminarEquipo),
    #path('equipos/<str:equid>', equipo.actualizarEquipo),
    #path('equipos/proyecto/<str:proyid>', equipo.equipoProyectoView),

    path('plantillas-equipo/list/', equipo.listadoEquipos), #JM OK
    path('plantillas-equipo/<str:planid>/delete/', equipo.eliminarEquipo), #JM OK
    path('plantillas-equipo/store/', equipo.crearEquipo), #JM OK
    path('plantillas-equipo/<str:planid>/', equipo.actualizarEquipo), #JM OK

    #path('miembros-plantilla/<str:planid>/list/', plantillaEquipo.miembrosPlantilla),
    #path('miembros-plantilla/<str:planid>/store/', plantillaEquipo.agregarMiembro),
    #path('miembros-plantilla/<str:miplid>/delete/', plantillaEquipo.eliminarMiembro),
    #path('miembros-plantilla/<str:planid>/usuarios-disponibles/', plantillaEquipo.miembrosDisponibles),

    path('acciones/list/', rolesview.listadoAcciones), #OK - S PERO EVALUAR LA CORRECCIÓN PROPUESTA

    path('funciones-rol/list/<str:rolid>', rolesview.listadoFuncionesRol), #ESTÁ CONFUSA - S O NO SÉ SI ES EL SUEÑO
    #path('funciones-rol/store/', rolesview.almacenamientoFuncionRol), #F, MUCHO SUEÑO - S
    #path('funciones-rol/delete/<str:funcrolid>', rolesview.eliminarFuncionRol),
    #path('funciones-rol/<str:funcrolid>', rolesview.actualizarFuncionRol),

    #path('instrumentos/', views.listadoInstrumentosView),
    #path('instrumentos/list/', views.listadoInstrumentos),
    #path('instrumentos/store/', views.almacenamientoInstrumento),
    #path('instrumentos/delete/<str:instrid>', views.eliminarInstrumento),
    #path('instrumentos/<str:instrid>', views.actualizarInstrumento),
    #path('instrumentos/<str:id>/informacion/', views.informacionInstrumento),
    #path('instrumentos/<str:id>/implementar/', views.implementarFormularioKoboToolbox),
    #path('instrumentos/<str:id>/verificar-implementacion/', views.verificarImplementaciónFormulario),
    #path('instrumentos/encuesta/crear', views.creacionEncuestaView),
    #path('instrumentos/formularios-kobotoolbox/list/', views.listadoFormulariosKoboToolbox),
    #path('instrumentos/enlace-formulario/<str:tareid>', views.enlaceFormularioKoboToolbox),
    #path('instrumentos/mapear/<str:tareid>', osm.AgregarElemento),
    #path('instrumentos/detalle-cartografia/<str:tareid>', osm.cartografiasInstrumento),
    #path('instrumentos/eliminar-cartografia/<str:cartografiaid>', osm.eliminarCartografia),
    #path('instrumentos/revisar-encuesta/<str:encuestaid>', views.revisarEncuesta),

    path('proyectos/', proyecto.listadoProyectosView), #JM
    path('proyectos/gestion/', proyecto.gestionProyectosView), #JM
    path('proyectos/list/', proyecto.listadoProyectos), #JM
    path('proyectos/store/', proyecto.almacenamientoProyecto), #JM
    #path('proyectos/delete/<str:proyid>/', proyecto.eliminarProyecto),
    #path('proyectos/<str:proyid>', proyecto.actualizarProyecto),
    #path('proyectos/detail/<str:proyid>', proyecto.detalleProyecto),
    #path('proyectos/dimensiones-territoriales/<str:proyid>', proyecto.dimensionesTerritoriales),
    #path('proyectos/<str:proyid>/tareas/', proyecto.tareasProyectoView),
    #path('proyectos/<str:dimensionid>/cambio-territorio/', proyecto.cambioTerritorio),

    path('tipos-proyecto/', tiposProyecto.tiposProyectoView), #OK - S PROBAR
    path('tipos-proyecto/list/', tiposProyecto.listadoTiposProyecto), #OK - S 
    path('tipos-proyecto/<str:tiproid>/delete/', tiposProyecto.eliminarTipoProyecto),#OK - S PROBAR
    path('tipos-proyecto/<str:tiproid>', tiposProyecto.edicionTipoProyecto), #OK - S PROBAR
    path('tipos-proyecto/store/', tiposProyecto.almacenamientoTiposProyecto), #OK - S PROBAR

    path('roles/', rolesview.listadoRolesView), #OK - S PROBAR
    path('roles/list/', rolesview.listadoRoles), #OK - S 
    path('roles/store/', rolesview.almacenamientoRol), #OK - S PROBAR
    path('roles/delete/<str:rolid>', rolesview.eliminarRol), #OK - S PROBAR
    path('roles/<str:rolid>', rolesview.actualizarRol), #OK - S PROBAR
    path('roles/permisos/<str:rolid>', rolesview.permisosRolView), #OK - S PROBAR

    #path('tareas/', tareas.listadoTareasView), #OK S
    #path('tareas/list/', tareas.listadoTareas), # S - QUEDO EN LA PARTE DE QUE LEO ANEXE LA COLUMNA DEL PROJECT ID
    #path('tareas/store/', tareas.almacenamientoTarea), S - Me dio sueño
    #path('tareas/delete/<str:tareid>/', tareas.eliminarTarea),
    #path('tareas/<str:tareid>', tareas.actualizarTarea),
    #path('tareas/datos-geoespaciales/', tareas.listadoTareasMapa),
    #path('tareas/detail/<str:tareid>', tareas.detalleTarea),
    #path('instrumentos/informacion/<str:id>', views.informacionInstrumentoView),
    #path('tareas-dimension-territorial/<str:dimensionid>', tareas.tareasXDimensionTerritorial),

    path('generos/list/', utilidades.listadoGeneros), #OK S
    path('niveles-educativos/list/', utilidades.listadoNivelesEducativos), #OK S
    #path('elementos-osm/list/', osm.elementosOsm),  # Falta cargarlo en el modelo para seguir

    path('barrios/list/', utilidades.listadoBarrios), #OK S

    #path('contextualizacion/categorizacion/', contextualizacion.categorizacion), # Falta cargarlo en el modelo para seguir
    #path('contextualizacion/todo/', contextualizacion.todo), # Falta cargarlo en el modelo para seguir
    #path('contextualizacion/mes/', contextualizacion.mensual), # Falta cargarlo en el modelo para seguir
    #path('contextualizacion/semana/', contextualizacion.semanal), # Falta cargarlo en el modelo para seguir
    #path('contextualizacion/dia/', contextualizacion.dia), # Falta cargarlo en el modelo para seguir

    # ========================== Estadisticas Antes =================================
    path('estadisticas/datos-generales/', estadisticas.datosGenerales), #OK - S PROBAR
    path('estadisticas/usuarios-x-rol/', estadisticas.usuariosXRol), #OK - S PROBAR
    path('estadisticas/usuarios-x-genero/', estadisticas.usuariosXGenero), #OK - S PROBAR
    path('estadisticas/usuarios-x-nivel-educativo/', estadisticas.usuariosXNivelEducativo), #OK - S PROBAR (OJO CON ESE NOMBRE EN LA IMAGEN DEL MODELO QUE NO ME LO VAYA A CAMBIAR)
    path('estadisticas/usuarios-x-barrio/', estadisticas.usuariosXBarrio), #OK - S PROBAR
    path('estadisticas/ranking/', estadisticas.ranking),  #OK - S PROBAR 
    path('estadisticas/tareas-x-tipo/', estadisticas.tareasXTipo), #OK - S OJO CON LOS CAMBIOS A HACER

    # ======================== Estadisticas Durante ===================================

    path('estadisticas/proyectos-tareas/', estadisticas.proyectosTareas), # QUEDÉ EN LA PARTE DE ENCUESTAS Y PROGRESO - S
    #path('estadisticas/estado-proyectos/', estadisticas.estadoActualProyectos), # AHORA QUE ME ACUERDO ESTO NO SE VA A USAR 

    # ======================== Estadisticas Después ===================================

    #path('estadisticas/proyectos-tareas-vencidos/', estadisticas.proyectosTareasVencidos),
    #path('estadisticas/estado-proyectos-vencidos/', estadisticas.estadoActualProyectosVencidos),

    # ======================== Estadísticas - Detalle Proyecto ========================

    #path('estadisticas/<str:proyid>/tareas-x-tipo/', estadisticas.tareasXTipoProyecto),
    #path('estadisticas/<str:proyid>/tareas-x-estado/', estadisticas.tareasXEstadoProyecto),
    #path('estadisticas/<str:proyid>/usuarios-x-rol/', estadisticas.usuariosXRolProyecto),
    #path('estadisticas/<str:proyid>/usuarios-x-barrio/', estadisticas.usuariosXBarrioProyecto),
    #path('estadisticas/<str:proyid>/usuarios-x-barrio/<str:keyword>', estadisticas.usuariosXBarrioEspecifico),
    #path('estadisticas/<str:proyid>/usuarios-x-genero/', estadisticas.usuariosXGeneroProyecto),
    #path('estadisticas/<str:proyid>/usuarios-x-nivel-educativo/', estadisticas.usuariosXNivelEducativoProyecto),
    #path('estadisticas/<str:proyid>/datos-generales/', estadisticas.datosGeneralesProyecto),
    #path('estadisticas/<str:proyid>/exportar-encuestas/', estadisticas.exportarDatos),
    #path('estadisticas/<str:proyid>/exportar-proyecto/', estadisticas.exportarDatosProyecto),
    #path('estadisticas/<str:proyid>/ranking/', estadisticas.rankingPorProyecto),
    #path('estadisticas/<str:proyid>/campanas/', estadisticas.dimensionesProyecto),
    #path('estadisticas/<str:dimensionid>/tareas-campana/', estadisticas.tareasDimensionProyecto),
    #path('estadisticas/<str:proyid>/instrumentos/', estadisticas.instrumentosProyecto),

    # ========================= Vista Estadísticas =====================================

    path('reportes/antes/', estadisticas.estadisticasView), #OK - S OJO CON LOS CAMBIOS A HACER
    path('reportes/durante/', estadisticas.estadisticasDuranteView), #OK - S OJO CON LOS CAMBIOS A HACER
    path('reportes/despues/', estadisticas.estadisticasDespuesView), #OK - S OJO CON LOS CAMBIOS A HACER
    path('reportes/<str:proyid>/detalle/', estadisticas.estadisticasDetalleView), #OK - S OJO CON LOS CAMBIOS A HACER

    #path('reportes/ranking/', estadisticas.rankingView),  #S - Vistas que se agregan después por nuestra funcionalidad
    #path('reportes/proyecto/', estadisticas.reportesProyectosIndividualesView), #S - Vistas que se agregan después por nuestra funcionalidad
    #path('reportes/proyectos/', estadisticas.reportesProyectosGeneralesView),  #S - Vistas que se agregan después por nuestra funcionalidad

    # =========================== Perfil ===============================================
    path('mi-perfil/', profileview.perfilView), # UFF TOCA RECONSTRUIR TODA LA CLASE DEL JS PORQUE TRABAJA SOLO LOS ATRIBUTOS DE USER QUE TENÍA ANTES USUARIO QUE PARA NOSOTROS SERÍA PERSON

    #Comment
    path('comentario/<str:proyid>/', comentario.listadoComentarios), #JM 
    path('comentario/<str:commentid>/delete/', comentario.eliminarComentario), #JM ???
    path('comentario/store/', comentario.crearComentario), #JM ???
    path('comentario/<str:commentid>/', comentario.actualizarComentario), #JM ???

    #TeamPerson
    path('equipo-persona/list/', equipoPersona.listadoEquiposPersona), #JM OK
    path('equipo-persona/<str:teamPersonId>/delete/', equipoPersona.eliminarEquipoPersona), #JM - pendiente que Leo le agregue Pk para verificar
    path('equipo-persona/store/', equipoPersona.crearEquipoPersona), #JM - pendiente que Leo le agregue Pk para verificar
    path('equipo-persona/<str:teamPersonId>/', equipoPersona.actualizarEquipoPersona), #JM -  pendiente que Leo le agregue Pk para verificar

]
