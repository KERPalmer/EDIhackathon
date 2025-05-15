
// add api key. Didn't have time to set it up with node.js and env
// const API_KEY =

const dropZone = document.getElementById("drop-zone");
const fileInput = document.getElementById("fileInput");

let selectedFile = null;
let transcribedText = "";
let translatedText = "";

// === Drag-and-drop file ===
dropZone.addEventListener("click", () => fileInput.click());
fileInput.addEventListener("change", handleFileSelect);
dropZone.addEventListener("dragover", (e) => {
  e.preventDefault();
  dropZone.classList.add("hover");
});
dropZone.addEventListener("dragleave", () =>
  dropZone.classList.remove("hover")
);
dropZone.addEventListener("drop", handleDrop);

function handleFileSelect(event) {
  selectedFile = event.target.files[0];
  dropZone.innerHTML = `<p>Selected: ${selectedFile.name}</p>`;
}

function handleDrop(event) {
  event.preventDefault();
  dropZone.classList.remove("hover");
  selectedFile = event.dataTransfer.files[0];
  dropZone.innerHTML = `<p>Dropped: ${selectedFile.name}</p>`;
}

// === Transcribe ===
document.getElementById("transcribeBtn").addEventListener("click", async () => {
  if (!selectedFile) return alert("Please select a file.");

  const sourceLang = document.getElementById("sourceLang").value;
  const formData = new FormData();
  formData.append("file", selectedFile);
  formData.append("model_id", "scribe_v1");
  formData.append("tag_audio_events", "true");
  formData.append("language_code", sourceLang);
  formData.append("diarize", "true");

  try {
    const res = await fetch("https://api.elevenlabs.io/v1/speech-to-text", {
      method: "POST",
      headers: { "xi-api-key": API_KEY },
      body: formData,
    });

    const data = await res.json();
    transcribedText = data.text || "[No text returned]";
    document.getElementById("transcriptionText").textContent = transcribedText;
  } catch (err) {
    alert("Transcription failed.");
    console.error(err);
  }
});

// === Translate ===
document.getElementById("translateBtn").addEventListener("click", async () => {
  if (!transcribedText) return alert("Please transcribe the file first.");
  const sourceLang = document.getElementById("sourceLang").value;
  const targetLang = document.getElementById("targetLang").value;

  const translateUrl = `https://www.apertium.org/apy/translate?q=${encodeURIComponent(
    transcribedText
  )}&langpair=${sourceLang}|${targetLang}`;

  try {
    const res = await fetch(translateUrl);
    const data = await res.json();
    translatedText =
      data.responseData?.translatedText || "[Translation failed]";
    document.getElementById("translatedText").textContent = translatedText;
  } catch (err) {
    alert("Translation failed.");
    console.error(err);
  }
});

// === Dub ===
document.getElementById("dubBtn").addEventListener("click", async () => {
  if (!selectedFile) return alert("Please select a file first.");

  const sourceLang = document.getElementById("sourceLang").value || "auto";
  const targetLang = document.getElementById("targetLang").value;

  if (!targetLang) return alert("Please select a target language.");

  const formData = new FormData();
  formData.append("file", selectedFile);
  formData.append("source_lang", sourceLang);
  formData.append("target_lang", targetLang);
  formData.append("name", "My Dubbing Project");
  formData.append("watermark", "true");

  try {
    const res = await fetch("https://api.elevenlabs.io/v1/dubbing", {
      method: "POST",
      headers: {
        "xi-api-key": API_KEY,
      },
      body: formData,
    });

    if (!res.ok) {
      const errorText = await res.text();
      throw new Error(`Dubbing API error: ${res.status} ${errorText}`);
    }

    const data = await res.json();
    const dubbingId = data.dubbing_id;
    document.getElementById("dubStatus").textContent = "Processing...";

    const videoElement = document.getElementById("dubbedVideo");
    videoElement.style.display = "none";

    // Polling for status
    const interval = setInterval(async () => {
      try {
        const statusRes = await fetch(
          `https://api.elevenlabs.io/v1/dubbing/${dubbingId}`,
          {
            headers: { "xi-api-key": API_KEY },
          }
        );

        if (!statusRes.ok) {
          clearInterval(interval);
          document.getElementById("dubStatus").textContent =
            `❌ Status check failed: ${statusRes.status}`;
          return;
        }

        const statusData = await statusRes.json();

        if (statusData.status === "dubbed") {
          clearInterval(interval);
          document.getElementById("dubStatus").textContent = "Dubbing complete ✅";

          if (statusData.download_url) {
            videoElement.src = statusData.download_url;
            videoElement.style.display = "block";
          } else {
            // No direct download_url - fetch media file from endpoint
            try {
              const fileRes = await fetch(
                `https://api.elevenlabs.io/v1/dubbing/${dubbingId}/audio/${targetLang}`,
                {
                  headers: { "xi-api-key": API_KEY },
                }
              );

              if (!fileRes.ok) {
                throw new Error(`Failed to get dubbed media: ${fileRes.statusText}`);
              }

              const blob = await fileRes.blob();
              const url = URL.createObjectURL(blob);

              videoElement.src = url;
              videoElement.style.display = "block";
            } catch (fetchErr) {
              document.getElementById("dubStatus").textContent =
                "❌ Failed to fetch dubbed media.";
              console.error(fetchErr);
            }
          }
        } else if (statusData.status === "failed") {
          clearInterval(interval);
          document.getElementById("dubStatus").textContent =
            "❌ Dubbing failed: " + (statusData.error || "Unknown error");
        } else {
          console.log("Dubbing in progress...");
        }
      } catch (pollErr) {
        clearInterval(interval);
        document.getElementById("dubStatus").textContent =
          "❌ Error during status polling.";
        console.error(pollErr);
      }
    }, 5000);
  } catch (err) {
    alert("Error starting dubbing: " + err.message);
    console.error(err);
  }
});
