gestionPerfil = new Vue({
    el: '#gestion-perfil',
    delimiters: ['[[', ']]'],
    data: {
        informacionUsuario: {},
        iniciales: ''
    },
    mounted(){

        let path = window.location.pathname;

        if(path == "/mi-perfil/"){

            this.obtenerInformacion();
        }
    },
    methods: {
        obtenerInformacion(){

            axios({
                url: '/usuarios/detail/' + getUser().userid,
                method: 'GET',
                headers: {
                    Authorization: getToken()
                }
            })
            .then(response => {

                if(response.data.code == 200 && response.data.status == 'success'){

                    this.informacionUsuario = response.data.usuario;

                    if(this.informacionUsuario.hasOwnProperty('userfullname') && this.informacionUsuario.userfullname != null){

                        this.getIniciales(this.informacionUsuario.userfullname);
                    }
                }
            })
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

                    if(response.data.code == 200 && response.data.status == 'success'){

                        Swal.fire({
                            title: 'Exito',
                            text: 'Su información fue actualizada correctamente',
                            type: 'success'
                        });
                    }
                })
                .catch(error => {

                    Swal.fire({
                        title: 'Error',
                        text: 'Ocurrio un error. Por favor intenta de nuevo.',
                        type: 'error'
                    });
                });

             } else{

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

        }
    }
});