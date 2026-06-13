from __future__ import annotations

import json
import os
import hashlib
from pathlib import Path

from flask import Flask, jsonify, render_template, request
try:
    from dotenv import load_dotenv
except ImportError:  # Keep template mode usable before optional env support is installed.
    load_dotenv = None

from simulator import ExposureCalculator, PhishingSimulator, defense_recommendations


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "profiles.json"
ENV_PATH = BASE_DIR / ".env"

app = Flask(__name__)


def load_local_env() -> None:
    if load_dotenv:
        load_dotenv(ENV_PATH, override=True)
        return

    if not ENV_PATH.exists():
        return

    for raw_line in ENV_PATH.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if value:
            os.environ[key] = value


load_local_env()


def get_api_key_info() -> dict:
    if os.environ.get("GEMINI_API_KEY"):
        key = os.environ["GEMINI_API_KEY"]
        source = "GEMINI_API_KEY"
    elif os.environ.get("GOOGLE_API_KEY"):
        key = os.environ["GOOGLE_API_KEY"]
        source = "GOOGLE_API_KEY"
    else:
        key = ""
        source = None

    fingerprint = hashlib.sha256(key.encode("utf-8")).hexdigest()[:12] if key else None
    return {"key": key, "source": source, "fingerprint": fingerprint}


def load_config() -> dict:
    with DATA_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def get_services(use_llm: bool = False) -> tuple[dict, ExposureCalculator, PhishingSimulator]:
    config = load_config()
    api_key = get_api_key_info()["key"]
    model = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
    simulator = PhishingSimulator(use_llm=use_llm, api_key=api_key, model=model)
    return config, ExposureCalculator(config["exposure_weights"]), simulator


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/profiles")
def profiles():
    config, calculator, _ = get_services()
    payload = []
    for profile in config["profiles"]:
        exposure = calculator.calculate(profile["details"])
        payload.append(
            {
                "id": profile["id"],
                "name": profile["name"],
                "title": profile["title"],
                "organization": profile["organization"],
                "city": profile["city"],
                "summary": profile["summary"],
                "color": profile["color"],
                "exposure_score": exposure.score,
                "risk_level": exposure.level,
                "factors": exposure.factors,
            }
        )
    return jsonify({"profiles": payload, "llm_available": bool(os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"))})


@app.get("/api/llm-status")
def llm_status():
    key_info = get_api_key_info()
    return jsonify(
        {
            "llm_available": bool(key_info["key"]),
            "key_source": key_info["source"],
            "key_fingerprint": key_info["fingerprint"],
            "model": os.environ.get("GEMINI_MODEL", "gemini-2.0-flash"),
            "env_file_present": ENV_PATH.exists(),
        }
    )


@app.get("/api/profile/<profile_id>")
def profile_detail(profile_id: str):
    config, calculator, _ = get_services()
    profile = next((item for item in config["profiles"] if item["id"] == profile_id), None)
    if profile is None:
        return jsonify({"error": "Profile not found"}), 404

    exposure = calculator.calculate(profile["details"])
    return jsonify({**profile, "exposure_score": exposure.score, "risk_level": exposure.level, "factors": exposure.factors})


@app.post("/api/simulate")
def simulate():
    body = request.get_json(silent=True) or {}
    profile_id = body.get("profile_id")
    use_llm = bool(body.get("use_llm"))
    
    config, calculator, simulator = get_services(use_llm=use_llm)
    profile = next((item for item in config["profiles"] if item["id"] == profile_id), None)
    if profile is None:
        return jsonify({"error": "Profile not found"}), 404

    exposure = calculator.calculate(profile["details"])
    
    # Check LLM availability BEFORE attempting generation
    if use_llm:
        key_info = get_api_key_info()
        if not key_info["key"]:
            return jsonify({
                "error": "LLM mode requires GEMINI_API_KEY or GOOGLE_API_KEY environment variable",
                "llm_available": False,
                "fix": "Set the API key in .env file or environment variable and restart",
                "profile": profile,
                "exposure_score": exposure.score,
                "risk_level": exposure.level,
                "factors": exposure.factors,
                "recommendations": defense_recommendations(exposure),
            }), 400
    
    try:
        if use_llm:
            # This will raise RuntimeError if LLM fails (no fallback)
            email = simulator.generate_email(profile, exposure)
            generation_method = "Gemini LLM"
        else:
            email = simulator.generate_template_email(profile, exposure)
            generation_method = "Template"

        metrics = simulator.evaluate(email, profile, exposure)
        key_info = get_api_key_info()
        
        return jsonify(
            {
                "profile": profile,
                "exposure_score": exposure.score,
                "risk_level": exposure.level,
                "factors": exposure.factors,
                "email": email,
                "generation_method": generation_method,
                "llm_requested": use_llm,
                "llm_available": bool(key_info["key"]),
                "key_fingerprint": key_info["fingerprint"],
                "llm_error": None,
                "metrics": metrics,
                "recommendations": defense_recommendations(exposure),
            }
        )
        
    except RuntimeError as e:
        # LLM failed - return error, no fallback
        return jsonify({
            "error": str(e),
            "profile": profile,
            "exposure_score": exposure.score,
            "risk_level": exposure.level,
            "factors": exposure.factors,
            "llm_requested": use_llm,
            "llm_available": bool(os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")),
            "key_fingerprint": get_api_key_info()["fingerprint"],
            "llm_error": str(e),
            "recommendations": defense_recommendations(exposure),
        }), 503  # Service Unavailable


@app.get("/api/compare")
def compare():
    """Comparison endpoint - ALWAYS uses template mode (no LLM)"""
    config, calculator, _ = get_services(use_llm=False)
    
    # Create a simulator instance WITHOUT LLM for template generation
    template_simulator = PhishingSimulator(use_llm=False, api_key=None)
    
    results = []
    for profile in config["profiles"]:
        exposure = calculator.calculate(profile["details"])
        # Use the instance method for template generation
        email = template_simulator.generate_template_email(profile, exposure)
        metrics = PhishingSimulator.evaluate(email, profile, exposure)
        results.append(
            {
                "id": profile["id"],
                "name": profile["name"],
                "score": exposure.score,
                "risk_level": exposure.level,
                "convincingness": metrics["convincingness"],
                "color": profile["color"],
            }
        )
    return jsonify(results)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
