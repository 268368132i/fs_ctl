

var setLayout = function (select) {
	var layout = select.value;
	sendCommand("vid-layout",null,layout);
}
