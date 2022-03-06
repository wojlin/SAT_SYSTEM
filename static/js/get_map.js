function get_map()
{
    let xhr = new XMLHttpRequest();
    xhr.open("POST", 'api/get_map');

    xhr.setRequestHeader("Accept", "application/json");
    xhr.setRequestHeader("Content-Type", "application/json");

    xhr.onreadystatechange = function () {
       if (xhr.readyState === 4) {
          var text = xhr.responseText;
          console.log(text);
          var map_box = document.getElementById('map_box')
          map_box.innerHTML = text;
          setInterval(function(){get_map()}, 60000);
       }};

    let data = `{
      "Id": 78912,
      "Customer": "Jason Sweet",
      "Quantity": 1,
      "Price": 18.00
    }`;

    xhr.send(data);
}

get_map();