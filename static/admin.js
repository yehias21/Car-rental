    live_search = function (str){
        let xhttp = new XMLHttpRequest();
        xhttp.open("POST","/admin/search_car",true);
        xhttp.setRequestHeader("Content-Type", "application/json");
        xhttp.onload = function (){
                let str = JSON.parse(xhttp.response)['new']
                const parser = new DOMParser();
                let  dom = parser.parseFromString(str,'text/html');
                var card_container = document.querySelector("#carbody");
                card_container.innerHTML = dom.children[0].children[1].children[0].innerHTML
        }
        let plateid = document.querySelector("#navbarmidle > form > div > input:nth-child(1)").value;
        let brand = document.querySelector("#navbarmidle > form > div > input:nth-child(2)").value;
        let model = document.querySelector("#navbarmidle > form > div > input:nth-child(3)").value;
        let modelYear = document.querySelector("#navbarmidle > form > div > input:nth-child(4)").value;
        let color = document.querySelector("#navbarmidle > form > div > input:nth-child(5)").value;
        let active = document.querySelector("#navbarmidle > form > div > input:nth-child(6)").value;
        let rate = document.querySelector("#navbarmidle > form > div > input:nth-child(7)").value;
        let officeloc = document.querySelector("#navbarmidle > form > div > input:nth-child(8)").value;
        let data = JSON.stringify({"plateID":plateid,"modelYear":modelYear,"model":model,"brand":brand,"color":color,"active":active,"rate":rate,"officeloc":officeloc});
        xhttp.send(data)




    }