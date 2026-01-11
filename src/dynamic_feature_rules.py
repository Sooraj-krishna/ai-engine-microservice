"""
Dynamic Feature Rules - Industry-specific feature detection rules

Provides feature detection rules dynamically based on detected industry type.
Supports multiple industries: E-commerce, Restaurant, Blog, SaaS, etc.
"""

from typing import Dict, List


class DynamicFeatureRules:
    """Manages feature detection rules for different industries."""
    
    # Industry-specific feature categories and rules
    INDUSTRY_RULES = {
        "ecommerce": {
            "categories": {
                "Payment": 95,
                "Delivery": 90,
                "Trust": 85,
                "Shopping Experience": 80,
                "Support": 75,
                "Discovery": 70,
                "Loyalty": 65,
                "Services": 60
            },
            "keywords": {
                "Payment": ["payment", "pay", "checkout", "billing", "card", "wallet", "cod", "upi", "emi"],
                "Delivery": ["delivery", "shipping", "ship", "dispatch", "courier", "freight"],
                "Trust": ["review", "rating", "verified", "certified", "guarantee", "authentic"],
                "Shopping Experience": ["try", "ar view", "virtual", "return", "exchange", "size"],
                "Support": ["support", "help", "chat", "contact", "service"],
                "Discovery": ["search", "filter", "sort", "recommend", "wishlist", "compare"],
                "Loyalty": ["loyalty", "reward", "points", "cashback", "member"],
                "Services": ["gift", "subscription", "warranty", "insurance"]
            }
        },
        
        "restaurant": {
            "categories": {
                "Ordering": 95,
                "Reservations": 90,
                "Menu": 85,
                "Delivery": 80,
                "Dining Experience": 75,
                "Customer Service": 70,
                "Loyalty": 65
            },
            "keywords": {
                "Ordering": ["order", "online order", "takeout", "pickup"],
                "Reservations": ["reservation", "book", "table", "booking", "reserve"],
                "Menu": ["menu", "dish", "cuisine", "food", "chef special", "appetizer"],
                "Delivery": ["delivery", "deliver", "door dash", "uber eats"],
                "Dining Experience": ["dine in", "ambiance", "atmosphere", "seating"],
                "Customer Service": ["contact", "feedback", "review", "rating"],
                "Loyalty": ["rewards", "loyalty", "member", "points"]
            }
        },
        
        "blog": {
            "categories": {
                "Content": 90,
                "Engagement": 85,
                "Subscription": 80,
                "Social": 75,
                "Navigation": 70,
                "Monetization": 65
            },
            "keywords": {
                "Content": ["article", "post", "blog", "story", "author", "published"],
                "Engagement": ["comment", "discussion", "share", "like", "reaction"],
                "Subscription": ["subscribe", "newsletter", "email", "updates", "notify"],
                "Social": ["share", "tweet", "facebook", "social", "follow"],
                "Navigation": ["archive", "category", "tag", "search", "filter"],
                "Monetization": ["ad", "sponsor", "affiliate", "donate", "support"]
            }
        },
        
        "saas": {
            "categories": {
                "Pricing": 95,
                "Integration": 90,
                "Features": 85,
                "Trial": 80,
                "Support": 75,
                "API": 70,
                "Security": 65
            },
            "keywords": {
                "Pricing": ["pricing", "plan", "subscription", "tier", "free", "premium"],
                "Integration": ["integration", "connect", "sync", "api", "webhook"],
                "Features": ["feature", "capability", "functionality", "tool"],
                "Trial": ["trial", "demo", "try", "test", "free"],
                "Support": ["support", "help", "documentation", "tutorial", "guide"],
                "API": ["api", "developer", "sdk", "rest", "endpoint"],
                "Security": ["security", "encrypt", "ssl", "compliance", "privacy"]
            }
        },
        
        "professional_services": {
            "categories": {
                "Portfolio": 90,
                "Services": 85,
                "Testimonials": 80,
                "Contact": 75,
                "Expertise": 70,
                "Process": 65
            },
            "keywords": {
                "Portfolio": ["portfolio", "work", "project", "case study", "showcase"],
                "Services": ["service", "offering", "solution", "consulting"],
                "Testimonials": ["testimonial", "review", "client", "feedback"],
                "Contact": ["contact", "quote", "consult", "inquiry", "hire"],
                "Expertise": ["expert", "specialist", "professional", "certified"],
                "Process": ["process", "methodology", "approach", "workflow"]
            }
        },
        
        "realestate": {
            "categories": {
                "Listings": 95,
                "Search": 90,
                "Property Details": 85,
                "Tours": 80,
                "Agent Contact": 75,
                "Transactions": 70
            },
            "keywords": {
                "Listings": ["listing", "property", "home", "house", "apartment"],
                "Search": ["search", "filter", "location", "price range", "bedroom"],
                "Property Details": ["sqft", "bathroom", "bedroom", "amenity", "feature"],
                "Tours": ["tour", "viewing", "visit", "schedule", "virtual tour"],
                "Agent Contact": ["agent", "realtor", "broker", "contact"],
                "Transactions": ["buy", "sell", "rent", "lease", "mortgage"]
            }
        },
        
        "education": {
            "categories": {
                "Courses": 95,
                "Enrollment": 90,
                "Learning": 85,
                "Certification": 80,
                "Support": 75,
                "Community": 70
            },
            "keywords": {
                "Courses": ["course", "class", "program", "curriculum", "training"],
                "Enrollment": ["enroll", "register", "admission", "apply", "join"],
                "Learning": ["learn", "lesson", "module", "video", "quiz"],
                "Certification": ["certificate", "certification", "degree", "diploma"],
                "Support": ["support", "help", "instructor", "tutor", "mentor"],
                "Community": ["discussion", "forum", "student", "peer", "community"]
            }
        },
        
        "portfolio": {
            "categories": {
                "Projects": 90,
                "Skills": 85,
                "Contact": 80,
                "About": 75,
                "Experience": 70
            },
            "keywords": {
                "Projects": ["project", "work", "portfolio", "showcase", "gallery"],
                "Skills": ["skill", "expertise", "proficient", "technology"],
                "Contact": ["contact", "hire", "email", "reach", "connect"],
                "About": ["about", "bio", "background", "story"],
                "Experience": ["experience", "year", "worked", "client"]
            }
        },
        
        "healthcare": {
            "categories": {
                "Appointments": 95,
                "Services": 90,
                "Providers": 85,
                "Insurance": 80,
                "Patient Portal": 75,
                "Information": 70
            },
            "keywords": {
                "Appointments": ["appointment", "schedule", "book", "visit"],
                "Services": ["treatment", "care", "service", "procedure", "exam"],
                "Providers": ["doctor", "physician", "specialist", "provider"],
                "Insurance": ["insurance", "coverage", "accept", "plan"],
                "Patient Portal": ["portal", "login", "account", "records"],
                "Information": ["health", "medical", "condition", "symptom"]
            }
        },
        
        "general": {
            "categories": {
                "Content": 80,
                "Navigation": 75,
                "Contact": 70,
                "Engagement": 65,
                "Information": 60
            },
            "keywords": {
                "Content": ["content", "information", "about", "page"],
                "Navigation": ["menu", "nav", "search", "link"],
                "Contact": ["contact", "email", "phone", "address"],
                "Engagement": ["share", "comment", "subscribe", "follow"],
                "Information": ["info", "detail", "description", "overview"]
            }
        }
    }
    
    def get_rules_for_industry(self, industry: str) -> Dict:
        """
        Get feature detection rules for a specific industry.
        
        Args:
            industry: Industry name
            
        Returns:
            Dictionary with categories, keywords, and priorities
        """
        return self.INDUSTRY_RULES.get(industry, self.INDUSTRY_RULES["general"])
    
    def get_category_priority(self, industry: str, category: str) -> int:
        """
        Get priority score for a category in a specific industry.
        
        Args:
            industry: Industry name
            category: Category name
            
        Returns:
            Priority score (0-100)
        """
        rules = self.get_rules_for_industry(industry)
        return rules["categories"].get(category, 50)
    
    def get_keywords_for_category(self, industry: str, category: str) -> List[str]:
        """
        Get keywords for a specific category in an industry.
        
        Args:
            industry: Industry name
            category: Category name
            
        Returns:
            List of keywords
        """
        rules = self.get_rules_for_industry(industry)
        return rules["keywords"].get(category, [])
    
    def get_all_keywords(self, industry: str) -> Dict[str, List[str]]:
        """
        Get all keywords for an industry.
        
        Args:
            industry: Industry name
            
        Returns:
            Dictionary of category -> keywords
        """
        rules = self.get_rules_for_industry(industry)
        return rules["keywords"]


# Global instance
dynamic_rules = DynamicFeatureRules()
