document.addEventListener("DOMContentLoaded", function () {

    const modal = document.getElementById("modal");
    const openAdd = document.getElementById("openAdd");
    const closeModal = document.getElementById("closeModal");

    const addForm = document.getElementById("addForm");

    const signatureInput = document.getElementById("signatureFiles");
    const signaturePreview = document.getElementById("signaturePreview");
    const addUploadArea = document.getElementById("addUploadArea");
    const saveBtn = document.getElementById("saveCustomer");

    const warningBox = document.getElementById("addWarning");

    const allowedTypes = ["image/png", "image/jpeg", "image/jpg"];
    const minFiles = 6;
    const maxFiles = 12;

    let selectedFiles = [];

    /* ================= VERIFY FORM ELEMENTS ================= */

    const verifyForm = document.getElementById("verifyForm");
    const openVerify = document.getElementById("openVerify");
    const verifyFileInput = document.getElementById("verifyFile");
    const verifyUploadArea = document.getElementById("verifyUploadArea");
    const verifyPreview = document.getElementById("verifyPreview");
    const verifyBtn = document.getElementById("verifyBtn");
    const verifyWarning = document.getElementById("verifyWarning");

    let verifySelectedFile = null;



    /* ================= CLOSE POPUP FUNCTION ================= */

    function closePopup() {

        // Close modal
        modal.classList.remove("show");
        document.body.classList.remove("modal-open");

        // Reset inputs
        document.getElementById("customerName").value = "";
        document.getElementById("customerId").value = "";

        // Reset images
        selectedFiles = [];
        signaturePreview.innerHTML = "";
        signatureInput.value = "";

        // Clear warnings
        warningBox.innerText = "";


        // Reset Verify form
        document.getElementById("verifyId").value = "";
        verifySelectedFile = null;
        verifyPreview.innerHTML = "";
        verifyFileInput.value = "";
        verifyWarning.innerText = "";

        addForm.classList.remove("active");
        verifyForm.classList.remove("active");

    }


    /* ================= OPEN MODAL ================= */

    openAdd?.addEventListener("click", () => {
        modal.classList.add("show");
        addForm.classList.add("active");
        document.body.classList.add("modal-open"); // disable scroll
        warningBox.innerText = "";
    });

    /* ================= OPEN VERIFY MODAL ================= */

    openVerify?.addEventListener("click", () => {
        modal.classList.add("show");

        addForm.classList.remove("active");   // hide add form
        verifyForm.classList.add("active");   // show verify form

        document.body.classList.add("modal-open");

        verifyWarning.innerText = "";          // clear old result
    });

    closeModal.addEventListener("click", closePopup);



    /* ================= CLOSE ON BACKGROUND CLICK ================= */

    modal.addEventListener("click", (e) => {
        if (e.target === modal) {
            closePopup();
        }
    });

    /* ================= CLOSE ON ESC KEY ================= */

    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && modal.classList.contains("show")) {
            closePopup();
        }
    });


    /* ================= UPLOAD CLICK ================= */

    addUploadArea.addEventListener("click", () => {
        signatureInput.click();
    });

    /* ================= VERIFY UPLOAD CLICK ================= */

    verifyUploadArea?.addEventListener("click", () => {
        verifyFileInput.click();
    });


    /* ================= FILE UPLOAD ================= */

    signatureInput.addEventListener("change", function () {

        const files = Array.from(this.files);
        warningBox.innerText = "";

        for (let file of files) {

            if (!allowedTypes.includes(file.type)) {
                warningBox.innerText = "File type not supported! Only PNG, JPG, JPEG allowed.";
                continue;
            }

            if (selectedFiles.length >= maxFiles) {
                warningBox.innerText = "Maximum 12 images allowed.";
                break;
            }

            selectedFiles.push(file);
        }

        renderPreview();
        signatureInput.value = "";
    });

    /* ================= VERIFY FILE UPLOAD ================= */

    verifyFileInput?.addEventListener("change", function () {

        const file = this.files[0];
        verifyWarning.innerText = "";

        if (!file) return;

        if (!allowedTypes.includes(file.type)) {
            verifyWarning.innerText = "File type not supported! Only PNG, JPG, JPEG allowed.";
            verifySelectedFile = null;
            return;
        }

        verifySelectedFile = file;
        renderVerifyPreview();
        verifyFileInput.value = "";
    });


    /* ================= PREVIEW RENDER ================= */

    function renderPreview() {

        signaturePreview.innerHTML = "";

        selectedFiles.forEach((file, index) => {

            const wrapper = document.createElement("div");
            wrapper.className = "preview-item";

            const img = document.createElement("img");
            img.src = URL.createObjectURL(file);

            img.addEventListener("click", () => openFullImage(img.src));

            const removeBtn = document.createElement("div");
            removeBtn.className = "remove-btn";
            removeBtn.innerHTML = "✖";

            removeBtn.addEventListener("click", (e) => {
                e.stopPropagation();
                selectedFiles.splice(index, 1);
                renderPreview();
            });

            wrapper.appendChild(img);
            wrapper.appendChild(removeBtn);
            signaturePreview.appendChild(wrapper);
        });
    }

    function renderVerifyPreview() {

        verifyPreview.innerHTML = "";

        const wrapper = document.createElement("div");
        wrapper.className = "preview-item";

        const img = document.createElement("img");
        img.src = URL.createObjectURL(verifySelectedFile);

        img.addEventListener("click", () => openFullImage(img.src));

        const removeBtn = document.createElement("div");
        removeBtn.className = "remove-btn";
        removeBtn.innerHTML = "✖";

        removeBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            verifySelectedFile = null;
            verifyPreview.innerHTML = "";
        });

        wrapper.appendChild(img);
        wrapper.appendChild(removeBtn);
        verifyPreview.appendChild(wrapper);
    }


    /* ================= SAVE VALIDATION ================= */

    saveBtn.addEventListener("click", () => {

        warningBox.innerText = "";

        const customerName = document.getElementById("customerName").value.trim();
        const customerId = document.getElementById("customerId").value.trim();

        // Check Name
        if (customerName === "") {
            warningBox.innerText = "Customer Name is required.";
            return;
        }

        // Check ID
        if (customerId === "") {
            warningBox.innerText = "Customer ID is required.";
            return;
        }

        // Check minimum images
        if (selectedFiles.length < minFiles) {
            warningBox.innerText = "Minimum 6 images required.";
            return;
        }

        // Check maximum images
        if (selectedFiles.length > maxFiles) {
            warningBox.innerText = "Maximum 12 images allowed.";
            return;
        }

        // If everything is valid
        alert("Customer Saved Successfully!");

        // Reset inputs
        document.getElementById("customerName").value = "";
        document.getElementById("customerId").value = "";

        // Reset uploaded files
        selectedFiles = [];
        signaturePreview.innerHTML = "";
        signatureInput.value = "";

        // Clear warning
        warningBox.innerText = "";

        // Close popup
        closePopup();

    });


    /* ================= VERIFY VALIDATION ================= */

    verifyBtn?.addEventListener("click", () => {

        verifyWarning.innerText = "";

        const verifyId = document.getElementById("verifyId").value.trim();

        if (verifyId === "") {
            verifyWarning.innerText = "Customer ID is required.";
            return;
        }

        if (!verifySelectedFile) {
            verifyWarning.innerText = "Please upload a signature to verify.";
            return;
        }

        // If validation passes, trigger external verification logic
        document.dispatchEvent(new CustomEvent("verifyFormValid", {
            detail: {
                customerId: verifyId,
                file: verifySelectedFile
            }
        }));

    });


    /* ================= FULL SCREEN VIEW ================= */

    function openFullImage(src) {

        const overlay = document.createElement("div");
        overlay.style.position = "fixed";
        overlay.style.inset = "0";
        overlay.style.background = "rgba(0,0,0,0.85)";
        overlay.style.display = "flex";
        overlay.style.alignItems = "center";
        overlay.style.justifyContent = "center";
        overlay.style.zIndex = "10000";

        const img = document.createElement("img");
        img.src = src;
        img.style.maxWidth = "90%";
        img.style.maxHeight = "90%";

        const closeBtn = document.createElement("div");
        closeBtn.innerHTML = "✖";
        closeBtn.style.position = "absolute";
        closeBtn.style.top = "25px";
        closeBtn.style.right = "35px";
        closeBtn.style.fontSize = "28px";
        closeBtn.style.color = "white";
        closeBtn.style.cursor = "pointer";

        overlay.appendChild(img);
        overlay.appendChild(closeBtn);
        document.body.appendChild(overlay);

        function closeViewer() {
            document.body.removeChild(overlay);
            document.removeEventListener("keydown", escHandler);
        }

        closeBtn.addEventListener("click", closeViewer);

        overlay.addEventListener("click", (e) => {
            if (e.target === overlay) closeViewer();
        });

        function escHandler(e) {
            if (e.key === "Escape") closeViewer();
        }

        document.addEventListener("keydown", escHandler);
    }

});
