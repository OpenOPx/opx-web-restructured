proyectoReporte = new Vue({
    el: '#reportes-proyectoindividual',
    delimiters: ['[[', ']]'],
    almacenamientoPlantilla: {},
    plantillas: [],
    deci: [],
    plantillaEdicion: {},
    // Paginación
    pagination: {
        currentPage: 1,
        perPage: 6
    },
    // Búsqueda
    filter: '',
    // Campos Equipo
    teamFields: [
        {
            label: 'Nombre',
            key: 'team_name'
        },
        {
            label: 'Efectividad',
            key: 'team_effectiveness'
        },
        {
            label: 'Miembros',
            key: 'team_miembros'
        },
        {
            label: '',
            key: 'acciones'
        }
    ],
    data: {
        proyecto: [], 
        tareas: [],
        comentarios: [],
        deci: [],
        projectdecision: [],
        proyectoID: '',
        loading: false,
        vistaGeneral: true,
        vistaTareas: false,
        vistaComentarios: false
    },
    created(){
        if(window.location.pathname.substr(1, 17) == "reportes/proyecto"){
            this.proyectoID = window.location.pathname.substr(19);
            this.listadoGeneral();
            this.listadoTareas();
            this.listadoComentarios();
            this.generarMapa(0);
            
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
                console.log(response.data)
                console.log("respondió" + response.data.detail.proyecto)
                if(response.data.code == 200 && response.data.status == 'success'){

                    this.proyecto = response.data.detail.proyecto;
                    console.log(this.proyecto)
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
                url: '/proyectos/'+this.proyectoID+'/tareas/',
                method: 'GET',
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {

                if(response.data.code == 200 && response.data.status == 'success' && response.data.data.length > 0){

                    this.tareas = response.data.data;

                }
            });
        }, 
        listadoComentarios(){

            axios({
                url: '/comentario/list/',
                data: this.datas(this.proyectoID),
                method: 'GET',
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {

                if(response.data.code == 200 && response.data.status == 'success'){

                    this.comentarios = response.data.data;
                }
            });
        },listadoEquipos(){
            axios({
                url: '/equipos/proyecto/'+ this.proyectoID,
                method: 'GET',
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {
                if(response.data.code == 200 && response.data.status == 'success'){
                    this.plantillas = response.data.data;
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
        //tareasXTipo(proyectoID){
//
        //    return new Promise((resolve,reject) => {
//
        //        axios({
        //            url: '/estadisticas/' + proyectoID + '/tareas-x-tipo/',
        //            method: 'GET',
        //            headers: {
        //                Authorization: getToken()
        //            }
        //        })
        //        .then(response => {
//
//
        //            
        //        })
        //    })
        //},
        //tareasXEstado(proyectoID){
//
        //    return new Promise((resolve,reject) => {
//
        //        axios({
        //            url: '/estadisticas/' + proyectoID + '/tareas-x-estado/',
        //            method: 'GET',
        //            headers: {
        //                Authorization: getToken()
        //            }
        //        })
        //        .then(response => {
//
        //            if(response.data.code == 200 && response.data.status == 'success'){
//
        //                let data = response.data.data;
//
        //                let ctx = document.getElementById("tareas-x-estado").getContext('2d')
        //                new Chart(ctx, {
        //                    type: 'doughnut',
        //                    data: {
        //                      labels: data.estados,
        //                      datasets: [
        //                        {
        //                          label: "Tareas Por Estado",
        //                          backgroundColor: ["#3e95cd", "#8e5ea2","#3cba9f","#e8c3b9","#c45850"],
        //                          data: data.cantidad
        //                        }
        //                      ]
        //                    },
        //                    options: {
        //                      title: {
        //                        display: true,
        //                        text: 'Tareas Por Estado'
        //                      }
        //                    }
        //                });
//
        //                resolve("");
//
        //            } else{
//
        //                reject("");
        //            }
        //        })
        //    });
        //},
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
        }
    },
    computed: {
        filteredTeams(){
            var filter = this.filter && this.filter.toLowerCase();
            var plantillas = this.plantillas;
            if(filter){
                var plantillas = plantillas.filter((row) => {
                    return Object.keys(row).some((key) => {
                        return String(row[key]).toLowerCase().indexOf(filter) > -1;
                    });
                });
            }
            return plantillas;
        }
    }
});