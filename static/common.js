function reqListener() {
	console.log(this.responseText);
}

function send_xhr(url, data, f) {
	console.log(data);
	if (f == undefined) {
		f = reqListener;
	}
	var xhr = new XMLHttpRequest();
	xhr.addEventListener("load", f);
	xhr.open("POST", url, true);
	xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8");
	xhr.send(data);
}