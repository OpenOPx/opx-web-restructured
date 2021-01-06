reporteMiembro = new Vue({
    el: '#reportes-individual-miembro',
    delimiters: ['[[', ']]'],
    data: {
        equipos: [],
        proyectos: [],
        personaId: '',
        persona: {},
        loading: false,
        // Campos Equipos
        teamFields: [
            {
                label: 'Nombre',
                key: 'team_name'
            },
            {
                label: 'Nombre lider',
                key: 'pers_name'
            },
            {
                label: 'Apellido lider',
                key: 'pers_lastname'
            },
            {
                label: 'Participacion',
                key: 'participation'
            },
        ],
        // Paginación Equipos
        paginationTeam: {
            currentPage: 1,
            perPage: 6
        },
        // Búsqueda Equipo
        filterTeam: '',
        // Campos proyectos
        projectFields: [
            {
                label: 'Nombre',
                key: 'proj_name'
            },
            {
                label: 'Fecha de creacion',
                key: 'proj_creation_date'
            },
            {
                label: 'Estado',
                key: 'isactive'
            },
            {
                label: 'Participacion',
                key: 'participation'
            },
        ],
        paginationProject: {
            currentPage: 1,
            perPage: 6
        },
        // Busqueda proyoectos
        filterProject: ''
    },
    created(){
            if(window.location.pathname.substr(1, 25) == "reportes/equipos/miembro/"){
                this.personaId = window.location.pathname.substr(26, 36);
                this.listadoEquipos();
                this.listadoProyectos();
                this.detalleUsuario();
            }
    },
    methods: {
        listadoEquipos(){
            axios({
                url: '/reportes/equipos/miembro/'+this.personaId+'/equipos/',
                method: 'GET',
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {
                if(response.data.code == 200 && response.data.status == 'success'){
                    this.equipos = response.data.data;
                }
            });
        },
        listadoProyectos(){
            axios({
                url: '/reportes/equipos/miembro/'+this.personaId+'/proyectos/',
                method: 'GET',
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {
                if(response.data.code == 200 && response.data.status == 'success'){
                    this.proyectos = response.data.data;
                }
            });
        },
        detalleUsuario(){
            axios({
                url: '/persona/detalle/'+this.personaId+'/',
                method: 'GET',
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {
                if(response.data.code == 200 && response.data.status == 'success'){
                    this.persona = response.data.data;
                }
            });
        },
    },
    computed: {
        filteredTeam(){
            var filter = this.filterTeam && this.filterTeam.toLowerCase();
            var equipos = this.equipos;
            if(filter){
                equipos = equipos.filter((row) => {
                    return Object.keys(row).some((key) => {
                        return String(row[key]).toLowerCase().indexOf(filter) > -1;
                    });
                });
            }
            return equipos;
        },
        filteredProject(){
            var filter = this.filterProject && this.filterProject.toLowerCase();
            var proyectos = this.proyectos;
            if(filter){
                proyectos = proyectos.filter((row) => {
                    return Object.keys(row).some((key) => {
                        return String(row[key]).toLowerCase().indexOf(filter) > -1;
                    });
                });
            }
            return proyectos;
        }

    }
})