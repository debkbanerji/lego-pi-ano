const FETCH_INTERVAL_MS = 50;

let isRequestInFlight = false;

let pressedKeys = [];
const sounds = Array(30) // Expect at most 30 keys
    .fill(0)
    .map(
        (_, i) =>
            new Howl({
                src: [
                    `assets/key-sounds/${(i + 1).toLocaleString("en-US", {
                        minimumIntegerDigits: 2,
                        useGrouping: false
                    })}.wav`
                ]
            })
    );

setInterval(() => {
    if (!isRequestInFlight) {
        fetch(`${window.location.origin}/keys`)
            .then(response => response.json())
            .then(data => {
                const displayKeys = data.map(key => (key ? "■" : "□"));
                const displayKeysString = displayKeys.join(" ");
                document.getElementById("no-signals-text").hidden = true;
                document.getElementById(
                    "debug-text"
                ).innerHTML = displayKeysString;

                const oldPressedKeys = pressedKeys;
                pressedKeys = data;

                Object.keys(pressedKeys).forEach(keyIndex => {
                    if (pressedKeys[keyIndex] && !oldPressedKeys[keyIndex]) {
                        sounds[keyIndex].play();
                    }
                });

                isRequestInFlight = false;
            })
            .catch(function() {
                isRequestInFlight = false;
            });
        isRequestInFlight = true;
    }
}, FETCH_INTERVAL_MS);
