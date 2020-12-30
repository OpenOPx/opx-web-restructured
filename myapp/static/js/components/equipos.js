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
                key: 'team_name'
            },
            {
                label: 'Efectividad',
                key: 'team_effectiveness'
            },
            {
                label: 'Lider',
                key: 'name_owner'
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
                key: 'team_name'
            },
            {
                label: 'Efectividad',
                key: 'team_effectiveness'
            },
            {
                label: 'Lider',
                key: 'name_owner'
            },
            {
                label: '',
                key: 'acciones'
            }
        ],
        paginationAvailableUsers: {
            currentPage: 1,
            perPage: 10
        },
        // Busqueda usuarios disponibles
        filterAvailableUsers: ''
    },
    created(){
        if(window.location.pathname.substr(1, 16) == "equipos/proyecto"){
            this.proyectoID = window.location.pathname.substr(18);
            this.obtenerEquipos();
            this.obtenerUsuariosDisponibles();
        }
    },
    methods: {
        obtenerEquipos(){
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
                    console.log(this.equipo)
                }
            });
        },
        obtenerUsuariosDisponibles(){

            axios({
                url: '/equipos/' + this.proyectoID + "/equipos-disponibles/",
                method: 'GET',
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {

                if(response.data.code == 200 && response.data.status == 'success'){

                    this.usuariosDisponibles = response.data.equipo;
                }
            })
        },
        addIntegrante(teamID){

            data = "equipoId=" + teamID + "&proyectoId=" + this.proyectoID;

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

                    this.obtenerEquipos();
                    this.obtenerUsuariosDisponibles();
                }
            });
        },
        eliminarIntegrante(equID){
            console.log(equID)
            axios({
                url: '/equipos/delete/' + equID,
                method: 'DELETE',
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {

                if(response.data.code == 200 && response.data.status == 'success'){

                    this.obtenerEquipos();
                    console.log(response)
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
            console.log("1")
            var filter = this.filterAvailableUsers && this.filterAvailableUsers.toLowerCase();
            console.log("2")
            var usuariosDisponibles = this.usuariosDisponibles;
            console.log("3")
            console.log(filter)
            if(filter){
                console.log("4")
                usuariosDisponibles = usuariosDisponibles.filter((row) => {
                    console.log("5")
                    return Object.keys(row).some((key) => {
                        console.log("6")
                        return String(row[key]).toLowerCase().indexOf(filter) > -1;
                    });
                });
            }

            return usuariosDisponibles;
        }
    }
})