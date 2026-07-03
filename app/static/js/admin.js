document.addEventListener("DOMContentLoaded", () => {
  initChipInputs();
  initCoverUpload();
  initDownloadUpload();
  initStatusSwitch();
  initShowInLibrarySwitch();
  initCategoryPicker();
  initMediaLinkRows();
  initReferredBooks();
  initLinkRows();
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

function initRichTextEditors() {
  document.querySelectorAll("[data-richtext]").forEach((wrap) => {
    const hidden = document.getElementById(wrap.dataset.target);
    const editor = wrap.querySelector(".richtext-editor");
    if (!hidden || !editor) return;

    const initial = hidden.value || "";
    editor.innerHTML = initial.includes("<")
      ? initial
      : escapeHtml(initial).replace(/\n/g, "<br>");

    editor.addEventListener("input", () => {
      hidden.value = editor.innerHTML;
    });

    wrap.querySelectorAll(".richtext-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        editor.focus();
        const command = btn.dataset.command;
        if (command === "createLink") {
          const url = window.prompt("آدرس لینک را وارد کنید:", "https://");
          if (!url) return;
          document.execCommand("createLink", false, url);
        } else if (command === "formatBlock") {
          document.execCommand("formatBlock", false, btn.dataset.value);
        } else {
          document.execCommand(command, false, null);
        }
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
  document.querySelectorAll("form[data-admin-form]").forEach((form) => {
    form.addEventListener("submit", () => {
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

      syncRichTextEditors();
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
