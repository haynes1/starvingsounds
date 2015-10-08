function optimizeNav(){
	device_width = $(window).width()
	console.log(device_width)
	if (device_width <= 420){
		window.location.replace("/mhome");
	}
}

                  function playSong(songname){
            var player=document.getElementById('acontrol');
              var sourceMp3=document.getElementById('acontrol');
              tsrc = '/audio/XXXXX'
              src = tsrc.replace('XXXXX', songname)
              console.log(src)
              sourceMp3.src= src;
              
             player.load(); //just start buffering (preload)
             player.play(); //start playing
          }

$(document).ready(function() {
    console.log( "ready!" );
    optimizeNav();
});

