function navbarHamburger () {
 let navbar = document.getElementById("topnav")
 if (navbar.className == "navbar navbar-expand-sm bg-dark navbar-dark navbar-static-top"){
    navbar.className += " responsive" // add responsive class to navbar 
 } else {
    navbar.className = "navbar navbar-expand-sm bg-dark navbar-dark navbar-static-top";
 }
}