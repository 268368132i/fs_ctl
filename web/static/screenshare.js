var currentCall;
$(function() {
  var vertoHandle, vertoCallbacks, screenshareCall;
  var vertoConf, liveArray;
  var params = (new URL(document.location)).searchParams;

  $.verto.init({skipDeviceCheck: true, skipPermCheck: true,}, bootstrap);
  
  //Function to send chat messages, i need this here so that i can remove an event later
  function sendMsg(){
    var msgBox = document.getElementById("myMessage");
    vertoConf.sendChat(msgBox.value,"msg");
    msgBox.value="";
  }
  
  function bootstrap(status) {
    vertoCallbacks = {
      onDialogState: onDialogState,
      onWSLogin: onWSLogin,
      onWSClose: onWSClose,
      onMessage: onMessage,
    };
    console.log("Bootstrapping...");
        
    vertoHandle = new jQuery.verto({
    login: FSLogin,
    passwd: FSPasswd,
    socketUrl: socketUrl,
    iceServers: true,
    deviceParams: devParms,

    tag: "video-container",
    }, vertoCallbacks);
    mainVertoHandle=vertoHandle;
    
    document.getElementById("make-call").addEventListener("click", function(){
        makeCall(confExt);
      });
    document.getElementById("end-call").addEventListener("click", function(){
        hangupCall();
      });
  }
  
  function printSessId(){
  	console.log(vertoHandle.sessid);
  	}

    function makeCall(dest) {
      vertoHandle.videoParams({
               maxWidth: 1360,
               maxHeight: 768,
               vertoBestFrameRate: 15,
            });
    console.log("UserName=" + userName + "; dest=" + dest);
    currentCall = vertoHandle.newCall({
             destination_number: dest + "-screen",
             caller_id_name: userName + '(Screen)',
             caller_id_number: '1008' + '(screen)',
             caller_id_name: userName,
             outgoingBandwidth: 1024*1024,
             screenShare: true,
             userVariables: {
               uuid: uuid,
             },
    });
 
    $(".conf-info").slideUp(800);
    console.log("------ScreenshareCall:------0");
    console.log(currentCall);
    
  }    
  
  //Send conference command
  sendCommand=function (command, userid, value){
		var ret = currentCall.verto.rpcClient.call("verto.broadcast",{
			"eventChannel": vertoConf.params.laData.modChannel,
			"data": {
				"application": "conf-control",
				"command": command,
				"id": userid,
				"value": value,
			}
		});
		console.log("Command return:");
		console.log(ret);
  }
  
  function hangupCall() {
    console.log("------CurrentCall:------");
    console.log(currentCall);
    
    if (currentCall) {
      document.getElementById("sendMyMessage").removeEventListener("click", sendMsg);
    if (screenshareCall) {
      console.log("Screenshare active. Hanging up.");
      screenshareCall.hangup();
      
    }
    currentCall.hangup();
    var i;
    console.log(vertoHandle);
    for (i in vertoHandle.eventSUBS){
      console.log(i);
      vertoHandle.unsubscribe(vertoHandle.eventSUBS[i]);
    }
    }
    
    $("#make-call").fadeIn(300);
  };
  
      // Receives call state messages from FreeSWITCH.
  function onDialogState(d) {
  console.log("dialogState");
  switch (d.state.name) {
    case "trying":
      console.log("trying");
      break;
    case "answering":
      console.log("answering");
      break;
    case "active":
      console.log("active");
      console.log(d);
      $('#end-call').prop('disabled',false);
      $('#make-call').prop('disabled',true);

      break;
    case "hangup":
      console.log("Call ended with cause: " + d.cause);
      break;
    case "destroy":
      // Some kind of client side cleanup...
      console.log("Destroying on dialog state...");
      console.log(d);
      console.log(d.params.screenShare);      
        //Manually removing tracks
        d.rtc.localStream.getTracks()
          .forEach(track => track.stop());
      $('#end-call').prop('disabled',true);
      $('#make-call').prop('disabled',false);
      break;
    }
  }

  function onMessage(verto, dialog, message, data) {
  console.log("----Message-----\n" + message);
  switch (message) {
    case $.verto.enum.message.pvtEvent:
      if (data.pvtData) {
        switch (data.pvtData.action) {
          // This client has joined the live array for the conference.
          case "conference-liveArray-join":
            // With the initial live array data from the server, you can
            // configure/subscribe to the live array.
            initLiveArray(verto, dialog, data);
            break;
          // This client has left the live array for the conference.
          case "conference-liveArray-part":
            // Some kind of client-side wrapup...
            console.log("Leaving live array");
            liveArray.destroy();
            liveArray=null;
            removeChildren(document.getElementById("users-block"));

            //Going back to conf list page. This thing gets called the last after a disconnect
            //window.location.replace(sourceUrl);
            break;
        }
      }
      break;
    // TODO: Needs doc.
    case $.verto.enum.message.info:
      break;
    // TODO: Needs doc.
    case $.verto.enum.message.display:
      break;
    case $.verto.enum.message.clientReady:
      // 1.8.x+
      // Fired when the server has finished re-attaching any active sessions.
      // data.reattached_sessions contains an array of session IDs for all
      // sessions that were re-attached.
      break;
    }
  }
  

/*
 * Setting up and subscribing to the live array.
 */
 

  
  var initLiveArray = function(verto, dialog, data) {
    // Set up addtional configuration specific to the call.
    vertoConf = new $.verto.conf(verto, {
      dialog: dialog,
      hasVid: true,
      laData: data.pvtData,
      // For subscribing to published chat messages.
      chatCallback: function(verto, eventObj) {
        var from = eventObj.data.fromDisplay || eventObj.data.from || 'Unknown';
        var message = eventObj.data.message || '';
        console.log("--Chat:" + from + ": " + message);
        appendToChat(from,message);
      },
    });

    document.getElementById("sendMyMessage").addEventListener("click", sendMsg);
    var config = {
      subParams: {
        callID: dialog ? dialog.callID : null
      },
    };
    // Set up the live array, using the live array data received from FreeSWITCH.
    liveArray = new $.verto.liveArray(verto, data.pvtData.laChannel, data.pvtData.laName, config);
    // Subscribe to live array changes.
    liveArray.onChange = function(liveArrayObj, args) {
      console.log("Call UUID is: " + args.key);
      console.log("Call data is: ", args.data);
      try {
        console.log(args.action);
        switch (args.action) {

          // Initial list of existing conference users.
          case "bootObj":
            if (currentCall) {
              populateParticipantsList(args.data,currentCall.callID);
            }
            break;

          // New user joined conference.
          case "add":
			if (args.data[5].hostCall){
				var hostCall=args.data[5].hostCall;
				console.log("Detected screenShare for callId " + hostCall);
				screenSharings[args.key]=hostCall;
				if (participants[hostCall]){
					var p=participants[args.data[5].hostCall];
					p.isScreenSharing(true);
				}
			} else {
				var p = new Participant(args.key,args.data);
				document.getElementById("users-block").appendChild(p.div);
				participants[args.key]=p;
			}
            break;

          // User left conference.
          case "del":
				//Test if it is a screen share:
				if (screenSharings[args.key]){
					participants[screenSharings[args.key]].isScreenSharing(false);
					screenSharings[args.key]=null;
				} else {
					document.getElementById("users-block").removeChild(participants[args.key].div);
					participants[args.key]=null;
				}
            break;

          // Existing user's state changed (mute/unmute, talking, floor, etc)
          case "modify":
			if (participants[args.key]!=null){
				datatmp=args.data;
				var p=participants[args.key];
				updateStatus(p,args.data);
				//p.updateTalking(args.data);
			} else if (args.data[5].hostCall==null) {
				var p = new Participant(args.key,args.data);
				document.getElementById("users-block").appendChild(p.div);
				participants[args.key]=p;
			}
            break;

        }
      } catch (err) {
        console.error("ERROR: " + err);
      }
    };
    // Called if the live array throws an error.
    liveArray.onErr = function (obj, args) {
      console.error("Error: ", obj, args);
    };
  }
  

  function onWSLogin(verto, success) {
    console.log('onWSLogin', success);
    $('#make-call').prop('disabled',false);
  };

  function onWSClose(verto, success) {
    console.log('onWSClose', success);
  };
});

