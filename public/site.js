// chalkmind.tech: early-access form, cookie-free page counts, campaign tags.
(function () {
  "use strict";
  var local = /^(localhost|127\.0\.0\.1)$/.test(location.hostname);
  var API = local ? "http://localhost:8090" : "https://api.chalkmind.tech";
  var store = window.sessionStorage;

  // Remember where the visitor came from for this visit (campaign tags and
  // the referring site), so a sign-up on a later page is credited correctly.
  try {
    var q = new URLSearchParams(location.search);
    ["utm_source", "utm_medium", "utm_campaign"].forEach(function (k) { if (q.get(k)) store.setItem(k, q.get(k)); });
    if (!store.getItem("ref") && document.referrer && document.referrer.indexOf(location.origin) !== 0) {
      store.setItem("ref", document.referrer);
    }
  } catch (_) {}
  function get(k) { try { return store.getItem(k) || ""; } catch (_) { return ""; } }

  // One page view: path only. No cookies, no personal data; respects Do Not Track.
  if (navigator.doNotTrack !== "1") {
    try {
      var body = JSON.stringify({ path: location.pathname });
      if (navigator.sendBeacon) navigator.sendBeacon(API + "/v1/pv", new Blob([body], { type: "text/plain" }));
    } catch (_) {}
  }

  // Early-access form (works without JS as a normal form post).
  document.querySelectorAll("form.join-form").forEach(function (f) {
    f.action = API + "/v1/waitlist";
    f.elements.source.value = location.pathname;
    var msg = f.querySelector(".join-msg");
    var btn = f.querySelector("button");
    f.addEventListener("submit", function (e) {
      e.preventDefault();
      var email = f.elements.email.value.trim();
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        msg.textContent = "Please enter a valid email address.";
        msg.className = "join-msg err";
        f.elements.email.focus();
        return;
      }
      btn.disabled = true;
      msg.textContent = "Adding you…";
      msg.className = "join-msg";
      fetch(API + "/v1/waitlist", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: email, role: f.elements.role.value, source: location.pathname, website: f.elements.website.value,
          referrer: get("ref"), utm_source: get("utm_source"), utm_medium: get("utm_medium"), utm_campaign: get("utm_campaign")
        })
      }).then(function (r) { return r.json().then(function (j) { return { ok: r.ok, j: j }; }); })
        .then(function (res) {
          if (res.ok) {
            f.classList.add("done");
            msg.className = "join-msg ok";
            msg.textContent = res.j.message || "You're on the list!";
          } else {
            msg.className = "join-msg err";
            msg.textContent = (res.j.error && res.j.error.message) || "Something went wrong. Please try again.";
            btn.disabled = false;
          }
        })
        .catch(function () {
          msg.className = "join-msg err";
          msg.textContent = "Couldn't reach the server. Check your connection and try again.";
          btn.disabled = false;
        });
    });
  });

  // Thanks page (no-JS form fallback lands here).
  var t = document.querySelector("[data-thanks]");
  if (t) {
    var p = new URLSearchParams(location.search);
    if (p.get("error")) {
      t.querySelector("h1").textContent = "That didn't work";
      t.querySelector("p").textContent = p.get("error");
    }
  }
})();
