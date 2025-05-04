let elem = document.querySelector('#answerCb1');
if (elem.checked == false) {
	document.querySelector('#answerIn1').disabled = "disabled";
	document.querySelector('#answerCb2').disabled = true;
	document.querySelector('#answerCb3').disabled = true;
	document.querySelector('#answerCb4').disabled = true;
}

elem = document.querySelector('#answerCb2');
if (elem.checked == false) {
	document.querySelector('#answerIn2').disabled = "disabled";
	document.querySelector('#answerCb3').disabled = true;
	document.querySelector('#answerCb4').disabled = true;
}

elem = document.querySelector('#answerCb3');
if (elem.checked == false) {
	document.querySelector('#answerIn3').disabled = "disabled";
	document.querySelector('#answerCb4').disabled = true;
}

elem = document.querySelector('#answerCb4');
if (elem.checked == false) {
	document.querySelector('#answerIn4').disabled = "disabled";
}

function changeAn1() {
	let elem = document.querySelector('#answerCb1');
	if (elem.checked) {
		document.getElementsByClassName("rad")[0].disabled = "";
		document.querySelector('#answerIn1').disabled = "";
		document.querySelector('#answerCb2').disabled = false;
	}
	else {
		document.getElementsByClassName("rad")[0].disabled = "disabled";
		document.querySelector('#answerIn1').disabled = "disabled";
		document.querySelector('#answerCb2').disabled = true;
		document.querySelector('#answerCb2').checked = false;
		changeAn2();
	}
}


function changeAn2() {
	let elem = document.querySelector('#answerCb2');
	if (elem.checked) {
		document.querySelector('#answerIn2').disabled = "";
		document.querySelector('#answerCb3').disabled = false;
		document.getElementsByClassName("rad")[1].disabled = "";
	}
	else {
		let rad = document.getElementsByClassName("rad")[1];
		rad.disabled = "disabled";
		if (rad.checked) {
			document.getElementsByClassName("rad")[0].click();
		}
		document.querySelector('#answerIn2').disabled = "disabled";
		document.querySelector('#answerCb3').disabled = true;
		document.querySelector('#answerCb3').checked = false;
		changeAn3();
	}
}

function changeAn3() {
	let elem = document.querySelector('#answerCb3');
	if (elem.checked) {
		document.querySelector('#answerIn3').disabled = "";
		document.querySelector('#answerCb4').disabled = false;
		document.getElementsByClassName("rad")[2].disabled = "";
	}
	else {
		let rad = document.getElementsByClassName("rad")[2];
		rad.disabled = "disabled";
		if (rad.checked) {
			document.getElementsByClassName("rad")[0].click();
		}
		document.querySelector('#answerIn3').disabled = "disabled";
		document.querySelector('#answerCb4').disabled = true;
		document.querySelector('#answerCb4').checked = false;
		changeAn4();
	}
}


function changeAn4() {
	let elem = document.querySelector('#answerCb4');
	if (elem.checked) {
		document.querySelector('#answerIn4').disabled = "";
		document.getElementsByClassName("rad")[3].disabled = "";
	}
	else {
		let rad = document.getElementsByClassName("rad")[3];
		if (rad.checked) {
			document.getElementsByClassName("rad")[0].click();
		}
		rad.disabled = "disabled";
		document.querySelector('#answerIn4').disabled = "disabled";
	}
}
