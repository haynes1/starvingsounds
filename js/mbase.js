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