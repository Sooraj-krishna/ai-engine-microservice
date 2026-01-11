"""
Multi-Domain Feature Detector - Works for ANY website type

Supports:
- E-commerce (Amazon, Flipkart)
- SaaS (Notion, Slack, Figma)
- Media/News (Medium, YouTube)
- Social Media (Twitter, LinkedIn)
- Finance (PayPal, Stripe)
- Education (Udemy, Coursera)
- Healthcare (Practo, 1mg)
- Real Estate (Zillow, MagicBricks)
"""

import re
from typing import Dict, List, Set
from dataclasses import dataclass


@dataclass
class FeatureMatch:
    feature_name: str
    category: str
    domain: str  # e-commerce, saas, media, etc.
    confidence: float
    evidence: List[str]
    page_type: str = "unknown"


class MultiDomainFeatureDetector:
    """Detects features across multiple website domains/industries."""
    
    FEATURE_RULES = {
        # ==================== E-COMMERCE ====================
        "Cash on Delivery": {
            "domain": "E-commerce",
            "category": "Payment",
            "patterns": [r"cash on delivery", r"\bCOD\b", r"pay on delivery"],
            "priority": 95
        },
        "Try & Buy": {
            "domain": "E-commerce",
            "category": "Shopping",
            "patterns": [r"try\s+(and|&)\s+buy", r"try at home"],
            "priority": 85
        },
        "Easy Returns": {
            "domain": "E-commerce",
            "category": "Shopping",
            "patterns": [r"easy returns?", r"\d+.day returns?"],
            "priority": 90
        },
        
        # ==================== SAAS ====================
        "Free Trial": {
            "domain": "SaaS",
            "category": "Pricing",
            "patterns": [
                r"free trial",
                r"try free",
                r"start free trial",
                r"\d+.day trial"
            ],
            "priority": 95
        },
        "Freemium Plan": {
            "domain": "SaaS",
            "category": "Pricing",
            "patterns": [
                r"free forever",
                r"always free",
                r"free plan",
                r"freemium"
            ],
            "priority": 90
        },
        "API Access": {
            "domain": "SaaS",
            "category": "Integration",
            "patterns": [
                r"\bAPI\b access",
                r"developer API",
                r"REST API",
                r"API documentation"
            ],
            "priority": 85
        },
        "SSO / SAML": {
            "domain": "SaaS",
            "category": "Security",
            "patterns": [
                r"\bSSO\b",
                r"single sign.?on",
                r"\bSAML\b",
                r"enterprise authentication"
            ],
            "priority": 80
        },
        "White-Label": {
            "domain": "SaaS",
            "category": "Enterprise",
            "patterns": [
                r"white.?label",
                r"custom branding",
                r"remove branding"
            ],
            "priority": 75
        },
        "Real-time Collaboration": {
            "domain": "SaaS",
            "category": "Features",
            "patterns": [
                r"real.?time collaboration",
                r"collaborative editing",
                r"work together",
                r"multiplayer"
            ],
            "priority": 90
        },
        "Version History": {
            "domain": "SaaS",
            "category": "Features",
            "patterns": [
                r"version history",
                r"revision history",
                r"restore previous",
                r"undo changes"
            ],
            "priority": 80
        },
        "Custom Workflows": {
            "domain": "SaaS",
            "category": "Features",
            "patterns": [
                r"custom workflows?",
                r"automation",
                r"workflow builder"
            ],
            "priority": 75
        },
        
        # ==================== MEDIA / CONTENT ====================
        "Dark Mode": {
            "domain": "Media",
            "category": "UX",
            "patterns": [
                r"dark mode",
                r"dark theme",
                r"night mode"
            ],
            "priority": 85
        },
        "Offline Reading": {
            "domain": "Media",
            "category": "Features",
            "patterns": [
                r"offline (reading|mode)",
                r"download for offline",
                r"save for offline"
            ],
            "priority": 75
        },
        "Bookmarking": {
            "domain": "Media",
            "category": "Features",
            "patterns": [
                r"bookmark",
                r"save (for|to) later",
                r"reading list"
            ],
            "priority": 80
        },
        "Comments Section": {
            "domain": "Media",
            "category": "Engagement",
            "patterns": [
                r"comments? section",
                r"leave a comment",
                r"join the discussion"
            ],
            "priority": 70
        },
        "Content Recommendations": {
            "domain": "Media",
            "category": "Discovery",
            "patterns": [
                r"recommended (for you|articles)",
                r"you might like",
                r"related content"
            ],
            "priority": 80
        },
        
        # ==================== SOCIAL MEDIA ====================
        "Private Messaging": {
            "domain": "Social",
            "category": "Communication",
            "patterns": [
                r"private message",
                r"send message",
                r"direct message",
                r"\bDM\b"
            ],
            "priority": 90
        },
        "Stories / Reels": {
            "domain": "Social",
            "category": "Content",
            "patterns": [
                r"\bstories\b",
                r"\breels\b",
                r"24.?hour stories"
            ],
            "priority": 85
        },
        "Live Streaming": {
            "domain": "Social",
            "category": "Content",
            "patterns": [
                r"live stream",
                r"go live",
                r"live video",
                r"streaming now"
            ],
            "priority": 80
        },
        "Verified Badge": {
            "domain": "Social",
            "category": "Trust",
            "patterns": [
                r"verified (badge|account)",
                r"blue check",
                r"verified ✓"
            ],
            "priority": 75
        },
        
        # ==================== FINANCE / FINTECH ====================
        "2FA / MFA": {
            "domain": "Finance",
            "category": "Security",
            "patterns": [
                r"two.?factor",
                r"\b2FA\b",
                r"multi.?factor",
                r"\bMFA\b",
                r"authentication app"
            ],
            "priority": 95
        },
        "Instant Transfers": {
            "domain": "Finance",
            "category": "Features",
            "patterns": [
                r"instant transfer",
                r"real.?time transfer",
                r"immediate transfer"
            ],
            "priority": 90
        },
        "Transaction History": {
            "domain": "Finance",
            "category": "Features",
            "patterns": [
                r"transaction history",
                r"view transactions",
                r"account statement"
            ],
            "priority": 85
        },
        "Bill Payment": {
            "domain": "Finance",
            "category": "Features",
            "patterns": [
                r"bill payment",
                r"pay bills",
                r"utility payments"
            ],
            "priority": 80
        },
        
        # ==================== EDUCATION ====================
        "Certificates": {
            "domain": "Education",
            "category": "Features",
            "patterns": [
                r"certificate of completion",
                r"earn certificate",
                r"verified certificate"
            ],
            "priority": 85
        },
        "Live Classes": {
            "domain": "Education",
            "category": "Learning",
            "patterns": [
                r"live class",
                r"instructor.?led",
                r"virtual classroom"
            ],
            "priority": 80
        },
        "Progress Tracking": {
            "domain": "Education",
            "category": "Features",
            "patterns": [
                r"track progress",
                r"learning progress",
                r"course completion"
            ],
            "priority": 75
        },
        "Discussion Forums": {
            "domain": "Education",
            "category": "Community",
            "patterns": [
                r"discussion forum",
                r"student community",
                r"ask questions"
            ],
            "priority": 70
        },
        
        # ==================== HEALTHCARE ====================
        "Video Consultation": {
            "domain": "Healthcare",
            "category": "Services",
            "patterns": [
                r"video consult",
                r"online consultation",
                r"telemedicine",
                r"virtual doctor"
            ],
            "priority": 90
        },
        "Prescription Upload": {
            "domain": "Healthcare",
            "category": "Features",
            "patterns": [
                r"upload prescription",
                r"submit prescription",
                r"prescription required"
            ],
            "priority": 85
        },
        "Medicine Reminder": {
            "domain": "Healthcare",
            "category": "Features",
            "patterns": [
                r"medicine reminder",
                r"medication reminder",
                r"pill reminder"
            ],
            "priority": 75
        },
        
        # ==================== REAL ESTATE ====================
        "Virtual Tour": {
            "domain": "Real Estate",
            "category": "Features",
            "patterns": [
                r"virtual tour",
                r"360.?view",
                r"3D tour",
                r"video tour"
            ],
            "priority": 90
        },
        "EMI Calculator": {
            "domain": "Real Estate",
            "category": "Tools",
            "patterns": [
                r"EMI calculator",
                r"loan calculator",
                r"mortgage calculator"
            ],
            "priority": 80
        },
        "Schedule Visit": {
            "domain": "Real Estate",
            "category": "Services",
            "patterns": [
                r"schedule (a )?visit",
                r"book (a )?visit",
                r"site visit"
            ],
            "priority": 85
        },
        
        # ==================== UNIVERSAL FEATURES ====================
        "Mobile App": {
            "domain": "Universal",
            "category": "Platform",
            "patterns": [
                r"mobile app",
                r"download app",
                r"app store",
                r"play store"
            ],
            "priority": 80
        },
        "24/7 Support": {
            "domain": "Universal",
            "category": "Support",
            "patterns": [
                r"24/7 support",
                r"24x7 support",
                r"round the clock",
                r"always available"
            ],
            "priority": 85
        },
        "Email Notifications": {
            "domain": "Universal",
            "category": "Notifications",
            "patterns": [
                r"email notification",
                r"email alert",
                r"subscribe to updates"
            ],
            "priority": 70
        },
        "Push Notifications": {
            "domain": "Universal",
            "category": "Notifications",
            "patterns": [
                r"push notification",
                r"browser notification",
                r"enable notifications"
            ],
            "priority": 75
        }
    }
    
    def detect_features(self, page_content: str, target_domain: str = "auto") -> List[FeatureMatch]:
        """
        Detect features from page content.
        
        Args:
            page_content: HTML or text content
            target_domain: Target domain (e-commerce, saas, media, etc.) or "auto" to detect all
            
        Returns:
            List of detected features
        """
        page_content_lower = page_content.lower()
        detected_features = []
        
        for feature_name, config in self.FEATURE_RULES.items():
            # Filter by domain if specified
            if target_domain != "auto" and config["domain"] != target_domain and config["domain"] != "Universal":
                continue
            
            evidence = []
            
            # Check each pattern
            for pattern in config["patterns"]:
                matches = re.finditer(pattern, page_content_lower, re.IGNORECASE)
                for match in matches:
                    start = max(0, match.start() - 50)
                    end = min(len(page_content), match.end() + 50)
                    context = page_content[start:end].strip()
                    evidence.append(context)
            
            if evidence:
                confidence = min(1.0, len(evidence) * 0.2 + 0.3)
                
                detected_features.append(FeatureMatch(
                    feature_name=feature_name,
                    category=config["category"],
                    domain=config["domain"],
                    confidence=confidence,
                    evidence=evidence[:3]
                ))
        
        return detected_features
    
    def get_domains(self) -> List[str]:
        """Get all supported domains."""
        domains = set()
        for config in self.FEATURE_RULES.values():
            domains.add(config["domain"])
        return sorted(list(domains))
    
    def get_features_by_domain(self, domain: str) -> List[str]:
        """Get all features for a specific domain."""
        return [
            name for name, config in self.FEATURE_RULES.items()
            if config["domain"] == domain
        ]


# Global instance
multi_domain_detector = MultiDomainFeatureDetector()
