// ==========================================
// 1. DOM ELEMENTS & VARIABLES
// ==========================================
const container = document.querySelector(".orb-container");
const orb = container.querySelector(".orb");
const eyes = document.querySelectorAll(".eye");
const settingsPanel = document.getElementById("settingsPanel");
const settingsBtn = document.querySelector(".settings-btn");
const closeSettings = document.querySelector(".close-settings");
const commandHint = document.getElementById("command-hint");

// Global variables
let bridge = null;
let currentState = "idle";

// ==========================================
// 2. QT WEBCHANNEL BRIDGE SETUP
// ==========================================
if (typeof qt !== "undefined") {
    new QWebChannel(qt.webChannelTransport, function (channel) {
        bridge = channel.objects.bridge;
        window.bridge = bridge; // Make global for debugging
        console.log("✅ [JS] Connected to Vision Python bridge");

        // --- Connect Signals from Python ---
        
        // 1. Listen for State Changes
        bridge.sendState.connect(switchState);

        // 2. Listen for Spotify Updates
        bridge.sendSpotify.connect((song, artist, isPlaying) => {
             console.log("[Spotify]", song, artist, isPlaying);
             // Update UI if you have a spotify element
        });
        
        // 3. Listen for Contact Updates
        bridge.sendContacts.connect((contactsJson) => {
            renderContacts(contactsJson);
        });

        // --- Initial Data Load ---
        loadContacts();
        loadSettings();
        loadApiKeys();
    });
} else {
    console.warn("⚠️ [JS] Qt WebChannel not detected. Running in browser mode.");
}

// ==========================================
// 3. STATE MANAGEMENT
// ==========================================
function switchState(newState) {
    console.log(`[Vision] Switching UI state to: ${newState}`);
    currentState = newState;
    
    // 1. Reset color classes
    container.classList.remove(
        "color-blue", 
        "color-green", 
        "color-yellow", 
        "color-red", 
        "color-purple", 
        "color-white"
    );

    // 2. Add new class based on state map
    switch (newState) {
        case "idle":
            container.classList.add("color-blue");
            break;
        case "listening":
            container.classList.add("color-green");
            hideHint(); 
            break;
        case "answering":
            container.classList.add("color-yellow"); 
            break;
        case "thinking":
            container.classList.add("color-red");
            break;
        case "camera":
            container.classList.add("color-purple");
            break;
        case "speaking":
             container.classList.add("color-white");
             break;
        default:
            container.classList.add("color-blue");
    }
}

function hideHint() {
    if(commandHint) commandHint.style.opacity = "0";
}

// ==========================================
// 4. ANIMATIONS (EYES)
// ==========================================
function randomEyeMovement() {
  if (currentState !== "camera") {
    const moveX = (Math.random() - 0.5) * 25;
    const moveY = (Math.random() - 0.5) * 15;
    eyes.forEach((eye) => {
      eye.style.transform = `translate(${moveX}px, ${moveY}px)`;
    });
  }
  setTimeout(randomEyeMovement, 800 + Math.random() * 2500);
}
randomEyeMovement();

// Random Blink
setInterval(() => {
  if (currentState !== "camera" && Math.random() > 0.65) {
    eyes.forEach((eye) => {
      eye.style.height = "6px";
      setTimeout(() => (eye.style.height = "80px"), 180);
    });
  }
}, 2800);

// ==========================================
// 5. SETTINGS PANEL INTERACTION
// ==========================================

// Open
if(settingsBtn) {
    settingsBtn.addEventListener("click", () => {
        settingsPanel.classList.add("active");
        if(bridge) {
            loadContacts();
            loadSettings();
            loadApiKeys();
        }
    });
}

// Close
if(closeSettings) {
    closeSettings.addEventListener("click", () => {
        settingsPanel.classList.remove("active");
    });
}

// Tab Switching
const settingsTabs = document.querySelectorAll(".settings-tab");
const tabPanels = document.querySelectorAll(".tab-panel");
const settingsTitle = document.getElementById("settings-title");

settingsTabs.forEach(tab => {
  tab.addEventListener("click", () => {
    // Reset
    settingsTabs.forEach(t => t.classList.remove("active"));
    tabPanels.forEach(panel => panel.classList.remove("active"));
    
    // Activate
    tab.classList.add("active");
    const targetId = tab.dataset.tab;
    const targetPanel = document.getElementById(targetId);
    
    if (targetPanel) targetPanel.classList.add("active");
    if (settingsTitle) settingsTitle.textContent = tab.textContent.trim();
  });
});

// ==========================================
// 6. CONTACTS LOGIC
// ==========================================
const contactListDiv = document.querySelector(".contact-list");
const addContactBtn = document.getElementById("addContactBtn");

function loadContacts() {
    if (!bridge) return;
    bridge.loadContacts(function (data) {
        renderContacts(data);
    });
}

function renderContacts(jsonString) {
    if(!contactListDiv) return;
    const contacts = JSON.parse(jsonString || "[]");
    
    if (contacts.length === 0) {
        contactListDiv.innerHTML = "<div style='color:#aaa; padding:10px;'>📇 Все още няма добавени контакти.</div>";
        return;
    }

    contactListDiv.innerHTML = contacts.map(c => `
      <div class="contact-item">
        <strong>${c["Име"]}</strong>
        <div class="contact-row"><i>📞</i> ${c["Телефон"]}</div>
        <div class="contact-row"><i>✉️</i> ${c["Имейл"]}</div>
        ${c["Линк"] ? `<div class="contact-row"><i>🔗</i> ${c["Линк"]}</div>` : ''}
      </div>
    `).join("");
}

if(addContactBtn) {
    addContactBtn.addEventListener("click", () => {
        const name = document.getElementById("contactName").value.trim();
        const phone = document.getElementById("contactPhone").value.trim();
        const email = document.getElementById("contactEmail").value.trim();
        const link = document.getElementById("contactInstagram").value.trim();

        if (!name || !email) return alert("Моля, попълнете име и имейл!");

        if (bridge) {
            bridge.addContact(name, phone, email, link);
            // Clear inputs
            document.getElementById("contactName").value = "";
            document.getElementById("contactPhone").value = "";
            document.getElementById("contactEmail").value = "";
            document.getElementById("contactInstagram").value = "";
        }
    });
}

// ==========================================
// 7. GENERAL SETTINGS LOGIC
// ==========================================
const saveGeneralBtn = document.getElementById("saveGeneralBtn");

function loadSettings() {
    if (!bridge) return;
    bridge.loadSettings(function (data) {
        const s = JSON.parse(data || "{}");
        
        const nameInput = document.getElementById("general-name-input");
        if(nameInput) nameInput.value = s["jarvis_name"] || "";
        
        const voiceSelect = document.getElementById("general-voice-select");
        if(voiceSelect) voiceSelect.value = s["jarvis_voice"] || "Slavi";

        const modeSelect = document.getElementById("general-mode-select");
        if(modeSelect) modeSelect.value = (s["type_discussion"] === "once") ? "Веднъж" : "Разговор";

        const waitRange = document.getElementById("general-wait-range");
        if(waitRange) waitRange.value = s["wait_interval_seconds"] || 10;
    });
}

if(saveGeneralBtn) {
    saveGeneralBtn.addEventListener("click", () => {
        if (!bridge) return;
        
        const name = document.getElementById("general-name-input").value;
        const voice = document.getElementById("general-voice-select").value;
        const modeRaw = document.getElementById("general-mode-select").value;
        const mode = (modeRaw === "Веднъж") ? "once" : "continuous";
        const wait = parseInt(document.getElementById("general-wait-range").value);

        bridge.saveSettings(name, voice, mode, wait);
        alert("✅ Настройките са запазени!");
    });
}

// ==========================================
// 8. API KEYS LOGIC
// ==========================================
const saveApiBtn = document.getElementById("saveApiKeysBtn");

function loadApiKeys() {
    if (!bridge) return;
    bridge.loadApiKeys(function (data) {
        const k = JSON.parse(data || "{}");
        if(document.getElementById("geminiKey")) document.getElementById("geminiKey").value = k.GEMINI_KEY || "";
        if(document.getElementById("elevenKey")) document.getElementById("elevenKey").value = k.ELEVEN_LABS_API || "";
        if(document.getElementById("spotifyId")) document.getElementById("spotifyId").value = k.SPOTIFY_CLIENT_ID || "";
        if(document.getElementById("spotifySecret")) document.getElementById("spotifySecret").value = k.SPOTIFY_CLIENT_SECRET || "";
        if(document.getElementById("deepseekKey")) document.getElementById("deepseekKey").value = k.DEEPSEEK_API_KEY || "";
    });
}

if(saveApiBtn) {
    saveApiBtn.addEventListener("click", () => {
        if (!bridge) return;
        const payload = {
            GEMINI_KEY: document.getElementById("geminiKey").value.trim(),
            ELEVEN_LABS_API: document.getElementById("elevenKey").value.trim(),
            SPOTIFY_CLIENT_ID: document.getElementById("spotifyId").value.trim(),
            SPOTIFY_CLIENT_SECRET: document.getElementById("spotifySecret").value.trim(),
            DEEPSEEK_API_KEY: document.getElementById("deepseekKey").value.trim()
        };
        bridge.saveApiKeys(JSON.stringify(payload));
        alert("✅ API ключовете са запазени!");
    });
}

// ==========================================
// 9. WIDGETS & INIT
// ==========================================
window.addEventListener("DOMContentLoaded", () => {
   buildCalendar();
   loadWeather();
   loadUserPhoto();
   loadUserSettings();
});

// Calendar
function buildCalendar() {
   const today = new Date();
   const year = today.getFullYear();
   const month = today.getMonth();
   const monthNames = ["January","February","March","April","May","June","July","August","September","October","November","December"];

   const header = document.querySelector(".cal-header");
   if(header) header.textContent = monthNames[month];

   const grid = document.querySelector(".calendar-grid");
   if(!grid) return;

   grid.innerHTML = `
       <div class="day-name">S</div><div class="day-name">M</div><div class="day-name">T</div>
       <div class="day-name">W</div><div class="day-name">T</div><div class="day-name">F</div><div class="day-name">S</div>
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

// Weather
async function loadWeather() {
   try {
       const lat = 43.0812;
       const lon = 25.6290;
       const url = `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current_weather=true`;
       const res = await fetch(url);
       const data = await res.json();
       
       const tempEl = document.querySelector(".temp-large");
       if(tempEl) tempEl.textContent = Math.round(data.current_weather.temperature) + "°";
   } catch (e) {
       console.log("Weather load failed");
   }
}

// User Settings (Greeting)
async function loadUserSettings() {
  try {
    const response = await fetch("../account/user_settings.json?cachebuster=" + Date.now());
    if (!response.ok) return;
    const user = await response.json();
    const data = user.data || user;

    // Greeting logic
    const h = new Date().getHours();
    let txt = "Добър вечер";
    if (h < 12) txt = "Добро утро";
    else if (h < 18) txt = "Добър ден";
    
    const greetingEl = document.getElementById("greeting");
    if(greetingEl) greetingEl.textContent = `${txt}, ${data.Name || "Sir"}`;

  } catch (err) {
    console.error("Error loading user settings:", err);
  }
}

// User Photo
async function loadUserPhoto() {
  try {
    const photoEl = document.getElementById("user-photo");
    if(!photoEl) return;

    const userPhoto = `assets/user_pfp.png?cb=${Date.now()}`;
    const defaultPhoto = "assets/default_pfp.png";

    const img = new Image();
    img.onload = () => { photoEl.src = userPhoto; };
    img.onerror = () => { photoEl.src = defaultPhoto; };
    img.src = userPhoto;
  } catch (err) {
    console.error("Error loading user photo:", err);
  }
}

// ==========================================
// 10. WALLPAPER PICKER
// ==========================================
const wallpaperThumbs = document.querySelectorAll(".wallpaper-thumb");
wallpaperThumbs.forEach(thumb => {
    thumb.addEventListener("click", () => {
        wallpaperThumbs.forEach(t => t.classList.remove("active"));
        thumb.classList.add("active");

        const id = thumb.dataset.wall;
        document.documentElement.style.setProperty("--current-wallpaper", `url("wallpapers/wallpaper_${id}.jpg")`);
        
        if(window.bridge && bridge.saveWallpaper) {
            try { bridge.saveWallpaper(id); } catch(e){}
        }
    });
});

// ==========================================
// 11. LIFECYCLE / LOADING SCREEN
// ==========================================
window.addEventListener("load", () => {
  const loader = document.getElementById("loadingScreen");
  if(loader) {
      setTimeout(() => {
        loader.classList.add("hidden");
        // Show command hint shortly after
        setTimeout(() => {
             if(commandHint) commandHint.classList.add("visible");
        }, 1200);
      }, 5200);
  }
});