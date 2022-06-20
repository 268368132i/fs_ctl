$(document).ready(function (){
  $.('#general_form').submit(function(){
    $.ajax({
      data: $(this).serialize(),
      type: $(this).attr('method'),
      url: "{% url 'exchange:ctl' uuid=assignment.id %}",
      success: function(){
        alert("Command sent");
      },
      error: function(){
        alert(response.responseJSON.error);
        console.log(response.responseJSON.error);
      }
    });
    return false;
  });
});