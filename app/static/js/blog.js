document.addEventListener("DOMContentLoaded", () => {
  initStarHoverPreview();
  initCopyLinkButtons();
});

function initStarHoverPreview() {
  const form = document.getElementById("star-form");
  if (!form) return;
  const buttons = [...form.querySelectorAll(".star-btn")]; // DOM order: 5,4,3,2,1

  const paint = (level) => {
    buttons.forEach((btn) => {
      const value = parseInt(btn.value, 10);
      btn.classList.toggle("is-hover", level > 0 && value <= level);
    });
  };

  buttons.forEach((btn) => {
    btn.addEventListener("mouseenter", () => paint(parseInt(btn.value, 10)));
  });
  form.addEventListener("mouseleave", () => paint(0));
}

function initCopyLinkButtons() {
  document.querySelectorAll("[data-copy-link]").forEach((btn) => {
    const originalLabel = btn.textContent;
    btn.addEventListener("click", async () => {
      const url = btn.dataset.copyLink;
      try {
        await navigator.clipboard.writeText(url);
      } catch (e) {
        return;
      }
      btn.textContent = "کپی شد ✓";
      setTimeout(() => {
        btn.textContent = originalLabel;
      }, 1800);
    });
  });
}
