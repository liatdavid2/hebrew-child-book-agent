const form = document.getElementById("bookForm");
const pagesList = document.getElementById("pagesList");
const addPageBtn = document.getElementById("addPageBtn");
const submitBtn = document.getElementById("submitBtn");
const statusText = document.getElementById("statusText");
const preview = document.getElementById("preview");
const downloadLink = document.getElementById("downloadLink");

let pageCount = 0;

function addPage(text = "") {
  pageCount += 1;
  const wrapper = document.createElement("div");
  wrapper.className = "page-input";
  wrapper.dataset.page = String(pageCount);
  wrapper.innerHTML = `
    <div class="page-input-header">
      <strong>עמוד ${pageCount}</strong>
      <button type="button" class="remove-page-btn">מחיקה</button>
    </div>
    <textarea rows="3" class="page-text" placeholder="מלל עמוד ${pageCount}">${text}</textarea>
  `;

  wrapper.querySelector(".remove-page-btn").addEventListener("click", () => {
    wrapper.remove();
    renumberPages();
  });

  pagesList.appendChild(wrapper);
}

function renumberPages() {
  const items = Array.from(document.querySelectorAll(".page-input"));
  pageCount = items.length;
  items.forEach((item, index) => {
    const n = index + 1;
    item.dataset.page = String(n);
    item.querySelector("strong").textContent = `עמוד ${n}`;
    item.querySelector("textarea").placeholder = `מלל עמוד ${n}`;
  });
}

function collectPayload() {
  const coverText = document.getElementById("coverText").value.trim();
  const childAge = document.getElementById("childAge").value.trim() || "4-7";
  const styleInstructions = document.getElementById("styleInstructions").value.trim();

  const pages = Array.from(document.querySelectorAll(".page-input"))
    .map((item, index) => ({
      page_number: index + 1,
      text: item.querySelector("textarea").value.trim(),
    }))
    .filter((page) => page.text.length > 0);

  return {
    cover_text: coverText,
    child_age: childAge,
    style_instructions: styleInstructions,
    pages,
  };
}

function esc(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function renderPreview(book, coverUrl) {
  const pagesHtml = (book.pages || []).map((page) => `
    <article class="book-page">
      <img src="${esc(page.preview_image_url || "")}" alt="עמוד ${esc(page.page_number)}" />
      <div class="page-number">עמוד ${esc(page.page_number)}</div>
      <p>${esc(page.final_text)}</p>
    </article>
  `).join("");

  preview.className = "preview";
  preview.innerHTML = `
    <article class="book-cover">
      <img src="${esc(coverUrl || "")}" alt="שער הספר" />
      <h3>${esc(book.title)}</h3>
      <p>${esc(book.subtitle || "")}</p>
      <p>${esc(book.cover_text || "")}</p>
    </article>
    ${pagesHtml}
  `;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const payload = collectPayload();
  if (!payload.cover_text) {
    statusText.textContent = "צריך למלא מלל שער.";
    return;
  }
  if (payload.pages.length === 0) {
    statusText.textContent = "צריך לפחות עמוד אחד.";
    return;
  }

  submitBtn.disabled = true;
  statusText.textContent = "המערכת כותבת ספר, מייצרת תמונות ובונה HTML...";
  downloadLink.classList.add("is-hidden");

  try {
    const response = await fetch("/api/generate-book", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || "Generation failed");
    }

    renderPreview(data.book, data.cover_preview_url);
    downloadLink.href = data.download_url;
    downloadLink.classList.remove("is-hidden");
    statusText.textContent = "הספר מוכן. אפשר להוריד ZIP של ספר HTML עם התמונות.";
  } catch (error) {
    statusText.textContent = `שגיאה: ${error.message}`;
  } finally {
    submitBtn.disabled = false;
  }
});

addPageBtn.addEventListener("click", () => addPage());

document.getElementById("coverText").value = "ילדה חצי חתולה";
addPage("ילדה חצי חתולה הלכה לבריכה.");
addPage("הילדים שאלו למה היא נולדה ככה.");
addPage("היא הסבירה שאבא שלה היה חתול ואמא שלה בת אדם.");
