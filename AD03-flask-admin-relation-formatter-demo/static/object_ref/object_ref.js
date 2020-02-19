//With bootbox

// bootbox.addLocale('zh_CN', {
//     OK: '确定',
//     CANCEL: '取消',
//     CONFIRM: '确定'
// });

$(document).ready(function () {
    $('[data-toggle="popover"]').popover({
        html: true, placement: "auto",
        viewport: {selector: 'body', padding: 5}
    });
});

// 单击其他地方则隐藏 object_ref
$('body').on('click', function (e) {
    $('[data-toggle="popover"]').each(function () {
        //the 'is' for buttons that trigger popups
        //the 'has' for icons within a button that triggers a popup
        if (!$(this).is(e.target) && $(this).has(e.target).length === 0
                && $('.popover').has(e.target).length === 0) {
            $(this).popover('hide');
        }
    });
});

