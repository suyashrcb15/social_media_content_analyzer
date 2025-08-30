
const uploadForm = document.getElementById("uploadForm");
const fileInput = document.getElementById("fileInput");
const dropArea = document.getElementById("drop-area");
const uploadBtn = document.getElementById("uploadBtn");
const loading = document.getElementById("loading");
const extractedTextEl = document.getElementById("extractedText");
const recommendationsEl = document.getElementById("recommendations");
const approachEl = document.getElementById("approach");

const approachText = `I built a lightweight Flask application that accepts PDFs and images, extracts text using PyMuPDF for PDFs and Tesseract OCR for images, and sends the extracted content to an AI service for engagement recommendations. The front-end is a single-page HTML with drag-and-drop upload and clear loading states. The backend provides an endpoint to request AI recommendations (Gemini or local fallback) and includes basic error handling. This solution prioritizes clarity, ease of deployment, and extensibility: you can swap the AI integration for any provider, add user auth, or expand analytics. (200 words max)`;
approachEl.textContent = approachText;

// File preview before upload
const previewImage = document.getElementById("previewImage");
const previewPDF = document.getElementById("previewPDF");
const previewMessage = document.getElementById("previewMessage");

fileInput.addEventListener("change", function () {
  const file = this.files[0];
  if (!file) return;

  const fileURL = URL.createObjectURL(file);

  // Show message
  previewMessage.style.display = "block";

  if (file.type.startsWith("image/")) {
    previewImage.src = fileURL;
    previewImage.style.display = "block";
    previewPDF.style.display = "none";
  } else if (file.type === "application/pdf") {
    previewPDF.src = fileURL;
    previewPDF.style.display = "block";
    previewImage.style.display = "none";
  } else {
    previewImage.style.display = "none";
    previewPDF.style.display = "none";
  }
});


function showLoading(show=true){ if(show){loading.classList.remove("hidden")}else{loading.classList.add("hidden")} }

uploadForm.addEventListener("submit", async (e)=>{
  e.preventDefault();
  const f = fileInput.files[0];
  if(!f){ alert("Please select a file."); return; }
  await uploadAndAnalyze(f);
});

async function uploadAndAnalyze(file){
  showLoading(true);
  extractedTextEl.textContent = "";
  recommendationsEl.innerHTML = "";
  try{
    const fd = new FormData();
    fd.append("file", file);
    const resp = await fetch("/upload", { method:"POST", body: fd });
    const data = await resp.json();

    if(resp.ok){
      extractedTextEl.textContent = data.text || "[No text extracted]";

      // ✅ Engagement + AI in one call
      const analysisResp = await fetch("/analyze_post", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({ text: data.text })
      });
      const analysis = await analysisResp.json();

      // ✅ Update metrics in UI
      document.getElementById("likesCount").textContent = analysis.likes;
      document.getElementById("commentsCount").textContent = analysis.comments;
      document.getElementById("updatedLikesCount").textContent = analysis.updated_likes;
      document.getElementById("updatedCommentsCount").textContent = analysis.updated_comments;

      renderRecommendations(analysis.recommendations);
    } else {
      extractedTextEl.textContent = JSON.stringify(data, null, 2);
    }
  } catch(err){
    extractedTextEl.textContent = "Upload error: " + err.message;
  } finally {
    showLoading(false);
  }
}


function renderRecommendations(obj){
  if(!obj) return;

  if(obj.source === "gemini"){
    const ul = document.createElement("ul");
    (obj.recommendations||[]).forEach(item=>{
      const li = document.createElement("li");
      if(typeof item === "object" && item.aspect && item.suggestion){
        li.innerHTML = `<b>${item.aspect}:</b> ${item.suggestion}`;
      } else {
        li.textContent = item;
      }
      ul.appendChild(li);
    });
    recommendationsEl.appendChild(ul);
  }
  else if(obj.source === "local-fallback"){
    const ul = document.createElement("ul");
    (obj.recommendations||[]).forEach(i=>{
      const li = document.createElement("li");
      li.textContent = i;
      ul.appendChild(li);
    });
    recommendationsEl.appendChild(ul);
  }
  else if(obj.source === "error"){
    recommendationsEl.textContent = "AI call error: " + (obj.error || "unknown");
  }
  else {
    recommendationsEl.textContent = JSON.stringify(obj, null, 2);
  }
}


// drag & drop UX
["dragenter","dragover"].forEach(e=> dropArea.addEventListener(e, ev=>{ ev.preventDefault(); dropArea.classList.add("dragover"); }));
["dragleave","drop"].forEach(e=> dropArea.addEventListener(e, ev=>{ ev.preventDefault(); dropArea.classList.remove("dragover"); }));
dropArea.addEventListener("drop", ev=>{
  const f = ev.dataTransfer.files[0];
  if(f){ fileInput.files = ev.dataTransfer.files; }
});
