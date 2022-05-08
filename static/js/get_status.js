function get_status() {
	let xhr = new XMLHttpRequest();


	var data = {};
    data["width"] = parseInt(document.getElementById("status_width").value);

    const querystring = encodeQueryData(data);
	xhr.open("GET", 'api/get_status?' + querystring);

	xhr.setRequestHeader("Accept", "application/json");
	xhr.setRequestHeader("Content-Type", "application/json");

	xhr.onreadystatechange = function() {
		if (xhr.readyState == 4) {
			if (xhr.status == 200) {
				var text = xhr.responseText;
				var map_box = document.getElementById('status_box')


				map_box.innerHTML = text;
			}
			setTimeout(function() {
				get_status()
			}, 1000);
		}
	};

	xhr.send();
}

get_status();