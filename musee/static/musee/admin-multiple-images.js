(function () {
    "use strict";

    function setupMultipleImageInput(input) {
        if (input.dataset.multipleImagesReady === "true") return;
        input.dataset.multipleImagesReady = "true";

        var queuedFiles = Array.from(input.files || []);
        var list = document.createElement("ul");
        list.className = "mnr-selected-images";
        list.setAttribute("aria-live", "polite");
        input.insertAdjacentElement("afterend", list);

        function fileKey(file) {
            return [file.name, file.size, file.lastModified].join(":");
        }

        function updateInput() {
            var transfer = new DataTransfer();
            queuedFiles.forEach(function (file) { transfer.items.add(file); });
            input.files = transfer.files;
        }

        function renderList() {
            list.replaceChildren();
            queuedFiles.forEach(function (file, index) {
                var item = document.createElement("li");
                var name = document.createElement("span");
                var remove = document.createElement("button");

                name.textContent = file.name;
                remove.type = "button";
                remove.className = "mnr-remove-image";
                remove.textContent = "Retirer";
                remove.setAttribute("aria-label", "Retirer " + file.name);
                remove.addEventListener("click", function () {
                    queuedFiles.splice(index, 1);
                    updateInput();
                    renderList();
                });

                item.append(name, remove);
                list.appendChild(item);
            });
        }

        input.addEventListener("change", function () {
            var knownFiles = new Set(queuedFiles.map(fileKey));
            Array.from(input.files || []).forEach(function (file) {
                var key = fileKey(file);
                if (!knownFiles.has(key)) {
                    queuedFiles.push(file);
                    knownFiles.add(key);
                }
            });
            updateInput();
            renderList();
        });

        renderList();
    }

    function start() {
        document.querySelectorAll("input.mnr-multiple-image-input").forEach(setupMultipleImageInput);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", start, { once: true });
    } else {
        start();
    }
})();
