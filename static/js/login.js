var app = new Vue({
    el: '#app',
    data: {
        username: '',
        password: '',
        login_state: '',
        login_info: '',
        other: '',
    },
    methods: {
        is_submit: function() {
            if (this.username && this.password) {
                axios.post('login', {
                    username: this.username,
                    password: this.password,
                    other: this.other,
                })
                .then(function(response) {
                    app.login_state = response.data.success
                    if (response.data.success) {
                        app.login_info = '认证成功'
                        document.location.pathname = document.location.pathname.split('/').slice(0, -1).join('/') + '/managepage'
                    }else{
                        console.log(response.data.data)
                        app.login_info = response.data.data || '认证失败'
                    }
                })
                .catch(function(error) {
                    console.log(error)
                })

            } else {
                console.log('登录信息不全')
            }
        },
    },

    created: function() {
        axios.get('getkey')
        .then(function(response) {
            app.other = response.data.data
        })
        .catch(function(error) {
            console.log(error)
        })
    },
})