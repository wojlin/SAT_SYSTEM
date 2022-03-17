function get_status() {
	let xhr = new XMLHttpRequest();

	xhr.open("GET", 'api/get_status', true);

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