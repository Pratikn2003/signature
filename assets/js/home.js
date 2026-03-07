// ================= ALWAYS OPEN PAGE FROM TOP =================
if ("scrollRestoration" in history) {
    history.scrollRestoration = "manual";
}

// ================= SCROLL TO TOP FUNCTION =================
function scrollHome() {
    window.scrollTo({ top: 0, behavior: "smooth" });
}

// ================= DOM LOADED =================
document.addEventListener("DOMContentLoaded", function () {

    // Immediately reset scroll (no flicker)
    window.scrollTo(0, 0);

    // ================= THEME TOGGLE =================
    const toggle = document.getElementById("themeToggle");

    if (toggle) {
        toggle.addEventListener("click", () => {
            document.documentElement.classList.toggle("dark");
            toggle.classList.toggle("ri-sun-line");
        });
    }

    // ================= SECTION ACTIVE LINK + NAVBAR EFFECT =================
    const sections = document.querySelectorAll("section");
    const navLinks = document.querySelectorAll(".nav-menu a");
    const navbar = document.querySelector("nav");

    window.addEventListener("scroll", () => {

        // Navbar background on scroll
        if (window.scrollY > 10) {
            navbar.classList.add("scrolled");
        } else {
            navbar.classList.remove("scrolled");
        }

        // Active section highlight
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

    // ================= CONTACT FORM RESET =================
    const contactForm = document.getElementById("contactForm");

    if (contactForm) {
        contactForm.addEventListener("submit", function (e) {
            e.preventDefault();

            // If invalid, show browser validation UI
            if (!contactForm.checkValidity()) {
                contactForm.reportValidity();
                return;
            }

            // Success message
            alert("Message Sent!");

            // Reset form fields
            contactForm.reset();

            // Remove focus (fix floating label issue)
            document.activeElement.blur();
        });
    }

    // ================= SCROLL UP BUTTON =================
    const scrollUp = document.getElementById("scrollUp");

    window.addEventListener("scroll", () => {
        if (window.scrollY > 400) {
            scrollUp.classList.add("show");
        } else {
            scrollUp.classList.remove("show");
        }
    });

    // ================= MOBILE SLIDE NAV =================
const hamburger = document.getElementById("hamburger");
const navMenu = document.getElementById("navMenu");
const navClose = document.getElementById("navClose");

if (hamburger && navMenu) {

    // OPEN MENU
    hamburger.addEventListener("click", () => {
        navMenu.classList.add("show-menu");
    });

    // CLOSE MENU (X button)
    if (navClose) {
        navClose.addEventListener("click", () => {
            navMenu.classList.remove("show-menu");
        });
    }

    // CLOSE WHEN CLICKING A LINK
    document.querySelectorAll(".nav-menu a").forEach(link => {
        link.addEventListener("click", () => {
            navMenu.classList.remove("show-menu");
        });
    });
}
});
