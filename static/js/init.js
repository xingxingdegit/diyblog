
var app = new Vue({
    el: '#app',
    data: {
        userdata: {
            sitename: '',
            admin_url: '',
            username: '',
            password: '',
        },
        connect_info: '正在连接服务器',
        websocket: {
            is_show: false,
            progress: 1,
            progress_info: [],
        },
        show_nav: false,

    },
    methods: {
        is_submit: function () {
            if (this.userdata) {
                this.websocket.is_show = true
                socket.emit('init', this.userdata)
                this.connect_info = '开始初始化...'
            } else {
                this.connect_ = '用户信息填写错误'
            }
        },

    },
    computed: {
        all_admin_url: function () {
            return 'admin/' + this.userdata.admin_url
        }
    }
})

socket = io();
socket.on('connect', function() {
    app.connect_info = '服务器已连接'
})

var init_key = ''
socket.on('init', function(data) {
    if (data.stage == 'start') {
        app.websocket.progress_info.push({class: "show-key", info: data.data})
    } else if (data.stage == 'end' ) {
        app.websocket.progress_info.push({class: "show-key", info: data.data})
        if (data.state) {
            app.connect_info = '初始化完毕'
            app.show_nav = true
        } else {
            app.connect_info = '初始化失败'
        }

    } else if (data.stage == 'in' && data.data.type == "key") {
        init_key = data.data.tag
        app.websocket.progress_info.push({class: "show-key", info: data.data.data})
        app.websocket.progress = data.data.progress
    } else if (data.stage == 'in' && data.data.type == 'value') {
        app.websocket.progress = data.data.progress
        if (init_key != data.data.tag) {
            app.websocket.progress_info.push({class: "show_error_info", info: "数据关系异常，需要要手动排查错误"})
        }
        if (data.data.state == 'success') {
            app.websocket.progress_info.push({class: "show-value-success", info: data.data.data})
        } else if (data.data.state == 'fail') {
            app.websocket.progress_info.push({class: "show-value-fail", info: data.data.data})
        } else {
            app.websocket.progress_info.push({class: "show_error_info", info: "执行状态state无法匹配"})
        }
    } else {
        app.websocket.progress_info.push({class: "show_error_info", info: "无法理解当前步骤"})
    }
})

socket.on('disconnect', function() {
    app.connect_info = '连接已中断(网络问题，或者曾经初始化过)'
})