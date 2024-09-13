document.addEventListener("DOMContentLoaded", function () {
  let dropZone = document.getElementById("dropZone");
  let fileInput = document.getElementById("fileInput");
  let uploadForm = document.getElementById("uploadForm");
  let icalData = null;

  dropZone.addEventListener("click", function () {
    fileInput.click();
  });

  fileInput.addEventListener("change", handleFileUpload);

  dropZone.addEventListener("dragover", function (e) {
    e.preventDefault();
    e.stopPropagation();
  });

  dropZone.addEventListener("drop", handleFileDrop);

  document
    .getElementById("downloadButton")
    .addEventListener("click", handleDownload);
  document
    .getElementById("createCalendarButton")
    .addEventListener("click", handleCreateCalendar);

  async function handleFileUpload() {
    if (fileInput.files.length > 0) {
      const formData = new FormData(uploadForm);
      await uploadFile(formData);
    }
  }

  async function handleFileDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    let file = e.dataTransfer.files[0];
    fileInput.files = e.dataTransfer.files;
    const formData = new FormData(uploadForm);
    await uploadFile(formData);
  }

  async function uploadFile(formData) {
    try {
      const response = await fetch("/upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Error uploading file");
      }

      const data = await response.json();
      icalData = data.ical_data;
      openModal();
    } catch (error) {
      console.error("Error uploading file:", error);
      // Handle error (e.g., show an error message to the user)
    } finally {
      uploadForm.reset();
    }
  }
  function handleDownload() {
    console.log("Download button clicked");
    console.log("icalData:", icalData);

    if (!icalData) {
      console.error("No iCal data available");
      alert("No calendar data available. Please upload a file first.");
      return;
    }

    const encodedData = encodeURIComponent(icalData);
    console.log("Encoded icalData:", encodedData);

    fetch(`/download?ical_data=${encodedData}`)
      .then((response) => {
        if (!response.ok) {
          console.error(
            "Server response:",
            response.status,
            response.statusText
          );
          return response.text().then((text) => {
            throw new Error(`Network response was not ok: ${text}`);
          });
        }
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
      .catch((error) => {
        console.error("There was a problem with the fetch operation:", error);
        alert("Failed to download the calendar. Please try again.");
      });
  }

  function handleCreateCalendar() {
    if (!icalData) {
      console.error("No iCal data available");
      return;
    }

    window.location.href = `/authorize?ical_data=${encodeURIComponent(
      icalData
    )}`;
  }

  function openModal() {
    document.getElementById("hiddenButton").click();
  }

  // Check for message parameter in URL (for callback from OAuth)
  const urlParams = new URLSearchParams(window.location.search);
  const message = urlParams.get("message");
  if (message) {
    // Display the message to the user (e.g., in a toast or alert)
    alert(message);
    // Remove the message from the URL
    window.history.replaceState({}, document.title, "/");
  }
});
