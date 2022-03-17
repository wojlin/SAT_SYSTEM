function get_info() {
	let xhr = new XMLHttpRequest();

	xhr.open("GET", 'api/get_info');

	xhr.setRequestHeader("Accept", "application/json");
	xhr.setRequestHeader("Content-Type", "application/json");

	xhr.onreadystatechange = function() {
		if (xhr.readyState == 4) {
			if (xhr.status == 200) {

				var text = xhr.responseText;
				var map_box = document.getElementById('info_box')
				map_box.innerHTML = text;
				setTimeout(function() {
					get_info()
				}, 1000);
			}
		}
	};

	xhr.send();
}

get_info();