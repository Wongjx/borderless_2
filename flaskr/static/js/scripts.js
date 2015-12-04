
$(document).ready(function(){$('#sidebar').affix({
      offset: {
        top: 240
      }
});
});


$('.editingcontrol label').click(function() {
    $(this).hide();
    $(this).parent().find('input')
        .val($(this).text())
        .show()
        .focus();
});

$('.editingcontrol input').blur(function() {
    $(this).hide();
    $(this).parent().find('label')
        .text($(this).val())
        .show()
});