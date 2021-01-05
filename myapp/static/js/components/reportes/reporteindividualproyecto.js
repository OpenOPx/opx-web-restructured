proyecto = new Vue({
    el: '#reportes-proyectoindividual',
    delimiters: ['[[', ']]'],
    data: {
        proyecto: [],
        tareas: [],
        comentarios: [],
        proyectoID: '',
        loading: false,
        vistaGeneral: true,
        vistaTareas: false,
        vistaComentarios: false
    },
    created(){
        if(window.location.pathname.substr(1, 17) == "reportes/proyecto"){
            this.proyectoID = window.location.pathname.substr(19);
            console.log(this.proyectoID)
            this.listadoGeneral();
            this.listadoTareas();
            this.listadoComentarios();
        }

    },
    methods: {
        listadoGeneral(){

            axios({
                url: '/estadisticas/estado-proyectos/',
                method: 'GET',
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {

                if(response.data.code == 200 && response.data.status == 'success'){

                    this.proyecto = response.data.data;
                }
            });
        },
        listadoTareas(){

            axios({
                url: '/estadisticas/proyectos-tareas/',
                method: 'GET',
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {

                if(response.data.code == 200 && response.data.status == 'success' && response.data.data.length > 0){

                    new Gantt('#proyectos-gantt', response.data.data, {
                        on_click: (task) => {

                            if(task.type == 'project'){

                                statsPromises = [this.tareasXTipo(task.id), this.tareasXEstado(task.id)];

                                Promise.all(statsPromises)
                                .then(() => {

                                    console.log("bn");
                                    $("#estadisticas-tareas").modal('show');
                                })
                                .catch((reason) => {
                                    console.log(reason)
                                    Swal.fire({
                                        title: 'Error',
                                        text: 'Ocurrio un error. Por favor intenta de nuevo',
                                        type: 'error'
                                    });
                                });
                            }
                        }
                    });
                }
            });
        },listadoComentarios(){

            axios({
                url: '/estadisticas/estado-proyectos/',
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
        tareasXTipo(proyectoID){

            return new Promise((resolve,reject) => {

                axios({
                    url: '/estadisticas/' + proyectoID + '/tareas-x-tipo/',
                    method: 'GET',
                    headers: {
                        Authorization: getToken()
                    }
                })
                .then(response => {


                    
                })
            })
        },
        tareasXEstado(proyectoID){

            return new Promise((resolve,reject) => {

                axios({
                    url: '/estadisticas/' + proyectoID + '/tareas-x-estado/',
                    method: 'GET',
                    headers: {
                        Authorization: getToken()
                    }
                })
                .then(response => {

                    if(response.data.code == 200 && response.data.status == 'success'){

                        let data = response.data.data;

                        let ctx = document.getElementById("tareas-x-estado").getContext('2d')
                        new Chart(ctx, {
                            type: 'doughnut',
                            data: {
                              labels: data.estados,
                              datasets: [
                                {
                                  label: "Tareas Por Estado",
                                  backgroundColor: ["#3e95cd", "#8e5ea2","#3cba9f","#e8c3b9","#c45850"],
                                  data: data.cantidad
                                }
                              ]
                            },
                            options: {
                              title: {
                                display: true,
                                text: 'Tareas Por Estado'
                              }
                            }
                        });

                        resolve("");

                    } else{

                        reject("");
                    }
                })
            });
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
        }
    }
});