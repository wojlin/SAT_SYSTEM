function encodeQueryData(data) {
   const ret = [];
   for (let d in data)
     ret.push(encodeURIComponent(d) + '=' + encodeURIComponent(data[d]));
   return ret.join('&');
}

function get_map()
{
    let xhr = new XMLHttpRequest();

    var data = {};
    data["draw_ground_station"] = document.getElementById("draw_ground_station").checked;
    data["draw_day_night_cycle"] = document.getElementById("draw_day_night_cycle").checked;
    data["draw_satellite_path"] = document.getElementById("draw_satellite_path").checked;
    data["satellite_path_resolution"] = parseInt(document.getElementById("satellite_path_resolution").value);
    data["satellite_path_time_ahead"] = parseInt(document.getElementById("satellite_path_time_ahead").value);

    const querystring = encodeQueryData(data);
    console.log(querystring)
    xhr.open("GET", 'api/get_map?' + querystring);

    xhr.setRequestHeader("Accept", "application/json");
    xhr.setRequestHeader("Content-Type", "application/json");

    xhr.onreadystatechange = function () {
       if (xhr.readyState === 4) {
          var text = xhr.responseText;
          var map_box = document.getElementById('map_box')
          map_box.innerHTML = text;
          setInterval(function(){get_map}, 60000);
       }};

    xhr.send();
}

get_map();