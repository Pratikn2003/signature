

function scrollHome() {
    window.scrollTo({ top: 0, behavior: "smooth" });
}

const toggle = document.getElementById("themeToggle");

toggle.addEventListener("click", () => {
    document.documentElement.classList.toggle("dark"); // <-- FIXED
    toggle.classList.toggle("ri-sun-line");
});

const sections = document.querySelectorAll("section");
const navLinks = document.querySelectorAll(".nav-menu a");

window.addEventListener("scroll", () => {

    const navbar = document.querySelector("nav");

    if (window.scrollY > 10) {
        navbar.classList.add("scrolled");
    } else {
        navbar.classList.remove("scrolled");
    }

    let current = "";

    sections.forEach(section => {
        const sectionTop = section.offsetTop - 200;
        if (window.scrollY >= sectionTop) {
            current = section.id;
        }
    });

    navLinks.forEach(link => {
        link.classList.remove("active");
        if (link.getAttribute("href") === "#" + current) {
            link.classList.add("active");
        }
    });
});





const scrollUp = document.getElementById("scrollUp");

window.addEventListener("scroll", () => {
    if (window.scrollY > 400) {
        scrollUp.classList.add("show");
    } else {
        scrollUp.classList.remove("show");
    }
});








