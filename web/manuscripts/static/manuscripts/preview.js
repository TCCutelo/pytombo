// Live preview for the manuscript URL field in the admin.
// If the URL is a direct image it is shown inline; otherwise an "open" button
// is shown so the expert can view it in a new tab while transcribing.
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
        img.style.display = "none";
        link.style.display = "none";
        empty.style.display = "";
        return;
      }
      empty.style.display = "none";
      link.href = url;
      img.onload = function () {
        img.style.display = "";
        link.style.display = "none";
      };
      img.onerror = function () {
        img.style.display = "none";
        link.style.display = "inline-block";
      };
      img.src = url;
    }

    input.addEventListener("input", update);
    input.addEventListener("change", update);
    update();
  }

  if (document.readyState !== "loading") init();
  else document.addEventListener("DOMContentLoaded", init);
})();
