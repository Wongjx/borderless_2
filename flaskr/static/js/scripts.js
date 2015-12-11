
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

function hide_this(isbn){
  $(this).hide();
  console.log(isbn);
  $("#id_"+isbn).show();
};

$('.qcell').click(function(e) {
  test=$(this)
  console.log(e)
  console.log("click")
  // $(this).hide();
  // $('.qcellselector').show();
});

$('.qcellselector').keypress(function (e) {
  if (e.which == 13) {
    var val = $(this).selectedIndex
    var test = parseInt($(".qcellselector").val(), 10);
    var number = parseInt($('.qcellselector').find('.number').text());
    $(this).hide();
    test=$(this);
    $('.qcell').text(String(test)).show();
    return false;    //<---- Add this line
  }
});




