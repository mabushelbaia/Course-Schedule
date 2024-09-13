document.addEventListener("DOMContentLoaded", function () {
  let dropZone = document.getElementById("dropZone");
  let fileInput = document.getElementById("fileInput");
  let uploadForm = document.getElementById("uploadForm");

  dropZone.addEventListener("click", function () {
    fileInput.click();
  });

  fileInput.addEventListener("change", async function () {
    if (fileInput.files.length > 0) {
      const formData = new FormData(uploadForm);

      const response = await fetch("/upload", {
        method: "POST",
        body: formData,
      });
      uploadForm.reset();
      openModal();
    }
  });

  dropZone.addEventListener("dragover", function (e) {
    e.preventDefault();
    e.stopPropagation();
  });

  dropZone.addEventListener("drop", async function (e) {
    e.preventDefault();
    e.stopPropagation();
    let file = e.dataTransfer.files[0];
    fileInput.files = e.dataTransfer.files;
    const formData = new FormData(uploadForm);
    const response = await fetch("/upload", {
      method: "POST",
      body: formData,
    });
    // reset the input
    uploadForm.reset();
    openModal();
  });

  function openModal() {
    document.getElementById("hiddenButton").click();
  }
  document
    .getElementById("downloadButton")
    .addEventListener("click", function () {
      fetch("/download")
        .then((response) => {
          if (!response.ok) throw new Error("Network response was not ok");
          return response.blob();
        })
        .then((blob) => {
          const url = URL.createObjectURL(blob);
          const a = document.createElement("a");
          a.href = url;
          a.download = "calendar.ics";
          a.click();
          URL.revokeObjectURL(url);
        })
        .catch((error) =>
          console.error("There was a problem with the fetch operation:", error)
        );
    });
});
