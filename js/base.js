function optimizeNav(){
	device_width = $(window).width()
	console.log(device_width)
	if (device_width <= 420){
		window.location.replace("/mhome");
	}
}


$(document).ready(function() {
    console.log( "ready!" );
    optimizeNav();
});