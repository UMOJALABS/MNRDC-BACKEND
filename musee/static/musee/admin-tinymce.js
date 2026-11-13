(function () {
    "use strict";

    var root = document.documentElement;

    function themeColor(name, fallback) {
        return getComputedStyle(root).getPropertyValue("--color-base-" + name).trim() || fallback;
    }

    function syncEditorTheme() {
        var dark = root.classList.contains("dark");
        var background = themeColor("900", "#24231f");
        var foreground = themeColor("100", "#eeede6");

        document.querySelectorAll(".tox-tinymce").forEach(function (container) {
            container.classList.toggle("mnr-dark-editor", dark);
            container.classList.toggle("mnr-light-editor", !dark);

            var iframe = container.querySelector("iframe");
            if (!iframe) return;

            if (iframe.dataset.mnrThemeListener !== "true") {
                iframe.dataset.mnrThemeListener = "true";
                iframe.addEventListener("load", syncEditorTheme);
            }

            try {
                var doc = iframe.contentDocument;
                if (!doc || !doc.documentElement || !doc.body) return;

                doc.documentElement.style.setProperty("color-scheme", dark ? "dark" : "light");
                doc.documentElement.style.setProperty("background-color", dark ? background : "#ffffff", "important");
                doc.body.style.setProperty("background-color", dark ? background : "#ffffff", "important");
                doc.body.style.setProperty("color", dark ? foreground : "#222f3e", "important");
            } catch (error) {
                // The iframe may not be ready yet; its load event retries synchronization.
            }
        });
    }

    function start() {
        syncEditorTheme();

        new MutationObserver(syncEditorTheme).observe(root, {
            attributes: true,
            attributeFilter: ["class", "data-mnr-dark-palette"],
        });

        new MutationObserver(syncEditorTheme).observe(document.body, {
            childList: true,
            subtree: true,
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", start, { once: true });
    } else {
        start();
    }
})();
