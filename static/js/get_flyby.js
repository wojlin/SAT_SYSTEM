function encodeQueryData(data) {
	const ret = [];
	for (let d in data)
		ret.push(encodeURIComponent(d) + '=' + encodeURIComponent(data[d]));
	return ret.join('&');
}

function get_flyby() {
	let xhr = new XMLHttpRequest();

	var data = {};
	data["hours_ahead"] = parseInt(document.getElementById("hours_ahead").value);
	data["minimal_angle"] = parseInt(document.getElementById("minimal_angle").value);
	data["display_amount"] = parseInt(document.getElementById("display_amount").value);
    data["display_amount"] = parseInt(document.getElementById("display_amount").value);
    data["width"] = parseInt(document.getElementById("flyby_width").value);

	const querystring = encodeQueryData(data);
	xhr.open("GET", 'api/get_flyby?' + querystring);

	xhr.setRequestHeader("Accept", "application/json");
	xhr.setRequestHeader("Content-Type", "application/json");

	xhr.onreadystatechange = function() {
		if (xhr.readyState == 4) {
			if (xhr.status == 200) {
				var text = xhr.responseText;
				var map_box = document.getElementById('flyby_box')
				map_box.innerHTML = text;

			}
			setTimeout(function() {
				get_flyby()
			}, 100000);
		}
	};

	xhr.send();
}

get_flyby();