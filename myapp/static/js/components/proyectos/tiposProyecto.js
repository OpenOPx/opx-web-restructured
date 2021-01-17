tiposProyecto = new Vue({
    el: '#gestion-tipos-proyecto',
    delimiters: ['[[', ']]'],
    data: {
        almacenamientoTipoProyecto: {},
        edicionTipoProyecto: {},
        tiposProyecto: [],
        loading: false,

    },
    created(){

        if(window.location.pathname == '/tipos-proyecto/'){

            this.listadoTiposProyecto();
        }
    },
    methods: {
        listadoTiposProyecto(){
            this.loader(true)

            axios({
                url: '/tipos-proyecto/list/',
                method: 'GET',
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {
                this.loader(false)

                if(response.data.code == 200 && response.data.status == 'success'){

                    this.tiposProyecto = response.data.data;
                }
            });
        },
        almacenarTipoProyecto(){
            
            queryString = Object.keys(this.almacenamientoTipoProyecto).map(key => {
                
                return key + "=" + this.almacenamientoTipoProyecto[key];
            })
            .join('&');
            this.loader(true)

            axios({
                url: '/tipos-proyecto/store/',
                method: 'POST',
                data: queryString,
                headers: {
                    Authorization: getToken(),
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            })
            .then(response => {
                this.loader(false)

                if(response.data.code == 201 && response.data.status == 'success'){

                    this.listadoTiposProyecto();
                    $("#agregar-tipo-proyecto").modal('hide');
                    this.almacenamientoTipoProyecto = {};

                    Swal.fire({
                        title: 'Exito',
                        text: 'Almacenamiento exitoso',
                        type: 'success'
                    });
                }
            });
        },
        editarTipoProyecto(ids){
            
            queryString = Object.keys(this.edicionTipoProyecto).map(key => {
                
                return key + "=" + this.edicionTipoProyecto[key];
            })
            .join('&');
            this.loader(true)

            axios({
                url: '/tipos-proyecto/' + ids,
                method: 'POST',
                data: queryString,
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {
                this.loader(false)

                if(response.data.code == 200 && response.data.status == 'success'){

                    this.listadoTiposProyecto();
                    $("#editar-tipo-proyecto").modal('hide');

                    Swal.fire({
                        title: 'Exito',
                        text: 'Modificación exitosa',
                        type: 'success'
                    });
                }
            });
        },
        eliminarTipoProyecto(tiproid){

            Swal.fire({
                text: '¿Estas Seguro?. Es irreversible',
                type: 'warning',
                showCancelButton: true
            })
            .then(result => {

                if(result.value){
                    this.loader(true)

                    axios({
                        url: '/tipos-proyecto/' + tiproid + '/delete/',
                        method: 'DELETE',
                        headers: {
                            Authorization: getToken()
                        }
                    })
                    .then(response => {
                        this.loader(false)

                        if(response.data.code == 200 && response.data.status == 'success'){

                            this.listadoTiposProyecto();

                            Swal.fire({
                                title: 'Exito',
                                text: 'Eliminación exitosa',
                                type: 'success'
                            });
                        }
                    });
                }
            });
        },
        loader(status){
            this.loading = status;
        }
    }
})