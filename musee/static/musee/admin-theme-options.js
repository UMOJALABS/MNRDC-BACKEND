(function () {
    "use strict";

    var storageKey = "mnrDarkPalette";
    var root = document.documentElement;

    function applySavedPalette() {
        if (window.localStorage.getItem(storageKey) === "classic") {
            root.dataset.mnrDarkPalette = "classic";
        } else {
            delete root.dataset.mnrDarkPalette;
        }
    }

    function init() {
        applySavedPalette();

        document.addEventListener("click", function (event) {
            var anchor = event.target.closest("[data-mnr-theme-option]");
            if (!anchor) return;
            if (anchor.hasAttribute("data-mnr-dark-classic")) {
                window.localStorage.setItem(storageKey, "classic");
                applySavedPalette();
                return;
            }

            var icon = anchor.querySelector(".material-symbols-outlined");
            if (icon && ["light_mode", "dark_mode", "computer"].includes(icon.textContent.trim())) {
                window.localStorage.removeItem(storageKey);
                delete root.dataset.mnrDarkPalette;
            }
        }, true);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init, { once: true });
    } else {
        init();
    }
})();
