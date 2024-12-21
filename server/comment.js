var strong = document.querySelectorAll("strong")[0];

// function lengthCheck() {
//     var value = this.getAttribute("value");
//     if (value.length > 100) {
//         strong.innerHMTL = "Comment too long!";
//     }
// }

var inputs = document.querySelectorAll("input");

for (var i = 0; i < inputs.length; i++) {
    inputs[i].addEventListener("keydown", function (e) {
        e.preventDefault();
        strong.innerHTML = new Date()
    });
}