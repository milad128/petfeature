(function () {
  var current = document.body.getAttribute("data-alt") || "";
  var items = [
    ["apm-map-alt-1-vertical.html", "۱ خط عمودی"],
    ["apm-map-alt-2-gantt.html", "۲ گانت"],
    ["apm-map-alt-3-grid.html", "۳ کارت"],
    ["apm-map-alt-4-metro.html", "۴ مترو"],
    ["apm-map-alt-5-swimlanes.html", "۵ شنا"],
    ["apm-map-alt-6-stepper.html", "۶ پله"],
    ["apm-map-alt-7-calendar.html", "۷ تقویم"],
    ["apm-map-alt-8-path.html", "۸ مسیر"],
    ["apm-map-alt-9-accordion.html", "۹ آکاردئون"],
    ["apm-map-alt-10-radial.html", "۱۰ شعاعی"],
  ];
  var wrap = document.querySelector(".proto-index-inner");
  if (!wrap) return;
  var links = document.createElement("span");
  links.className = "proto-nav-links";
  items.forEach(function (item) {
    var a = document.createElement("a");
    a.href = item[0];
    a.textContent = item[1];
    if (item[0].indexOf("alt-" + current + "-") !== -1) a.className = "is-active";
    links.appendChild(a);
  });
  wrap.querySelectorAll("a").forEach(function (a) { a.remove(); });
  wrap.appendChild(links);
})();
