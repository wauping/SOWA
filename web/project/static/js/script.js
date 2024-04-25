var cost = 0;
function fun1() {
var chbox;
var test;
chbox=document.getElementById('one');
	if (chbox.checked) {
        cost = cost + 1578.32;
        var test = cost;
        document.getElementById("mytext").value = test;
	}
	else {
if (cost > 0){
            cost = cost - 1578.32;
            var test = cost;
            document.getElementById("mytext").value = test;
        }
	}
}
function fun2(){
chbox=document.getElementById('two');
	if (chbox.checked) {
        cost = cost + 436765.79;
        var test = cost;
        document.getElementById("mytext").value = test;
	}
	else {
        if (cost > 0){
            cost = cost - 436765.79;
            var test = cost;
            document.getElementById("mytext").value = test;
        }
	}
}
function fun3(){
chbox=document.getElementById('three');
	if (chbox.checked) {
        cost = cost + 8965.60;
        var test = cost;
        document.getElementById("mytext").value = test;
	}
	else {
        if (cost > 0){
            cost = cost - 8965.60;
            var test = cost;
            document.getElementById("mytext").value = test;
        }

	}
}
function fun4(){
chbox=document.getElementById('four');
	if (chbox.checked) {
        cost = cost + 420.69;
        var test = cost;
        document.getElementById("mytext").value = test;
	}
	else {
        if (cost > 0){
            cost = cost - 420.69;
            var test = cost;
            document.getElementById("mytext").value = test;
        }

	}
}
function fun5(){
chbox=document.getElementById('five');
	if (chbox.checked) {
        cost = cost + 723.21;
        var test = cost;
        document.getElementById("mytext").value = test;
	}
	else {
        if (cost > 0){
            cost = cost - 723.21;
            var test = cost;
            document.getElementById("mytext").value = test;
        }

	}
}
function fun6(){
chbox=document.getElementById('six');
	if (chbox.checked) {
        cost = cost + 2357.74;
        var test = cost;
        document.getElementById("mytext").value = test;
	}
	else {
        if (cost > 0){
            cost = cost - 2357.74;
            var test = cost;
            document.getElementById("mytext").value = test;
        }

	}
}
var test = cost;
document.getElementById("mytext").value = test;