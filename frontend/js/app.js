(function () {
    "use strict";

    const API_BASE = "/api/photo";
    const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
    const ALLOWED_TYPES = ["image/jpeg", "image/png"];

    // Elements
    const dropZone = document.getElementById("dropZone");
    const fileInput = document.getElementById("fileInput");
    const preview = document.getElementById("preview");
    const previewImg = document.getElementById("previewImg");
    const removeBtn = document.getElementById("removeBtn");
    const uploadError = document.getElementById("uploadError");
    const generateBtn = document.getElementById("generateBtn");
    const resultSection = document.getElementById("resultSection");
    const resultImg = document.getElementById("resultImg");
    const downloadBtn = document.getElementById("downloadBtn");
    const regenerateBtn = document.getElementById("regenerateBtn");
    const loadingOverlay = document.getElementById("loadingOverlay");

    let selectedFile = null;

    // --- File Validation ---
    function validateFile(file) {
        if (!ALLOWED_TYPES.includes(file.type)) {
            return "仅支持 JPEG 和 PNG 格式";
        }
        if (file.size > MAX_FILE_SIZE) {
            return "文件大小不能超过 10MB";
        }
        return null;
    }

    function showError(msg) {
        uploadError.textContent = msg;
        uploadError.hidden = false;
    }

    function hideError() {
        uploadError.hidden = true;
    }

    // --- File Selection ---
    function handleFile(file) {
        hideError();
        const err = validateFile(file);
        if (err) {
            showError(err);
            return;
        }
        selectedFile = file;
        const reader = new FileReader();
        reader.onload = function (e) {
            previewImg.src = e.target.result;
            preview.hidden = false;
            dropZone.hidden = true;
            generateBtn.disabled = false;
        };
        reader.readAsDataURL(file);
    }

    function clearFile() {
        selectedFile = null;
        fileInput.value = "";
        previewImg.src = "";
        preview.hidden = true;
        dropZone.hidden = false;
        generateBtn.disabled = true;
        resultSection.hidden = true;
        hideError();
    }

    // --- Events ---
    dropZone.addEventListener("click", function () {
        fileInput.click();
    });

    fileInput.addEventListener("change", function () {
        if (fileInput.files.length) {
            handleFile(fileInput.files[0]);
        }
    });

    dropZone.addEventListener("dragover", function (e) {
        e.preventDefault();
        dropZone.classList.add("dragover");
    });

    dropZone.addEventListener("dragleave", function () {
        dropZone.classList.remove("dragover");
    });

    dropZone.addEventListener("drop", function (e) {
        e.preventDefault();
        dropZone.classList.remove("dragover");
        if (e.dataTransfer.files.length) {
            handleFile(e.dataTransfer.files[0]);
        }
    });

    removeBtn.addEventListener("click", clearFile);

    // --- Custom Color Picker ---
    const customColorPicker = document.getElementById("customColorPicker");
    const customRadio = document.querySelector('input[name="bg_color"][value="custom"]');
    const customSwatch = customRadio.nextElementSibling;

    customColorPicker.addEventListener("input", function () {
        customRadio.checked = true;
        customSwatch.style.background = customColorPicker.value;
        customSwatch.style.border = "none";
    });

    customColorPicker.addEventListener("click", function (e) {
        e.stopPropagation();
        customRadio.checked = true;
    });

    // Initialize custom swatch with picker's default color
    customSwatch.style.background = customColorPicker.value;

    // --- API ---
    function getSelectedParams() {
        const size = document.querySelector('input[name="size"]:checked').value;
        const bg_color_radio = document.querySelector('input[name="bg_color"]:checked');
        let bg_color = bg_color_radio.value;
        if (bg_color === "custom") {
            bg_color = document.getElementById("customColorPicker").value;
        }
        return { size, bg_color };
    }

    async function generatePhoto() {
        if (!selectedFile) return;

        const { size, bg_color } = getSelectedParams();
        const formData = new FormData();
        formData.append("file", selectedFile);
        formData.append("size", size);
        formData.append("bg_color", bg_color);

        loadingOverlay.hidden = false;
        generateBtn.disabled = true;

        try {
            const resp = await fetch(API_BASE + "/generate", {
                method: "POST",
                body: formData,
            });

            if (!resp.ok) {
                const data = await resp.json().catch(function () { return {}; });
                throw new Error(data.message || data.detail || "生成失败，请重试");
            }

            const result = await resp.json();
            showResult(result);
        } catch (err) {
            showError(err.message || "生成失败，请重试");
        } finally {
            loadingOverlay.hidden = true;
            generateBtn.disabled = false;
        }
    }

    function showResult(result) {
        var data = result.data || result;
        resultImg.src = data.photo_url || API_BASE + "/download/" + data.photo_id;
        downloadBtn.href = resultImg.src;
        resultSection.hidden = false;
        resultSection.scrollIntoView({ behavior: "smooth" });
    }

    generateBtn.addEventListener("click", generatePhoto);

    regenerateBtn.addEventListener("click", function () {
        resultSection.hidden = true;
        generatePhoto();
    });
})();
