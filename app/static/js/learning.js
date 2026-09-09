(function () {
  var fa = "۰۱۲۳۴۵۶۷۸۹";
  function toFa(n) {
    return String(n).replace(/\d/g, function (d) { return fa[d]; });
  }

  var track = document.getElementById("track");
  if (!track) return;

  var slugMatch = location.pathname.match(/\/dashboard\/learning\/([^/]+)\/track\//);
  if (!slugMatch) return;
  var slug = slugMatch[1];

  document.querySelectorAll(".learn-status-form").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      if (!window.fetch) return;
      e.preventDefault();
      var select = form.querySelector(".learn-status");
      var resourceId = form.querySelector('[name="resource_id"]').value;
      var status = select.value;
      fetch("/api/v1/learning/" + slug + "/progress/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ resource_id: Number(resourceId), status: status }),
      })
        .then(function (res) { return res.json(); })
        .then(function (data) {
          if (!data || !data.ok) {
            form.submit();
            return;
          }
          var row = form.closest(".ra-res");
          select.setAttribute("data-status", status);
          if (row) row.setAttribute("data-status", status);
          var p = data.progress;
          document.getElementById("progress-pct").innerHTML = toFa(p.pct) + "<span>٪</span>";
          document.getElementById("progress-bar").style.setProperty("--p", p.pct + "%");
          document.getElementById("stat-done").textContent = toFa(p.done);
          document.getElementById("stat-total").textContent = toFa(p.required);
          document.getElementById("stat-studying").textContent = toFa(p.studying);
          document.getElementById("stat-blank").textContent = toFa(p.blank);
          var badge = document.getElementById("level-badge");
          badge.className = "learn-badge";
          if (p.badge === "completed") badge.classList.add("learn-badge--done");
          else if (p.badge === "in_progress") badge.classList.add("learn-badge--progress");
          else badge.classList.add("learn-badge--enrolled");
          badge.textContent = p.badge_fa;
        })
        .catch(function () { form.submit(); });
    });
  });
})();
