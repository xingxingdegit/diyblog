
var app = new Vue({
    el: '#app',
    data: {
        userdata: {
            sitename: '',
            username: '',
            password: '',
        },
        connect_info: '正在连接服务器',
        websocket: {
            is_show: false,
            progress: 1,
            progress_info: [],
        }
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

    }
})

socket = io();
socket.on('connect', function() {
    app.connect_info = '服务器已连接，完成操作开始初始化'
})

var init_key = ''
socket.on('init', function(data) {
    console.log(data)
    if (data.stage == 'start' || data.stage == 'end') {
        app.websocket.progress_info.push({class: "show-key", info: data.data})
    } else if (data.stage == 'in' && data.data.type == "key") {
        init_key = data.data.tag
        app.websocket.progress_info.push({class: "show-key", info: data.data.data})
    } else if (data.stage == 'in' && data.data.type == 'value') {
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
