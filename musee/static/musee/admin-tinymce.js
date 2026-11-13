(function () {
    "use strict";

    var root = document.documentElement;
    var palettes = {
        default: { background: "#18181b", foreground: "#e4e4e7" },
        classic: { background: "#0f172a", foreground: "#e2e8f0" },
    };

    function syncEditorTheme() {
        var dark = root.classList.contains("dark");
        var palette = palettes[root.dataset.mnrDarkPalette] || palettes.default;

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
                doc.documentElement.style.setProperty("background-color", dark ? palette.background : "#ffffff", "important");
                doc.body.style.setProperty("background-color", dark ? palette.background : "#ffffff", "important");
                doc.body.style.setProperty("color", dark ? palette.foreground : "#222f3e", "important");
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
