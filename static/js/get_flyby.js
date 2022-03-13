function encodeQueryData(data) {
   const ret = [];
   for (let d in data)
     ret.push(encodeURIComponent(d) + '=' + encodeURIComponent(data[d]));
   return ret.join('&');
}

function get_flyby()
{
    let xhr = new XMLHttpRequest();

    var data = {};
    data["hours_ahead"] = parseInt(document.getElementById("hours_ahead").value);
    data["minimal_angle"] = parseInt(document.getElementById("minimal_angle").value);
    data["display_amount"] = parseInt(document.getElementById("display_amount").value);

    const querystring = encodeQueryData(data);
    console.log(querystring)
    xhr.open("GET", 'api/get_flyby?' + querystring);

    xhr.setRequestHeader("Accept", "application/json");
    xhr.setRequestHeader("Content-Type", "application/json");

    xhr.onreadystatechange = function () {
       if (xhr.readyState === 4) {
          var text = xhr.responseText;
          var map_box = document.getElementById('flyby_box')
          map_box.innerHTML = text;
          setInterval(function(){get_flyby}, 10000);
       }};

    xhr.send();
}

get_flyby();