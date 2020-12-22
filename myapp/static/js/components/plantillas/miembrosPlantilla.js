miembrosPlantilla = new Vue({
    el: '#gestion-miembros-plantilla',
    delimiters: ['[[', ']]'],
    data: {
        plantillaID: '',
        miembrosPlantilla: [],
        usuariosDisponibles: [],
        // Campos Equipo
        teamFields: [
            {
                label: 'Nombre',
                key: 'userfullname'
            },
            {
                label: '',
                key: 'acciones'
            }
        ],
        // Paginación Equipo
        paginationTeam: {
            currentPage: 1,
            perPage: 3
        },
        // Búsqueda Equipo
        filterTeam: '',
        // Campos usuarios Disponibles
        availableUserFields: [
            {
                label: 'Nombre',
                key: 'userfullname'
            },
            {
                label: '',
                key: 'acciones'
            }
        ],
        paginationAvailableUsers: {
            currentPage: 1,
            perPage: 3
        },
        // Busqueda usuarios disponibles
        filterAvailableUsers: ''
    },
    created(){

        window.setTimeout(() => {
            if(window.location.pathname.substr(1, 7) == "equipos" && window.location.pathname.substr(46, 8) == "miembros"){
            
                this.listadoMiembros();
                this.listadoUsuariosDisponibles();
            }

        }, 1000);
    },
    methods: {
        listadoMiembros(){

            axios({
                url: '/miembros-plantilla/' + this.plantillaID + '/list/',
                method: 'GET',
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {

                if(response.data.code == 200 && response.data.status == 'success'){

                    this.miembrosPlantilla = response.data.data;
                }
            });
        },
        listadoUsuariosDisponibles(){

            axios({
                url: '/miembros-plantilla/' + this.plantillaID + '/usuarios-disponibles/',
                method: 'GET',
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {

                if(response.data.code == 200 && response.data.status == 'success'){

                    this.usuariosDisponibles = response.data.data;
                }
            });
        },
        agregarIntegrante(userid){

            axios({
                url: '/miembros-plantilla/' + this.plantillaID + '/store/',
                method: 'POST',
                data: 'userid=' + userid,
                headers: {
                    Authorization: getToken(),
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            })
            .then(response => {

                if(response.data.code == 201 && response.data.status == 'success'){

                    this.listadoMiembros();
                    this.listadoUsuariosDisponibles();
                }
            });
        },
        eliminarIntegrante(miplid){

            Swal.fire({
                text: 'Estas seguro?',
                showCancelButton: true
            })
            .then(result => {

                if(result.value){

                     axios({
                        url: '/miembros-plantilla/' + miplid + '/delete/',
                        method: 'DELETE',
                        headers: {
                            Authorization: getToken()
                        }
                    })
                    .then(response => {

                        if(response.data.code == 200 && response.data.status == 'success'){

                            this.listadoMiembros();
                            this.listadoUsuariosDisponibles();

                            Swal.fire(
                                'Exito',
                                'Miembro Eliminado correctamente del equipo',
                                'success'
                            )
                        }
                    })
                }
            });
        }
    },
    computed: {
        filteredTeam(){

            var filter = this.filterTeam && this.filterTeam.toLowerCase();
            var miembrosPlantilla = this.miembrosPlantilla;

            if(filter){

                miembrosPlantilla = miembrosPlantilla.filter((row) => {

                    return Object.keys(row).some((key) => {

                        return String(row[key]).toLowerCase().indexOf(filter) > -1;
                    });
                });
            }

            return miembrosPlantilla;
        },
        filteredAvailableUsers(){

            var filter = this.filterAvailableUsers && this.filterAvailableUsers.toLowerCase();
            var usuariosDisponibles = this.usuariosDisponibles;

            if(filter){

                usuariosDisponibles = usuariosDisponibles.filter((row) => {

                    return Object.keys(row).some((key) => {

                        return String(row[key]).toLowerCase().indexOf(filter) > -1;
                    });
                });
            }

            return usuariosDisponibles;
        }
    }
})