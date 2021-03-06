gestionPerfil = new Vue({
    el: '#gestion-perfil',
    delimiters: ['[[', ']]'],
    data: {
        informacionUsuario: {},
        iniciales: '',
        generos: [],
        barrios: [],
        nivelesEducativos: [],
    },
    mounted(){

        let path = window.location.pathname;

        if(path == "/mi-perfil/"){

            this.obtenerInformacion();
            this.listadoGeneros();
            this.listadoBarrios();
            this.listadoNivelesEducativos();
        }
    },
    methods: {
        obtenerInformacion(){
            this.loader(true)
            axios({
                url: '/usuarios/detail/' + getUser().userid,
                method: 'GET',
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {
                this.loader(false)

                if(response.data.code == 200 && response.data.status == 'success'){

                    this.informacionUsuario = response.data.usuario;
                    //this.informacionUsuario.userfullname = this.informacionUsuario.pers_name + " " + this.informacionUsuario.pers_lastname
                    this.iniciales = this.informacionUsuario.pers_name.charAt(0)+this.informacionUsuario.pers_lastname.charAt(0)
                }
            })
        },
        listadoGeneros(){
            this.loader(true)

            axios.get('/generos/list/')
            .then(response => {
                this.loader(false)

                if(response.data.code == 200 && response.data.status == 'success'){

                    this.generos = response.data.generos;
                }
            });
        },
        listadoBarrios(){
            this.loader(true)

            axios.get('/barrios/list/')
            .then(response => {
                this.loader(false)

                if(response.data.code == 200 && response.data.status == 'success'){

                    this.barrios = response.data.barrios;
                }
            });
        },
        listadoNivelesEducativos(){
            this.loader(true)

            axios.get('/niveles-educativos/list/')
            .then(response => {
                this.loader(false)

                if(response.data.code == 200 && response.data.status == 'success'){

                    this.nivelesEducativos = response.data.nivelesEducativos;
                }
            });
        },
        verificacionPassword(){

            response = false;

            if((!this.informacionUsuario.hasOwnProperty('password') || this.informacionUsuario.password == "" ) && (!this.informacionUsuario.hasOwnProperty('passwordConfirm') || this.informacionUsuario.passwordConfirm == "" )){

                response = true;

            } else if((this.informacionUsuario.hasOwnProperty('password') && this.informacionUsuario.password != "" ) && (this.informacionUsuario.hasOwnProperty('passwordConfirm') && this.informacionUsuario.passwordConfirm != "" )){

                if(this.informacionUsuario.password == this.informacionUsuario.passwordConfirm){

                    response = true;
                }
            }

            return response;
        },
        actualizarInformacion(){
            this.loader(true)

             if(this.verificacionPassword()){

                let data = Object.keys(this.informacionUsuario).map(key => {

                    return key + "=" + this.informacionUsuario[key];
                })
                .join('&');

                axios({
                    headers: {
                        Authorization: getToken(),
                        'Content-Type': 'application/x-www-form-urlencoded'
                    },
                    data: data,
                    method: 'POST',
                    url: '/usuarios/' + getUser().userid
                })
                .then(response => {
                    this.loader(false)

                    if(response.data.code == 200 && response.data.status == 'success'){

                        Swal.fire({
                            title: 'Exito',
                            text: 'Su información fue actualizada correctamente',
                            type: 'success'
                        });
                    }
                })
                .catch(error => {
                    this.loader(false)

                    Swal.fire({
                        title: 'Error',
                        text: 'Ocurrio un error. Por favor intenta de nuevo.',
                        type: 'error'
                    });
                });

             } else{
                this.loader(false)

                Swal.fire({
                    title: 'Error',
                    text: 'Por favor diligencia la contraseña adecuadamente',
                    type: 'error'
                });
             }
        },
        getIniciales(nombre){

            let inicialesArray = nombre.split(' ');
            inicialesArray.map((letter) => {

                this.iniciales += letter.charAt(0);
            });

        },
        loader(status){

            this.loading = status;
        }
    }
});