/**
 * JARVIES 4.0 - ADVANCED HOLOGRAPHIC HUD CONTROLLER
 */

document.addEventListener("DOMContentLoaded", () => {
  // DOM Elements
  const chatMessages = document.getElementById("chatMessages");
  const chatInput = document.getElementById("chatInput");
  const sendBtn = document.getElementById("sendBtn");
  const micBtn = document.getElementById("micBtn");
  const reactorWrapper = document.getElementById("reactorWrapper");
  const reactorStatusText = document.getElementById("reactorStatusText");
  const reactorSubtext = document.getElementById("reactorSubtext");
  const voiceSelector = document.getElementById("voiceSelector");
  const speakerAudioToggle = document.getElementById("speakerAudioToggle");
  const audioPlayer = document.getElementById("audioPlayer");
  const audioVisualizer = document.getElementById("audioVisualizer");
  const hudToast = document.getElementById("hudToast");

  // Telemetry Badges
  const cpuBadge = document.getElementById("cpuBadge");
  const ramBadge = document.getElementById("ramBadge");
  const batteryBadge = document.getElementById("batteryBadge");
  const systemState = document.getElementById("systemState");

  // Audio Context & Visualizer State
  let audioCtx = null;
  let analyser = null;
  let sourceNode = null;
  let visualizerAnimId = null;
  let isListening = false;
  let isSpeaking = false;

  // Initialize Canvas Visualizer
  const canvasCtx = audioVisualizer.getContext("2d");
  function resizeCanvas() {
    audioVisualizer.width = audioVisualizer.parentElement.clientWidth;
    audioVisualizer.height = audioVisualizer.parentElement.clientHeight;
  }
  resizeCanvas();
  window.addEventListener("resize", resizeCanvas);

  // ----------------------------------------------------
  // AMBIENT & REACTIVE VISUALIZER ANIMATION
  // ----------------------------------------------------
  let wavePhase = 0;
  function renderVisualizer() {
    visualizerAnimId = requestAnimationFrame(renderVisualizer);
    const width = audioVisualizer.width;
    const height = audioVisualizer.height;
    canvasCtx.clearRect(0, 0, width, height);

    if (isSpeaking && analyser) {
      const bufferLength = analyser.frequencyBinCount;
      const dataArray = new Uint8Array(bufferLength);
      analyser.getByteFrequencyData(dataArray);

      const barCount = 36;
      const step = Math.floor(bufferLength / barCount);
      const barWidth = (width / barCount) - 3;

      for (let i = 0; i < barCount; i++) {
        const val = dataArray[i * step] || 0;
        const barHeight = Math.max(4, (val / 255) * height * 0.9);
        const x = i * (barWidth + 3);
        const y = (height - barHeight) / 2;

        const gradient = canvasCtx.createLinearGradient(0, y, 0, y + barHeight);
        gradient.addColorStop(0, "#00f2fe");
        gradient.addColorStop(0.5, "#4facfe");
        gradient.addColorStop(1, "#00ffd2");

        canvasCtx.fillStyle = gradient;
        canvasCtx.shadowBlur = 8;
        canvasCtx.shadowColor = "#00f2fe";
        canvasCtx.fillRect(x, y, barWidth, barHeight);
      }
    } else if (isListening) {
      // Dynamic listening waves
      wavePhase += 0.08;
      canvasCtx.beginPath();
      canvasCtx.lineWidth = 2.5;
      canvasCtx.strokeStyle = "#00ffd2";
      canvasCtx.shadowBlur = 12;
      canvasCtx.shadowColor = "#00ffd2";

      for (let x = 0; x < width; x += 3) {
        const y = height / 2 + Math.sin(x * 0.035 + wavePhase) * (height * 0.32);
        if (x === 0) canvasCtx.moveTo(x, y);
        else canvasCtx.lineTo(x, y);
      }
      canvasCtx.stroke();
    } else {
      // Subtle Idle Ambient Pulse
      wavePhase += 0.03;
      canvasCtx.beginPath();
      canvasCtx.lineWidth = 1.5;
      canvasCtx.strokeStyle = "rgba(0, 242, 254, 0.35)";
      canvasCtx.shadowBlur = 6;
      canvasCtx.shadowColor = "rgba(0, 242, 254, 0.3)";

      for (let x = 0; x < width; x += 4) {
        const y = height / 2 + Math.sin(x * 0.02 + wavePhase) * 5;
        if (x === 0) canvasCtx.moveTo(x, y);
        else canvasCtx.lineTo(x, y);
      }
      canvasCtx.stroke();
    }
  }
  renderVisualizer();

  // Setup Web Audio connection to audioPlayer
  function setupAudioContext() {
    if (!audioCtx) {
      const AudioContextClass = window.AudioContext || window.webkitAudioContext;
      audioCtx = new AudioContextClass();
      analyser = audioCtx.createAnalyser();
      analyser.fftSize = 128;
      sourceNode = audioCtx.createMediaElementSource(audioPlayer);
      sourceNode.connect(analyser);
      analyser.connect(audioCtx.destination);
    }
    if (audioCtx.state === "suspended") {
      audioCtx.resume();
    }
  }

  // ----------------------------------------------------
  // MESSAGE DISPLAY & CHAT LOGIC
  // ----------------------------------------------------
  function addMessage(sender, text, isUser = false) {
    const bubble = document.createElement("div");
    bubble.className = `message-bubble ${isUser ? "user" : "jarvis"}`;

    const senderHeader = document.createElement("div");
    senderHeader.className = "message-sender";
    senderHeader.innerHTML = isUser
      ? '<i class="fa-solid fa-user"></i> You'
      : '<i class="fa-solid fa-atom"></i> Jarvies Core';

    const contentDiv = document.createElement("div");
    contentDiv.className = "message-content";
    contentDiv.textContent = text;

    bubble.appendChild(senderHeader);
    bubble.appendChild(contentDiv);
    chatMessages.appendChild(bubble);

    chatMessages.scrollTop = chatMessages.scrollHeight;
    return bubble;
  }

  function showToast(text) {
    hudToast.textContent = text;
    hudToast.classList.add("show");
    setTimeout(() => {
      hudToast.classList.remove("show");
    }, 3200);
  }

  async function sendPrompt(text) {
    const trimmed = text.trim();
    if (!trimmed) return;

    // Add user message
    addMessage("You", trimmed, true);
    chatInput.value = "";

    // Show temporary thinking message
    const thinkingBubble = addMessage("Jarvies Core", "Thinking...", false);
    thinkingBubble.classList.add("thinking");

    // Update reactor state
    reactorStatusText.textContent = "Processing Query...";
    reactorSubtext.textContent = "Interpreting intent and executing tools";
    reactorWrapper.classList.add("speaking");

    try {
      const payload = {
        message: trimmed,
        voice: voiceSelector.value,
        play_on_speaker: speakerAudioToggle.checked
      };

      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const data = await res.json();

      // Remove thinking bubble
      thinkingBubble.remove();

      // Add actual response
      addMessage("Jarvies Core", data.reply || "Done.", false);

      if (data.tool_executed) {
        showToast(`Tool Executed: ${data.tool_executed}`);
      }

      // Play Neural Voice Audio if available
      if (data.audio_url) {
        setupAudioContext();
        audioPlayer.src = data.audio_url;
        isSpeaking = true;
        reactorStatusText.textContent = "Speaking...";
        reactorSubtext.textContent = `Edge Neural Voice (${voiceSelector.options[voiceSelector.selectedIndex].text})`;

        audioPlayer.play().catch(err => {
          console.warn("Audio autoplay blocked by browser policy:", err);
          isSpeaking = false;
          reactorWrapper.classList.remove("speaking");
          reactorStatusText.textContent = "Jarvies Core Ready";
          reactorSubtext.textContent = "Click the Arc Reactor or press the Mic button to talk";
        });

        audioPlayer.onended = () => {
          isSpeaking = false;
          reactorWrapper.classList.remove("speaking");
          reactorStatusText.textContent = "Jarvies Core Ready";
          reactorSubtext.textContent = "Click the Arc Reactor or press the Mic button to talk";
        };
      } else {
        reactorWrapper.classList.remove("speaking");
        reactorStatusText.textContent = "Jarvies Core Ready";
        reactorSubtext.textContent = "Click the Arc Reactor or press the Mic button to talk";
      }

    } catch (err) {
      thinkingBubble.remove();
      addMessage("Jarvies Core", "Sir, request process karne me error aaya: " + err.message, false);
      reactorWrapper.classList.remove("speaking");
      reactorStatusText.textContent = "Jarvies Core Ready";
      reactorSubtext.textContent = "Click the Arc Reactor or press the Mic button to talk";
    }
  }

  // ----------------------------------------------------
  // EVENT LISTENERS: SEND BUTTON & ENTER KEY
  // ----------------------------------------------------
  sendBtn.addEventListener("click", () => {
    sendPrompt(chatInput.value);
  });

  chatInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendPrompt(chatInput.value);
    }
  });

  // Global Quick Prompt Trigger
  window.sendQuickPrompt = (promptText) => {
    chatInput.value = promptText;
    sendPrompt(promptText);
  };

  // ----------------------------------------------------
  // WEB SPEECH API (VOICE INPUT IN BROWSER)
  // ----------------------------------------------------
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  let recognition = null;

  if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = "en-IN"; // Supports English + Hinglish recognition

    recognition.onstart = () => {
      isListening = true;
      reactorWrapper.classList.add("listening");
      micBtn.classList.add("listening");
      reactorStatusText.textContent = "Listening to you...";
      reactorSubtext.textContent = "Speak clearly into your microphone";
    };

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      chatInput.value = transcript;
      sendPrompt(transcript);
    };

    recognition.onerror = (event) => {
      console.warn("Speech recognition error:", event.error);
      showToast("Speech recognition: " + event.error);
      stopListening();
    };

    recognition.onend = () => {
      stopListening();
    };
  }

  function startListening() {
    if (!recognition) {
      showToast("Speech Recognition not supported in this browser. Please type your query.");
      return;
    }
    if (isListening) {
      recognition.stop();
      return;
    }
    try {
      recognition.start();
    } catch (e) {
      console.warn("Recognition already active", e);
    }
  }

  function stopListening() {
    isListening = false;
    reactorWrapper.classList.remove("listening");
    micBtn.classList.remove("listening");
    if (!isSpeaking) {
      reactorStatusText.textContent = "Jarvies Core Ready";
      reactorSubtext.textContent = "Click the Arc Reactor or press the Mic button to talk";
    }
  }

  // Bind Voice Triggers
  micBtn.addEventListener("click", startListening);
  reactorWrapper.addEventListener("click", startListening);

  // ----------------------------------------------------
  // TOOL EXECUTION API
  // ----------------------------------------------------
  window.executeTool = async (action, param = "") => {
    showToast(`Executing ${action}...`);
    try {
      const res = await fetch("/api/execute_tool", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action, param })
      });
      const data = await res.json();
      if (data.success) {
        showToast(data.result);
        addMessage("Jarvies Core", `⚡ Action: ${data.result}`, false);
      } else {
        showToast(`Error: ${data.error}`);
      }
    } catch (e) {
      showToast(`Execution error: ${e.message}`);
    }
  };

  // ----------------------------------------------------
  // SYSTEM STATS POLLING (CPU, RAM, BATTERY)
  // ----------------------------------------------------
  async function updateTelemetry() {
    try {
      const res = await fetch("/api/system/stats");
      const stats = await res.json();

      if (stats.cpu_percent !== undefined) {
        cpuBadge.textContent = `${stats.cpu_percent}%`;
        ramBadge.textContent = `${stats.memory_percent}% (${stats.memory_used_gb}/${stats.memory_total_gb} GB)`;

        if (stats.battery_percent !== null && stats.battery_percent !== undefined) {
          batteryBadge.textContent = `${stats.battery_percent}%${stats.battery_plugged ? ' ⚡' : ''}`;
        } else {
          document.getElementById("batteryBadgeWrapper").style.display = "none";
        }

        // Update Study / Gate mode buttons visual state
        const studyBtn = document.getElementById("toolStudyMode");
        const gateBtn = document.getElementById("toolGateMode");
        if (studyBtn) studyBtn.classList.toggle("active-mode", Boolean(stats.study_mode));
        if (gateBtn) gateBtn.classList.toggle("active-mode", Boolean(stats.gate_mode));
      }
    } catch (e) {
      // Server might be busy
    }
  }

  // Poll every 2.5 seconds
  setInterval(updateTelemetry, 2500);
  updateTelemetry();
});
