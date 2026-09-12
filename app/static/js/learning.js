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
  var overlay = document.getElementById("learn-rate-overlay");
  var dialogForm = document.getElementById("learn-rate-dialog-form");
  var dialogResource = document.getElementById("learn-rate-resource-id");
  var dialogTitle = document.getElementById("learn-rate-title");

  function fillStars(form, stars) {
    if (!form) return;
    form.querySelectorAll(".bd2-star-btn").forEach(function (btn) {
      btn.classList.toggle("filled", parseInt(btn.value, 10) <= stars);
    });
    var legend = form.querySelector("legend");
    if (legend && stars) {
      legend.textContent = "امتیاز شما: " + toFa(stars) + " از ۵";
    }
  }

  function bindStarHover(form) {
    if (!form || form.dataset.hoverBound) return;
    form.dataset.hoverBound = "1";
    var buttons = Array.from(form.querySelectorAll(".bd2-star-btn"));
    function highlight(upTo) {
      buttons.forEach(function (btn) {
        btn.classList.toggle("filled", parseInt(btn.value, 10) <= upTo);
      });
    }
    buttons.forEach(function (btn) {
      btn.addEventListener("mouseenter", function () {
        highlight(parseInt(btn.value, 10));
      });
    });
    form.addEventListener("mouseleave", function () {
      var row = form.closest(".ra-res");
      var current = row ? parseInt(row.getAttribute("data-stars") || "0", 10) : 0;
      highlight(current);
    });
  }

  function syncRateUi(row, status, stars) {
    var cta = row.querySelector(".learn-rate-cta");
    var form = row.querySelector(".learn-rate-form");
    var hasStars = !!stars;
    var rateable = hasStars || status === "DONE" || status === "ALREADY_KNEW";
    row.setAttribute("data-stars", hasStars ? String(stars) : "");
    if (hasStars) {
      if (cta) cta.hidden = true;
      if (form) {
        form.hidden = false;
        fillStars(form, stars);
      }
    } else if (rateable) {
      if (cta) cta.hidden = false;
      if (form) form.hidden = true;
    } else {
      if (cta) cta.hidden = true;
      if (form) form.hidden = true;
    }
  }

  function closeRateDialog() {
    if (overlay) overlay.hidden = true;
    if (history.replaceState) {
      var url = new URL(window.location.href);
      url.searchParams.delete("rate");
      history.replaceState(null, "", url.pathname + url.search + url.hash);
    }
  }

  function openRateDialog(resourceId, title) {
    if (!overlay) return;
    if (dialogResource) dialogResource.value = resourceId;
    if (dialogTitle) dialogTitle.textContent = title || "";
    overlay.hidden = false;
    var firstStar = overlay.querySelector(".bd2-star-btn");
    if (firstStar && firstStar.focus) firstStar.focus();
  }

  function postJson(path, body) {
    return fetch(path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }).then(function (res) {
      return res.json().then(function (data) {
        data._status = res.status;
        return data;
      });
    });
  }

  document.querySelectorAll(".learn-status-form").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      if (!window.fetch) return;
      e.preventDefault();
      var select = form.querySelector(".learn-status");
      var resourceId = form.querySelector('[name="resource_id"]').value;
      var status = select.value;
      postJson("/api/v1/learning/" + slug + "/progress/", {
        resource_id: Number(resourceId),
        status: status,
      })
        .then(function (data) {
          if (!data || !data.ok) {
            form.submit();
            return;
          }
          var row = form.closest(".ra-res");
          select.setAttribute("data-status", status);
          if (row) {
            row.setAttribute("data-status", status);
            var existing = parseInt(row.getAttribute("data-stars") || "0", 10) || 0;
            syncRateUi(row, status, existing || null);
          }
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
          if (data.prompt_rating && row) {
            openRateDialog(resourceId, row.getAttribute("data-title") || "");
          }
        })
        .catch(function () { form.submit(); });
    });
  });

  document.querySelectorAll(".learn-rate-form").forEach(function (form) {
    bindStarHover(form);
    form.addEventListener("submit", function (e) {
      if (!window.fetch) return;
      e.preventDefault();
      var resourceInput = form.querySelector('[name="resource_id"]');
      var submitter = e.submitter;
      var stars = submitter && submitter.name === "stars"
        ? Number(submitter.value)
        : Number((form.querySelector('[name="stars"]:checked') || {}).value);
      if (!stars) {
        form.submit();
        return;
      }
      postJson("/api/v1/learning/" + slug + "/rate/", {
        resource_id: Number(resourceInput.value),
        stars: stars,
      })
        .then(function (data) {
          if (!data || !data.ok) {
            form.submit();
            return;
          }
          var row = document.querySelector('.ra-res[data-resource-id="' + resourceInput.value + '"]');
          if (row) {
            syncRateUi(row, row.getAttribute("data-status") || "", data.stars);
            bindStarHover(row.querySelector(".learn-rate-form"));
          }
          closeRateDialog();
        })
        .catch(function () { form.submit(); });
    });
  });

  function onSkip(e) {
    e.preventDefault();
    closeRateDialog();
  }
  var skip = document.getElementById("learn-rate-skip");
  var closeBtn = document.getElementById("learn-rate-close");
  if (skip) skip.addEventListener("click", onSkip);
  if (closeBtn) closeBtn.addEventListener("click", onSkip);

  if (dialogForm) bindStarHover(dialogForm);
})();
