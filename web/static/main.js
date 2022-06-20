var currentCall;
$(function() {
  var vertoHandle, vertoCallbacks, screenshareCall;
  var vertoConf, liveArray;
  var params = (new URL(document.location)).searchParams;

  $.verto.init(vertoInitParams, bootstrap);
  
  
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
    
    //Populate devices list
    var vidS=document.getElementById('vidSources');
    var vidDevices = $.verto.videoDevices;
    vidDevices.forEach(e=>appendOption(vidS,e.id,e.label));
    appendOption(vidS,'none','none');
        
    vertoHandle = new jQuery.verto({
    login: FSLogin,
    passwd: FSPasswd,
    // As configured in verto.conf.xml on the server.
    socketUrl: socketUrl,
    // TODO: Where is this file, on the server? What is the base path?
    ringFile: 'sounds/bell_ring2.wav',
    // STUN/TURN server config, more than one is allowed.
    // Instead of an array of objects, you can also pass a Boolean value,
    // false disables STUN, true uses the default Google STUN servers.
    iceServers: true,
    // These can be set per-call as well as per-login. They can also be set to
    // A specific device ID, or 'none' to disable that particular element of
    // the media flow.
    deviceParams: devParms,

    // Optional Id of the HTML audio/video tag to be used for playing video/audio.
    // This can even be a function which will return an element id. (Use this as
    // function to create unique element for every new call specially when dealing
    // with multiple calls simultaneously to avoid conflicts between streams.
    // In this case, once call is finished, newly generated element will be
    // destroyed automatically)
    tag: "video-container",
    // Below are some more advanced configuration parameters.
    // Google Chrome specific adjustments/filters for audio.
    // Official documentation is scant, best to try them out and see!
    //audioParams: {
    //  googEchoCancellation: true,
    //  googAutoGainControl: true,
    //  googNoiseSuppression: true,
    //  googHighpassFilter: true,
    //  googTypingNoiseDetection: true,
    //  googEchoCancellation2: false,
    //  googAutoGainControl2: false,
    //},
    // Internal session ID used by Verto to track the call, eg. for call
    // recovery. A random one will be generated if none is provided, and,
    // it can be useful to provide a custom ID to store and reference for
    // other purposes.
    //sessid: sessid,
    }, vertoCallbacks);
    mainVertoHandle=vertoHandle;
    document.getElementById("make-call").addEventListener("click", function(){
        makeCall(confExt);
      });

//      document.getElementById("make-call").addEventListener("click",makeCall);*/
      
    document.getElementById("hang-up-call").addEventListener("click", hangupCall);
    
    var useIce = document.getElementById('use-ice-checkbox');
    if (useIce){
      if (localStorage.getItem('noIce')){
        useIce.checked = false;
        vertoHandle.options.iceServers = false;
      } else {
        useIce.checked = vertoHandle.options.iceServers;
      }
      useIce.addEventListener('click', function(){
        vertoHandle.options.iceServers = useIce.checked;
        if (useIce.checked){
          localStorage.removeItem('noIce');
        } else {
          localStorage.setItem('noIce','1');
        }
      });
    }
    

  }
  
  function printSessId(){
  	console.log(vertoHandle.sessid);
  	}

    function makeCall(dest) {
        //Hangup previous calls
        console.log(vertoHandle);
        for (d in vertoHandle.dialogs){
            console.log(d);
            vertoHandle.dialogs[d].hangup();
        }
        
      vertoHandle.videoParams({
        minWidth: 320,
        minHeight: 240,
        maxWidth:1280,
        maxHeight:720,
        minFrameRate: 7,
        maxFrameRate: 20,
      });
    console.log("UserName=" + userName + "; dest=" + dest);
    currentCall = vertoHandle.newCall({
      // Extension to dial.      
      destination_number: dest,
      caller_id_name: userName,
      caller_id_number: '1008',
      outgoingBandwidth: false,
      incomingBandwidth: false,
      // Enable stereo audio.
      useStereo: false,
      // Set to false to disable inbound video.
      useVideo: true,
      // You can pass any application/call specific variables here, and they will
      // be available as a dialplan variable, prefixed with 'verto_dvar_'.
      userVariables: {
        // Shows up as a 'verto_dvar_uuid' dialplan variable.
        uuid: uuid,
      },
      // Use a dedicated outbound encoder for this user's video.
      // NOTE: This is generally only needed if the user has some kind of
      // non-standard video setup, and is not recommended to use, as it
      // dramatically increases the CPU usage for the conference.
      dedEnc: false,
      // Example of setting the devices per-call.
      //useMic: 'any',
      //useSpeak: 'any',
      useCamera: document.getElementById('vidSources').value,
	//useCamera: "none",

    });
    
    $(".conf-info").slideUp(800);
 //   $("#make-call").fadeOut(800,function(){
//      $("#hang-up-call").fadeIn(300);
          $("#start-screenshare, #secondary-screenshare").click(function(){
           vertoHandle.videoParams({
             minWidth: false,
             minHeight: false,
             maxWidth:false,
             maxHeight:false,
             minFrameRate: 2,
             maxFrameRate: 12,
           });
          //States: 2 - trying (might be active currently) 9 - hangup (not active)
           screenshareCall = vertoHandle.newCall({
             destination_number: dest + "-screen",
             caller_id_name: userName + '(Screen)',
             caller_id_number: '1008' + '(screen)',
             videoParams: {},
             caller_id_name: userName,
             /*useVideo: false,
             useAudio: false,
             useMic: false,
             useSpeak: false,*/
             screenShare: true,
             userVariables: {
               hostCall: currentCall.callID,
             },
           });
          });
//    });
    //$("#video-container").width($("#main-area").width());
    console.log("------CurrentCall:------0");
    console.log(currentCall);
    
  }
  
   function startScreenshareCall(dest, button, currentCallId=0) {
      vertoHandle.videoParams({
        minWidth: false,
        minHeight: false,
        maxWidth:false,
        maxHeight:false,
        minFrameRate: 2,
        maxFrameRate: 12,
      });
    console.log("UserName=" + userName + "; dest=" + dest);
    screenshareCall = vertoHandle.newCall({
             destination_number: dest + "-screen",
             caller_id_name: userName + '(Screen)',
             caller_id_number: '1008' + '(screen)',
             videoParams: {},
             caller_id_name: userName,
             /*useVideo: false,
             useAudio: false,
             useMic: false,
             useSpeak: false,*/
             userVariables: {
                // Shows up as a 'verto_dvar_uuid' dialplan variable.
                uuid: uuid,
             },
             screenShare: true,
             userVariables: {
               hostCall: currentCallId,
             },
    });
 
    $(".conf-info").slideUp(800);
 //   $("#make-call").fadeOut(800,function(){
//      $("#hang-up-call").fadeIn(300);
//    });
    //$("#video-container").width($("#main-area").width());
    console.log("------ScreenshareCall:------0");
    console.log(screenshareCall);
    
  }
  
      $("#secondary-screenshare").click(function(){
        console.log("Starting standalone screenshare");
        startScreenshareCall(confExt,document.getElementById('secondary-screenshare'))
        
    });
    
  
  //Send conference command
  sendCommand=function (command, userid, value){
                console.log("vertoConf=");
                console.log(vertoConf);
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
    console.log("------CurrentCall:------0");
    console.log(currentCall);
    
    if (currentCall) {
      document.getElementById("sendMyMessage").removeEventListener("click", sendMsg);
    if (screenshareCall) {
      console.log("Screenshare active. Hanging up.");
      screenshareCall.hangup();
      
    }
    currentCall.hangup();
    /*liveArray.destroy();
    liveArray = null;
    console.log(vertoConf);*/
    var i;
    console.log(vertoHandle);
    for (i in vertoHandle.eventSUBS){
      console.log(i);
      vertoHandle.unsubscribe(vertoHandle.eventSUBS[i]);
    }
    }
    
    //$("#hang-up-call").fadeOut(0,function(){$("#make-call").fadeIn(300);});
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
        if (!d.params.screenShare){
          currentCall=d;
          mainCall=currentCall;
          $("#amute").click(amuteToggle);
          $("#vmute").click(vmuteToggle);
          $("#start-screenshare").fadeIn(300);
          $("#video-container").on("mousemove",showEvent);
          $("#video-container").trigger("mousemove");

        } else if (d.params.screenShare){
          $("#start-screenshare").fadeOut(300);
          $("#stop-screenshare").fadeIn(300);
          $("#stop-screenshare").click(function(){
            screenshareCall.hangup();
          });
        }
      break;
    case "hangup":
      console.log("Call ended with cause: " + d.cause);
      break;
    case "recovering":
        d.hangup();
        break;        
    case "destroy":
      // Some kind of client side cleanup...
      console.log("Destroying on dialog state...");
      console.log(d);
      console.log(d.params.screenShare);
      if (d.params.screenShare){
        //Manually removing tracks
        d.rtc.localStream.getTracks()
          .forEach(track => track.stop());
        
        $("#stop-screenshare").fadeOut(300,function(){
          console.log("Main call state:\n" + currentCall.state.name);
          if (currentCall.state.name=="active") $("#start-screenshare").fadeIn(300);
          });
      } else {
        exitFullscreen();
        $("#video-container").off("mousemove");
        $(".hide").removeClass("show");
        $("#start-screenshare").off().fadeOut(300);
        $("#amute").off();
        $("#vmute").off();
        $('#make-call').prop('disabled',false);
      }
      break;
    }
  }

//Processing muting
  
  function amuteToggle(){
    var res = currentCall.setMute("toggle");
    if (res) {
      currentCall.dtmf("00");
      $("#amute")[0].setAttribute("style","background: rgb(202,50,50);");
    } else {
      $("#amute")[0].setAttribute("style","");
      currentCall.dtmf("01");
    }
  }
  
  function vmuteToggle(){
    var res = currentCall.setVideoMute("toggle");
    if (res) {
      currentCall.dtmf("*00");
      $("#vmute")[0].setAttribute("style","background: rgb(202,50,50);");
    } else {
      $("#vmute")[0].setAttribute("style","");
      currentCall.dtmf("*01");
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
/*    console.log("calling 6522...");*/
//    makeCall(confExt);
    $('#make-call').prop('disabled',false);
  };

  function onWSClose(verto, success) {
    console.log('onWSClose', success);
  };
});

