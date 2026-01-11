"""
Rule-Based Feature Detector - Detects 50+ E-commerce Business Features

Focuses on:
- Payment options (COD, UPI, EMI)
- Delivery features (Same Day, Express, Free Shipping)
- Shopping experience (Try & Buy, AR View, Easy Returns)
- Trust signals (Reviews, Verified Badges, Q&A)
- Discovery (Wishlist, Compare, Filters)
"""

import re
from typing import Dict, List, Set
from dataclasses import dataclass


@dataclass
class FeatureMatch:
    feature_name: str
    category: str
    confidence: float
    evidence: List[str]
    page_type: str = "unknown"


class RuleBasedFeatureDetector:
    """Detects e-commerce features using regex patterns."""
    
    # 50+ E-commerce feature detection rules
    FEATURE_RULES = {
        # ========== PAYMENT OPTIONS ==========
        "Cash on Delivery": {
            "category": "Payment",
            "patterns": [
                r"cash on delivery",
                r"\bCOD\b",
                r"pay on delivery",
                r"cash payment at delivery",
                r"pay when you receive"
            ],
            "priority": 95
        },
        "UPI Payment": {
            "category": "Payment",
            "patterns": [
                r"\bUPI\b",
                r"unified payments",
                r"google pay",
                r"phonepe",
                r"paytm"
            ],
            "priority": 85
        },
        "EMI Options": {
            "category": "Payment",
            "patterns": [
                r"\bEMI\b",
                r"easy installments",
                r"no cost EMI",
                r"equated monthly",
                r"pay in installments"
            ],
            "priority": 80
        },
        "Pay Later": {
            "category": "Payment",
            "patterns": [
                r"pay later",
                r"buy now pay later",
                r"lazy pay",
                r"simpl",
                r"zest money"
            ],
            "priority": 75
        },
        "Digital Wallets": {
            "category": "Payment",
            "patterns": [
                r"wallet",
                r"amazon pay",
                r"mobikwik",
                r"freecharge"
            ],
            "priority": 70
        },
        
        # ========== DELIVERY & FULFILLMENT ==========
        "Same Day Delivery": {
            "category": "Delivery",
            "patterns": [
                r"same day delivery",
                r"delivered today",
                r"get it today",
                r"delivered by tonight"
            ],
            "priority": 90
        },
        "Next Day Delivery": {
            "category": "Delivery",
            "patterns": [
                r"next day delivery",
                r"delivered tomorrow",
                r"get it tomorrow",
                r"1-day delivery"
            ],
            "priority": 85
        },
        "Free Shipping": {
            "category": "Delivery",
            "patterns": [
                r"free shipping",
                r"free delivery",
                r"no delivery charges",
                r"zero delivery fee"
            ],
            "priority": 90
        },
        "Express Delivery": {
            "category": "Delivery",
            "patterns": [
                r"express delivery",
                r"fast delivery",
                r"quick delivery",
                r"priority shipping"
            ],
            "priority": 75
        },
        "Store Pickup": {
            "category": "Delivery",
            "patterns": [
                r"store pickup",
                r"pick up from store",
                r"collect from store",
                r"pickup location"
            ],
            "priority": 70
        },
        "International Shipping": {
            "category": "Delivery",
            "patterns": [
                r"international shipping",
                r"ships worldwide",
                r"global delivery",
                r"international delivery"
            ],
            "priority": 65
        },
        
        # ========== SHOPPING EXPERIENCE ==========
        "Try & Buy": {
            "category": "Shopping Experience",
            "patterns": [
                r"try\s+(and|&)\s+buy",
                r"try before you buy",
                r"try at home",
                r"home trial"
            ],
            "priority": 85
        },
        "Easy Returns": {
            "category": "Shopping Experience",
            "patterns": [
                r"easy returns?",
                r"hassle.free returns?",
                r"no questions? asked",
                r"\d+.day returns?"
            ],
            "priority": 90
        },
        "Exchange Available": {
            "category": "Shopping Experience",
            "patterns": [
                r"exchange available",
                r"easy exchange",
                r"exchange policy",
                r"swap product"
            ],
            "priority": 80
        },
        "Size Recommendation": {
            "category": "Shopping Experience",
            "patterns": [
                r"size recommendation",
                r"find your size",
                r"size guide",
                r"perfect fit"
            ],
            "priority": 75
        },
        "AR View": {
            "category": "Shopping Experience",
            "patterns": [
                r"\bAR\b view",
                r"augmented reality",
                r"virtual try",
                r"view in your space",
                r"3D view"
            ],
            "priority": 85
        },
        "Virtual Try-On": {
            "category": "Shopping Experience",
            "patterns": [
                r"virtual try.?on",
                r"try on virtually",
                r"camera try"
            ],
            "priority": 85
        },
        "Size Chart": {
            "category": "Shopping Experience",
            "patterns": [
                r"size chart",
                r"sizing guide",
                r"measurement guide"
            ],
            "priority": 70
        },
        "Color Swatches": {
            "category": "Shopping Experience",
            "patterns": [
                r"more colors",
                r"available in \d+ colors",
                r"color options"
            ],
            "priority": 60
        },
        
        # ========== TRUST & SOCIAL PROOF ==========
        "Product Reviews": {
            "category": "Trust",
            "patterns": [
                r"customer reviews",
                r"\d+\s+reviews?",
                r"read reviews",
                r"verified reviews"
            ],
            "priority": 90
        },
        "Verified Purchase Badge": {
            "category": "Trust",
            "patterns": [
                r"verified purchase",
                r"verified buyer",
                r"certified buyer"
            ],
            "priority": 85
        },
        "Ratings & Reviews": {
            "category": "Trust",
            "patterns": [
                r"\d+(\.\d+)?\s*(star|stars|\*|★)",
                r"rated \d+",
                r"rating"
            ],
            "priority": 90
        },
        "Customer Photos": {
            "category": "Trust",
            "patterns": [
                r"customer photos",
                r"buyer photos",
                r"real photos",
                r"user images"
            ],
            "priority": 75
        },
        "Q&A Section": {
            "category": "Trust",
            "patterns": [
                r"questions?\s+(and|&)\s+answers?",
                r"customer questions",
                r"ask a question",
                r"\bQ&A\b"
            ],
            "priority": 70
        },
        
        # ========== PRODUCT DISCOVERY ==========
        "Wishlist": {
            "category": "Discovery",
            "patterns": [
                r"wishlist",
                r"add to wish list",
                r"save for later",
                r"favorites"
            ],
            "priority": 80
        },
        "Recently Viewed": {
            "category": "Discovery",
            "patterns": [
                r"recently viewed",
                r"your history",
                r"items you viewed"
            ],
            "priority": 70
        },
        "Personalized Recommendations": {
            "category": "Discovery",
            "patterns": [
                r"recommended for you",
                r"you might also like",
                r"inspired by your",
                r"based on your browsing"
            ],
            "priority": 80
        },
        "Compare Products": {
            "category": "Discovery",
            "patterns": [
                r"compare products",
                r"add to compare",
                r"product comparison"
            ],
            "priority": 75
        },
        "Advanced Filters": {
            "category": "Discovery",
            "patterns": [
                r"filter by",
                r"refine results",
                r"narrow your search",
                r"apply filters"
            ],
            "priority": 85
        },
        "Sort Options": {
            "category": "Discovery",
            "patterns": [
                r"sort by",
                r"price: low to high",
                r"popularity",
                r"newest first"
            ],
            "priority": 75
        },
        "Search Autocomplete": {
            "category": "Discovery",
            "patterns": [
                r"autocomplete",
                r"search suggestions",
                r"trending searches"
            ],
            "priority": 70
        },
        
        # ========== CUSTOMER ENGAGEMENT ==========
        "Live Chat": {
            "category": "Support",
            "patterns": [
                r"live chat",
                r"chat with us",
                r"chat support",
                r"online support"
            ],
            "priority": 80
        },
        "WhatsApp Chat": {
            "category": "Support",
            "patterns": [
                r"whatsapp",
                r"chat on whatsapp",
                r"message us on whatsapp"
            ],
            "priority": 85
        },
        "Order Tracking": {
            "category": "Support",
            "patterns": [
                r"track order",
                r"track your order",
                r"order tracking",
                r"where is my order"
            ],
            "priority": 90
        },
        "Rewards Program": {
            "category": "Loyalty",
            "patterns": [
                r"rewards? program",
                r"loyalty program",
                r"earn points",
                r"supercoins"
            ],
            "priority": 75
        },
        "Referral Program": {
            "category": "Loyalty",
            "patterns": [
                r"refer (and|&) earn",
                r"referral program",
                r"invite friends",
                r"earn rewards"
            ],
            "priority": 70
        },
        
        # ========== ADDITIONAL FEATURES ==========
        "Gift Wrapping": {
            "category": "Services",
            "patterns": [
                r"gift wrap",
                r"gift packaging",
                r"wrapped as gift"
            ],
            "priority": 60
        },
        "Gift Cards": {
            "category": "Services",
            "patterns": [
                r"gift card",
                r"e-gift card",
                r"voucher"
            ],
            "priority": 65
        },
        "Subscription Service": {
            "category": "Services",
            "patterns": [
                r"subscribe",
                r"subscription",
                r"auto-delivery",
                r"recurring order"
            ],
            "priority": 70
        },
        "Price Drop Alert": {
            "category": "Services",
            "patterns": [
                r"price (drop|alert)",
                r"notify when price drops",
                r"price watch"
            ],
            "priority": 65
        },
        "Stock Alert": {
            "category": "Services",
            "patterns": [
                r"notify when available",
                r"back in stock",
                r"stock alert",
                r"notify me"
            ],
            "priority": 70
        }
    }
    
    def detect_features(self, page_content: str, page_type: str = "unknown") -> List[FeatureMatch]:
        """
        Detect features from page content using regex patterns.
        
        Args:
            page_content: HTML or text content from the page
            page_type: Type of page (homepage, product, checkout, etc.)
            
        Returns:
            List of detected features with confidence scores
        """
        page_content_lower = page_content.lower()
        detected_features = []
        
        for feature_name, config in self.FEATURE_RULES.items():
            evidence = []
            
            # Check each pattern
            for pattern in config["patterns"]:
                matches = re.finditer(pattern, page_content_lower, re.IGNORECASE)
                for match in matches:
                    # Get context around the match
                    start = max(0, match.start() - 50)
                    end = min(len(page_content), match.end() + 50)
                    context = page_content[start:end].strip()
                    evidence.append(context)
            
            # If feature detected, create match object
            if evidence:
                confidence = min(1.0, len(evidence) * 0.2 + 0.3)  # More evidence = higher confidence
                
                detected_features.append(FeatureMatch(
                    feature_name=feature_name,
                    category=config["category"],
                    confidence=confidence,
                    evidence=evidence[:3],  # Keep top 3 pieces of evidence
                    page_type=page_type
                ))
        
        return detected_features
    
    def get_feature_categories(self) -> Set[str]:
        """Get all unique feature categories."""
        return {config["category"] for config in self.FEATURE_RULES.values()}
    
    def get_features_by_category(self, category: str) -> List[str]:
        """Get all feature names in a category."""
        return [
            name for name, config in self.FEATURE_RULES.items()
            if config["category"] == category
        ]
    
    def get_feature_priority(self, feature_name: str) -> int:
        """Get priority score for a feature (0-100)."""
        return self.FEATURE_RULES.get(feature_name, {}).get("priority", 50)


# Global instance
rule_detector = RuleBasedFeatureDetector()
