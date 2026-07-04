// --- Global State ---
let currentUser = null; // Keeps track of who is logged in

// --- 1. Accessibility Controls & Live Number Updates ---
function updateStyling() {
    const size = document.getElementById('fontSizeSlider').value;
    const color = document.getElementById('fontColorPicker').value;
    document.getElementById('sizeVal').innerText = size;
    
    const outputBox = document.getElementById('outputText');
    outputBox.style.fontSize = size + 'px';
    outputBox.style.color = color;
}

function updateTTSValues() {
    const vol = document.getElementById('ttsVolume').value;
    const spd = document.getElementById('ttsSpeed').value;
    document.getElementById('volVal').innerText = parseFloat(vol).toFixed(1);
    document.getElementById('spdVal').innerText = parseFloat(spd).toFixed(1);
}

// --- 2. Text-to-Speech (Web Speech API) ---
let speech = new SpeechSynthesisUtterance();

function triggerTTS(textElementId) {
    const textToRead = document.getElementById(textElementId).value;
    if (!textToRead) {
        alert("There is no text to read yet!");
        return;
    }
    
    window.speechSynthesis.cancel(); 
    speech.text = textToRead;
    speech.volume = document.getElementById('ttsVolume').value;
    speech.rate = document.getElementById('ttsSpeed').value;
    speech.pitch = 1; 
    
    window.speechSynthesis.speak(speech);
}

function speakInputText() { triggerTTS('inputText'); }
function speakOutputText() { triggerTTS('outputText'); }
function stopSpeech() { window.speechSynthesis.cancel(); }

// --- 3. Backend Text Simplification API ---
async function processText() {
    const text = document.getElementById('inputText').value;
    if (!text) { alert("Please paste some original text first!"); return; }

    document.getElementById('loadingMsg').style.display = 'block';
    document.getElementById('mainSimplifyBtn').disabled = true;

    try {
        const response = await fetch('http://127.0.0.1:5000/simplify', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text }) 
        });

        const data = await response.json();
        document.getElementById('outputText').value = data.simplified;

        const glossarySection = document.getElementById('glossarySection');
        const glossaryGrid = document.getElementById('glossaryGrid');
        glossaryGrid.innerHTML = ""; 
        
        if (data.glossary && data.glossary.length > 0) {
            data.glossary.forEach(item => {
                const wordBox = document.createElement('div');
                wordBox.className = 'glossary-item';
                wordBox.innerHTML = `<span class="glossary-old">${item.original}</span> ➔ <span class="glossary-new">${item.simplified}</span>`;
                glossaryGrid.appendChild(wordBox);
            });
            glossarySection.style.display = 'block';
        } else {
            glossarySection.style.display = 'none';
        }
    } catch (error) {
        alert("Failed to connect to backend. Make sure your Python app.py server is running!");
    } finally {
        document.getElementById('loadingMsg').style.display = 'none';
        document.getElementById('mainSimplifyBtn').disabled = false;
    }
}

// --- 4. OCR Image Extraction ---
async function extractTextFromImage() {
    const fileInput = document.getElementById('imageUpload');
    if (!fileInput.files.length) return;

    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('image', file);

    document.getElementById('ocrLoadingText').style.display = 'inline';
    const inputBox = document.getElementById('inputText');
    inputBox.value = ""; 
    inputBox.placeholder = "Extracting text from image... please wait.";

    try {
        const response = await fetch('http://127.0.0.1:5000/ocr', { method: 'POST', body: formData });
        const data = await response.json();
        if (data.text.trim() === "") { alert("Could not find any readable text. Try a clearer photo!"); } 
        else { inputBox.value = data.text; }
    } catch (error) {
        alert("Failed to extract text. Make sure Tesseract is installed and Python is running!");
    } finally {
        document.getElementById('ocrLoadingText').style.display = 'none';
        inputBox.placeholder = "Paste your complex textbook material here, or upload an image to extract text...";
        fileInput.value = ""; 
    }
}

// --- 5. Chatbot Widget ---
function toggleChatbot() {
    const panel = document.getElementById('chatbotPanel');
    if (panel.classList.contains('open')) {
        panel.classList.remove('open');
        setTimeout(() => panel.style.display = 'none', 300); 
    } else {
        panel.style.display = 'flex';
        setTimeout(() => panel.classList.add('open'), 10); 
    }
}

function handleChatEnter(event) { if (event.key === 'Enter') sendChatMessage(); }

async function sendChatMessage() {
    const input = document.getElementById('chatInput');
    const msg = input.value.trim();
    if (!msg) return;

    const chatBody = document.getElementById('chatbotBody');

    // 🟢 User message
    const userBubble = document.createElement('div');
    userBubble.className = 'user-msg';
    userBubble.innerText = msg;
    chatBody.appendChild(userBubble);

    input.value = '';
    chatBody.scrollTop = chatBody.scrollHeight;

    // 🟡 Bot "thinking..."
    const botBubble = document.createElement('div');
    botBubble.className = 'bot-msg';
    botBubble.innerText = "Thinking...";
    chatBody.appendChild(botBubble);
    chatBody.scrollTop = chatBody.scrollHeight;

    try {
        const response = await fetch('http://127.0.0.1:5000/chat-assist', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: msg })
        });

        const data = await response.json();

        if (!response.ok) {
            botBubble.innerText = "Error: " + (data.reply || "Something went wrong");
            return;
        }

        // ✅ Replace thinking with real reply
        botBubble.innerText = data.reply;

    } catch (error) {
        botBubble.innerText = "Cannot connect to server!";
        console.error(error);
    }

    chatBody.scrollTop = chatBody.scrollHeight;
}

// ==========================================
// 🔐 6. AUTHENTICATION & DATABASE LOGIC
// ==========================================
let authMode = 'login'; // 'login' or 'signup'

function openModal(mode) {
    authMode = mode;
    document.getElementById('authModal').style.display = 'flex';
    document.getElementById('modalTitle').innerText = mode === 'login' ? 'Log In' : 'Sign Up';
    document.getElementById('authMessage').innerText = '';
    document.getElementById('authMessage').style.color = 'black';
}

function closeModal() {
    document.getElementById('authModal').style.display = 'none';
    document.getElementById('authUsername').value = '';
    document.getElementById('authPassword').value = '';
}

async function handleAuth(event) {
    event.preventDefault(); // Stop page reload
    
    const username = document.getElementById('authUsername').value;
    const password = document.getElementById('authPassword').value;
    const msgBox = document.getElementById('authMessage');
    
    msgBox.innerText = 'Processing...';
    msgBox.style.color = 'blue';

    const route = authMode === 'login' ? '/login' : '/signup';

    try {
        const response = await fetch(`http://127.0.0.1:5000${route}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();

        if (!response.ok) {
            msgBox.innerText = data.error;
            msgBox.style.color = 'red';
        } else {
            if (authMode === 'signup') {
                msgBox.innerText = "Success! You can now log in.";
                msgBox.style.color = 'green';
                setTimeout(() => openModal('login'), 1500); // Switch to login screen
            } else {
                // LOGIN SUCCESS!
                currentUser = username;
                closeModal();
                
                // Update UI Header
                document.getElementById('navAuth').style.display = 'none';
                document.getElementById('navProfile').style.display = 'flex';
                document.getElementById('welcomeText').innerText = `Welcome, ${username}!`;
                document.getElementById('saveSettingsBtn').style.display = 'inline-block'; // Show save button
                
                // Apply their saved settings!
                if (data.settings) {
                    document.getElementById('fontSizeSlider').value = data.settings.font_size;
                    document.getElementById('fontColorPicker').value = data.settings.font_color;
                    document.getElementById('ttsVolume').value = data.settings.tts_volume;
                    document.getElementById('ttsSpeed').value = data.settings.tts_speed;
                    
                    updateStyling();
                    updateTTSValues();
                }
            }
        }
    } catch (error) {
        msgBox.innerText = "Server error. Is app.py running?";
        msgBox.style.color = 'red';
    }
}

function logoutUser() {
    currentUser = null;
    document.getElementById('navAuth').style.display = 'flex';
    document.getElementById('navProfile').style.display = 'none';
    document.getElementById('saveSettingsBtn').style.display = 'none';
    alert("You have been logged out.");
}

// Grab the slider and the text area you want to change
const spacingSlider = document.getElementById('spacing-slider');
const outputText = document.getElementById('outputText'); 

// Whenever the user drags the slider, update the CSS!
spacingSlider.addEventListener('input', function() {
    // Adds 'px' to the number (e.g., "2px")
outputText.style.letterSpacing = this.value + "px"; 
});
async function saveUserSettings() {
    if (!currentUser) return;
    
    const settings = {
        username: currentUser,
        font_size: document.getElementById('fontSizeSlider').value,
        font_color: document.getElementById('fontColorPicker').value,
        tts_volume: document.getElementById('ttsVolume').value,
        tts_speed: document.getElementById('ttsSpeed').value
    };

    try {
        const response = await fetch('http://127.0.0.1:5000/save_settings', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(settings)
        });
        
        if (response.ok) {
            alert("Preferences saved to database! They will load automatically next time you log in.");
        }
    } catch (error) {
        alert("Failed to save settings.");
    }
}