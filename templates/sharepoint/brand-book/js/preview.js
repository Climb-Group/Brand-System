/* ClimbUK brand book: runs inside each component preview frame.
   Follows the theme the page asks for (dark, light, aaa-dark, aaa-light), loops the marquees, and reports its height
   so the frame can fit the component. */
(function () {
    "use strict";
    var root = document.documentElement;

    function apply(theme) {
        var light = theme === "light" || theme === "aaa-light";
        var aaa = theme === "aaa-dark" || theme === "aaa-light";
        root.setAttribute("data-theme", light ? "light" : "dark");
        root.setAttribute("data-climb-theme", theme);
        document.querySelectorAll("section").forEach(function (s) {
            s.classList.toggle("climb-aaa", aaa);
        });
        report();
    }

    function report() {
        if (window.parent === window) {
            return;
        }
        var h = Math.ceil(document.body.getBoundingClientRect().height);
        window.parent.postMessage({ cbbFrame: window.name, height: h }, "*");
    }

    var params = new URLSearchParams(location.search);
    if (window.ClimbUK && window.ClimbUK.mount) {
        window.ClimbUK.mount(document);
    }
    apply(params.get("theme") || "dark");

    // Previews show sample links: keep a reader on the brand book page.
    document.addEventListener("click", function (e) {
        var a = e.target.closest && e.target.closest("a[href]");
        if (a && a.getAttribute("href").charAt(0) === "#") {
            e.preventDefault();
        }
    });
    window.addEventListener("message", function (e) {
        if (e.source === window.parent && e.data && e.data.cbbTheme) {
            apply(e.data.cbbTheme);
        }
    });
    window.addEventListener("load", report);
    if (window.ResizeObserver) {
        new ResizeObserver(report).observe(document.body);
    }
})();
