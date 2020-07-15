var app = new Vue({
    el: '#app',
    data: {
        message: 'Hello Vue!',
        seen: true,
        todos: ['vue', 'html', 'css', 'js'],
        somes: {
            name: 'star',
            age: 28,
            gender: 'M',
            ps: 'dfdfdfdf',
        },
    },
    methods: {
        testAbc: function() {
            console.log('abc')
        },
        testA: function(event) {
            console.log(event)
        }
    },
    computed: {
        testB: {
            get: function() {
                console.log('abc')
            },
            set: function(aa) {
                console.log(aa)
            }

        }

    }

})