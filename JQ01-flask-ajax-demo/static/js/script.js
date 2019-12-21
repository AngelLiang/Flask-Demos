$(function(){

    // ajax 配置
    $.ajaxSetup({
        // 发送之前事件
        beforeSend: function (xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                // 设置请求头部
                // csrf_token 变量已经在 base.html 里设置了
                xhr.setRequestHeader("X-CSRFToken", csrf_token);
            }
        }
    });

    $('.delete-button').on('click', function () {
        var $this = $(this);
        $.ajax({
            type: 'DELETE',
            url: $this.data('href'),
            success: function () {
                alert('Success!')
            },
            error: function () {
                alert('Oops, something was wrong!')
            }
        });
    });

})
