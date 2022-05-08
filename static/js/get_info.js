function get_info() {
	let xhr = new XMLHttpRequest();

	var data = {};
    data["width"] = parseInt(document.getElementById("info_width").value);

    const querystring = encodeQueryData(data);
	xhr.open("GET", 'api/get_info?' + querystring);

	xhr.setRequestHeader("Accept", "application/json");
	xhr.setRequestHeader("Content-Type", "application/json");

	xhr.onreadystatechange = function() {
		if (xhr.readyState == 4) {
			if (xhr.status == 200) {

				var text = xhr.responseText;
				var map_box = document.getElementById('info_box')
				map_box.innerHTML = text;

				var size = calculate_size(data["map_width"]);
				document.getElementById("SATELLITE INFO").style.fontSize = size;

				setTimeout(function() {
					get_info()
				}, 1000);
			}
		}
	};

	xhr.send();
}

get_info();