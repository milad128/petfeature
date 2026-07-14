document.addEventListener("DOMContentLoaded", () => {
  initStarHoverPreview();
  initCopyLinkButtons();
});

function initStarHoverPreview() {
  const form = document.getElementById("star-form");
  if (!form) return;
  const buttons = [...form.querySelectorAll(".bd2-star-btn")]; // DOM order: 1,2,3,4,5

  const paint = (level) => {
    buttons.forEach((btn) => {
      const value = parseInt(btn.value, 10);
      btn.classList.toggle("filled", level > 0 && value <= level);
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
