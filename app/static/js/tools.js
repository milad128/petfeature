document.addEventListener("DOMContentLoaded", () => {
  const strip = document.getElementById("tools-filter");
  const grid = document.getElementById("tools-grid");
  if (!strip || !grid) return;

  const cards = [...grid.querySelectorAll(".tool-card")];
  const emptyState = document.getElementById("tools-filter-empty");
  const pills = [...strip.querySelectorAll(".filter-pill")];

  strip.addEventListener("click", (e) => {
    const pill = e.target.closest(".filter-pill");
    if (!pill) return;

    pills.forEach((p) => p.classList.toggle("active", p === pill));

    const filter = pill.dataset.filter;
    let visibleCount = 0;
    cards.forEach((card) => {
      const categories = (card.dataset.categories || "").split("|").filter(Boolean);
      const match = filter === "همه" || categories.includes(filter);
      card.hidden = !match;
      if (match) visibleCount += 1;
    });

    if (emptyState) emptyState.hidden = visibleCount > 0;
  });
});
