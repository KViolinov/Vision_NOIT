// === DOM References ===
const container = document.querySelector(".orb-container");
const orb = container.querySelector(".orb");
const eyes = document.querySelectorAll(".eye");
const flash = document.querySelector(".flash");
const spotifyInfo = document.getElementById("spotify-info");
const currentTimeEl = document.getElementById("current-time");
let state = "idle";

// === Qt Bridge Setup ===
// This connects JS ↔ Python via QWebChannel (in PySide6 / PyQt6)
if (typeof qt !== "undefined") {
  new QWebChannel(qt.webChannelTransport, function (channel) {
    window.bridge = channel.objects.bridge;
    console.log("✅ Connected to Vision Python bridge");

    // You can listen to messages from Python
    bridge.sendState.connect(function (newState) {
      switchState(newState);
    });

    bridge.sendSpotify.connect(function (song, artist, isPlaying) {
      updateSpotify(song, artist, isPlaying);
    });
  });
} else {
  console.warn("⚠️ Qt WebChannel not detected. Running in standalone mode.");
}

// === Animations ===
// Random eye movement

function randomEyeMovement() {
  if (state !== "camera") {
    const moveX = (Math.random() - 0.5) * 25;
    const moveY = (Math.random() - 0.5) * 15;
    eyes.forEach((eye) => {
      eye.style.transform = `translate(${moveX}px, ${moveY}px)`;
    });
  }
  setTimeout(randomEyeMovement, 800 + Math.random() * 2500);
}
randomEyeMovement();

// Eye blink animation
setInterval(() => {
  if (state !== "camera" && Math.random() > 0.65) {
    eyes.forEach((eye) => {
      eye.style.height = "6px";
      setTimeout(() => (eye.style.height = "80px"), 180);
    });
  }
}, 2800);

// === Orb color management ===
function changeColor(color) {
    container.className = `orb-container color-${color}`;
    const pixelatedBg = container.querySelector('.pixelated-bg');

    // Fade out slightly for smooth cross-transition
    pixelatedBg.style.opacity = 0.6;

    // Delay gradient update slightly to sync with orb
    setTimeout(() => {
        if (color === 'blue') {
        pixelatedBg.style.background = `
            radial-gradient(ellipse 120% 100% at 50% 50%,
            rgba(100, 150, 255, 0.8) 0%,
            rgba(150, 100, 255, 0.6) 40%,
            rgba(100, 200, 200, 0.4) 70%,
            transparent 100%)`;
        } else if (color === 'orange') {
        pixelatedBg.style.background = `
            radial-gradient(ellipse 120% 100% at 50% 50%,
            rgba(255, 180, 100, 0.8) 0%,
            rgba(255, 100, 50, 0.6) 40%,
            rgba(255, 200, 100, 0.4) 70%,
            transparent 100%)`;
        } else if (color === 'green') {
        pixelatedBg.style.background = `
            radial-gradient(ellipse 120% 100% at 50% 50%,
            rgba(100, 255, 150, 0.8) 0%,
            rgba(150, 255, 100, 0.6) 40%,
            rgba(100, 200, 255, 0.4) 70%,
            transparent 100%)`;
        }

        // Fade back in
        pixelatedBg.style.opacity = 1;
    }, 100);
}

// === State switching (called from Python or internally) ===
function switchState(newState) {
  console.log("[Vision] Switching UI state to:", newState);
  state = newState;
  const orbContainer = document.querySelector(".orb-container");
  if (!orbContainer) return;

  orbContainer.classList.remove(
    "color-blue",
    "color-green",
    "color-red",
    "color-yellow",
    "color-purple"
  );

  switch (newState) {
    case "idle":
      orbContainer.classList.add("color-blue");
      changeColor("blue");
      break;
    case "listening":
      orbContainer.classList.add("color-green");
      changeColor("green");
      break;
    case "answering":
      orbContainer.classList.add("color-yellow");
      changeColor("yellow");
      break;
    case "thinking":
      orbContainer.classList.add("color-red");
      changeColor("red");
      break;
    case "camera":
      orbContainer.classList.add("color-purple");
      changeColor("purple");
      break;
    default:
      orbContainer.classList.add("color-blue");
      changeColor("blue");
  }
}


//    // === Spotify info update ===
//    function updateSpotify(song, artist, isPlaying) {
//      console.log("[Vision] updateSpotify:", song, artist, isPlaying);
//      if (spotifyInfo) {
//        if (isPlaying) {
//          spotifyInfo.innerText = `🎵 ${song} – ${artist}`;
//        } else {
//          spotifyInfo.innerText = "Not playing";
//        }
//      }
//    }
//
//    // === Clock display ===
//    setInterval(() => {
//      const now = new Date();
//      const timeStr = now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
//      currentTimeEl.textContent = timeStr;
//    }, 1000);


let bridge = null;

// --- WebChannel setup ---
if (typeof qt !== "undefined") {
  new QWebChannel(qt.webChannelTransport, (channel) => {
    bridge = channel.objects.bridge;
    console.log("[JS] ✅ Connected to VisionBridge");

    // Listen for signals
    bridge.sendState.connect((s) => switchState(s));
    bridge.sendSpotify.connect((song, artist, playing) => {
      console.log("[Spotify]", song, artist, playing);
    });
  });
}

// === Settings Panel Toggle ===
const settingsBtn = document.querySelector(".settings-btn");
const settingsPanel = document.getElementById("settingsPanel");
const closeSettings = document.querySelector(".close-settings");
settingsBtn.addEventListener("click", () => {
  settingsPanel.classList.add("active");
  loadContacts();
  loadSettings();
  loadApiKeys();
});
closeSettings.addEventListener("click", () => {
  settingsPanel.classList.remove("active");
});

// === Tabs ===
//    document.querySelectorAll(".tab-btn").forEach((btn) => {
//      btn.addEventListener("click", () => {
//        document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
//        document.querySelectorAll(".tab-content").forEach((c) => c.classList.remove("active"));
//        btn.classList.add("active");
//        document.getElementById(btn.dataset.tab).classList.add("active");
//      });
//    });

// === NEW Settings Tabs ===
const settingsTabs = document.querySelectorAll(".settings-tab");
const tabPanels = document.querySelectorAll(".tab-panel");
const settingsTitle = document.getElementById("settings-title");

settingsTabs.forEach(tab => {
  tab.addEventListener("click", () => {

    // Deactivate all sidebar tabs
    settingsTabs.forEach(t => t.classList.remove("active"));

    // Hide all panels
    tabPanels.forEach(panel => panel.classList.remove("active"));

    // Activate clicked tab
    tab.classList.add("active");

    const panel = document.getElementById(tab.dataset.tab);
    if (panel) {
      panel.classList.add("active");
    }

    // Update header label
    settingsTitle.textContent = tab.textContent.trim();
  });
});


// === Contacts Handling ===
const contactListDiv = document.querySelector(".contact-list");
const addBtn = document.getElementById("addContactBtn");

function loadContacts() {
  if (!bridge) return;
  bridge.loadContacts(function (data) {
    const contacts = JSON.parse(data || "[]");
    if (contacts.length === 0) {
      contactListDiv.innerHTML = "<div>📇 Все още няма добавени контакти.</div>";
      return;
    }
    contactListDiv.innerHTML = contacts.map(c => `
      <div class="contact-item">
        <strong>${c["Име"]}</strong>

        <div class="contact-row">
          <i>📞</i> ${c["Телефон"]}
        </div>

        <div class="contact-row">
          <i>✉️</i> ${c["Имейл"]}
        </div>

        <div class="contact-row">
          <i>🔗</i> ${c["Линк"] || "none"}
        </div>
      </div>
    `).join("");
  });
}

addBtn.addEventListener("click", () => {
  const name = document.getElementById("contactName").value.trim();
  const phone = document.getElementById("contactPhone").value.trim();
  const email = document.getElementById("contactEmail").value.trim();
  const link = document.getElementById("contactInstagram").value.trim();
  if (!name || !email) return alert("Моля, попълнете всички полета!");

  bridge.addContact(name, phone, email, link);
  setTimeout(loadContacts, 300);
});

// === Orb state handling ===
function switchState(state) {
  console.log("[Vision] Orb state:", state);
  const container = document.querySelector(".orb-container");
  container.className = `orb-container color-${state}`;
}



// === General Settings Handling ===
const saveSettingsBtn = document.querySelector("#general .btn");
const nameInput = document.querySelector("#general input[type='text']");
const voiceSelect = document.querySelector("#general select:nth-of-type(1)");
const modeSelect = document.querySelector("#general select:nth-of-type(2)");
const waitRange = document.querySelector("#general input[type='range']");

function loadSettings() {
  if (!bridge) return;
  bridge.loadSettings(function (data) {
    const settings = JSON.parse(data || "{}");
    if (!settings) return;

    nameInput.value = settings["jarvis_name"] || "";
    voiceSelect.value = settings["jarvis_voice"] || "Slavi";
    modeSelect.value =
      settings["type_discussion"] === "once" ? "Веднъж" : "Разговор";
    waitRange.value = settings["wait_interval_seconds"] || 10;
  });
}

saveSettingsBtn.addEventListener("click", async () => {
  if (!bridge) {
    console.error("❌ Bridge not available!");
    return;
  }

  const name = nameInput.value.trim();
  const voice = voiceSelect.value;
  const mode = modeSelect.value === "Веднъж" ? "once" : "continuous";
  const waitTime = parseInt(waitRange.value);

  if (!name) return alert("Моля, въведете име!");

  try {
    const result = await bridge.saveSettings(name, voice, mode, waitTime);
    if (result) {
      console.log("[JS] ✅ Settings saved successfully!");
      alert("✅ Настройките са запазени успешно!");
    } else {
      console.error("[JS] ⚠️ saveSettings returned false");
      alert("⚠️ Грешка при запис на настройките!");
    }
  } catch (e) {
    console.error("[JS] ❌ Error calling saveSettings:", e);
  }
});


// === LOADING SCREEN HANDLER ===
window.addEventListener("load", () => {
  const loader = document.getElementById("loadingScreen");

  // 5-second loading animation
  setTimeout(() => {
    loader.classList.add("hidden");
  }, 5200); // Slightly longer than the bar animation
});


async function loadUserSettings() {
  try {
    // prevent caching
    const response = await fetch("../account/user_settings.json?cachebuster=" + Date.now());
    if (!response.ok) throw new Error("Cannot load user settings");
    const user = await response.json();

    const data = user.data || user;

    // Greeting logic
    const now = new Date();
    const hour = now.getHours();
    let greeting;
    if (hour >= 5 && hour < 12) greeting = "Добро утро";
    else if (hour >= 12 && hour < 18) greeting = "Добър ден";
    else greeting = "Добър вечер";

    // Greeting
    document.getElementById("greeting").textContent = `${greeting}, ${data.Name}`;

    // Badge
    const badgeEl = document.getElementById("account-badge");
    const accountType = (data.AccountType || "").toLowerCase();
    console.log("Account type:", accountType);

  } catch (err) {
    console.error("⚠️ Error loading user settings:", err);
  }
}

loadUserSettings();

// == LOAD USER PICTURE
async function loadUserPhoto() {
  try {
    const response = await fetch("../account/user_settings.json?cachebuster=" + Date.now());
    const user = await response.json();
    const data = user.data || user;
    const photoEl = document.getElementById("user-photo");

    // Use cache-buster to force reload
    const userPhoto = `assets/user_pfp.png?cb=${Date.now()}`;
    const defaultPhoto = "assets/default_pfp.png";

    const img = new Image();
    img.onload = () => { photoEl.src = userPhoto; };
    img.onerror = () => { photoEl.src = defaultPhoto; };
    img.src = userPhoto;
  } catch (err) {
    console.error("⚠️ Error loading user photo:", err);
  }
}

loadUserPhoto();

// === WALLPAPER PICKER ===
const wallpaperThumbs = document.querySelectorAll(".wallpaper-thumb");

if (wallpaperThumbs.length) {
  wallpaperThumbs.forEach(thumb => {
    thumb.addEventListener("click", () => {
      const id = thumb.dataset.wall;

      // Highlight selected thumb
      wallpaperThumbs.forEach(t => t.classList.remove("active"));
      thumb.classList.add("active");

      // Change CSS variable so body::before updates
      document.documentElement.style.setProperty(
        "--current-wallpaper",
        `url("wallpapers/wallpaper_${id}.jpg")`
      );

      // Optional: tell Python which wallpaper was chosen
      if (window.bridge && typeof bridge.saveWallpaper === "function") {
        try {
          bridge.saveWallpaper(id);
        } catch (e) {
          console.warn("saveWallpaper failed:", e);
        }
      }
    });
  });
}


// === API KEYS ===
const geminiKeyInput = document.getElementById("geminiKey");
const elevenKeyInput = document.getElementById("elevenKey");
const spotifyIdInput = document.getElementById("spotifyId");
const spotifySecretInput = document.getElementById("spotifySecret");
const deepseekKeyInput = document.getElementById("deepseekKey");
const saveApiBtn = document.getElementById("saveApiKeysBtn");

function loadApiKeys() {
    if (!bridge) return;

    bridge.loadApiKeys(function (data) {
        try {
            const keys = JSON.parse(data || "{}");

            geminiKeyInput.value       = keys.GEMINI_KEY || "";
            elevenKeyInput.value       = keys.ELEVEN_LABS_API || "";
            spotifyIdInput.value       = keys.SPOTIFY_CLIENT_ID || "";
            spotifySecretInput.value   = keys.SPOTIFY_CLIENT_SECRET || "";
            deepseekKeyInput.value     = keys.DEEPSEEK_API_KEY || "";

        } catch (e) {
            console.error("Failed parsing API keys:", e);
        }
    });
}

saveApiBtn.addEventListener("click", () => {
    if (!bridge) return alert("Bridge not connected!");

    const payload = {
        GEMINI_KEY: geminiKeyInput.value.trim(),
        ELEVEN_LABS_API: elevenKeyInput.value.trim(),
        SPOTIFY_CLIENT_ID: spotifyIdInput.value.trim(),
        SPOTIFY_CLIENT_SECRET: spotifySecretInput.value.trim(),
        DEEPSEEK_API_KEY: deepseekKeyInput.value.trim()
    };

    bridge.saveApiKeys(JSON.stringify(payload));
    alert("✅ API ключовете са запазени!");
});



document.addEventListener("DOMContentLoaded", () => {
    buildCalendar();
    loadWeather();
});

function buildCalendar() {
    const today = new Date();
    const year = today.getFullYear();
    const month = today.getMonth();

    const monthNames = [
        "January","February","March","April","May","June",
        "July","August","September","October","November","December"
    ];

    document.querySelector(".cal-header").textContent = monthNames[month];

    const grid = document.querySelector(".calendar-grid");
    grid.innerHTML = `
        <div class="day-name">S</div>
        <div class="day-name">M</div>
        <div class="day-name">T</div>
        <div class="day-name">W</div>
        <div class="day-name">T</div>
        <div class="day-name">F</div>
        <div class="day-name">S</div>
    `;

    const firstDay = new Date(year, month, 1).getDay();
    const lastDate = new Date(year, month + 1, 0).getDate();
    const prevLastDate = new Date(year, month, 0).getDate();

    for (let i = firstDay; i > 0; i--) {
        grid.innerHTML += `<div class="date-num prev-month">${prevLastDate - i + 1}</div>`;
    }

    for (let i = 1; i <= lastDate; i++) {
        const isToday = i === today.getDate();
        grid.innerHTML += `<div class="date-num ${isToday ? "current-day" : ""}">${i}</div>`;
    }
}

async function loadWeather() {
    const lat = 43.0812;
    const lon = 25.6290;

    const url = `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current_weather=true`;
    const res = await fetch(url);
    const data = await res.json();

    document.querySelector(".temp-large").textContent =
        Math.round(data.current_weather.temperature) + "°";
}


setTimeout(() => {
  document.getElementById("command-hint").classList.add("visible");
}, 1200);

// hide when assistant activates
function hideHint() {
  document.getElementById("command-hint").classList.remove("visible");
}

function setState(state) {
  const orb = document.querySelector(".orb");
  orb.dataset.state = state;
}


const audioCtx = new AudioContext();
const analyser = audioCtx.createAnalyser();
analyser.fftSize = 256;

const dataArray = new Uint8Array(analyser.frequencyBinCount);

// connect your audio source here
// source.connect(analyser).connect(audioCtx.destination);

function animateAudio() {
  analyser.getByteFrequencyData(dataArray);
  const avg = dataArray.reduce((a,b)=>a+b,0) / dataArray.length;

  const glow = Math.min(200, avg * 1.2);
  document.querySelector(".orb").style.boxShadow =
    `0 0 ${glow}px rgba(255,255,255,0.8)`;

  requestAnimationFrame(animateAudio);
}