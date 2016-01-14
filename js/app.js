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

function playSong_deprecated(songname){
    var player=document.getElementById('acontrol');
    var sourceMp3=document.getElementById('acontrol');
    tsrc = '/assets/XXXXX'
    src = tsrc.replace('XXXXX', songname)
    console.log(src)
    sourceMp3.src= src;
              
    player.load(); //just start buffering (preload)
    player.play(); //start playing
}

//gets a set of two songs to match up
function getSet(){
	var current_set = $('#songbay').attr('value')
	$.post('/matchups', {funct:'getSet', current_set:current_set}, function(data){
		a = data.split(';')
		$('#songbay').attr('value',a[0])
		$('#songbay').html(data)
		songinfo1 = a[1].split(',')
		songinfo2 = a[2].split(',')
		//enter the info
		$('#aname1').html(songinfo1[0])
		$('#aname2').html(songinfo2[0])
		$('#songname1').html(songinfo1[1])
		$('#songname2').html(songinfo2[1])
		songwinp1 = (100 * parseInt(songinfo1[2])/(parseInt(songinfo1[3])+parseInt(songinfo1[2]))).toFixed(2)
		songwinp2 = (100 * parseInt(songinfo2[2])/(parseInt(songinfo2[3])+parseInt(songinfo2[2]))).toFixed(2)
		$('#songwinp1').html('Song Win%: '+songwinp1+'%')
		$('#songwinp2').html('Song Win%: '+songwinp2+'%')
		artistwinp1 = (100 * parseInt(songinfo1[4])/(parseInt(songinfo1[5])+parseInt(songinfo1[4]))).toFixed(2)
		artistwinp2 = (100 * parseInt(songinfo2[4])/(parseInt(songinfo2[5])+parseInt(songinfo2[4]))).toFixed(2)
		$('#artistwinp1').html('Artist Win%: '+artistwinp1+'%')
		$('#artistwinp2').html('Artist Win%: '+artistwinp2+'%')
	});
}

function playSong(c){
	$('#playbutton'+c).attr('value','played')
}


//helper for choose winner
function updateStats(i,win){
	data = $('#songbay').html()
	r = data.split(';')[i].split(',')
	//update winner
	if (win == '1') {
		songwinp = (100 * (parseInt(r[2])+1)/(parseInt(r[3])+1+parseInt(r[2]))).toFixed(2);
		artistwinp = (100 * (parseInt(r[4])+1)/(parseInt(r[5])+1+parseInt(r[4]))).toFixed(2);
	} else{
		songwinp = (100 * parseInt(r[2])/(parseInt(r[3])+parseInt(r[2]))).toFixed(2);
		artistwinp = (100 * parseInt(r[4])/(parseInt(r[5])+parseInt(r[4]))).toFixed(2);
	}
	$('#songwinp'+i).html('Song Win%: '+songwinp+'%')
	$('#artistwinp'+i).html('Artist Win%: '+artistwinp+'%')
}

//chooses the winner
function chooseWinner(winner){
	//check to see that both songs have been played
	if ($('#playbutton1').attr('value') == 'played' && $('#playbutton2').attr('value') == 'played'){
		loser = (parseInt(winner) + 1) % 2
		if (winner=='1'){loser = 2}
		updateStats(loser, '0')
		updateStats(winner, '1')

	} else {console.log('please play both songs before selecting a winner')}
}

//shows )your image when uploading a profile picture
function readimg(input) {
	console.log('reading image')
	if (input.files && input.files[0]) {
		var reader = new FileReader();
		reader.onload = function (e) {
			console.log(e.target.result)
			$('#demo_profile_pic').css('background-image', 'url('+e.target.result+')')
        };
		reader.readAsDataURL(input.files[0]);
	}
}

function submitSignup(){
	
}

