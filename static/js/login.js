var app = new Vue({
    el: '#app',
    data: {
        username: '',
        password: '',
        login_state: '',
        other: '',
    },
    methods: {
        is_submit: function() {
            if (this.username && this.password) {
                axios.post(document.location.pathname + '/login', {
                    username: this.username,
                    password: this.password,
                    other: this.other,
                })
                .then(function(response) {
                    app.login_state = response.data.success
                    if (response.data.success) {
                        document.location.pathname = document.location.pathname + '/back_manage'
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
        axios.get(document.location.pathname + '/getkey')
        .then(function(response) {
            app.other = response.data.data
        })
        .catch(function(error) {
            console.log(error)
        })
    },
})