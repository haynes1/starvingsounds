function expandNav(){
	console.log('expanding nav')
	$('#nav_container').animate({
        left: '0vw',
    }, 500, function(){
    	$('#nav_expand').attr('onclick', 'collapseNav()')
    	console.log('now collapsable')
    });
}

function collapseNav(){
	$('#nav_container').animate({
        left: '-55vw',
    }, 500, function(){
    	$('#nav_expand').attr('onclick', 'expandNav()')
    });
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