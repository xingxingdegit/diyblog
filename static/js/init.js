function submit_data(form, event) {
    event.preventDefault();
    var connect_info = document.getElementById('connect')
    var content = document.getElementById('pro-content')
    var userdata = get_user()
    if (userdata) {
        var socket = io();
        connect_info.innerText = '正在连接服务器'
        socket.on('connect', function() {
            connect_info.innerText = '已连接，正在初始化'
            show_some()
            socket.emit('init', userdata)
        })
    } else {
        connect_info.innerText = '用户信息填写错误'
    }
    var append_html = ''
    var init_key = ''
    socket.on('init', function(data) {
        console.log(data)
        if (data.stage == 'start' || data.stage == 'end') {
            append_html += '<p class="show-key">' + data.data + '</p>'
        } else if (data.stage == 'in' && data.data.type == "key") {
            init_key = data.data.tag
            console.log('key:' + init_key)
            append_html += '<p class="show-key">' + data.data.data + '</p>'
        } else if (data.stage == 'in' && data.data.type == 'value') {
            if (init_key != data.data.tag) {
                append_html += '<p style="color:red">数据关系异常，需要要手动排查错误</p>'
            }
            if (data.data.state == 'success') {
                append_html += '<p class="show-value-success">' + data.data.data + '</p>'
            } else if (data.data.state == 'fail') {
                append_html += '<p class="show-value-fail">' + data.data.data + '</p>'
            } else {
                append_html += '<p style="color:red">执行状态state无法匹配</p>'
            }
        } else {
            append_html += '<p style="color:red">无法理解当前步骤</p>'
        }

        content.innerHTML = append_html
    })
}

function show_some() {
    var show_bar = document.getElementsByClassName('show-bar')
    for (var i=0; i<show_bar.length; i++) {
        show_bar[i].hidden = false
    }
}

function get_user() {
    var inputs = document.getElementsByTagName('input')
    var user = inputs.username.value
    var password = inputs.password.value
    if (user && password) {
        return {username: user, password: password}
    } else {
        return false
    }
}

/*
document.getElementById('create_user').onclick = function(){

}
//    socket.on('disconnect', function() {
//        console.log('disconnect')
//    })
*/