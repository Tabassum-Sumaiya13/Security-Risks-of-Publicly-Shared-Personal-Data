let profiles = [];
let selectedProfile = null;
let comparison = [];
let llmAvailable = false;

const profileList = document.getElementById("profileList");
const profileCount = document.getElementById("profileCount");
const emptyState = document.getElementById("emptyState");
const results = document.getElementById("results");
const simulateButton = document.getElementById("simulateButton");
const llmToggle = document.getElementById("llmToggle");

document.addEventListener("DOMContentLoaded", async () => {
    await loadProfiles();
    await loadComparison();
});

simulateButton.addEventListener("click", runSimulation);

async function loadProfiles() {
    const response = await fetch("/api/profiles");
    const data = await response.json();
    profiles = data.profiles;
    llmAvailable = data.llm_available;
    llmToggle.disabled = !llmAvailable;
    llmToggle.parentElement.title = llmAvailable
        ? "Generate with Gemini using GEMINI_API_KEY."
        : "Set GEMINI_API_KEY and restart Flask to enable LLM mode.";
    profileCount.textContent = profiles.length;
    profileList.innerHTML = profiles.map(renderProfileCard).join("");

    document.querySelectorAll(".profile-card").forEach((card) => {
        card.addEventListener("click", () => selectProfile(card.dataset.id));
    });
}

async function loadComparison() {
    const response = await fetch("/api/compare");
    comparison = await response.json();
}

function renderProfileCard(profile) {
    const initials = profile.name.split(" ").map((part) => part[0]).join("");
    return `
        <button class="profile-card" data-id="${profile.id}" type="button">
            <span class="avatar" style="--accent:${profile.color}">${initials}</span>
            <span class="profile-copy">
                <strong>${profile.name}</strong>
                <small>${profile.title || "Demo profile"}${profile.organization ? " at " + profile.organization : ""}</small>
                <span class="score-line">
                    <span class="mini-bar"><span style="width:${profile.exposure_score * 100}%; background:${profile.color}"></span></span>
                    ${profile.risk_level} / ${profile.exposure_score.toFixed(2)}
                </span>
            </span>
        </button>
    `;
}

function selectProfile(id) {
    selectedProfile = profiles.find((profile) => profile.id === id);
    document.querySelectorAll(".profile-card").forEach((card) => {
        card.classList.toggle("active", card.dataset.id === id);
    });

    emptyState.classList.add("hidden");
    results.classList.remove("hidden");

    document.getElementById("selectedName").textContent = selectedProfile.name;
    document.getElementById("selectedMeta").textContent = [
        selectedProfile.title,
        selectedProfile.organization,
        selectedProfile.city
    ].filter(Boolean).join(" / ");
    document.getElementById("exposureScore").textContent = selectedProfile.exposure_score.toFixed(2);
    document.getElementById("riskLevel").textContent = selectedProfile.risk_level;
    document.getElementById("convincingness").textContent = "-";
    document.getElementById("emailPreview").textContent = "Run the simulation to generate a safe training example.";
    document.getElementById("generationMethod").textContent = "Template";
    document.getElementById("defenseList").innerHTML = "";

    renderFactors(selectedProfile.factors);
    drawComparison();
}

async function runSimulation() {
    if (!selectedProfile) return;

    simulateButton.disabled = true;
    simulateButton.textContent = "Running...";

    try {
        const response = await fetch("/api/simulate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ profile_id: selectedProfile.id, use_llm: llmToggle.checked })
        });
        const result = await response.json();

        document.getElementById("exposureScore").textContent = result.exposure_score.toFixed(2);
        document.getElementById("riskLevel").textContent = result.risk_level;

        if (!response.ok) {
            document.getElementById("convincingness").textContent = "-";
            document.getElementById("emailPreview").textContent = result.error || "Simulation failed.";
            document.getElementById("generationMethod").textContent = result.llm_requested
                ? "Gemini error"
                : "Simulation error";
            document.getElementById("defenseList").innerHTML = (result.recommendations || [])
                .map((item) => `<li>${item}</li>`)
                .join("");
            renderFactors(result.factors || {});
            return;
        }

        document.getElementById("convincingness").textContent = `${result.metrics.convincingness}/10`;
        document.getElementById("emailPreview").textContent = result.email;
        document.getElementById("generationMethod").textContent = result.llm_error
            ? "Template fallback"
            : result.generation_method;
        if (result.llm_error) {
            console.warn("Gemini generation failed:", result.llm_error);
        }
        document.getElementById("defenseList").innerHTML = result.recommendations
            .map((item) => `<li>${item}</li>`)
            .join("");
        renderFactors(result.factors);
    } finally {
        simulateButton.disabled = false;
        simulateButton.textContent = "Run simulation";
    }
}

function renderFactors(factors) {
    const labels = {
        identity: "Identity",
        location: "Location",
        social: "Social graph",
        behavioral: "Behavior",
        preferences: "Interests"
    };

    document.getElementById("factorBars").innerHTML = Object.entries(factors).map(([key, value]) => `
        <div class="factor">
            <div>
                <strong>${labels[key] || key}</strong>
                <span>${Math.round(value * 100)}%</span>
            </div>
            <div class="bar"><span style="width:${value * 100}%"></span></div>
        </div>
    `).join("");
}

function drawComparison() {
    const canvas = document.getElementById("comparisonChart");
    const ctx = canvas.getContext("2d");
    const width = canvas.width;
    const height = canvas.height;
    const pad = 42;

    ctx.clearRect(0, 0, width, height);
    ctx.fillStyle = "#ffffff";
    ctx.fillRect(0, 0, width, height);

    ctx.strokeStyle = "#d8dee8";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(pad, pad);
    ctx.lineTo(pad, height - pad);
    ctx.lineTo(width - pad, height - pad);
    ctx.stroke();

    ctx.fillStyle = "#526071";
    ctx.font = "12px Inter, sans-serif";
    ctx.fillText("Convincingness", 12, 24);
    ctx.fillText("Exposure", width - 96, height - 12);

    comparison.forEach((item) => {
        const x = pad + item.score * (width - pad * 2);
        const y = height - pad - (item.convincingness / 10) * (height - pad * 2);
        const active = selectedProfile && item.id === selectedProfile.id;

        ctx.beginPath();
        ctx.arc(x, y, active ? 10 : 7, 0, Math.PI * 2);
        ctx.fillStyle = item.color;
        ctx.fill();
        ctx.lineWidth = active ? 4 : 2;
        ctx.strokeStyle = active ? "#111827" : "#ffffff";
        ctx.stroke();
    });
}
