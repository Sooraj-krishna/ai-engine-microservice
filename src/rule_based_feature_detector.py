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
    
    # 200+ E-commerce feature detection rules - COMPREHENSIVE BETA COVERAGE
    FEATURE_RULES = {
        # ========== PAYMENT OPTIONS (15 features) ==========
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
                r"paytm",
                r"bhim"
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
                r"pay in installments",
                r"monthly payments"
            ],
            "priority": 80
        },
        "Pay Later (BNPL)": {
            "category": "Payment",
            "patterns": [
                r"pay later",
                r"buy now pay later",
                r"\bBNPL\b",
                r"lazy pay",
                r"simpl",
                r"zest money",
                r"klarna",
                r"afterpay"
            ],
            "priority": 75
        },
        "Digital Wallets": {
            "category": "Payment",
            "patterns": [
                r"wallet",
                r"amazon pay",
                r"mobikwik",
                r"freecharge",
                r"paypal"
            ],
            "priority": 70
        },
        "Credit/Debit Cards": {
            "category": "Payment",
            "patterns": [
                r"credit card",
                r"debit card",
                r"visa",
                r"mastercard",
                r"american express",
                r"rupay"
            ],
            "priority": 95
        },
        "Net Banking": {
            "category": "Payment",
            "patterns": [
                r"net banking",
                r"internet banking",
                r"online banking"
            ],
            "priority": 80
        },
        "Cryptocurrency Payment": {
            "category": "Payment",
            "patterns": [
                r"bitcoin",
                r"crypto",
                r"cryptocurrency",
                r"btc accepted"
            ],
            "priority": 50
        },
        "Saved Cards": {
            "category": "Payment",
            "patterns": [
                r"saved cards",
                r"remember card",
                r"saved payment methods"
            ],
            "priority": 70
        },
        "Auto-Debit": {
            "category": "Payment",
            "patterns": [
                r"auto.?debit",
                r"automatic payment",
                r"standing instruction"
            ],
            "priority": 65
        },
        "Split Payment": {
            "category": "Payment",
            "patterns": [
                r"split payment",
                r"pay with multiple",
                r"partial payment"
            ],
            "priority": 60
        },
        "Bank Offers": {
            "category": "Payment",
            "patterns": [
                r"bank offer",
                r"card offer",
                r"cashback on.*card",
                r"discount.*credit card"
            ],
            "priority": 75
        },
        "Payment Plans": {
            "category": "Payment",
            "patterns": [
                r"payment plan",
                r"flexible payment",
                r"customized emi"
            ],
            "priority": 65
        },
        "Secure Payment Badge": {
            "category": "Payment",
            "patterns": [
                r"secure payment",
                r"ssl encrypted",
                r"pci compliant",
                r"verified by visa"
            ],
            "priority": 70
        },
        "One-Click Checkout": {
            "category": "Payment",
            "patterns": [
                r"one.?click",
                r"express checkout",
                r"quick buy"
            ],
            "priority": 80
        },
        
        # ========== DELIVERY & FULFILLMENT (20 features) ==========
        "Same Day Delivery": {
            "category": "Delivery",
            "patterns": [
                r"same day delivery",
                r"delivered today",
                r"get it today",
                r"delivered by tonight",
                r"hyperlocal"
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
        "2-Hour Delivery": {
            "category": "Delivery",
            "patterns": [
                r"2.hour delivery",
                r"instant delivery",
                r"delivered in.*hours"
            ],
            "priority": 95
        },
        "Free Shipping": {
            "category": "Delivery",
            "patterns": [
                r"free shipping",
                r"free delivery",
                r"no delivery charges",
                r"zero delivery fee",
                r"free standard shipping"
            ],
            "priority": 90
        },
        "Free Shipping Threshold": {
            "category": "Delivery",
            "patterns": [
                r"free.*above.*\d+",
                r"orders over.*free",
                r"minimum.*free shipping"
            ],
            "priority": 85
        },
        "Express Delivery": {
            "category": "Delivery",
            "patterns": [
                r"express delivery",
                r"fast delivery",
                r"quick delivery",
                r"priority shipping",
                r"expedited shipping"
            ],
            "priority": 75
        },
        "Store Pickup": {
            "category": "Delivery",
            "patterns": [
                r"store pickup",
                r"pick up from store",
                r"collect from store",
                r"pickup location",
                r"curbside pickup"
            ],
            "priority": 70
        },
        "International Shipping": {
            "category": "Delivery",
            "patterns": [
                r"international shipping",
                r"ships worldwide",
                r"global delivery",
                r"international delivery",
                r"ships to \d+ countries"
            ],
            "priority": 65
        },
        "Scheduled Delivery": {
            "category": "Delivery",
            "patterns": [
                r"schedule.*delivery",
                r"choose.*delivery.*time",
                r"delivery slot"
            ],
            "priority": 75
        },
        "Contactless Delivery": {
            "category": "Delivery",
            "patterns": [
                r"contactless",
                r"no.?contact delivery",
                r"safe delivery"
            ],
            "priority": 80
        },
        "Real-time Tracking": {
            "category": "Delivery",
            "patterns": [
                r"real.time tracking",
                r"live tracking",
                r"track in real.time"
            ],
            "priority": 85
        },
        "Delivery ETA": {
            "category": "Delivery",
            "patterns": [
                r"estimated delivery",
                r"delivery by",
                r"expected delivery.*date"
            ],
            "priority": 75
        },
        "Multiple Delivery Addresses": {
            "category": "Delivery",
            "patterns": [
                r"multiple.*address",
                r"ship to different address",
                r"add new address"
            ],
            "priority": 70
        },
        "Delivery Instructions": {
            "category": "Delivery",
            "patterns": [
                r"delivery instructions",
                r"special instructions",
                r"leave at door"
            ],
            "priority": 65
        },
        "Partial Delivery": {
            "category": "Delivery",
            "patterns": [
                r"partial delivery",
                r"split shipment",
                r"delivered separately"
            ],
            "priority": 60
        },
        "Signature Required": {
            "category": "Delivery",
            "patterns": [
                r"signature required",
                r"proof of delivery",
                r"OTP delivery"
            ],
            "priority": 65
        },
        "Locker Delivery": {
            "category": "Delivery",
            "patterns": [
                r"locker delivery",
                r"amazon locker",
                r"pickup point"
            ],
            "priority": 60
        },
        "Green Delivery": {
            "category": "Delivery",
            "patterns": [
                r"eco.?friendly delivery",
                r"carbon neutral",
                r"green shipping"
            ],
            "priority": 55
        },
        "Weekend Delivery": {
            "category": "Delivery",
            "patterns": [
                r"weekend delivery",
                r"saturday delivery",
                r"sunday delivery"
            ],
            "priority": 70
        },
        "Delivery Partner Choice": {
            "category": "Delivery",
            "patterns": [
                r"choose.*courier",
                r"delivery partner",
                r"preferred courier"
            ],
            "priority": 60
        },
        
        # ========== SHOPPING EXPERIENCE (25 features) ==========
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
                r"\d+.day returns?",
                r"return policy"
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
                r"perfect fit",
                r"size predictor"
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
                r"3D view",
                r"place in room"
            ],
            "priority": 85
        },
        "Virtual Try-On": {
            "category": "Shopping Experience",
            "patterns": [
                r"virtual try.?on",
                r"try on virtually",
                r"camera try",
                r"face try"
            ],
            "priority": 85
        },
        "Size Chart": {
            "category": "Shopping Experience",
            "patterns": [
                r"size chart",
                r"sizing guide",
                r"measurement guide",
                r"fit guide"
            ],
            "priority": 70
        },
        "Color Swatches": {
            "category": "Shopping Experience",
            "patterns": [
                r"more colors",
                r"available in \d+ colors",
                r"color options",
                r"color selector"
            ],
            "priority": 60
        },
        "Product Videos": {
            "category": "Shopping Experience",
            "patterns": [
                r"product video",
                r"watch video",
                r"video review",
                r"360.?view"
            ],
            "priority": 75
        },
        "Image Zoom": {
            "category": "Shopping Experience",
            "patterns": [
                r"zoom",
                r"enlarge image",
                r"view larger",
                r"magnify"
            ],
            "priority": 60
        },
        "Variant Selector": {
            "category": "Shopping Experience",
            "patterns": [
                r"select.*variant",
                r"choose.*option",
                r"size.*color selector"
            ],
            "priority": 70
        },
        "Bulk Purchase": {
            "category": "Shopping Experience",
            "patterns": [
                r"bulk.*purchase",
                r"wholesale",
                r"quantity discount",
                r"buy in bulk"
            ],
            "priority": 65
        },
        "Pre-Order": {
            "category": "Shopping Experience",
            "patterns": [
                r"pre.?order",
                r"coming soon",
                r"reserve now",
                r"early access"
            ],
            "priority": 70
        },
        "Back in Stock Notification": {
            "category": "Shopping Experience",
            "patterns": [
                r"notify.*back in stock",
                r"restock alert",
                r"availability alert"
            ],
            "priority": 75
        },
        "Product Bundles": {
            "category": "Shopping Experience",
            "patterns": [
                r"bundle",
                r"combo offer",
                r"package deal",
                r"buy together"
            ],
            "priority": 70
        },
        "Product Customization": {
            "category": "Shopping Experience",
            "patterns": [
                r"customiz",
                r"personalize",
                r"add.*text",
                r"custom.*design"
            ],
            "priority": 75
        },
        "Quick View": {
            "category": "Shopping Experience",
            "patterns": [
                r"quick view",
                r"quick look",
                r"preview"
            ],
            "priority": 65
        },
        "Recently Viewed Items": {
            "category": "Shopping Experience",
            "patterns": [
                r"recently viewed",
                r"your history",
                r"items you.*viewed"
            ],
            "priority": 70
        },
        "Product Specifications": {
            "category": "Shopping Experience",
            "patterns": [
                r"specification",
                r"technical.*details",
                r"product.*details",
                r"features \u0026 specs"
            ],
            "priority": 75
        },
        "Size Comparison Tool": {
            "category": "Shopping Experience",
            "patterns": [
                r"size.*compar",
                r"fit.*compar",
                r"compare.*sizes"
            ],
            "priority": 65
        },
        "Stock Availability": {
            "category": "Shopping Experience",
            "patterns": [
                r"in stock",
                r"available",
                r"only.*left",
                r"\d+ in stock"
            ],
            "priority": 80
        },
        "Low Stock Warning": {
            "category": "Shopping Experience",
            "patterns": [
                r"low stock",
                r"limited.*stock",
                r"hurry.*only.*left",
                r"selling fast"
            ],
            "priority": 75
        },
        "Product Care Instructions": {
            "category": "Shopping Experience",
            "patterns": [
                r"care instructions",
                r"wash.*care",
                r"maintenance guide"
            ],
            "priority": 60
        },
        "Material Information": {
            "category": "Shopping Experience",
            "patterns": [
                r"material",
                r"fabric",
                r"made of",
                r"composition"
            ],
            "priority": 65
        },
        "Warranty Information": {
            "category": "Shopping Experience",
            "patterns": [
                r"warranty",
                r"guarantee",
                r"year.*coverage",
                r"manufacturer warranty"
            ],
            "priority": 75
        },
        
        # ========== TRUST & SOCIAL PROOF (18 features) ==========
        "Product Reviews": {
            "category": "Trust",
            "patterns": [
                r"customer reviews",
                r"\d+\s+reviews?",
                r"read reviews",
                r"verified reviews",
                r"write a review"
            ],
            "priority": 90
        },
        "Verified Purchase Badge": {
            "category": "Trust",
            "patterns": [
                r"verified purchase",
                r"verified buyer",
                r"certified buyer",
                r"authentic review"
            ],
            "priority": 85
        },
        "Ratings & Reviews": {
            "category": "Trust",
            "patterns": [
                r"\d+(\.\d+)?\s*(star|stars|\*|★)",
                r"rated \d+",
                r"rating",
                r"review score"
            ],
            "priority": 90
        },
        "Customer Photos": {
            "category": "Trust",
            "patterns": [
                r"customer photos",
                r"buyer photos",
                r"real photos",
                r"user images",
                r"customer gallery"
            ],
            "priority": 75
        },
        "Q&A Section": {
            "category": "Trust",
            "patterns": [
                r"questions?\s+(and|&)\s+answers?",
                r"customer questions",
                r"ask a question",
                r"\bQ&A\b",
                r"community Q&A"
            ],
            "priority": 70
        },
        "Seller Information": {
            "category": "Trust",
            "patterns": [
                r"sold by",
                r"seller",
                r"fulfilled by",
                r"vendor"
            ],
            "priority": 70
        },
        "Authenticity Guarantee": {
            "category": "Trust",
            "patterns": [
                r"100% authentic",
                r"genuine product",
                r"original",
                r"authenticity guarantee"
            ],
            "priority": 85
        },
        "Expert Reviews": {
            "category": "Trust",
            "patterns": [
                r"expert review",
                r"professional review",
                r"tested by"
            ],
            "priority": 70
        },
        "Bestseller Badge": {
            "category": "Trust",
            "patterns": [
                r"bestseller",
                r"best seller",
                r"#1 seller",
                r"top rated"
            ],
            "priority": 75
        },
        "Trust Badges": {
            "category": "Trust",
            "patterns": [
                r"secure checkout",
                r"money back",
                r"satisfaction guaranteed",
                r"trusted by \d+"
            ],
            "priority": 80
        },
        "Customer Testimonials": {
            "category": "Trust",
            "patterns": [
                r"testimonial",
                r"customer story",
                r"success story"
            ],
            "priority": 70
        },
        "Influencer Reviews": {
            "category": "Trust",
            "patterns": [
                r"influencer",
                r"as seen on",
                r"celebrity.*wear"
            ],
            "priority": 65
        },
        "Award Badges": {
            "category": "Trust",
            "patterns": [
                r"award",
                r"winner",
                r"certified",
                r"accredited"
            ],
            "priority": 70
        },
        "Media Coverage": {
            "category": "Trust",
            "patterns": [
                r"featured in",
                r"as seen in",
                r"press coverage"
            ],
            "priority": 65
        },
        "Social Proof Counter": {
            "category": "Trust",
            "patterns": [
                r"\d+\s+people.*bought",
                r"\d+\s+customers",
                r"viewed by \d+"
            ],
            "priority": 75
        },
        "Return Rate Display": {
            "category": "Trust",
            "patterns": [
                r"return rate",
                r"% satisfaction",
                r"customer satisfaction"
            ],
            "priority": 65
        },
        "Eco-Friendly Badge": {
            "category": "Trust",
            "patterns": [
                r"eco.?friendly",
                r"sustainable",
                r"organic",
                r"green certified"
            ],
            "priority": 70
        },
        "Made In Label": {
            "category": "Trust",
            "patterns": [
                r"made in",
                r"manufactured in",
                r"product of"
            ],
            "priority": 65
        },
        
        # ========== PRODUCT DISCOVERY (22 features) ==========
        "Wishlist": {
            "category": "Discovery",
            "patterns": [
                r"wishlist",
                r"add to wish list",
                r"save for later",
                r"favorites",
                r"heart"
            ],
            "priority": 80
        },
        "Recently Viewed": {
            "category": "Discovery",
            "patterns": [
                r"recently viewed",
                r"your history",
                r"items you viewed",
                r"browsing history"
            ],
            "priority": 70
        },
        "Personalized Recommendations": {
            "category": "Discovery",
            "patterns": [
                r"recommended for you",
                r"you might also like",
                r"inspired by your",
                r"based on your browsing",
                r"picked for you"
            ],
            "priority": 80
        },
        "Frequently Bought Together": {
            "category": "Discovery",
            "patterns": [
                r"frequently bought together",
                r"customers also bought",
                r"complete the look"
            ],
            "priority": 85
        },
        "Compare Products": {
            "category": "Discovery",
            "patterns": [
                r"compare products",
                r"add to compare",
                r"product comparison",
                r"vs\."
            ],
            "priority": 75
        },
        "Advanced Filters": {
            "category": "Discovery",
            "patterns": [
                r"filter by",
                r"refine results",
                r"narrow your search",
                r"apply filters",
                r"faceted search"
            ],
            "priority": 85
        },
        "Sort Options": {
            "category": "Discovery",
            "patterns": [
                r"sort by",
                r"price: low to high",
                r"popularity",
                r"newest first",
                r"relevance"
            ],
            "priority": 75
        },
        "Search Autocomplete": {
            "category": "Discovery",
            "patterns": [
                r"autocomplete",
                r"search suggestions",
                r"trending searches",
                r"popular searches"
            ],
            "priority": 70
        },
        "Visual Search": {
            "category": "Discovery",
            "patterns": [
                r"visual search",
                r"image search",
                r"search by image",
                r"camera search"
            ],
            "priority": 80
        },
        "Voice Search": {
            "category": "Discovery",
            "patterns": [
                r"voice search",
                r"speak to search",
                r"voice assistant"
            ],
            "priority": 75
        },
        "Category Navigation": {
            "category": "Discovery",
            "patterns": [
                r"browse categories",
                r"shop by category",
                r"all categories"
            ],
            "priority": 70
        },
        "Trending Products": {
            "category": "Discovery",
            "patterns": [
                r"trending",
                r"popular now",
                r"hot.*products"
            ],
            "priority": 75
        },
        "New Arrivals": {
            "category": "Discovery",
            "patterns": [
                r"new arrivals",
                r"just in",
                r"latest products",
                r"new collection"
            ],
            "priority": 75
        },
        "Sale Section": {
            "category": "Discovery",
            "patterns": [
                r"\bsale\b",
                r"deals",
                r"offers",
                r"discounts",
                r"clearance"
            ],
            "priority": 80
        },
        "Collections/Curated Sets": {
            "category": "Discovery",
            "patterns": [
                r"collection",
                r"curated",
                r"handpicked",
                r"featured collection"
            ],
            "priority": 70
        },
        "Brand Filter": {
            "category": "Discovery",
            "patterns": [
                r"filter.*brand",
                r"shop by brand",
                r"all brands"
            ],
            "priority": 75
        },
        "Price Range Filter": {
            "category": "Discovery",
            "patterns": [
                r"price range",
                r"price filter",
                r"budget filter"
            ],
            "priority": 80
        },
        "Related Products": {
            "category": "Discovery",
            "patterns": [
                r"related products",
                r"similar items",
                r"you may also like"
            ],
            "priority": 75
        },
        "Shop by Look": {
            "category": "Discovery",
            "patterns": [
                r"shop.*look",
                r"get.*look",
                r"complete.*outfit"
            ],
            "priority": 70
        },
        "Seasonal Collections": {
            "category": "Discovery",
            "patterns": [
                r"seasonal",
                r"summer collection",
                r"winter.*sale"
            ],
            "priority": 65
        },
        "Gift Finder": {
            "category": "Discovery",
            "patterns": [
                r"gift finder",
                r"gift guide",
                r"gift ideas"
            ],
            "priority": 70
        },
        "Quiz/Product Finder": {
            "category": "Discovery",
            "patterns": [
                r"product finder",
                r"find.*perfect",
                r"quiz",
                r"recommendation.*quiz"
            ],
            "priority": 75
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
