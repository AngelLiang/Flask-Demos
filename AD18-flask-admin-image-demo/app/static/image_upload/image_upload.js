/**
 * Notice: Many elements in this file is generated dynamically upon user operstion
 * So to access those elements, $("#xxxx") is not working,
 * We should use $("#images-preview-panel").find('li[id=' + id + ']') to get it
 * Or use  $("#images-preview-panel").on('click', 'span[id^="delete-"]', function () { }
 * to attach event to those elements.
 */

function handleFileSelect(evt) {
    var files = evt.target.files;
    // Loop through the FileList and render image files as thumbnails.
    for (var i = 0, f; f = files[i]; i++) {
        // Only process image files.
        if (!f.type.match('image.*')) {
            continue;
        }
        var reader = new FileReader();
        // Closure to capture the file information.
        reader.onload = (function (theFile) {
            return function (e) {
                // Render thumbnail.
                var li = document.createElement('li');
                // We are using total size of the file as a unique id here
                // Hopefully there will be no collision here.
                var li_id = e.total;
                li.setAttribute("id", li_id);
                var span_id = "delete-" + li_id;
                li.innerHTML = [
                    '<div>',
                    '<img src="', e.target.result, '"/>',
                    '<span class="glyphicon glyphicon-remove-circle" id="', span_id ,'"></span>',
                    '</div>'
                ].join('');
                // This line can not be change to  $("#images-preview-panel"), please stop wasting time to optimize it.
                document.getElementById('images-preview-panel').insertBefore(li, null);
            };
        })(f);
        // Read in the image file as a data URL.
        reader.readAsDataURL(f);
    }
}

//Update the thumbnails when user select new image from local disk.
var image_placeholder = document.getElementById('images_placeholder');
if (image_placeholder != null) {
    image_placeholder.addEventListener('change', handleFileSelect, false);
}

$(function () {
    $("#upload_image_trigger").click(function () {
        $("input[id='images_placeholder']").click();
    });
    $("#upload_text_trigger").click(function () {
        $("input[id='images_placeholder']").click();
    });
    // $("span[id^='delete-']") is not working since all the span with id delete-*** are created dynamically
    // Reference http://stackoverflow.com/questions/1359018/in-jquery-how-to-attach-events-to-dynamic-html-elements
    $("#images-preview-panel").on('click', 'span[id^="delete-"]', function () {
        if (confirm('确定删除本图片吗？')) {
            var id = event.target.id.slice('delete-'.length);
            var to_delete_images = $("#images-to-delete");
            if (to_delete_images.val() === '') {
                to_delete_images.val(id);
            } else {
                to_delete_images.val(
                        to_delete_images.val() + ',' + id
                );
            }
            $("#images-preview-panel").find('li[id=' + id + ']').fadeOut();
        }
    });
});
