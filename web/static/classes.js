class Participant {

	constructor(key,data){
		this.name=data[2];
		this.div=document.createElement("div");
		this.div.setAttribute("class","stdText");
		
		this.nameArea = document.createElement("span");

		this.text=document.createTextNode(this.name);

		this.talking = document.createTextNode(":-)");
		this.statusArea = document.createElement("span");
		this.statusArea.setAttribute("class","smallElement");
		this.cameraSharing = document.createTextNode("-");
		this.screenSharing = document.createTextNode("-");
		this.audioSharing = document.createTextNode("-");
		
		this.statusArea.appendChild(this.cameraSharing);
		this.statusArea.appendChild(this.screenSharing);
		this.statusArea.appendChild(this.audioSharing);
		
		this.nameArea.appendChild(this.text);
		this.nameArea.appendChild(this.talking);

		this.div.appendChild(this.statusArea);
		this.div.appendChild(this.nameArea);
		this.talkingTextVariants = Array();
		this.talkingTextVariants[0]=":-)";
		this.talkingTextVariants[1]=":-O";
		this.talkingTextVariants[2]=":-X";

	}

	talkingText(data){
		console.log(data[4].audio);
		var parsed = JSON.parse(data[4]);
		var status = parsed.audio.talking;
		var muted = parsed.audio.muted;
		if (status && !muted) {
			return this.talkingTextVariants[1];
		} else if (muted){
			return this.talkingTextVariants[2];
		} else {
			return this.talkingTextVariants[0];
		}
	}

	updateTalking(data){
		this.talking.textContent=this.talkingText(data);
	}
	
	setTalking(val){
		this.talking.textContent=this.talkingTextVariants[val];
	}
	
	isCameraShared(status){
		if (status) {
			this.cameraSharing.textContent="V";
		} else {
			this.cameraSharing.textContent="-";
		}
	}
	
	isScreenSharing(status){
		if (status) {
			this.screenSharing.textContent="S";
		} else {
			this.screenSharing.textContent="-";
		}
	}
	
	isAudioShared(status){
		if (status) {
			this.audioSharing.textContent="A";
		} else {
			this.audioSharing.textContent="-";
		}
	}
	
}


