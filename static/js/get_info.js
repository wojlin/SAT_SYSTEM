function get_info()
{
    let xhr = new XMLHttpRequest();

    xhr.open("GET", 'api/get_info');

    xhr.setRequestHeader("Accept", "application/json");
    xhr.setRequestHeader("Content-Type", "application/json");

    xhr.onreadystatechange = function () {
       if (xhr.readyState === 4) {
          var text = xhr.responseText;
          var map_box = document.getElementById('info_box')
          map_box.innerHTML = text;
          setInterval(function(){get_info}, 60000);
       }};

    xhr.send();
}

get_info();