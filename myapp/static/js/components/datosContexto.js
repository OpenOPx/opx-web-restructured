let datoContexto = new Vue({
    delimiters: ['[[', ']]'],
    el: '#gestion-datos-contexto',
    created(){

        if(window.location.pathname.substr(1, 15) == "contextos/datos"){

            this.contextoID = window.location.pathname.substr(17, 41);
            this.listadoDatosContexto();
        }
    },
    data: {
        contextoID: 0,
        datosContexto: [],
        edicionDatoContexto: {},
        almacenamientoDatoContexto: {},
        loading: false,
        // Paginación
        pagination: {
            currentPage: 1,
            perPage: 10
        },
        // Busqueda
        filter: '',
        // Campos Datos de Contexto
        contextsDataFields: [
            {
                label: 'HDX',
                key: 'hdxtag'
            },
            {
                label: 'Descripción',
                key: 'descripcion'
            },
            {
                label: 'Valor',
                key: 'datavalor'
            },
            {
                label: 'Métrica',
                key: 'datatipe'
            },
            {
                label: '',
                key: 'acciones'
            }
        ]
    },
    methods: {
        listadoDatosContexto(){

            this.loader(true);

            axios({
                method: 'GET',
                url: '/datos-contexto/list/' + this.contextoID,
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {

                this.datosContexto = response.data.datosContexto;
                this.loader(false);
            });
        },
        almacenarDatoContexto(){

            this.loader(true);

            formData = new FormData(document.getElementById('registro-dato-contexto'))
            formData.append('contextoid', this.contextoID);

            axios({
                method: 'post',
                url: '/datos-contexto/store/',
                data: formData,
                headers: {
                    'Content-type': 'application/x-www-form-urlencoded',
                    Authorization: getToken()
                }
            })
            .then(response => {

                $("#agregar-dato-contexto").modal('hide');
                this.almacenamientoDatoContexto = {};
                this.listadoDatosContexto();

                this.loader(false);

                Swal.fire({
                  title: 'Exito!',
                  text: 'Dato de Contexto creado satisfactoriamente',
                  type: 'success',
                  confirmButtonText: 'Acepto'
                });
            })
            .catch(error => {

                this.loader(false);

                if(error.response.status == 400){

                    Swal.fire({
                      title: 'Error!',
                      text: 'El archivo no fue enviado no es de tipo CSV',
                      type: 'error',
                      confirmButtonText: 'Acepto'
                    });

                } else{

                    Swal.fire({
                      title: 'Error!',
                      text: 'Ocurrio un error. Por favor intenta de nuevo',
                      type: 'error',
                      confirmButtonText: 'Acepto'
                    });
                }
            });
        },
        eliminarDatoContexto(id){

            Swal.fire({
              title: 'Estas seguro?',
              text: "No lo puedes revertir",
              type: 'warning',
              showCancelButton: true,
              confirmButtonColor: '#3085d6',
              cancelButtonColor: '#d33',
              confirmButtonText: 'Acepto!'

            }).then((result) => {

              if (result.value) {

                this.loader(true);

                axios({
                    method: 'DELETE',
                    url: '/datos-contexto/delete/' + id,
                    headers: {
                        Authorization: getToken()
                    }
                })
                .then(response => {

                    this.listadoDatosContexto();

                    this.loader(false);

                    Swal.fire(
                      'Eliminado!',
                      'El dato de contexto fue eliminado de forma exitosa',
                      'success'
                    );
                })
                .catch(response => {

                     this.listadoDatosContexto();
                     this.loader(false);

                     Swal.fire(
                      'Error!',
                      'Ocurrio un error por favor intenta de nuevo',
                      'error'
                    );
                });
              }
            });
        },
        editarDatoContexto(){

//            formData = new FormData(document.getElementById('edicion-dato-contexto'))
//            formData.append('contextoid', this.contextoID);

            this.loader(true);

            this.edicionDatoContexto.contextoid = this.contextoID;

            querystring = Object.keys(this.edicionDatoContexto).map(key => {

                return key + "=" + this.edicionDatoContexto[key];
            }).join("&")

            axios({
                method: 'post',
                url: '/datos-contexto/' + this.edicionDatoContexto.dataid,
                data: querystring,
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    Authorization: getToken()
                }
            })
            .then(response => {

                $("#editar-dato-contexto").modal('hide');
                this.listadoDatosContexto();
                this.loader(false);

                Swal.fire(
                    'Exito!',
                    'Dato de Contexto modificado satisfactoriamente',
                    'success'
                );
            })
            .catch(error => {

                $("#editar-dato-contexto").modal('hide');

                this.loader(false);

//                if(error.response.status == 400){
//
//                    Swal.fire({
//                      title: 'Error!',
//                      text: 'El archivo no es de tipo CSV',
//                      type: 'error',
//                      confirmButtonText: 'Acepto'
//                    });
//
//                } else{

                    Swal.fire(
                        'Error!',
                        'Ocurrio un error. Por favor intenta de nuevo',
                        'error'
                    );
                //}
            });
        },
        loader(status){

            this.loading = status;
        }
    },
    computed: {
        filteredContextsData(){

            var filter = this.filter && this.filter.toLowerCase();
            var datosContexto = this.datosContexto;

            if(filter){

                datosContexto = datosContexto.filter((row) => {

                    return Object.keys(row).some((key) => {

                        return String(row[key]).toLowerCase().indexOf(filter) > -1;
                    });
                });
            }

            return datosContexto;
        }
    }
})