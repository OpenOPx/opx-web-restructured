proyectoReporte = new Vue({
    el: '#reportes-proyectoindividual',
    delimiters: ['[[', ']]'],
    data: {
        proyecto: [],
        almacenamientoComentario: {}, 
        almacenamientoPlantilla: {},
        tareas: [],
        comentarios: [],
        deci: [],
        projectdecision: [],
        equipos:[],
        proyectoID: '',
        loading: false,
        vistaGeneral: true,
        vistaTareas: false,
        vistaComentarios: false,
        plantillas: [],
        plantillaEdicion: {},
        // Paginación
        pagination: {
            currentPage: 1,
            perPage: 6
        },
        // Búsqueda
        filter: '',
        // Campos Equipo
        comentariosFields: [
            {
                label: 'Nombre',
                key: 'comment_title'
            },
            {
                label: 'Descripción',
                key: 'comment_description'
            },
            {
                label: 'Creación',
                key: 'comment_date'
            },
            {
                label: '',
                key: 'acciones'
            }
        ],
        teamFields: [
            {
                label: 'Nombre',
                key: 'team_name'
            },
            {
                label: 'cantidad',
                key: 'team_miembros'
            }
        ]
    },
    created(){
        if(window.location.pathname.substr(1, 17) == "reportes/proyecto"){
            this.proyectoID = window.location.pathname.substr(19);
            this.listadoGeneral();
            this.listadoTareas();
            this.listadoComentarios(); 
            this.listadoEquipos();
        }

    },
    methods: {
        listadoGeneral(){

            axios({
                url: '/proyectos/detail/'+ this.proyectoID,
                method: 'GET',
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {
                if(response.data.code == 200 && response.data.status == 'success'){
                    this.proyecto = response.data.detail.proyecto;
                }
            });
            axios({
                url: '/decisiones/reportes/'+ this.proyectoID,
                method: 'GET',
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {
                if(response.data.code == 200 && response.data.status == 'success'){

                    this.projectdecision = response.data.decisiones;
                }
            });
        },
        listadoTareas(){
            axios({
                
                url: '/proyectos/details/'+this.proyectoID,
                method: 'GET',
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {

                if(response.data.code == 200 && response.data.status == 'success' && response.data.detail.tareas.length > 0){
                    this.tareas = response.data.detail.tareas;
                }
            });
        }, 
        listadoComentarios(){
            axios({
                url: '/comentario/list/'+ this.proyectoID,
                method: 'GET',
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {
                if(response.data.code == 200 && response.data.status == 'success'){
                    this.comentarios = response.data.comentarios;
                }
            });
        },
        datas () {
            return {
            id: this.proyectoID
            }
        },
        listadoEquipos(){
            axios({
                url: '/equipos/list/'+ this.proyectoID,
                method: 'GET',
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {
                if(response.data.code == 200 && response.data.status == 'success'){
                    this.equipos = response.data.equipo;
                    console.log(this.equipos)
                }
            })
        },
        generarMapa(timeout, coordenadas){

            window.setTimeout(() => {

                let mapObject = L.map('dimension').setView([3.450572, -76.538705], 13);

                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
                }).addTo(mapObject);

                L.tileLayer.wms('http://ws-idesc.cali.gov.co:8081/geoserver/wms?service=WMS', {
                  layers: 'idesc:mc_barrios',
                  format: 'image/png',
                  transparent: !0,
                  version: '1.1.0'
                }).addTo(mapObject);

                var editableLayers = new L.FeatureGroup();

                mapObject.addLayer(editableLayers);

                var options = {
                    // position: 'topright',
                    draw: {
                        polygon: {
                            allowIntersection: true, // Restricts shapes to simple polygons
                            drawError: {
                                color: '#e1e100', // Color the shape will turn when intersects
                                message: '<strong>Oh snap!</strong> you can\'t draw that!' // Message that will show when intersect
                            },
                            shapeOptions: {
                                color: '#0CBAEF'
                            }
                        },
                        polyline: false,
                        circle: false, // Turns off this drawing tool
                        rectangle: false,
                        marker: false,
                        circlemaker: false
                    },
                    edit: {
                        featureGroup: editableLayers, //REQUIRED!!
                        //remove: false
                    }
                };

                var drawControl = new L.Control.Draw(options);

                mapObject.addControl(drawControl);

                mapObject.on(L.Draw.Event.CREATED, (e) => {
                    type = e.layerType;
                    layer = e.layer;

                    if (type === 'polygon' && this.cantidadAreasMapa(editableLayers) == 0) {

                        editableLayers.addLayer(layer);

                        this.delimitacionGeografica['geojson'] = JSON.stringify(layer.toGeoJSON());
                    }
                });

                mapObject.on(L.Draw.Event.DELETED, (e) => {

                     if(this.cantidadAreasMapa(editableLayers) == 0){

                        this.delimitacionGeografica.geojson = null;
                     }
                });

                if(coordenadas){

                    L.polygon(coordenadas).addTo(mapObject);
                }

                this.mapObject = mapObject;

            }, timeout);
        },
        almacenarComentario(){
            //this.almacenamientoDecision.userid = getUser().userid;
            var queryString = Object.keys(this.almacenamientoComentario).map(key => {
                return key + '=' + this.almacenamientoComentario[key]
            }).join('&');
            this.loader(true);
            axios({
                method: 'post',
                url: '/comentario/store/'+ this.proyectoID,
                data: queryString,
                headers: {
                    'Content-type': 'application/x-www-form-urlencoded',
                    Authorization: getToken()
                }
            })
            .then(response => {

                $("#agregar-comentario").modal('hide')
                this.almacenamientoComentario = {};
                this.listadoComentarios(); //HACER

                this.loader(false);

                Swal.fire({
                  title: 'Exito!',
                  text: 'Comentario creado satisfactoriamente',
                  type: 'success',
                  confirmButtonText: 'Acepto'
                });
            })
            .catch(response => {

                $("#agregar-comentario").modal('hide')
                this.almacenamientoDecision = {};

                this.loader(false);

                Swal.fire({
                  title: 'Error!',
                  text: 'Ocurrio un error. Por favor intenta de nuevo',
                  type: 'error',
                  confirmButtonText: 'Acepto'
                });
            });
        },
        loader(status){
            this.loading = status;
        },
        cambioVista(vista){

            if(vista == 1){

                this.vistaGeneral = true;
                this.vistaTareas = false;
                this.vistaComentarios = false;

            } else if(vista == 2){

                this.vistaGeneral = false;
                this.vistaTareas = true;
                this.vistaComentarios = false;
            } else{

                this.vistaGeneral = false;
                this.vistaTareas = false;
                this.vistaComentarios = true;
            }
        },
        detalle(id){

            location.href = '/reportes/' + id + '/detalle/';
        },
        eliminarComentario(id){

            Swal.fire({
              title: 'Estas seguro que quiere borrar el comentario?',
              text: "No lo puedes revertir",
              type: 'warning',
              showCancelButton: true,
              confirmButtonColor: '#3085d6',
              cancelButtonColor: '#d33',
              confirmButtonText: 'Acepto!'

            }).then((result) => {

              if (result.value) {

                this.loader(true);

                axios({
                    method: 'delete',
                    url: '/comentario/delete/' + id,
                    headers: {
                        Authorization: getToken()
                    }
                })
                .then(response => {

                    this.listadoComentarios;

                    this.loader(true);

                    Swal.fire(
                      'Eliminado!',
                      'El comentario fue eliminado de forma exitosa',
                      'success'
                    );
                })
                .catch(response => {

                     this.listadoProyectos();

                     this.loader(false);

                     Swal.fire(
                      'Error!',
                      'Ocurrio un error por favor intenta eliminar el comentario de nuevo',
                      'error'
                    );
                });
              }
            });
        },

    },
    computed: {
        filteredComments(){
            var filter = this.filter && this.filter.toLowerCase();
            var comentarios = this.comentarios
            if(filter){
                var comentarios = comentarios.filter((row) => {
                    return Object.keys(row).some((key) => {
                        return String(row[key]).toLowerCase().indexOf(filter) > -1;
                    });
                });
            }
            return comentarios;
        },
        filteredTeams(){
            var filter = this.filter && this.filter.toLowerCase();
            var equipos = this.equipos
            if(filter){
                var equipos = equipos.filter((row) => {
                    return Object.keys(row).some((key) => {
                        return String(row[key]).toLowerCase().indexOf(filter) > -1;
                    });
                });
            }
            return equipos;
        }
    }
});
