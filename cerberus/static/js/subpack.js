
function activeClass (){
var header = document.getElementById("subPack");
var btns = header.getElementsByClassName("sub_pack");
for (var i = 0; i < btns.length; i++) {
  btns[i].addEventListener("click", function() {
  var current = document.getElementsByClassName("active");
  current[0].className = current[0].className.replace(" active", "");
  this.className += " active";
  console.log("this.className",this.className)
  });
}
}
