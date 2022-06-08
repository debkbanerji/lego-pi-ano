const FETCH_INTERVAL_MS = 50;
const MAX_KEY_COUNT = 30; // Expect at most 30 keys

const keysTarget = document.getElementById("keys-container");
let isSoundEnabled = false;
let isRequestInFlight = false;
let pressedKeys = [];

let pinMap = Array(MAX_KEY_COUNT)
    .fill(0)
    .map((_, i) => i);
const sounds = Array(MAX_KEY_COUNT)
    .fill(0)
    .map((_, i) => {
        return new Howl({
            src: [
                `assets/key-sounds/${(i + 1).toLocaleString("en-US", {
                    minimumIntegerDigits: 2,
                    useGrouping: false
                })}.wav`
            ]
        });
    });

function onTapPage() {
    isSoundEnabled = true;
    keysTarget.innerHTML = "Waiting for signal...";
}
document.addEventListener("click", onTapPage);
document.addEventListener("touchstart", onTapPage);

setInterval(() => {
    if (!isRequestInFlight) {
        fetch(`${window.location.origin}/keys`)
            .then(response => response.json())
            .then(data => {
                if (isSoundEnabled) {
                    const oldPressedKeys = pressedKeys;
                    pressedKeys = data.map(pin => pinMap[pin]);

                    keysTarget.innerHTML = "";

                    Object.keys(pressedKeys).forEach(keyIndex => {
                        if (
                            pressedKeys[keyIndex] &&
                            !oldPressedKeys[keyIndex]
                        ) {
                            sounds[keyIndex].play();
                        }

                        const key = document.createElement("div");
                        key.className = `display-key${
                            pressedKeys[keyIndex] ? " display-key-pressed" : ""
                        }`;
                        keysTarget.appendChild(key);
                    });
                }
                isRequestInFlight = false;
            })
            .catch(function() {
                keysTarget.innerHTML = "No signal received yet";
                isRequestInFlight = false;
            });
        isRequestInFlight = true;
    }
}, FETCH_INTERVAL_MS);
