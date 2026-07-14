// Lamp toggle — persists state in localStorage
(function () {
  var KEY = "pf-lamp";
  var saved = localStorage.getItem(KEY);
  // Apply saved "off" state immediately (before paint) to avoid flicker
  if (saved === "off") {
    document.documentElement.setAttribute("data-lamp", "off");
  }

  function toggle() {
    var isOff = document.documentElement.getAttribute("data-lamp") === "off";
    if (isOff) {
      document.documentElement.removeAttribute("data-lamp");
      localStorage.setItem(KEY, "on");
    } else {
      document.documentElement.setAttribute("data-lamp", "off");
      localStorage.setItem(KEY, "off");
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    // Header lamp button
    var headerBtn = document.getElementById("lamp-toggle");
    if (headerBtn) headerBtn.addEventListener("click", toggle);

    // Desk lamp button (library page)
    var deskBtn = document.getElementById("lamp-toggle-desk");
    if (deskBtn) deskBtn.addEventListener("click", toggle);

    // Shelf lamp button (book detail page)
    var shelfBtn = document.getElementById("lamp-toggle-shelf");
    if (shelfBtn) shelfBtn.addEventListener("click", toggle);

    // Side table lamp button (blog page)
    var blogBtn = document.getElementById("lamp-toggle-blog");
    if (blogBtn) blogBtn.addEventListener("click", toggle);

    // Side table lamp button (tools page)
    var toolsBtn = document.getElementById("lamp-toggle-tools");
    if (toolsBtn) toolsBtn.addEventListener("click", toggle);

    // Shelf lamp button (home page)
    var homeBtn = document.getElementById("lamp-toggle-home");
    if (homeBtn) homeBtn.addEventListener("click", toggle);
  });
})();
