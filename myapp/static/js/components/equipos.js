let equipo = new Vue({
    delimiters: ['[[', ']]'],
    el: '#gestion-equipo',
    data: {
        equipo: [],
        usuariosDisponibles: [],
        proyectoID: '',
        loading: false,
        // Campos Equipo
        teamFields: [
            {
                label: 'Nombre',
                key: 'userfullname'
            },
            {
                label: 'Equipo(s)',
                key: 'equipos'
            },
            {
                label: '',
                key: 'acciones'
            }
        ],
        // Paginación Equipo
        paginationTeam: {
            currentPage: 1,
            perPage: 10
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
                label: 'Equipo(s)',
                key: 'equipos'
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

        if(window.location.pathname.substr(1, 16) == "equipos/proyecto"){

            this.proyectoID = window.location.pathname.substr(18);
            this.obtenerEquipo();
            this.obtenerUsuariosDisponibles();
        }
    },
    methods: {
        obtenerEquipo(){

            this.loader(true);

            axios({
                url: '/equipos/list/' + this.proyectoID,
                method: 'GET',
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {

                this.loader(false);

                if(response.data.code == 200 && response.data.status == 'success'){

                    this.equipo = response.data.equipo;
                }
            });
        },
        obtenerUsuariosDisponibles(){

            axios({
                url: '/equipos/' + this.proyectoID + "/usuarios-disponibles/",
                method: 'GET',
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {

                if(response.data.code == 200 && response.data.status == 'success'){

                    this.usuariosDisponibles = response.data.usuarios;
                }
            })
        },
        addIntegrante(userID){

            data = "userid=" + userID + "&proyid=" + this.proyectoID;

            axios({
                url: '/equipos/store/',
                method: 'POST',
                data: data,
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    Authorization: getToken()
                }
            })
            .then(response => {

                if(response.data.code == 201 && response.data.status == 'success'){

                    this.obtenerEquipo();
                    this.obtenerUsuariosDisponibles();
                }
            });
        },
        eliminarIntegrante(equID){

            axios({
                url: '/equipos/delete/' + equID,
                method: 'DELETE',
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {

                if(response.data.code == 200 && response.data.status == 'success'){

                    this.obtenerEquipo();
                    this.obtenerUsuariosDisponibles();
                }
            })
        },
        loader(status){

            this.loading = status;
        }
    },
    computed: {
        filteredTeam(){

            var filter = this.filterTeam && this.filterTeam.toLowerCase();
            var equipo = this.equipo;

            if(filter){

                equipo = equipo.filter((row) => {

                    return Object.keys(row).some((key) => {

                        return String(row[key]).toLowerCase().indexOf(filter) > -1;
                    });
                });
            }

            return equipo;
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