/**
 * Created by xqianliu on 4/15/17.
 */

// When user clicks remove inline field icon
// Reorder the inline orders and recalculate line number cell.
$('body').on('click', '.inline-remove-field' , function(e) {
    var inline_lines_tr = parent.find(".inline-field");
    for (i = 0; i < inline_lines_tr.length; i++){
        var line = $(inline_lines_tr[i]);
        if (line.attr("class").indexOf('fresh') > 0) {
            $('.line-number', line).each(function (e1) {
                var me = $(this);
                me.html(i+ 1);
            });
        }
    }
});

// 添加行列字段
function addInlineField(parent_id) {
    parent = $("#" + parent_id);
    inline_lines_tr = parent.find(".inline-field");
    var prefix = parent_id + '-' + inline_lines_tr.length;

    // Get template
    var $template = $($('.inline-field-template-' + parent_id).text());

    // Set form ID
    $template.attr('id', prefix);

    // Mark form that we just created
    $template.addClass('fresh');
    $template.removeClass('hide');
    // Display line number for newly added line.
    $('.line-number', $template).each(function(e) {
        var me = $(this);
        me.html(inline_lines_tr.length + 1);
    });
    // Fix form IDs
    $('[name]', $template).each(function (e) {
        var me = $(this);

        var id = me.attr('id');
        var name = me.attr('name');

        id = prefix + (id !== '' ? '-' + id : '');
        name = prefix + (name !== '' ? '-' + name : '');

        me.attr('id', id);
        me.attr('name', name);
        if (me.attr('class') === 'line-number') {
            me.text(prefix);
        }
    });

    $template.appendTo(parent);

    // Select first field
    $('input:first', $template).focus();

    // Apply styles
    faForm.applyGlobalStyles($template);
}

