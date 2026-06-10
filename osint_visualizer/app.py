from flask import Flask, render_template, request, jsonify
import requests
import re
import time
import json
from datetime import datetime

app = Flask(__name__)

class OSINTAttackSimulator:
    """Simulates an OSINT attack for visualization"""
    
    def __init__(self, username):
        self.username = username
        self.attack_log = []
        self.collected_data = {
            "identity": {},
            "social_media": [],
            "email_addresses": [],
            "breach_data": [],
            "relationships": [],
            "behavioral": {},
            "risk_score": 0,
            "attack_readiness": "LOW"
        }
    
    def log(self, message, step_type="info"):
        """Add entry to attack log"""
        self.attack_log.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "message": message,
            "type": step_type  # info, success, warning, error
        })
        print(f"[{step_type.upper()}] {message}")
    
    def simulate_step(self, step_name="", duration=0.5):
        """Simulate a step with delay"""
        time.sleep(duration)
        return True
    
    def phase1_target_selection(self):
        """Phase 1: Identify target and basic info"""
        self.log("🔍 PHASE 1: Target Selection & Initial Recon", "info")
        
        # Simulate searching for target
        self.log(f"   → Scanning for username: @{self.username}", "info")
        self.simulate_step("searching")
        
        # Extract potential full name from username pattern
        name_patterns = [
            (r'^([a-z]+)\.([a-z]+)$', r'\1 \2'),  # john.doe
            (r'^([a-z]+)_([a-z]+)$', r'\1 \2'),  # john_doe
            (r'^([a-z]+)(\d+)$', r'\1'),          # john123
        ]
        
        full_name = self.username.capitalize()
        for pattern, replacement in name_patterns:
            match = re.match(pattern, self.username.lower())
            if match:
                full_name = re.sub(pattern, replacement, self.username.lower()).title()
                break
        
        self.collected_data["identity"]["username"] = self.username
        self.collected_data["identity"]["full_name"] = full_name
        
        self.log(f"   ✓ Target identified: {full_name}", "success")
        self.log(f"   ✓ Username registered across 47 platforms (estimate)", "success")
        
        # Simulate location detection
        self.log(f"   → Geolocating IP patterns...", "info")
        self.simulate_step()
        self.collected_data["identity"]["location"] = "[REDACTED - US based]"
        self.log(f"   ✓ Location cluster identified", "success")
        
        return True
    
    def phase2_data_collection(self):
        """Phase 2: Collect data from platforms"""
        self.log("\n📊 PHASE 2: Multi-Platform Data Collection", "info")
        
        platforms = [
            ("Twitter/X", "https://twitter.com/" + self.username, "Profile found, 847 followers"),
            ("Instagram", "https://instagram.com/" + self.username, "Profile found, 23 posts"),
            ("LinkedIn", "https://linkedin.com/in/" + self.username, "Professional profile"),
            ("GitHub", "https://github.com/" + self.username, "Repository activity detected"),
            ("Facebook", "https://facebook.com/" + self.username, "Limited public data"),
        ]
        
        for platform, url, details in platforms:
            self.log(f"   → Scraping {platform}...", "info")
            self.simulate_step(duration=0.3)
            self.collected_data["social_media"].append({
                "platform": platform,
                "url": url,
                "details": details
            })
            self.log(f"   ✓ {platform}: {details}", "success")
        
        # Extract email patterns
        self.log(f"\n   → Searching for email addresses...", "info")
        email_patterns = [
            f"{self.username}@gmail.com",
            f"{self.collected_data['identity']['full_name'].lower().replace(' ', '.')}@company.com",
            f"{self.username}@outlook.com"
        ]
        
        for email in email_patterns[:1]:  # Simulate finding one
            self.collected_data["email_addresses"].append({
                "email": email,
                "source": "Pattern matching + breach correlation",
                "confidence": "HIGH"
            })
            self.log(f"   ✓ Email discovered: {email}", "success")
            self.simulate_step(duration=0.2)
        
        return True
    
    def phase3_breach_check(self):
        """Phase 3: Check breach databases"""
        self.log("\n💀 PHASE 3: Breach Database Correlation", "warning")
        
        if self.collected_data["email_addresses"]:
            email = self.collected_data["email_addresses"][0]["email"]
            self.log(f"   → Checking {email} in breach databases...", "info")
            self.simulate_step(duration=0.8)
            
            breaches = [
                {"name": "LinkedIn 2021", "data": "Email, Password hash"},
                {"name": "Collection #1", "data": "Email, Password"},
                {"name": "AntiPublic", "data": "Email, Password hash"}
            ]
            
            for breach in breaches:
                self.collected_data["breach_data"].append(breach)
                self.log(f"   ⚠ Found in: {breach['name']} ({breach['data']})", "warning")
                self.simulate_step(duration=0.2)
        
        return True
    
    def phase4_relationship_mapping(self):
        """Phase 4: Map relationships and network"""
        self.log("\n👥 PHASE 4: Social Graph & Relationship Mapping", "info")
        
        relationships = [
            "Sarah Chen - Manager at TechCorp (LinkedIn)",
            "Mike Johnson - Coworker, frequent interactions (Twitter)",
            "Emily Davis - Likely family member (Instagram photos)",
            "David Kim - Direct report (LinkedIn)"
        ]
        
        for rel in relationships:
            self.log(f"   → Identifying: {rel.split(' - ')[0]}", "info")
            self.simulate_step(duration=0.2)
            self.collected_data["relationships"].append(rel)
            self.log(f"   ✓ Mapped: {rel}", "success")
        
        return True
    
    def phase5_behavioral_analysis(self):
        """Phase 5: Analyze behavior patterns"""
        self.log("\n🧠 PHASE 5: Behavioral Pattern Analysis", "info")
        
        self.log(f"   → Analyzing posting schedules...", "info")
        self.simulate_step(duration=0.3)
        
        patterns = {
            "active_hours": "9 AM - 11 AM, 7 PM - 10 PM EST",
            "common_topics": ["Technology", "Security", "Gaming", "Coffee"],
            "emotional_state": "Recent posts indicate work stress",
            "vulnerabilities": [
                "Recently complained about technical issues",
                "Discussed upcoming travel",
                "Mentioned feeling overwhelmed"
            ]
        }
        
        self.collected_data["behavioral"] = patterns
        
        self.log(f"   ✓ Active hours identified: {patterns['active_hours']}", "success")
        self.log(f"   ✓ Interests detected: {', '.join(patterns['common_topics'])}", "success")
        self.log(f"   ⚠ Emotional vulnerability detected: {patterns['emotional_state']}", "warning")
        
        for vuln in patterns['vulnerabilities']:
            self.log(f"   ⚠ Vulnerability: {vuln}", "warning")
            self.simulate_step(duration=0.2)
        
        return True
    
    def phase6_risk_assessment(self):
        """Phase 6: Calculate risk score"""
        self.log("\n🎯 PHASE 6: Attack Risk Assessment", "info")
        
        risk_factors = {
            "public_profile_photos": 15,
            "email_exposed": 25,
            "breach_data_found": 30,
            "relationships_mapped": 10,
            "behavioral_patterns": 10,
            "location_identified": 10
        }
        
        total_risk = 0
        for factor, weight in risk_factors.items():
            total_risk += weight
            self.log(f"   → {factor.replace('_', ' ').title()}: +{weight}", "info")
            self.simulate_step(duration=0.1)
        
        self.collected_data["risk_score"] = total_risk
        
        if total_risk >= 70:
            level = "CRITICAL"
            self.log(f"\n   ⚠⚠⚠ RISK SCORE: {total_risk}/100 - {level} - ATTACK IMMINENT", "error")
        elif total_risk >= 40:
            level = "HIGH"
            self.log(f"\n   ⚠ RISK SCORE: {total_risk}/100 - {level} - VULNERABLE", "warning")
        else:
            level = "MEDIUM"
            self.log(f"\n   RISK SCORE: {total_risk}/100 - {level}", "info")
        
        self.collected_data["attack_readiness"] = level
        
        return True
    
    def generate_phishing_email(self):
        """Generate personalized phishing email"""
        name = self.collected_data["identity"]["full_name"]
        email = self.collected_data["email_addresses"][0]["email"] if self.collected_data["email_addresses"] else "[email]"
        
        email_template = f"""
From: security@internal-verify.com
Subject: URGENT: Security Incident Response Required

Dear {name},

Our security systems detected suspicious activity associated with your account ({email}) from an unrecognized device.

INCIDENT DETAILS:
• Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC
• Location: [REDACTED - matches your recent activity]
• Account: {self.username}

Based on breach data from LinkedIn 2021 (which contained your email), we recommend immediate password rotation.

ACTION REQUIRED:
Click here to verify your identity and secure your account:
🔗 https://secure-portal-verify.com/{self.username}/verify

This link expires in 2 hours.

Reference: SEC-{datetime.now().strftime('%Y%m%d')}-{self.username.upper()}

Security Team
[This is a SIMULATED phishing email for demonstration purposes]
"""
        return email_template
    
    def generate_attack_summary(self):
        """Generate final attack summary"""
        summary = f"""
╔══════════════════════════════════════════════════════════════╗
║                    ATTACK READINESS REPORT                    ║
╠══════════════════════════════════════════════════════════════╣
║ Target: {self.collected_data['identity']['full_name']:<45} ║
║ Username: @{self.username:<44} ║
╠══════════════════════════════════════════════════════════════╣
║ DATA COLLECTED:                                              ║
║ • Social Media Profiles: {len(self.collected_data['social_media']):<38} ║
║ • Emails Found: {len(self.collected_data['email_addresses']):<41} ║
║ • Breach Records: {len(self.collected_data['breach_data']):<40} ║
║ • Relationships: {len(self.collected_data['relationships']):<42} ║
╠══════════════════════════════════════════════════════════════╣
║ RISK SCORE: {self.collected_data['risk_score']}/100 ({self.collected_data['attack_readiness']:<25}) ║
╠══════════════════════════════════════════════════════════════╣
║ ATTACK VECTORS IDENTIFIED:                                   ║
║ • Spear Phishing ✅                                          ║
║ • Credential Reuse ✅ (breach data available)                ║
║ • Social Engineering ✅ (relationships mapped)               ║
║ • Vishing (voice phishing) ✅ (behavioral patterns)          ║
╠══════════════════════════════════════════════════════════════╣
║ RECOMMENDED ATTACK: Spear Phishing + Credential Stuffing     ║
║ ESTIMATED SUCCESS RATE: 87%                                  ║
║ TIME TO COMPROMISE: 15-30 minutes                            ║
╚══════════════════════════════════════════════════════════════╝
"""
        return summary
    
    def run_full_attack(self):
        """Execute complete OSINT attack simulation"""
        self.log("🚀 INITIATING OSINT ATTACK SIMULATION", "warning")
        self.log(f"🎯 Target: @{self.username}", "info")
        self.log("=" * 50, "info")
        
        self.phase1_target_selection()
        self.phase2_data_collection()
        self.phase3_breach_check()
        self.phase4_relationship_mapping()
        self.phase5_behavioral_analysis()
        self.phase6_risk_assessment()
        
        self.log("\n" + "=" * 50, "info")
        self.log("✅ OSINT ATTACK SIMULATION COMPLETE", "success")
        self.log("⚠️  DEMONSTRATION ONLY - No actual attack was executed", "warning")
        
        return {
            "logs": self.attack_log,
            "data": self.collected_data,
            "phishing_email": self.generate_phishing_email(),
            "summary": self.generate_attack_summary()
        }


@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')


@app.route('/api/attack', methods=['POST'])
def run_attack():
    """API endpoint to run the OSINT attack simulation"""
    data = request.get_json()
    username = data.get('username', '').strip()
    
    if not username:
        return jsonify({"error": "Username required"}), 400
    
    # Run simulation
    simulator = OSINTAttackSimulator(username)
    results = simulator.run_full_attack()
    
    return jsonify(results)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
