
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

$('.qcell').click(function() {
  $(this).hide();
  $('.qcellselector').show();
})

$('.qcellselector').change(function(){
  var val = $(this).selectedIndex;
    var prevval= $('.qcell').val();
  $(this).hide();
  $('.qcell').text(val+prevval);
})

$('.qcellselector').keypress(function (e) {
  if (e.which == 13) {
    var val = $(this).selectedIndex
    var test = parseInt($(".qcellselector").val(), 10);
    var number = parseInt($('.qcellselector').find('.number').text());
    $(this).hide();
    $('.qcell').text(String(test)).show();
    return false;    //<---- Add this line
  }
});