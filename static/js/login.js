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
                axios.post('/login/login', {
                    username: this.username,
                    password: this.password,
                    other: this.other,
                })
                .then(function(response) {
                    app.login_state = response.data.success
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
        axios.get('/login/getkey')
        .then(function(response) {
            app.other = response.data.data
        })
        .catch(function(error) {
            console.log(error)
        })
    },
})