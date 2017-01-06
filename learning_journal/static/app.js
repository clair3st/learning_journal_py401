
$(document).ready(function(){
    var csrfToken = "{{request.session.get_csrf_token()}}"
    var form_submit = $("#create");
    form_submit.on("click", function(e){

        console.log('in function')
        $.ajax({
            url: "/create-home",
            headers: { 'X-CSRF-Token': csrfToken },
            data: {
                "title": $("[name='title']").val(),
                "body": $("[name='body']").val(),
            },
            success: function(){
                console.log("updated");

                // Render info to list
                var heading = $('#list-title')
                var title = $("[name='title']").val()
                var text = '<article><h2 class="entrytitle" id="journal-entry"><a>'
                var text2 = '</a></h2><p class="date">'
                var date = new Date()
                var date = date.toDateString().slice(4)
                var date_output = [date.slice(0, 6), ',', date.slice(6)].join('');

                var text3 = '</p></article>'
                heading.after(text + title + text2 + date_output + text3)

                // Clear form
                $("[name='title']").val('')
                $("[name='body']").val('')

            }
        
        }); 

        e.preventDefault();    
        
    });

});