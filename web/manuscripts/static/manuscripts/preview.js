// Live preview for the manuscript URL field in the admin.
// As soon as a URL is entered we ALWAYS show an "open in new tab" button (so
// there is always a way to view the manuscript), and we additionally try to
// load it inline as an image — shown on top if it is a direct image URL.
(function () {
  function init() {
    var input = document.getElementById("id_source_url");
    var box = document.getElementById("ms-preview");
    if (!input || !box) return;

    var img = box.querySelector(".ms-preview-img");
    var link = box.querySelector(".ms-preview-link");
    var empty = box.querySelector(".ms-preview-empty");

    function update() {
      var url = (input.value || "").trim();
      if (!url) {
        empty.style.display = "";
        link.style.display = "none";
        img.style.display = "none";
        img.removeAttribute("src");
        return;
      }
      empty.style.display = "none";
      // Always offer a way to open the manuscript.
      link.href = url;
      link.style.display = "inline-block";
      // Try to show it inline; only an actual image will appear.
      img.style.display = "none";
      img.onload = function () {
        img.style.display = "block";
      };
      img.onerror = function () {
        img.style.display = "none";
      };
      img.src = url;
    }

    ["input", "change", "keyup", "paste", "blur"].forEach(function (ev) {
      input.addEventListener(ev, function () {
        // paste fills the value on the next tick
        setTimeout(update, 0);
      });
    });
    update();
  }

  if (document.readyState !== "loading") init();
  else document.addEventListener("DOMContentLoaded", init);
})();
