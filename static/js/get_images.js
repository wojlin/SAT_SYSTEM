
function get_thumbnail(name) {
	let xhr = new XMLHttpRequest();
    var data = {"name": name};
    const querystring = encodeQueryData(data);
    return 'http://localhost:2137/api/get_image_thumbnail?' + querystring
}

function get_images() {
	let xhr = new XMLHttpRequest();

    var data = {};
	data["show_x_first"] = parseInt(document.getElementById("show_x_first").value);
    const querystring = encodeQueryData(data);
	console.log(querystring)
	xhr.open("GET", 'api/get_images_list?' + querystring, true);

	xhr.onreadystatechange = function() {
		if (xhr.readyState == 4) {
			if (xhr.status == 200) {
				var text = xhr.responseText;
				var map_box = document.getElementById('images_box')
                var json = JSON.parse(text);
                console.log(json);
				var gallery = document.getElementById("gallery");
                for(var i in json){
                    var key = i;
                    var val = json[i];

                    var img_bin = get_thumbnail(json[i]);
                    console.log(img_bin)

                    var block = document.createElement("li")
                    block.classList.add("item");
                    var inner = '<img class="gallery_image" src="'+img_bin+'"></img><p class="gallery_name">'+val+'</p>'
                    block.innerHTML = inner;
                    gallery.appendChild(block);

                }


			}
			setTimeout(function() {
				get_images()
			}, 100000);
		}
	};

	xhr.send();
}

get_images();