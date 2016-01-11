function navShowHide(i){
	state = $('#mainav_wrapper').attr('value')
	if (state != 'contracted' || i == 'close'){ //contract nav
		$('#mainav_wrapper').animate({
        	left: '-100vw',
    	}, 700);
		$('#mainav_wrapper').attr('value','contracted')
		
	}else{ //expand nav
		$('#mainav_wrapper').animate({
        	left: '0',
    	}, 700);
		$('#mainav_wrapper').attr('value','expanded')
	}
}

function playSong(songname){
    var player=document.getElementById('acontrol');
    var sourceMp3=document.getElementById('acontrol');
    tsrc = '/assets/XXXXX'
    src = tsrc.replace('XXXXX', songname)
    console.log(src)
    sourceMp3.src= src;
              
    player.load(); //just start buffering (preload)
    player.play(); //start playing
}

function nextSet(){
	current = $('#nextset').attr('value')
	if(current == 1){
		$('#play1').attr('onclick', "javascript:playSong('ElectricBody.mp3');return false;")
		$('#play2').attr('onclick', "javascript:playSong('galvanize.mp3');return false;")
		$('#nextset').attr('value', '2')
	} else if (current == 2){
		$('#play1').attr('onclick', "javascript:playSong('Gold.mp3');return false;")
		$('#play2').attr('onclick', "javascript:playSong('StopTrippin.mp3');return false;")
		$('#nextset').attr('value', '3')
	} else if (current == 3){
		$('#play1').attr('onclick', "javascript:playSong('finewaytodie.mp3');return false;")
		$('#play2').attr('onclick', "javascript:playSong('FunkParty.mp3');return false;")
		$('#nextset').attr('value', '1')
	}
}

$( document ).ready(function() {
    console.log( "ready!" );
});