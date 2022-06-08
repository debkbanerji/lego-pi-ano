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
    keysTarget.innerHTML = "Waiting for Signal/Loading in audio files...";
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
                    pressedKeys = [];

                    data.forEach((pressed, pin) => {
                        pressedKeys[pinMap[pin]] = pressed || 0;
                    });

                    keysTarget.innerHTML = "";

                    Object.keys(pressedKeys).forEach(keyIndex => {
                        if (
                            pressedKeys[keyIndex] &&
                            oldPressedKeys[keyIndex] == null
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

const pinMapControls = document.getElementById("pin-map-controls");
document
    .getElementById("toggle-pin-map-controls")
    .addEventListener("click", () => {
        pinMapControls.hidden = !pinMapControls.hidden;
    });

Array(MAX_KEY_COUNT)
    .fill(0)
    .forEach((_, i) => {
        const container = document.createElement("div");
        container.innerHTML = `
        <div>
        <b>Pin ${i} Key: </b>  <input type="number" id="key-${i}" name="key-${i}" step="1" min="0" max="${MAX_KEY_COUNT -
            1}" value="${pinMap[i]}">
        </div>
      `;
        pinMapControls.appendChild(container);
    });

[...pinMapControls.children].forEach(container => {
    container.children[0].children[1].addEventListener("change", val => {
        const newPinMap = [];
        [...pinMapControls.children].forEach((container, i) => {
            newPinMap[i] = Number(container.children[0].children[1].value);
        });
        pinMap = newPinMap;
    });
});

// TODO: Write to pin map and URL on value change
