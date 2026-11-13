(function () {
    "use strict";

    function syncEditorTheme() {
        var dark = document.documentElement.classList.contains("dark");

        document.querySelectorAll(".tox-tinymce").forEach(function (container) {
            container.classList.toggle("mnr-dark-editor", dark);
            var iframe = container.querySelector("iframe");
            if (!iframe) return;

            if (!iframe.dataset.mnrThemeListener) {
                iframe.dataset.mnrThemeListener = "true";
                iframe.addEventListener("load", syncEditorTheme);
            }
            if (!iframe.contentDocument || !iframe.contentDocument.body) return;

            var doc = iframe.contentDocument;
            doc.documentElement.classList.toggle("mnr-dark-editor", dark);
            doc.body.classList.toggle("mnr-dark-editor", dark);
            doc.documentElement.style.colorScheme = dark ? "dark" : "light";
            doc.body.style.backgroundColor = dark ? "#0f172a" : "#ffffff";
            doc.body.style.color = dark ? "#e2e8f0" : "#222f3e";
        });
    }

    function watchTheme() {
        syncEditorTheme();
        new MutationObserver(syncEditorTheme).observe(document.documentElement, {
            attributes: true,
            attributeFilter: ["class"],
        });

        if (window.tinymce) {
            window.tinymce.on("AddEditor", function (event) {
                event.editor.on("init", syncEditorTheme);
            });
        }

        new MutationObserver(function (mutations) {
            mutations.forEach(function (mutation) {
                mutation.addedNodes.forEach(function (node) {
                    if (node.nodeType !== Node.ELEMENT_NODE) return;
                    var iframes = [];
                    if (node.matches && node.matches(".tox-tinymce iframe")) iframes.push(node);
                    if (node.querySelectorAll) iframes.push.apply(iframes, node.querySelectorAll(".tox-tinymce iframe"));
                    iframes.forEach(function (iframe) {
                        if (!iframe.dataset.mnrThemeListener) {
                            iframe.dataset.mnrThemeListener = "true";
                            iframe.addEventListener("load", syncEditorTheme);
                        }
                    });
                });
            });
            syncEditorTheme();
        }).observe(document.body, {
            childList: true,
            subtree: true,
        });

        document.addEventListener("DOMContentLoaded", syncEditorTheme);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", watchTheme, { once: true });
    } else {
        watchTheme();
    }
})();
