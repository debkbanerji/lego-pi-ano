const FETCH_INTERVAL_MS = 50;

let isRequestInFlight = false;

setInterval(() => {
    if (!isRequestInFlight) {
        fetch(`${window.location.origin}/keys`)
            .then(response => response.json())
            .then(keyArray => {
                console.log(keyArray);
                const displayKeys = keyArray.map(key => (key ? "■" : "□"));
                const displayKeysString = displayKeys.join(" ");
                // const displayKeysLabelString = Object.keys(displayKeys).join(" ");
                document.getElementById("no-signals-text").hidden = true;
                document.getElementById(
                    "debug-text"
                ).innerHTML = displayKeysString;
                isRequestInFlight = false;
            })
            .catch(function() {
                isRequestInFlight = false;
            });
        isRequestInFlight = true;
    }
}, FETCH_INTERVAL_MS);
