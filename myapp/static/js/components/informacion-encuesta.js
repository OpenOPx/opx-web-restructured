let informacionEncuesta = new Vue({
    el: '#gestion-informacion-encuesta',
    delimiters: ['[[', ']]'],
    created(){

        if(window.location.pathname.substr(1, 24) == "instrumentos/informacion"){

            this.instrumentoID = window.location.pathname.substr(26, 36);
            this.informacionInstrumento();
        }
    },
    data:{
        informacion: [],
        instrumentoID: 0,
        camposIgnorados: [
            "_notes",
            "meta/instanceID",
            "end",
            "start",
            "_submission_time",
            "_uuid",
            "_bamboo_dataset_id",
            "_tags",
            "_attachments",
            "_submitted_by",
            "_geolocation",
            "_validation_status",
            "_xform_id_string",
            "_status",
            "_id",
            "__version__",
            "formhub/uuid",
            "encuestaid",
            "estado",
            "observacion"
        ],
        camposInformacion: [],
        mapeoCampos: {},
        encuestaID: 0,
        detalleEncuesta: [],
        observacionEncuesta: '',
        map: {},
        almacenamientoCartografia: {},
        tiposElementoOSM: [],
        loading: false
    },
    methods: {
        informacionInstrumento(id){

            this.loader(true);

            axios({
                method: 'GET',
                url: '/instrumentos/' + this.instrumentoID + '/informacion/',
                headers:{
                    Authorization: getToken()
                }
            })
            .then(response => {

                this.loader(false);

                if(response.data.code == 200 && response.data.status == 'success'){

                    if(response.data.info['tipoInstrumento'] == 1){

                        this.informacionEncuesta(response.data.info);

                    } else if(response.data.info['tipoInstrumento'] == 2){

                        this.informacionCartografia(response.data);
                    }
                }


            })
        },
        informacionEncuesta(info){

            this.informacion = info.info;
            camposBackend = info.campos;

            // Obtencion de campos del recurso
            camposTotales = [];

            for(let i = 0; i < camposBackend.length; i++){

                if(camposBackend[i].hasOwnProperty('label')){

                    camposTotales.push({
                        label: camposBackend[i].label[0],
                        value: camposBackend[i].$autoname
                    });
                }
            }

            // Captura de campos de interés

            this.camposInformacion = [];

            for(let i = 0; i < camposTotales.length; i++){

                let matchs = 0

                for(let j = 0; j < this.camposIgnorados.length; j++){

                    if(camposTotales[i].value == this.camposIgnorados[j]){

                        matchs++;
                    }

                    if(j == this.camposIgnorados.length - 1 && matchs == 0){

                        this.camposInformacion.push(camposTotales[i])
                        this.mapeoCampos[camposTotales[i].value] = camposTotales[i].label;
                    }
                }

            }

            // Acotación de los 3 primeros campos de la encuesta
            this.camposInformacion = this.camposInformacion.slice(0, 3);
        },
        obtenerDetalleEncuesta(info){

            this.detalleEncuesta = [];

            camposTotales = Object.keys(info);

            // Captura de campos de interés
            for(let i = 0; i < camposTotales.length; i++){

                let matchs = 0

                for(let j = 0; j < this.camposIgnorados.length; j++){

                    if(camposTotales[i] == this.camposIgnorados[j]){

                        matchs++;
                    }

                    if(j == this.camposIgnorados.length - 1 && matchs == 0){

                        //this.detalleEncuesta[camposTotales[i]] = info[camposTotales[i]];
                        this.detalleEncuesta.push({
                            label: this.mapeoCampos[camposTotales[i]],
                            value: info[camposTotales[i]]
                        });
                    }
                }

            }

            // Modal
            $("#detalle-encuesta").modal({
                show: true,
                backdrop: 'static'
            });
        },
        validarEncuesta(encuestaID, estado, observacion){

            this.encuestaID = encuestaID;

            if(estado == 1 && !observacion){

                $("#validacion-encuesta").modal({
                    show: true,
                    backdrop: 'static'
                });

            } else if(estado == 1 && observacion){

                data = {
                    estado: estado,
                    observacion: observacion
                }

                this.enviarValidacionEncuesta(data);

            } else if(estado == 2){

                data = {
                    estado: estado
                }

                this.enviarValidacionEncuesta(data);

            }
        },
        enviarValidacionEncuesta(data){

            querystring = Object.keys(data).map(key => {

                return key + "=" + data[key];
            })
            .join('&');

            axios({
                url: '/instrumentos/revisar-encuesta/' + this.encuestaID,
                method: 'POST',
                data: querystring,
                headers: {
                    Authorization: getToken(),
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            })
            .then(response => {

                this.informacionInstrumento();
                this.observacionEncuesta = '';
                $("#validacion-encuesta").modal('hide');
            });
        },
        async informacionCartografia(data){

            // Obtención de Coordenadas
            let coordenadasTM = data.info.areaOfInterest.coordinates[0][0];
            geojson = JSON.parse(data.geojson);
            let coordenadas = [];

            for(let i = 0; i < coordenadasTM.length; i++){

                coordenadas.push(coordenadasTM[i].reverse());
            }

            // Obtención del centro de las Coordenadas
            let centroCoordenadas = this.obtenerCentroCoordenadas(coordenadas);

            // Configuración del Mapa
            if(typeof mymap == 'object'){
                mymap.remove();
            }

            var mymap = L.map('tmmap').setView(centroCoordenadas, 16);

            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
            }).addTo(mymap);

            L.tileLayer.wms('http://ws-idesc.cali.gov.co:8081/geoserver/wms?service=WMS', {
              layers: 'idesc:mc_barrios',
              format: 'image/png',
              transparent: !0,
              version: '1.1.0'
            }).addTo(mymap);

            if(Object.keys(geojson).length > 0){

                editableLayers = L.geoJSON(geojson);

            } else{

                var editableLayers = new L.FeatureGroup();
            }

            mymap.addLayer(editableLayers);

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
                    polyline: true,
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
            mymap.addControl(drawControl);

            // Cargando área de la tarea
            //var polygon = L.polygon(coordenadas).addTo(mymap);

            mymap.on(L.Draw.Event.CREATED, (e) => {

                type = e.layerType;
                layer = e.layer;

                if (type === 'polygon') {

                    this.obtenerTiposElementoOSM(1);
                    this.almacenamientoCartografia.coordinates = e.layer._latlngs[0];
                    //editableLayers.addLayer(layer);

                } else if(type === "polyline"){

                    this.obtenerTiposElementoOSM(0);
                    this.almacenamientoCartografia.coordinates = e.layer._latlngs;
                    //editableLayers.addLayer(layer);
                }

                if(type === 'polygon' || type === 'polyline'){

                    $("#validacion-cartografia").modal({
                        show: true,
                        backdrop: 'static'
                    });
                }
            });

            mymap.on(L.Draw.Event.DELETED, async (e) => {

                layers = e.layers._layers
                iLayers = Object.keys(e.layers._layers)

                this.loader(true);

                for(let i = 0; i < iLayers.length; i++){

                    if(layers[iLayers[i]].hasOwnProperty('feature')){

                        await this.eliminarCartografia(layers[iLayers[i]].feature.properties.id);
                    }
                }

                this.loader(false);

                this.restablecerMapa();
                this.informacionInstrumento();
            });

            this.map = mymap;

        },
        restablecerMapa(){

            this.map.remove();
        },
        almacenarCartografia(){

            this.loader(true);

            axios({
                url: '/instrumentos/mapear/' + this.instrumentoID,
                method: 'POST',
                data: JSON.stringify(this.almacenamientoCartografia),
                headers: {
                    Authorization: getToken(),
                    'Content-Type': 'application/json'
                }
            })
            .then(response => {

                this.loader(false);

                if(response.data.code == 200 && response.data.status == 'success'){

                    this.almacenamientoCartografia = {};
                    $("#validacion-cartografia").modal('hide');
                    this.restablecerMapa();
                    this.informacionInstrumento();

                } else{

                    Swal.fire({
                        title: 'Error',
                        text: 'Ocurrio un error. Por favor intenta de nuevo',
                        type: 'error'
                    });
                }
            });
        },
        eliminarCartografia(id){

            return new Promise((resolve, reject) => {

                axios({
                    url: '/instrumentos/eliminar-cartografia/' + id,
                    method: 'DELETE',
                    headers: {
                        Authorization: getToken()
                    }
                })
                .then(response => {

                    resolve(response)
                })
                .catch(response => {

                    reject(response)
                });
            });

        },
        obtenerTiposElementoOSM(closed_way){

            this.tiposElementoOSM = [];

            axios({
                url: '/elementos-osm/list/',
                method: 'GET',
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {

                if(response.data.code == 200 && response.data.status == 'success'){

                    let elementosOSM = response.data.elementosOSM;

                    for(let i = 0; i < elementosOSM.length; i++){

                        if(elementosOSM[i]['closed_way'] == closed_way){

                            this.tiposElementoOSM.push(elementosOSM[i]);
                        }
                    }
                }
            })
            .catch(() => {

                this.tiposElementoOSM = [];
            })
        },
        obtenerCentroCoordenadas(data){

            if (!(data.length > 0)){
                return false;
            }

            var num_coords = data.length;

            var X = 0.0;
            var Y = 0.0;
            var Z = 0.0;

            for(i = 0; i < data.length; i++){
                var lat = data[i][0] * Math.PI / 180;
                var lon = data[i][1] * Math.PI / 180;

                var a = Math.cos(lat) * Math.cos(lon);
                var b = Math.cos(lat) * Math.sin(lon);
                var c = Math.sin(lat);

                X += a;
                Y += b;
                Z += c;
            }

            X /= num_coords;
            Y /= num_coords;
            Z /= num_coords;

            var lon = Math.atan2(Y, X);
            var hyp = Math.sqrt(X * X + Y * Y);
            var lat = Math.atan2(Z, hyp);

            var newX = (lat * 180 / Math.PI);
            var newY = (lon * 180 / Math.PI);

            return new Array(newX, newY);
        },
        loader(status){

            this.loading = status;
        },
    }
});