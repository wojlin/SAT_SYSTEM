var host = document.getElementById("host").dataset.host;
var port = document.getElementById("port").dataset.port;


function get_metadata(name) {
	let xhr = new XMLHttpRequest();

    var data = {"name": name};
    const querystring = encodeQueryData(data);
    xhr.open("GET", 'api/get_image_metadata?' + querystring);

	xhr.onreadystatechange = function() {
		if (xhr.readyState == 4) {
			if (xhr.status == 200) {

                var desc = document.getElementById("image_viewer_description");
                var desc_ul = document.createElement("ul");
                desc_ul.id = "description_list"
				const json = JSON.parse(xhr.responseText);
				console.log(json);
				if (json["status"] == "metadata_enabled")
				{
				    var text = ""
				    text += "<pre class='space_block'>"
				    text += "<p>satellite  : " + "<span style='color:#f2c549'>" + json["satellite_name"] + "</span></p>"
				    text += "<p>type       : " + "<span style='color:#f2c549'>" + json["transmission_type"] + "</span></p>"
				    text += "<p>frequency  : " + "<span style='color:#f2c549'>" + json["frequency"] + "</span> Mhz</p>"
				    text += "<p>duration   : "+"<span style='color:#f2c549'>" +parseFloat(json["flyby_duration"])+ "</span> s</p>"
				    text += "<p>max alt    : "+"<span style='color:#f2c549'>" + parseFloat(json["culminate"]["perspective"]["altitude"]).toFixed(2)+ "</span>°</p>"
				    text += "<p>tle:</p><pre class='code_block'>"
				    text += "<p>"+json["tle_line1"]+"</p>"
				    text += "<p>"+json["tle_line2"] + "</p>"
				    text += "</pre>"
				    text += "</pre>"

                    function date_to_str(time_str)
                    {
                        var rise_epoch = (parseFloat(time_str)) * 1000
                        var rise_date = new Date(rise_epoch)
                        var date_str = rise_date.toLocaleString('fr-CA', { hour12: false, year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit',  minute: '2-digit', second: '2-digit' });
                        date_str = date_str.replace('h', ':')
                        date_str = date_str.replace('min', ':')
                        date_str = date_str.replace('s', '')
                        date_str = date_str.replace(' : ', ':')
                        date_str = date_str.replace(' : ', ':')
                        date_str = date_str.replace(',', '')
                        return date_str
                    }

                    text += "<pre class='space_block'>"
				    text += "<p>rise:</p>"
				    text += "<p>    time      : <span style='color:#f2c549'>" + date_to_str(json["rise"]["epoch"]) + "</span></p>"
				    text += "<p>    direction : <span style='color:#f2c549'>" + parseFloat(json["rise"]["perspective"]["azimuth"]).toFixed(2) + " (" + json["rise"]["perspective"]["direction"] + ")</span></p>"
                    text += "<p>    distance  : <span style='color:#f2c549'>" + parseFloat(json["rise"]["perspective"]["distance"]).toFixed(2) + "</span> km</p>"
                    text += "<p></p>"
                    text += "<p>culminate:</p>"
				    text += "<p>    time      : <span style='color:#f2c549'>" + date_to_str(json["culminate"]["epoch"]) + "</span></p>"
				    text += "<p>    direction : <span style='color:#f2c549'>" + parseFloat(json["culminate"]["perspective"]["azimuth"]).toFixed(2) + " (" + json["culminate"]["perspective"]["direction"] + ")</span></p>"
                    text += "<p>    distance  : <span style='color:#f2c549'>" + parseFloat(json["culminate"]["perspective"]["distance"]).toFixed(2) + "</span> km</p>"
                    text += "<p></p>"
                    text += "<p>set:</p>"
				    text += "<p>    time      : <span style='color:#f2c549'>" + date_to_str(json["set"]["epoch"]) + "</span></p>"
				    text += "<p>    direction : <span style='color:#f2c549'>" + parseFloat(json["set"]["perspective"]["azimuth"]).toFixed(2) + " (" + json["set"]["perspective"]["direction"] + ")</span></p>"
                    text += "<p>    distance  : <span style='color:#f2c549'>" + parseFloat(json["set"]["perspective"]["distance"]).toFixed(2) + "</span> km</p>"
                    text += "<p></p>"

				    text += "</pre>"

				    desc_ul.innerHTML = text;

				}else
				{
                    var text = "<p><span style='color:red'>metadata disabled</span></p>"
				    desc_ul.innerHTML = text;
				}



                desc.innerHTML = '';
                desc.appendChild(desc_ul);

			}
		}
	};
	xhr.send();
}

function open_gallery(name)
{
    console.log(name);
    var data = {"name": name};
    const querystring = encodeQueryData(data);
    document.getElementById("image_viewer_box").style='';
    var image = document.getElementById("image_viewer_box_image");
    image.style='';
    var url = 'http://'+host+':'+port+'/api/get_image?' + querystring
    image.src = url;
    document.getElementById("image_viewer").style.display = "block";
    document.getElementById("image_viewer_captions_filename").innerHTML = name;

    get_metadata(name);
}


function get_thumbnail(name) {
	let xhr = new XMLHttpRequest();
    var data = {"name": name};
    const querystring = encodeQueryData(data);
    return 'http://'+host+':'+port+'/api/get_image_thumbnail?' + querystring
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
				gallery.innerHTML = "";
                for(var i in json){
                    var key = i;

                    var img_bin = get_thumbnail(json[i]['filename']);
                    console.log(img_bin)

                    var block = document.createElement("li")
                    block.classList.add("item");
                    console.log(json[i]['filename']);

                     block.onclick = (function(i) {return function() {open_gallery(json[i]['filename']);};})(i);


                    var inner = '<img class="gallery_image" src="'+img_bin+'"></img><div class="gallery_name_div" ><p class="gallery_name">'+json[i]['date']+'</p><p class="gallery_name">'+json[i]['sat_name']+'</p></div>'
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


const zoomElement = document.getElementById("image_viewer_box_image");
let zoom = 1;
const ZOOM_SPEED = 0.05;

document.addEventListener("wheel", function(e) {

    if(e.deltaY > 0){
        zoomElement.style.transform = `scale(${zoom -= ZOOM_SPEED}) translateY(-50%)`;
    }else{
        zoomElement.style.transform = `scale(${zoom += ZOOM_SPEED}) translateY(-50%)`;  }

});








dragElement(document.getElementById("image_viewer_box"));

function dragElement(elmnt) {
  var pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
  if (document.getElementById(elmnt.id + "header")) {
    // if present, the header is where you move the DIV from:
    document.getElementById(elmnt.id + "header").onmousedown = dragMouseDown;
  } else {
    // otherwise, move the DIV from anywhere inside the DIV:
    elmnt.onmousedown = dragMouseDown;
  }

  function dragMouseDown(e) {
    e = e || window.event;
    e.preventDefault();
    // get the mouse cursor position at startup:
    pos3 = e.clientX;
    pos4 = e.clientY;
    document.onmouseup = closeDragElement;
    // call a function whenever the cursor moves:
    document.onmousemove = elementDrag;
  }

  function elementDrag(e) {
    e = e || window.event;
    e.preventDefault();
    // calculate the new cursor position:
    pos1 = pos3 - e.clientX;
    pos2 = pos4 - e.clientY;
    pos3 = e.clientX;
    pos4 = e.clientY;
    // set the element's new position:
    elmnt.style.top = (elmnt.offsetTop - pos2) + "px";
    elmnt.style.left = (elmnt.offsetLeft - pos1) + "px";
  }

  function closeDragElement() {
    // stop moving when mouse button is released:
    document.onmouseup = null;
    document.onmousemove = null;
  }
}
