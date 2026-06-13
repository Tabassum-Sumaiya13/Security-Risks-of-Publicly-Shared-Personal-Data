from __future__ import annotations

from dataclasses import dataclass
from typing import Any

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    genai = None
    GENAI_AVAILABLE = False


@dataclass(frozen=True)
class ExposureResult:
    score: float
    level: str
    factors: dict[str, float]


class ExposureCalculator:
    def __init__(self, weights: dict[str, float]):
        self.weights = weights
        self.total_weight = sum(weights.values()) or 1

    def calculate(self, details: dict[str, Any]) -> ExposureResult:
        factors = {
            "identity": 1.0 if details.get("public_photo") or details.get("username") else 0.0,
            "location": 1.0 if details.get("city") else 0.0,
            "social": 1.0 if details.get("colleagues") else (0.45 if details.get("workplace") else 0.0),
            "behavioral": 1.0 if details.get("routine") or details.get("recent_activity") else 0.0,
            "preferences": 1.0 if details.get("interests") else 0.0,
        }
        weighted = sum(self.weights[key] * factors[key] for key in self.weights)
        score = round(weighted / self.total_weight, 2)
        return ExposureResult(score=score, level=self.level_for(score), factors=factors)

    @staticmethod
    def level_for(score: float) -> str:
        if score < 0.25:
            return "Low"
        if score < 0.55:
            return "Medium"
        if score < 0.8:
            return "High"
        return "Critical"


class PhishingSimulator:
    def __init__(self, use_llm: bool = False, api_key: str | None = None, model: str = "gemini-2.0-flash"):
        self.use_llm = use_llm
        self.model = model
        self.client = None
        self.last_error: str | None = None
        
        # Check if we should initialize LLM
        if use_llm:
            if not GENAI_AVAILABLE:
                raise RuntimeError(
                    "LLM mode requested but google-generativeai package not installed. "
                    "Run: pip install google-generativeai"
                )
            if not api_key:
                raise RuntimeError(
                    "LLM mode requested but no API key provided. "
                    "Set GEMINI_API_KEY in .env file"
                )
            
            # Initialize Gemini
            try:
                genai.configure(api_key=api_key)
                self.client = genai.GenerativeModel(model)
                print(f"✅ Gemini initialized with model: {model}")
            except Exception as e:
                raise RuntimeError(f"Failed to initialize Gemini: {e}")

    def generate_email(self, profile: dict[str, Any], exposure: ExposureResult) -> str:
        """Generate email - NO FALLBACK. If LLM fails, raise exception."""
        if self.client:
            return self._generate_with_llm(profile, exposure)
        
        # Clear error message
        if self.use_llm:
            raise RuntimeError(
                "LLM mode requested but Gemini client not initialized. "
                "Check that API key is valid and restart the server."
            )
        else:
            raise RuntimeError(
                "LLM mode requested but use_llm=False. This should not happen."
            )

    def _generate_with_llm(self, profile: dict[str, Any], exposure: ExposureResult) -> str:
        details = profile["details"]
        
        prompt = f"""
Create a simulated spear-phishing awareness training email for a classroom/demo app.

⚠️ CRITICAL SAFETY RULES:
- Start with "[SECURITY TRAINING SIMULATION - DO NOT SEND]"
- Use only the synthetic profile details below
- Do NOT ask for passwords, MFA codes, payment, credential entry, or malware
- Use exactly "[SIMULATED LINK]" instead of any URL
- Make it realistic enough for training

Synthetic profile:
- Name: {profile["name"]}
- Role: {profile.get("title") or "Unknown"}
- Organization: {details.get("workplace") or "Unknown"}
- City: {details.get("city") or "Unknown"}
- Colleagues: {", ".join(details.get("colleagues", [])) or "Unknown"}
- Recent activity: {details.get("recent_activity") or "Unknown"}
- Routine: {details.get("routine") or "Unknown"}
- Interests: {", ".join(details.get("interests", [])) or "Unknown"}
- Exposure score: {exposure.score}
- Risk level: {exposure.level}

Generate a realistic phishing email that demonstrates how attackers use this information.
Keep it under 300 words.
""".strip()

        try:
            response = self.client.generate_content(prompt)
            
            if not response or not response.text:
                raise RuntimeError("Empty response from Gemini API")
            
            email_content = response.text.strip()
            
            # Ensure safety warning
            if "[SECURITY TRAINING SIMULATION" not in email_content:
                email_content = "[SECURITY TRAINING SIMULATION - DO NOT SEND]\n\n" + email_content
                
            return email_content
            
        except Exception as exc:
            self.last_error = str(exc)
            raise RuntimeError(f"Gemini API call failed: {exc}")

    def generate_template_email(self, profile: dict[str, Any], exposure: ExposureResult) -> str:
        """Instance method for template generation (no LLM)"""
        details = profile["details"]
        name = profile["name"]
        workplace = details.get("workplace") or "your organization"
        colleague = details.get("colleagues", ["IT Support"])[0] if details.get("colleagues") else "IT Support"
        recent = details.get("recent_activity")
        routine = details.get("routine")
        interest = details.get("interests", ["security review"])[0] if details.get("interests") else "security review"

        if exposure.score < 0.25:
            return (
                "[SECURITY TRAINING SIMULATION - DO NOT SEND]\n\n"
                "Subject: Account security reminder\n\n"
                f"Hi {name},\n\n"
                "Please review the latest account security checklist when you have a moment.\n\n"
                "[SIMULATED LINK]\n\n"
                "Security Awareness Team"
            )

        if exposure.score < 0.55:
            return (
                "[SECURITY TRAINING SIMULATION - DO NOT SEND]\n\n"
                f"Subject: {workplace} security policy review\n\n"
                f"Hi {name},\n\n"
                f"We are refreshing internal security guidance for {workplace}. "
                "Please review the short policy summary below.\n\n"
                "[SIMULATED LINK]\n\n"
                "IT Support"
            )

        context = f" after you {recent}" if recent else ""
        timing = f" Since you {routine}, this should only take a minute." if routine else ""
        return (
            "[SECURITY TRAINING SIMULATION - DO NOT SEND]\n\n"
            f"Subject: Follow-up on {interest} access\n\n"
            f"Hi {name},\n\n"
            f"This is {colleague}. I am following up on the {interest} access review for {workplace}{context}."
            f"{timing}\n\n"
            "Please confirm the simulated request here: [SIMULATED LINK]\n\n"
            f"Thanks,\n{colleague}\n\n"
            "Training note: this message is generated for awareness only."
        )

    @staticmethod
    def evaluate(email: str, profile: dict[str, Any], exposure: ExposureResult) -> dict[str, Any]:
        details = profile["details"]
        checked_values = [
            profile.get("name"),
            details.get("workplace"),
            details.get("city"),
            details.get("recent_activity"),
            details.get("routine"),
            *details.get("interests", []),
            *details.get("colleagues", []),
        ]
        available = sum(1 for value in checked_values if value)
        used = sum(1 for value in checked_values if value and value.lower() in email.lower())
        convincingness = min(10, round(2 + exposure.score * 6 + used * 0.45, 1))
        probability = round(0.04 + exposure.score * 0.46, 2)

        return {
            "available_details": available,
            "used_details": used,
            "convincingness": convincingness,
            "simulated_success_probability": probability,
        }


def defense_recommendations(exposure: ExposureResult) -> list[str]:
    recommendations = [
        "Use multi-factor authentication on important accounts.",
        "Confirm unexpected requests through a separate trusted channel.",
        "Treat messages that reference personal details as higher risk, not more trustworthy.",
    ]
    if exposure.score >= 0.55:
        recommendations.append("Review public profile fields, old posts, tagged photos, and visible colleague lists.")
    if exposure.score >= 0.8:
        recommendations.append("Reduce routine, travel, and relationship details that make timing and impersonation easier.")
    return recommendations