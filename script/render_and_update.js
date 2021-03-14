const nameField = document.getElementById("bookid");
const sendbookidButton = document.getElementById("sendbookidButton")
sendbookidButton.disabled = true;

nameField.addEventListener("input", event => {
    const elem = event.target;
    const valid = elem.value.length != 0;
    const book_id = elem.value;
    if (valid && sendbookidButton.disabled) {
        sendbookidButton.disabled = false;
    } else if (!valid && !sendbookidButton.disabled) {
        sendbookidButton.disabled = true;
    }
    sendbookidButton.onclick = function() {
        $.ajax({
            headers: { "Accept": "application/json"},
            url:"http://127.0.0.1:5000/api/book?id=" + book_id,
            type:'get',
            success:function(res){
                var res_json = JSON.parse(res);
                var result = "Results: </br>";
                for(item in res_json[0]) {
                    if (item == "_id") {
                        continue;
                    }
                    result += item + ": " + res_json[0][item] + "</br>"; 
                }
                document.getElementById("p1").innerHTML = result;
            }
        }); 
        return false;
    }
});

const nameField1 = document.getElementById("authorid");
const sendauthoridButton = document.getElementById("sendauthoridButton")
sendauthoridButton.disabled = true;

nameField1.addEventListener("input", event => {
    const elem = event.target;
    const valid = elem.value.length != 0;
    const author_id = elem.value;
    if (valid && sendauthoridButton.disabled) {
        sendauthoridButton.disabled = false;
    } else if (!valid && !sendauthoridButton.disabled) {
        sendauthoridButton.disabled = true;
    }
    sendauthoridButton.onclick = function() {
        $.ajax({
            headers: { "Accept": "application/json"},
            url:"http://127.0.0.1:5000/api/author?id=" + author_id,
            type:'get',
            success:function(res){
                var res_json = JSON.parse(res);
                var result = "Results: </br>";
                for(item in res_json[0]) {
                    if (item == "_id") {
                        continue;
                    }
                    result += item + ": " + res_json[0][item] + "</br>"; 
                }
                document.getElementById("p1").innerHTML = result;
            }
        }); 
        return false;
    }
});
