reporteClasificacion = new Vue({
    el: '#reporteRank',
    delimiters: ['[[', ']]'],
    data: {
            top: [],
            others: [],
            loading: false,
            // Campos Equipos
            topUsersFields: [
                {
                    label: 'Nombre',
                    key: 'pers_name'
                },
                {
                    label: 'Apellido',
                    key: 'pers_lastname'
                },
                {
                    label: 'Puntaje',
                    key: 'pers_score'
                },
                {
                    label: 'Clasificacion',
                    key: 'clasificacion'
                },
            ],
            // Paginación Equipos
            paginationTop: {
                currentPage: 1,
                perPage: 3
            },

            // Campos proyectos
            otherUsersFields: [
                {
                    label: 'Nombre',
                    key: 'pers_name'
                },
                {
                    label: 'Apellido',
                    key: 'pers_lastname'
                },
                {
                    label: 'Puntaje',
                    key: 'pers_score'
                },
                {
                    label: 'Clasificacion',
                    key: 'clasificacion'
                },
            ],
            paginationOtherUsers: {
                currentPage: 1,
                perPage: 10
            },
            // Busqueda proyoectos
            filteredOtherUsers: ''
    },
    created(){
        window.setTimeout(() => {
            if(window.location.pathname.substr(1, 18) == "reportes/ranking/"){
                this.listadoTop();
                this.listadoOthers();

            }
        }, 1000);
    },
    methods: {
        listadoTop(){

            axios({
                url: '/reportes/rank/?inicio=0&fin=3',
                method: 'GET',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    Authorization: getToken()
                }
            })
            .then(response => {
                if(response.data.code == 200 && response.data.status == 'success'){
                    this.top = response.data.data;
                }
            });
        },
        listadoOthers(){
            axios({
                url: '/reportes/rank/?inicio=3&fin=30',
                method: 'GET',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    Authorization: getToken()
                }
            })
            .then(response => {
                if(response.data.code == 200 && response.data.status == 'success'){
                    this.others = response.data.data;
                }
            });
        },
    },
    computed: {
        filteredOtherUs(){

            var filter = this.filteredOtherUsers && this.filteredOtherUsers.toLowerCase();
            var others = this.others;

            if(filter){

                others = others.filter((row) => {

                    return Object.keys(row).some((key) => {

                        return String(row[key]).toLowerCase().indexOf(filter) > -1;
                    });
                });
            }

            return others;
        },

    }
})