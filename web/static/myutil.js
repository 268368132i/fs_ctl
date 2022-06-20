function removeChildren(node){
	while(node.firstChild){
		node.removeChild(node.firstChild);
	}
}

//Update participand status on data: p-participant object, d-data object
function updateStatus(p,d){
	var status = JSON.parse(d[4]);
	//Processing audio
	var a = status.audio;
	if (!a.muted && !a.deaf && !a.onHold){
		p.isAudioShared(true);
		if (a.talking){
			p.setTalking(1);
		} else {
			p.setTalking(0);
		}
	} else {
		p.isAudioShared(false);
		p/setTalking(2);
	}
	
	//Processing video
	var v = status.video;
	if (v.visible && ( v.mediaFlow=="sendRecv" || v.mediaFlow=="send" ) && !v.muted){
		p.isCameraShared(true);
	} else {
		p.isCameraShared(false);
	}
}

function populateParticipantsList(data,selfUUID){
	data.forEach(participantData => {
			var p = new Participant(participantData[0],participantData[1]);
			updateStatus(p,participantData[1]);
			participants[participantData[0]]=p;
			//Making self participant the first in a list
			if (participantData[0]==selfUUID && document.getElementById("users-block").childNodes.length>0){
				document.getElementById("users-block").insertBefore(p.div,document.getElementById("users-block").childNodes[0]);
			} else {
				document.getElementById("users-block").appendChild(p.div);
			}
		});
}



//Show and hide call control buttons

var timedelay = 1;
var _delay = setInterval(delayCheck, 1000);

$('#video-container').on('mousemove',showEvent);

function delayCheck(){
	if (timedelay == 3) {
		$('.hide').removeClass('show');
		timedelay=1;
	}
	timedelay+=1;
}

function showEvent() {
	$('.hide').addClass('show');
	timedelay = 1;
	clearInterval(_delay);
	_delay = setInterval(delayCheck,1000);
}

function toggleFullscreen(element){
  if (
    document.fullscreenElement ||
    document.webkitFullscreenElement ||
    document.mozFullScreenElement ||
    document.msFullscreenElement
  ) {
    if (document.exitFullscreen) {
      document.exitFullscreen();
    } else if (document.mozCancelFullScreen) {
      document.mozCancelFullScreen();
    } else if (document.webkitExitFullscreen) {
      document.webkitExitFullscreen();
    } else if (document.msExitFullscreen) {
      document.msExitFullscreen();
    }
  } else {
    if (element.requestFullscreen) {
      element.requestFullscreen();
    } else if (element.mozRequestFullScreen) {
      element.mozRequestFullScreen();
    } else if (element.webkitRequestFullscreen) {
      element.webkitRequestFullscreen(Element.ALLOW_KEYBOARD_INPUT);
    } else if (element.msRequestFullscreen) {
      element.msRequestFullscreen();
    }
  }
}

function exitFullscreen(){
  if (
    document.fullscreenElement ||
    document.webkitFullscreenElement ||
    document.mozFullScreenElement ||
    document.msFullscreenElement
  ) {
    if (document.exitFullscreen) {
      document.exitFullscreen();
    } else if (document.mozCancelFullScreen) {
      document.mozCancelFullScreen();
    } else if (document.webkitExitFullscreen) {
      document.webkitExitFullscreen();
    } else if (document.msExitFullscreen) {
      document.msExitFullscreen();
    }
  }
}

function appendOption(element, value, text){
	var opt = document.createElement('option');
	opt.appendChild(document.createTextNode(text));
	opt.value=value;
	element.appendChild(opt);
}
function populateSelectFromArray(element,array){
	
}
