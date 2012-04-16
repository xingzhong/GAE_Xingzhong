var symbol=new Array();
var share=new Array();
var time=new Array();
function addOneLine (form) {
    var table=document.getElementById("list");
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