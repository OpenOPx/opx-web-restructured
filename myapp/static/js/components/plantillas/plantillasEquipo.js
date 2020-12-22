let gestionPlantilla = new Vue({
    el: '#gestion-plantillas',
    delimiters: ['[[', ']]'],
    data: {
        almacenamientoPlantilla: {},
        plantillas: [],
        plantillaEdicion: {},
        // Paginación
        pagination: {
            currentPage: 1,
            perPage: 2
        },
        // Búsqueda
        filter: '',
        // Campos Equipo
        teamFields: [
            {
                label: 'Nombre',
                key: 'descripcion'
            },
            {
                label: '',
                key: 'acciones'
            }
        ]
    },
    created(){

        if(window.location.pathname == '/equipos/'){

            this.listadoPlantillas();
        }
    },
    methods: {
        listadoPlantillas(){

            axios({
                url: '/plantillas-equipo/list/',
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
        eliminarPlantilla(planid){

            Swal.fire({
                text: 'Estas seguro?. Es irreversible',
                type: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#3085d6',
                cancelButtonColor: '#d33',
                confirmButtonText: 'Si',
                cancelButtonText: 'No',
            })
            .then(result => {

                if(result.value){

                    axios({
                        url: '/plantillas-equipo/' + planid + '/delete/',
                        method: 'DELETE',
                        headers: {
                            Authorization: getToken(),
                        }
                    })
                    .then(response => {

                        if(response.data.code == 200 && response.data.status == 'success'){

                            this.listadoPlantillas();

                            Swal.fire({
                                title: 'Exito',
                                text: 'Plantilla Eliminada',
                                type: 'success'
                            })
                        }
                    });
                }
            });
        },
        guardarPlantilla(){

            queryString = Object.keys(this.almacenamientoPlantilla).map(key => {

                return key + "=" + this.almacenamientoPlantilla[key];
            })
            .join('&');

            axios({
                url: '/plantillas-equipo/store/',
                data: queryString,
                method: 'POST',
                headers: {
                    Authorization: getToken(),
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            })
            .then(response => {

                if(response.data.code == 201 && response.data.status == 'success'){

                    this.listadoPlantillas();
                    $("#agregar-plantilla").modal('hide');
                    this.almacenamientoPlantilla = {}
                }
            })
        },
        editarPlantilla(){

            queryString =  Object.keys(this.plantillaEdicion).map(key => {

                return key + "=" + this.plantillaEdicion[key];
            })
            .join('&');

            axios({
                url: '/plantillas-equipo/' + this.plantillaEdicion.planid,
                method: 'PUT',
                data: queryString,
                headers: {
                    Authorization: getToken(),
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            })
            .then(response => {

                if(response.data.code == 200 && response.data.status == 'success'){

                    $("#editar-plantilla").modal('hide');

                    Swal.fire({
                        title: 'Exito',
                        text: 'Plantilla modificada',
                        type: 'success',
                    });
                }
            })
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
})