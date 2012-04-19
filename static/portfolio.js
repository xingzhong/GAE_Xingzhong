

var symbol=new Array();
var share=new Array();
var time=new Array();
function addOneLine (form) {
    var table=document.getElementById("one-column-emphasis");
    var row=table.insertRow(1);
    var cell1=row.insertCell(0);
    var cell2=row.insertCell(1);
    var cell3=row.insertCell(2);
    cell1.innerHTML=form.symbol.value;
    cell2.innerHTML=form.share.value;
    cell3.innerHTML=form.time.value;
    symbol.push(form.symbol.value);
    share.push(form.share.value);
    time.push(form.time.value);
}

function submitAll(form){
    form.elements[0].value = toList(symbol);
    form.elements[1].value = toList(share);
    form.elements[2].value = toList(time);
    form.submit();
}

function toList(array){
    var len = array.length;
    var list = new String();
    list += '[';
    for (var i=0;i<len;i++){
        list += "'" + array[i] + "'";
        list += ',';
    }
    list += ']';
    return list;
}



function showResult(){
    var xmlhttp;
    if (window.XMLHttpRequest)
      {// code for IE7+, Firefox, Chrome, Opera, Safari
      xmlhttp=new XMLHttpRequest();
      }
    else{// code for IE6, IE5
      xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
      }
    xmlhttp.onreadystatechange=function(){
      if (xmlhttp.readyState==4 && xmlhttp.status==200){
            var data = xmlhttp.responseText.split(',');
            var table=document.getElementById("hor-minimalist-a");
            var expRet = document.getElementsByName("expectedRet")[0];
            var Ret = 0;
            for (d in data){
                d = parseInt(d);
                var wei = table.rows[d+1].cells[1];
                var sha = table.rows[d+1].cells[2];
                var val = table.rows[d+1].cells[3];
                var ret = expRet.rows[d+1].cells[3];
                
                wei.innerHTML = parseFloat(data[d]);
                val.innerHTML = parseFloat(data[d]) * parseFloat(val.innerHTML);
                sha.innerHTML = parseFloat(val.innerHTML) / parseFloat(sha.innerHTML);
                
                Ret = Ret + parseFloat(ret.innerHTML) * parseFloat(wei.innerHTML);
                
            }
            $("#longOnlyExpRet").text(Ret);
        }
    }
    xmlhttp.open("GET","/picloudjob",true);
    xmlhttp.send();
}
