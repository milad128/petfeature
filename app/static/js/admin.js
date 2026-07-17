document.addEventListener("DOMContentLoaded", () => {
  initChipInputs();
  initCoverUpload();
  initDownloadUpload();
  initStatusSwitch();
  initShowInLibrarySwitch();
  initFeaturedSwitch();
  initCategoryPicker();
  initMediaLinkRows();
  initReferredBooks();
  initLinkRows();
  initToolFileRows();
  initItemPicker({
    selectedId: "related-books-selected",
    hiddenId: "related-books-hidden",
    addBtnId: "add-related-book-btn",
    modalId: "related-books-modal",
    modalCloseId: "related-books-modal-close",
    modalListId: "related-books-modal-list",
    searchId: "related-books-search",
  });
  initItemPicker({
    selectedId: "related-posts-selected",
    hiddenId: "related-posts-hidden",
    addBtnId: "add-related-post-btn",
    modalId: "related-posts-modal",
    modalCloseId: "related-posts-modal-close",
    modalListId: "related-posts-modal-list",
    searchId: "related-posts-search",
  });
  initRichTextEditors();
  initDeleteForms();
  syncFormsBeforeSubmit();
});

function initCoverUpload() {
  const input = document.getElementById("cover-file");
  const preview = document.getElementById("cover-preview");
  const wrap = document.getElementById("cover-preview-wrap");
  const placeholder = document.getElementById("cover-preview-placeholder");
  if (!input || !preview) return;

  input.addEventListener("change", () => {
    const file = input.files?.[0];
    if (!file) return;
    preview.src = URL.createObjectURL(file);
    preview.hidden = false;
    wrap?.classList.remove("is-empty");
    if (placeholder) placeholder.hidden = true;
  });
}

function initDownloadUpload() {
  const input = document.getElementById("download-file");
  const current = document.getElementById("download-current");
  if (!input) return;

  input.addEventListener("change", () => {
    const file = input.files?.[0];
    if (!file || !current) return;
    current.hidden = false;
    current.classList.remove("is-empty");
    current.innerHTML = `<span dir="ltr">${escapeHtml(file.name)}</span> <span class="form-hint">(فایل جدید — پس از ذخیره جایگزین می‌شود)</span>`;
  });
}

function initChipInputs() {
  document.querySelectorAll(".tag-input-box[data-hidden]").forEach((box) => {
    const hiddenId = box.dataset.hidden;
    const hidden = document.getElementById(hiddenId);
    const input = box.querySelector('input[type="text"]');

    box.addEventListener("click", () => input?.focus());

    input?.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        const value = input.value.trim();
        if (!value) return;
        addChip(box, input, value);
        input.value = "";
        syncChipHidden(box, hidden);
      }
    });

    box.querySelectorAll(".tag-chip button").forEach((btn) => {
      btn.addEventListener("click", () => {
        btn.closest(".tag-chip")?.remove();
        syncChipHidden(box, hidden);
      });
    });
  });
}

function addChip(box, input, value) {
  const chip = document.createElement("span");
  chip.className = "tag-chip";
  chip.innerHTML = `${escapeHtml(value)} <button type="button" aria-label="حذف">×</button>`;
  chip.querySelector("button")?.addEventListener("click", () => {
    chip.remove();
    const hidden = document.getElementById(box.dataset.hidden);
    syncChipHidden(box, hidden);
  });
  box.insertBefore(chip, input);
}

function syncChipHidden(box, hidden) {
  if (!hidden) return;
  const values = [...box.querySelectorAll(".tag-chip")].map((chip) =>
    chip.childNodes[0].textContent.trim()
  );
  hidden.value = JSON.stringify(values);
}

function initStatusSwitch() {
  const toggle = document.getElementById("status-switch");
  const hidden = document.getElementById("status-hidden");
  const hint = document.getElementById("status-hint");
  if (!toggle || !hidden) return;

  toggle.addEventListener("click", () => {
    const on = toggle.classList.toggle("on");
    hidden.value = on ? "published" : "draft";
    toggle.setAttribute("aria-checked", on ? "true" : "false");
    if (hint) {
      hint.textContent = on
        ? "منتشرشده — روی سایت قابل مشاهده است"
        : "پیش‌نویس — فقط برای شما قابل مشاهده است";
    }
  });
}

function initShowInLibrarySwitch() {
  const toggle = document.getElementById("show-in-library-switch");
  const hidden = document.getElementById("show-in-library-hidden");
  const hint = document.getElementById("show-in-library-hint");
  if (!toggle || !hidden) return;

  toggle.addEventListener("click", () => {
    const on = toggle.classList.toggle("on");
    hidden.value = on ? "true" : "false";
    toggle.setAttribute("aria-checked", on ? "true" : "false");
    if (hint) {
      hint.textContent = on
        ? "در لیست کتابخانه نمایش داده می‌شود"
        : "در لیست کتابخانه پنهان است — فقط با لینک مستقیم یا ارجاع قابل مشاهده است";
    }
  });
}

function initFeaturedSwitch() {
  const toggle = document.getElementById("is-featured-switch");
  const hidden = document.getElementById("is-featured-hidden");
  const hint = document.getElementById("is-featured-hint");
  if (!toggle || !hidden) return;

  toggle.addEventListener("click", () => {
    const on = toggle.classList.toggle("on");
    hidden.value = on ? "true" : "false";
    toggle.setAttribute("aria-checked", on ? "true" : "false");
    if (hint) {
      hint.textContent = on
        ? "در کارت بزرگ بالای بلاگ نمایش داده می‌شود"
        : "در لیست عادی نمایش داده می‌شود";
    }
  });
}

function initCategoryPicker() {
  const picker = document.getElementById("category-picker");
  const hidden = document.getElementById("category-ids-hidden");
  if (!picker || !hidden) return;

  picker.querySelectorAll('input[type="checkbox"]').forEach((checkbox) => {
    checkbox.addEventListener("change", () => syncCategoryIdsHidden(picker, hidden));
  });
}

function syncCategoryIdsHidden(picker, hidden) {
  const ids = [...picker.querySelectorAll('input[type="checkbox"]:checked')]
    .map((el) => parseInt(el.value, 10))
    .filter((id) => !Number.isNaN(id));
  hidden.value = JSON.stringify(ids);
}

function initMediaLinkRows() {
  const container = document.getElementById("media-link-rows");
  const addBtn = document.getElementById("add-media-link-btn");
  const hidden = document.getElementById("media-links-hidden");
  if (!container || !hidden) return;

  container.querySelectorAll(".media-link-row").forEach((row) => bindMediaLinkRow(row, container, hidden));

  addBtn?.addEventListener("click", () => {
    const row = createMediaLinkRow();
    container.appendChild(row);
    bindMediaLinkRow(row, container, hidden);
    syncMediaLinksHidden(container, hidden);
  });
}

function createMediaLinkRow() {
  const row = document.createElement("div");
  row.className = "resource-row media-link-row";
  row.innerHTML = `
    <select class="form-control" aria-label="نوع">
      <option value="video" selected>ویدیو</option>
      <option value="podcast">پادکست</option>
    </select>
    <input class="form-control" type="text" placeholder="عنوان">
    <input class="form-control" type="text" placeholder="آدرس URL" dir="ltr">
    <button type="button" class="btn btn-ghost btn-icon remove-row" aria-label="حذف">🗑</button>
  `;
  return row;
}

function bindMediaLinkRow(row, container, hidden) {
  row.querySelectorAll("select, input").forEach((el) => {
    el.addEventListener("input", () => syncMediaLinksHidden(container, hidden));
    el.addEventListener("change", () => syncMediaLinksHidden(container, hidden));
  });
  row.querySelector(".remove-row")?.addEventListener("click", () => {
    row.remove();
    syncMediaLinksHidden(container, hidden);
  });
}

function syncMediaLinksHidden(container, hidden) {
  const links = [...container.querySelectorAll(".media-link-row")]
    .map((row) => {
      const textInputs = row.querySelectorAll('input[type="text"]');
      return {
        type: row.querySelector("select")?.value || "video",
        title: textInputs[0]?.value.trim() || "",
        url: textInputs[1]?.value.trim() || "",
      };
    })
    .filter((link) => link.url);
  hidden.value = JSON.stringify(links);
}

function initReferredBooks() {
  const selected = document.getElementById("referred-books-selected");
  const hidden = document.getElementById("referred-books-hidden");
  const addBtn = document.getElementById("add-referred-book-btn");
  const modal = document.getElementById("referred-books-modal");
  const modalClose = document.getElementById("referred-books-modal-close");
  const modalList = document.getElementById("referred-books-modal-list");
  const searchInput = document.getElementById("referred-books-search");
  if (!selected || !hidden || !addBtn || !modal || !modalList) return;

  const updateModalVisibility = () => {
    const selectedIds = new Set(
      [...selected.querySelectorAll(".referred-book-chip")].map((chip) => chip.dataset.bookId)
    );
    const query = (searchInput?.value || "").trim().toLowerCase();
    modalList.querySelectorAll(".modal-list-item").forEach((item) => {
      const isSelected = selectedIds.has(item.dataset.bookId);
      const matchesQuery =
        !query ||
        item.dataset.bookTitle.toLowerCase().includes(query) ||
        (item.dataset.bookAuthor || "").toLowerCase().includes(query);
      item.hidden = isSelected || !matchesQuery;
    });
  };

  const bindRemove = (btn) => {
    btn.addEventListener("click", () => {
      btn.closest(".referred-book-chip")?.remove();
      syncReferredBooksHidden(selected, hidden);
      updateModalVisibility();
    });
  };

  const addChip = (id, title, author) => {
    const chip = document.createElement("div");
    chip.className = "referred-book-chip";
    chip.dataset.bookId = id;
    chip.innerHTML = `
      <span>
        <span class="referred-book-chip-title">${escapeHtml(title)}</span>
        ${author ? `<small>${escapeHtml(author)}</small>` : ""}
      </span>
      <button type="button" class="remove-referred-book" aria-label="حذف">×</button>
    `;
    selected.appendChild(chip);
    bindRemove(chip.querySelector(".remove-referred-book"));
  };

  const openModal = () => {
    modal.hidden = false;
    updateModalVisibility();
    searchInput?.focus();
  };
  const closeModal = () => {
    modal.hidden = true;
    if (searchInput) searchInput.value = "";
  };

  addBtn.addEventListener("click", openModal);
  modalClose?.addEventListener("click", closeModal);
  modal.addEventListener("click", (e) => {
    if (e.target === modal) closeModal();
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !modal.hidden) closeModal();
  });

  searchInput?.addEventListener("input", updateModalVisibility);

  modalList.querySelectorAll(".modal-list-item").forEach((item) => {
    item.addEventListener("click", () => {
      addChip(item.dataset.bookId, item.dataset.bookTitle, item.dataset.bookAuthor || "");
      syncReferredBooksHidden(selected, hidden);
      updateModalVisibility();
    });
  });

  selected.querySelectorAll(".remove-referred-book").forEach(bindRemove);

  syncReferredBooksHidden(selected, hidden);
}

function syncReferredBooksHidden(container, hidden) {
  const ids = [...container.querySelectorAll(".referred-book-chip")]
    .map((chip) => parseInt(chip.dataset.bookId, 10))
    .filter((id) => !Number.isNaN(id));
  hidden.value = JSON.stringify(ids);
}

function initToolFileRows() {
  const container = document.getElementById("tool-file-rows");
  const addBtn = document.getElementById("add-tool-file-btn");
  const hidden = document.getElementById("tool-files-hidden");
  if (!container || !hidden) return;

  container.querySelectorAll(".tool-file-row").forEach((row) => bindToolFileRow(row, container, hidden));

  addBtn?.addEventListener("click", () => {
    const row = createToolFileRow();
    container.appendChild(row);
    bindToolFileRow(row, container, hidden);
    syncToolFilesHidden(container, hidden);
  });

  syncToolFilesHidden(container, hidden);
}

function createToolFileRow() {
  const row = document.createElement("div");
  row.className = "resource-row tool-file-row";
  row.innerHTML = `
    <input class="form-control" type="text" placeholder="نام نسخه (مثلاً نسخه‌ی PDF)">
    <input class="form-control" type="text" placeholder="توضیح کوتاه">
    <input class="form-control" type="file" name="tool_file_uploads" accept=".pdf,.xlsx,.docx,.pptx,.csv">
    <button type="button" class="btn btn-ghost btn-icon remove-row" aria-label="حذف">🗑</button>
  `;
  return row;
}

function bindToolFileRow(row, container, hidden) {
  row.querySelectorAll('input[type="text"]').forEach((el) => {
    el.addEventListener("input", () => syncToolFilesHidden(container, hidden));
  });
  row.querySelector(".remove-row")?.addEventListener("click", () => {
    row.remove();
    syncToolFilesHidden(container, hidden);
  });
}

function syncToolFilesHidden(container, hidden) {
  const files = [...container.querySelectorAll(".tool-file-row")]
    .map((row) => {
      const textInputs = row.querySelectorAll('input[type="text"]');
      return {
        name: textInputs[0]?.value.trim() || "",
        description: textInputs[1]?.value.trim() || "",
        file: row.dataset.existingFile || "",
      };
    })
    .filter((file) => file.name);
  hidden.value = JSON.stringify(files);
}

function initItemPicker({ selectedId, hiddenId, addBtnId, modalId, modalCloseId, modalListId, searchId }) {
  const selected = document.getElementById(selectedId);
  const hidden = document.getElementById(hiddenId);
  const addBtn = document.getElementById(addBtnId);
  const modal = document.getElementById(modalId);
  const modalClose = document.getElementById(modalCloseId);
  const modalList = document.getElementById(modalListId);
  const searchInput = document.getElementById(searchId);
  if (!selected || !hidden || !addBtn || !modal || !modalList) return;

  const updateModalVisibility = () => {
    const selectedIds = new Set(
      [...selected.querySelectorAll(".referred-book-chip")].map((chip) => chip.dataset.itemId)
    );
    const query = (searchInput?.value || "").trim().toLowerCase();
    modalList.querySelectorAll(".modal-list-item").forEach((item) => {
      const isSelected = selectedIds.has(item.dataset.itemId);
      const matchesQuery =
        !query ||
        item.dataset.itemTitle.toLowerCase().includes(query) ||
        (item.dataset.itemSubtitle || "").toLowerCase().includes(query);
      item.hidden = isSelected || !matchesQuery;
    });
  };

  const syncHidden = () => {
    const ids = [...selected.querySelectorAll(".referred-book-chip")]
      .map((chip) => parseInt(chip.dataset.itemId, 10))
      .filter((id) => !Number.isNaN(id));
    hidden.value = JSON.stringify(ids);
  };

  const bindRemove = (btn) => {
    btn.addEventListener("click", () => {
      btn.closest(".referred-book-chip")?.remove();
      syncHidden();
      updateModalVisibility();
    });
  };

  const addChip = (id, title, subtitle) => {
    const chip = document.createElement("div");
    chip.className = "referred-book-chip";
    chip.dataset.itemId = id;
    chip.innerHTML = `
      <span>
        <span class="referred-book-chip-title">${escapeHtml(title)}</span>
        ${subtitle ? `<small>${escapeHtml(subtitle)}</small>` : ""}
      </span>
      <button type="button" class="remove-referred-book" aria-label="حذف">×</button>
    `;
    selected.appendChild(chip);
    bindRemove(chip.querySelector(".remove-referred-book"));
  };

  const openModal = () => {
    modal.hidden = false;
    updateModalVisibility();
    searchInput?.focus();
  };
  const closeModal = () => {
    modal.hidden = true;
    if (searchInput) searchInput.value = "";
  };

  addBtn.addEventListener("click", openModal);
  modalClose?.addEventListener("click", closeModal);
  modal.addEventListener("click", (e) => {
    if (e.target === modal) closeModal();
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !modal.hidden) closeModal();
  });

  searchInput?.addEventListener("input", updateModalVisibility);

  modalList.querySelectorAll(".modal-list-item").forEach((item) => {
    item.addEventListener("click", () => {
      addChip(item.dataset.itemId, item.dataset.itemTitle, item.dataset.itemSubtitle || "");
      syncHidden();
      updateModalVisibility();
    });
  });

  selected.querySelectorAll(".remove-referred-book").forEach(bindRemove);

  syncHidden();
}

function initLinkRows() {
  const container = document.getElementById("link-rows");
  const addBtn = document.getElementById("add-link-btn");
  const hidden = document.getElementById("links-hidden");
  if (!container || !hidden) return;

  container.querySelectorAll(".resource-row").forEach((row) => bindAboutLinkRow(row, container, hidden));

  addBtn?.addEventListener("click", () => {
    const row = createAboutLinkRow();
    container.appendChild(row);
    bindAboutLinkRow(row, container, hidden);
    syncAboutLinksHidden(container, hidden);
  });

  syncAboutLinksHidden(container, hidden);
}

function createAboutLinkRow() {
  const row = document.createElement("div");
  row.className = "resource-row";
  row.style.gridTemplateColumns = "1fr 1fr auto";
  row.innerHTML = `
    <input class="form-control" type="text" placeholder="عنوان (مثلاً لینکدین)">
    <input class="form-control" type="text" placeholder="آدرس URL" dir="ltr">
    <button type="button" class="btn btn-ghost btn-icon remove-row" aria-label="حذف لینک">🗑</button>
  `;
  return row;
}

function bindAboutLinkRow(row, container, hidden) {
  row.querySelectorAll("input").forEach((el) => {
    el.addEventListener("input", () => syncAboutLinksHidden(container, hidden));
  });
  row.querySelector(".remove-row")?.addEventListener("click", () => {
    row.remove();
    syncAboutLinksHidden(container, hidden);
  });
}

function syncAboutLinksHidden(container, hidden) {
  const links = [...container.querySelectorAll(".resource-row")]
    .map((row) => ({
      title: row.querySelectorAll("input")[0]?.value.trim() || "",
      url: row.querySelectorAll("input")[1]?.value.trim() || "",
    }))
    .filter((link) => link.title);
  hidden.value = JSON.stringify(links);
}

// ── Rich text editor helpers ─────────────────────────────────────────────────

function _rtBuildVideoEmbed(url) {
  url = url.trim();
  // YouTube
  const ytMatch = url.match(
    /(?:youtube\.com\/(?:watch\?v=|embed\/)|youtu\.be\/)([a-zA-Z0-9_-]{11})/
  );
  if (ytMatch) {
    return (
      `<div class="richtext-video">` +
      `<iframe src="https://www.youtube.com/embed/${ytMatch[1]}" ` +
      `frameborder="0" allowfullscreen loading="lazy" ` +
      `allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture">` +
      `</iframe></div>`
    );
  }
  // Vimeo
  const vimeoMatch = url.match(/vimeo\.com\/(\d+)/);
  if (vimeoMatch) {
    return (
      `<div class="richtext-video">` +
      `<iframe src="https://player.vimeo.com/video/${vimeoMatch[1]}" ` +
      `frameborder="0" allowfullscreen loading="lazy">` +
      `</iframe></div>`
    );
  }
  // Direct video file
  if (/\.(mp4|webm|ogg)(\?|$)/i.test(url)) {
    return (
      `<div class="richtext-video">` +
      `<video controls style="width:100%;border-radius:8px;"><source src="${url}"></video>` +
      `</div>`
    );
  }
  // Generic iframe fallback
  return (
    `<div class="richtext-video">` +
    `<iframe src="${url}" frameborder="0" allowfullscreen loading="lazy"></iframe>` +
    `</div>`
  );
}

function _rtBuildTable(rows, cols) {
  let html =
    `<table style="width:100%;border-collapse:collapse;margin:1rem 0;direction:rtl;">`;
  for (let r = 0; r < rows; r++) {
    html += "<tr>";
    for (let c = 0; c < cols; c++) {
      const tag = r === 0 ? "th" : "td";
      const content =
        r === 0
          ? `عنوان ${_rtFaDigits(c + 1)}`
          : `ردیف ${_rtFaDigits(r)} · ستون ${_rtFaDigits(c + 1)}`;
      html +=
        `<${tag} style="border:1px solid var(--border,#3a3026);` +
        `padding:8px 12px;text-align:right;">${content}</${tag}>`;
    }
    html += "</tr>";
  }
  html += "</table>";
  return html;
}

function _rtFaDigits(n) {
  return String(n).replace(/[0-9]/g, (d) => "۰۱۲۳۴۵۶۷۸۹"[+d]);
}

// ── Main initialiser ─────────────────────────────────────────────────────────

function initRichTextEditors() {
  document.querySelectorAll("[data-richtext]").forEach((wrap) => {
    const hidden = document.getElementById(wrap.dataset.target);
    const editor = wrap.querySelector(".richtext-editor");
    if (!hidden || !editor) return;

    // Populate editor from the hidden textarea on load
    const initial = hidden.value || "";
    editor.innerHTML = initial.includes("<")
      ? initial
      : escapeHtml(initial).replace(/\n/g, "<br>");

    editor.addEventListener("input", () => {
      hidden.value = editor.innerHTML;
    });

    // ── Image upload ───────────────────────────────────────────────────────
    const imageInput = wrap.querySelector(".richtext-image-input");
    let _savedRange = null; // used to restore cursor after image/select dialogs

    if (imageInput) {
      imageInput.addEventListener("change", async () => {
        const file = imageInput.files[0];
        imageInput.value = "";
        if (!file) return;

        editor.focus();
        if (_savedRange) {
          const sel = window.getSelection();
          sel.removeAllRanges();
          sel.addRange(_savedRange);
          _savedRange = null;
        }

        const placeholder = document.createElement("span");
        placeholder.textContent = "…در حال آپلود…";
        placeholder.style.color = "var(--muted)";
        placeholder.style.fontSize = ".85rem";
        document.execCommand("insertHTML", false, placeholder.outerHTML);

        try {
          const fd = new FormData();
          fd.append("file", file);
          const resp = await fetch("/admin/upload/image/", { method: "POST", body: fd });
          const data = await resp.json();

          if (data.url) {
            const img =
              `<img src="${data.url}" ` +
              `style="max-width:100%;height:auto;border-radius:6px;margin:8px 0;" alt="">`;
            hidden.value = editor.innerHTML.replace(placeholder.outerHTML, img);
            editor.innerHTML = hidden.value;
          } else {
            hidden.value = editor.innerHTML.replace(placeholder.outerHTML, "");
            editor.innerHTML = hidden.value;
            alert(data.error || "آپلود تصویر ناموفق بود.");
          }
        } catch {
          hidden.value = editor.innerHTML.replace(placeholder.outerHTML, "");
          editor.innerHTML = hidden.value;
          alert("خطا در آپلود تصویر. اتصال اینترنت را بررسی کنید.");
        }
        hidden.value = editor.innerHTML;
      });
    }

    // ── Toolbar buttons ────────────────────────────────────────────────────
    wrap.querySelectorAll(".richtext-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        const command = btn.dataset.command;

        if (command === "insertImage") {
          // Save cursor position before file picker steals focus
          const sel = window.getSelection();
          if (sel && sel.rangeCount > 0) _savedRange = sel.getRangeAt(0).cloneRange();
          if (imageInput) imageInput.click();
          return;
        }

        if (command === "toggleFullscreen") {
          wrap.classList.toggle("richtext--fullscreen");
          btn.title = wrap.classList.contains("richtext--fullscreen")
            ? "خروج از تمام‌صفحه"
            : "تمام‌صفحه";
          return;
        }

        editor.focus();

        if (command === "createLink") {
          const url = window.prompt("آدرس لینک را وارد کنید:", "https://");
          if (!url) return;
          document.execCommand("createLink", false, url);

        } else if (command === "insertVideo") {
          const url = window.prompt(
            "آدرس ویدیو (YouTube, Vimeo, mp4):",
            "https://www.youtube.com/watch?v="
          );
          if (!url) return;
          document.execCommand("insertHTML", false, _rtBuildVideoEmbed(url));

        } else if (command === "insertTable") {
          const rows = parseInt(window.prompt("تعداد ردیف (شامل سرستون):", "3"), 10) || 3;
          const cols = parseInt(window.prompt("تعداد ستون:", "3"), 10) || 3;
          document.execCommand(
            "insertHTML",
            false,
            _rtBuildTable(
              Math.min(Math.max(rows, 1), 20),
              Math.min(Math.max(cols, 1), 10)
            )
          );

        } else if (command === "insertHorizontalRule") {
          document.execCommand("insertHTML", false, "<hr>");

        } else if (command === "formatBlock" && btn.dataset.value) {
          document.execCommand("formatBlock", false, btn.dataset.value);

        } else {
          document.execCommand(command, false, null);
        }

        hidden.value = editor.innerHTML;
      });
    });

    // ── Selects: save selection on mousedown, restore on change ───────────
    // (Selects steal focus when their dropdown opens, so we snapshot beforehand)
    function _attachSelect(selector, execFn) {
      const sel = wrap.querySelector(selector);
      if (!sel) return;
      sel.addEventListener("mousedown", () => {
        const s = window.getSelection();
        if (s && s.rangeCount > 0) _savedRange = s.getRangeAt(0).cloneRange();
      });
      sel.addEventListener("change", () => {
        if (!sel.value) return;
        editor.focus();
        if (_savedRange) {
          const s = window.getSelection();
          s.removeAllRanges();
          s.addRange(_savedRange);
          _savedRange = null;
        }
        execFn(sel.value);
        hidden.value = editor.innerHTML;
        sel.value = "";
      });
    }

    _attachSelect(".richtext-block-select", (v) =>
      document.execCommand("formatBlock", false, v)
    );
    _attachSelect(".richtext-font-select", (v) =>
      document.execCommand("fontName", false, v)
    );
    _attachSelect(".richtext-size-select", (v) =>
      document.execCommand("fontSize", false, v)
    );

    // ── Color inputs (foreColor + hiliteColor) ────────────────────────────
    wrap.querySelectorAll(".richtext-color-input").forEach((colorInput) => {
      colorInput.addEventListener("input", () => {
        editor.focus();
        document.execCommand(colorInput.dataset.command, false, colorInput.value);
        hidden.value = editor.innerHTML;
      });
    });
  });
}

function syncRichTextEditors() {
  document.querySelectorAll("[data-richtext]").forEach((wrap) => {
    const hidden = document.getElementById(wrap.dataset.target);
    const editor = wrap.querySelector(".richtext-editor");
    if (hidden && editor) hidden.value = editor.innerHTML;
  });
}

function initDeleteForms() {
  document.querySelectorAll("[data-delete-form]").forEach((form) => {
    form.addEventListener("submit", (e) => {
      const message = form.getAttribute("data-confirm") || "آیا مطمئن هستید؟";
      if (!window.confirm(message)) {
        e.preventDefault();
      }
    });
  });
}

function syncFormsBeforeSubmit() {
  document.querySelectorAll("form").forEach((form) => {
    form.addEventListener("submit", () => {
      if (!form.hasAttribute("data-admin-form") && !form.querySelector("[data-richtext]")) return;

      if (form.hasAttribute("data-admin-form")) {
        document.querySelectorAll(".tag-input-box[data-hidden]").forEach((box) => {
          const hidden = document.getElementById(box.dataset.hidden);
          syncChipHidden(box, hidden);
        });

        const mediaContainer = document.getElementById("media-link-rows");
        const mediaHidden = document.getElementById("media-links-hidden");
        if (mediaContainer && mediaHidden) syncMediaLinksHidden(mediaContainer, mediaHidden);

        const referredSelected = document.getElementById("referred-books-selected");
        const referredHidden = document.getElementById("referred-books-hidden");
        if (referredSelected && referredHidden) syncReferredBooksHidden(referredSelected, referredHidden);

        const categoryPicker = document.getElementById("category-picker");
        const categoryHidden = document.getElementById("category-ids-hidden");
        if (categoryPicker && categoryHidden) syncCategoryIdsHidden(categoryPicker, categoryHidden);

        const linkContainer = document.getElementById("link-rows");
        const linksHidden = document.getElementById("links-hidden");
        if (linkContainer && linksHidden) syncAboutLinksHidden(linkContainer, linksHidden);

        const toolFileContainer = document.getElementById("tool-file-rows");
        const toolFilesHidden = document.getElementById("tool-files-hidden");
        if (toolFileContainer && toolFilesHidden) syncToolFilesHidden(toolFileContainer, toolFilesHidden);
      }

      if (form.querySelector("[data-richtext]")) syncRichTextEditors();
    });
  });
}

function escapeHtml(text) {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
