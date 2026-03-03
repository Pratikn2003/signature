

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


// ================= CONTACT FORM (EmailJS - Send to any email) =================
// Initialize EmailJS with your Public Key
emailjs.init("eB8aNYx7sURbZXido");

const contactForm = document.getElementById("contactForm");
const formStatus = document.getElementById("formStatus");
const submitBtn = document.getElementById("submitBtn");

contactForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    submitBtn.disabled = true;
    submitBtn.innerHTML = 'Sending... <i class="ri-loader-4-line"></i>';
    formStatus.textContent = "";
    formStatus.style.color = "";

    // Collect form data
    const templateParams = {


        to_email: document.getElementById("toEmail").value.trim(),
        from_name: document.getElementById("username").value.trim(),
        subject: document.getElementById("emailSubject").value.trim(),
        message: document.getElementById("usermessage").value.trim(),
    };

    // Validate all fields are filled
    if (!templateParams.to_email || !templateParams.from_name || !templateParams.subject || !templateParams.message) {
        formStatus.textContent = "❌ Please fill in all fields.";
        formStatus.style.color = "#ef4444";
        submitBtn.disabled = false;
        submitBtn.innerHTML = 'Send Message <i class="ri-arrow-right-up-line"></i>';
        return;
    }

    console.log("Sending email with params:", templateParams);

    try {
        // Use sendForm to directly pass form fields to EmailJS template
        const response = await emailjs.sendForm("service_2200x2e", "template_dgs9ba5", contactForm);
        console.log("EmailJS Response:", response);

        formStatus.textContent = "✅ Message sent successfully!";
        formStatus.style.color = "#22c55e";
        contactForm.reset();
    } catch (error) {
        console.error("EmailJS Full Error:", error);
        console.error("Error status:", error.status);
        console.error("Error text:", error.text);
        formStatus.textContent = "❌ Failed to send: " + (error.text || error.message || JSON.stringify(error));
        formStatus.style.color = "#ef4444";
    }

    submitBtn.disabled = false;
    submitBtn.innerHTML = 'Send Message <i class="ri-arrow-right-up-line"></i>';
});








