function validEmail(email){
	re = /.+@.+\..+/i
	return re.test(email);
}
function validDate(date){
	re = /(0[1-9]|1[012])[- \/.](0[1-9]|[12][0-9]|3[01])[- \/.](19|20)\d\d/
	return re.test(date);
}


function signupSuccess(){
	$('#sformstuff').hide()
	$('#signupsuccess').show()
	setTimeout(function() {signupShowHide();$('#sformstuff').show();$('#signupsuccess').hide();}, 1500);
}

function signupSubmit(){
	console.log('submitting this bitch');
	$('.signupinput').addClass('invalidinput')
	$('#sexerror').html('')
	name = document.getElementById('name').value;
	email = document.getElementById('email').value;
	var have_error = 0;
	if (!name){var nameerror = 'invalid name';have_error = 1;} 
	if(!validEmail(email)){console.log('wtf is happening');var emailerror = 'invalid email';have_error=1;} 
	if (have_error == 0){ //proceed to submit the form
		console.log('yay we can submit the form')
		serialized = $('#signupform').serialize();
		$.ajax({
        type: "POST",
        	url: '/emailcontact', //sumbits it to the given url of the form
        	data: serialized,
    	}).success(function(data){
        	//var jdata = $.parseJSON(data)
        	status = data.message
        	if (status == 'success!'){//the email was sent!
        		signupSuccess()
        	}else{
        		emailerror = "that email didn't work"
        		$('#email').val('');
        		$('#email').attr('placeholder', emailerror)
        	}
    	}).fail(function(data){
    		console.log("failure", data)
    	});
	} else { //give error values
		if (nameerror){$('#name').val('');$('#name').attr('placeholder', nameerror)}
		if (emailerror){$('#email').val('');$('#email').attr('placeholder', emailerror)}
	}
}

$( document ).ready(function() {
	console.log('ready')
    $('#signupsuccess').hide()
});