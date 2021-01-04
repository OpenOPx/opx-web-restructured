let reporteEquipo = new Vue({
    el: '#reporte-equipo',
    delimiters: ['[[', ']]'],
    data: {
        almacenamientoPlantilla: {},
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
        ]
    },
    created(){
        if(window.location.pathname == '/reportes/equipos/'){
            this.listadoEquipos();
            window.setTimeout(() => {
                this.datosGenerales();
                this.canva1();
                this.canva2();
                this.canva3();
            }, 1000);
        }
    },
    methods: {
        listadoEquipos(){
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
        canva1(){
            axios({
                url: '/reportes/equipos/estadisticas/1/',
                method: 'GET',
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {
                let data = response.data.data;
                let ctx = document.getElementById("usuariosXgenero").getContext('2d')
                
                var titulos = [];
                var valores = [];
                
                for (let i = 0; i < data.length; i++) {
                    titulos[i] = data[i].gender_name;
                    valores[i] = data[i].count;   
                }
                
                new Chart(ctx, {
                    type: 'bar',
                    data: {
                        axisY: {
                            includeZero: true
                          },
                      labels: titulos,
                      datasets: [
                        {
                          backgroundColor: ["#00B9FD", "#f4a900","#3cba9f","#e8c3b9","#c45850"],
                          data: valores
                        }
                      ]
                    },
                    options: {
                      title: {
                        display: true,
                        text: 'Usuarios por género'
                      }
                    }
                });

            })
        },
        canva2(){
            axios({
                url: '/reportes/equipos/estadisticas/2/',
                method: 'GET',
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {
                let data = response.data.data;
                let ctx = document.getElementById("usuariosXrol").getContext('2d')
                
                var titulos = [];
                var valores = [];
                
                for (let i = 0; i < data.length; i++) {
                    titulos[i] = data[i].role_name;
                    valores[i] = data[i].count;   
                }
                
                new Chart(ctx, {
                    type: 'bar',
                    data: {

                      labels: titulos,
                      datasets: [
                        {
                          backgroundColor: ["#00B9FD", "#f4a900","#3cba9f","#FDDDCA","#9370db"],
                          data: valores
                        }
                      ]
                    },
                    options: {
                      title: {
                        display: true,
                        text: 'Usuarios por rol'
                      }
                    }
                });

            })
        },
        canva3(){
            axios({
                url: '/reportes/equipos/estadisticas/3/',
                method: 'GET',
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {
                let data = response.data.data;
                let ctx = document.getElementById("usuariosXnivelE").getContext('2d')
                
                var titulos = [];
                var valores = [];
                
                for (let i = 0; i < data.length; i++) {
                    titulos[i] = data[i].educlevel_name;
                    valores[i] = data[i].count;   
                }
                
                new Chart(ctx, {
                    type: 'pie',
                    data: {

                      labels: titulos,
                      datasets: [
                        {
                          backgroundColor: ["#00B9FD", "#f4a900","#3cba9f","#FDDDCA","#9370db"],
                          data: valores
                        }
                      ]
                    },
                    options: {
                      title: {
                        display: true,
                        text: 'Usuarios por nivel educativo'
                      }
                    }
                });

            })
        },
        datosGenerales(){
            axios({
                url: '/reportes/equipos/estadisticas/generales/',
                method: 'GET',
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {
                console.log(response.data.data)
                this.datosGenerales = response.data.data;
            })
        },
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