
$(document).ready(function(){
    var form_submit = $("#create");
    form_submit.on("click", function(){
        console.log('in function')
        $.ajax({
            url: "/create-home",
            data: {
                "title": $("[name='title']").val(),
                "body": $("[name='body']").val(),
            },
            success: function(){
                console.log("updated");
            }
        });        
        
    });

//     var csrfToken = ${request.session.get_csrf_token()};
//     $.ajax({
//         type: "POST",
//         url: "/journal/new",
//         headers: { 'X-CSRF-Token': csrfToken }
//         }).done(function() {
//             alert("Ajaxed it");
//         });

});