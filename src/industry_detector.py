"""
Industry Detector - Automatically detects the type/industry of a website

Detects:
- E-commerce (online stores)
- Restaurant (food services)
- Blog/Content (news, articles)
- SaaS (software as a service)
- Professional Services (agencies, consultants)
- Real Estate (property listings)
- Education (courses, training)
- Portfolio (freelancers, creatives)
- Healthcare (medical services)
- General/Other
"""

import re
from typing import Dict, Tuple
from collections import Counter


class IndustryDetector:
    """Detects website industry type from content."""
    
    # Industry detection keywords with weights
    INDUSTRY_SIGNATURES = {
        "ecommerce": {
            "keywords": [
                ("cart", 3), ("buy", 3), ("product", 3), ("price", 3),
                ("checkout", 5), ("shipping", 4), ("payment", 4),
                ("add to cart", 5), ("shop", 3), ("store", 2),
                ("order", 3), ("delivery", 3), ("purchase", 3),
                ("wishlist", 4), ("sku", 5), ("inventory", 4)
            ],
            "patterns": [
                r"\$[\d,]+\.?\d*",  # Price patterns
                r"add to (cart|bag|basket)",
                r"free shipping",
                r"in stock"
            ]
        },
        
        "restaurant": {
            "keywords": [
                ("menu", 5), ("reservation", 5), ("book table", 5),
                ("order online", 4), ("delivery", 3), ("takeout", 4),
                ("cuisine", 4), ("chef", 3), ("restaurant", 5),
                ("dine", 3), ("food", 2), ("dish", 3),
                ("appetizer", 4), ("entree", 4), ("dessert", 3),
                ("wine list", 4), ("hours", 2)
            ],
            "patterns": [
                r"open (hours?|time)",
                r"reserve (a )?table",
                r"menu items?",
                r"our (chef|kitchen)"
            ]
        },
        
        "blog": {
            "keywords": [
                ("blog", 5), ("article", 4), ("post", 3), ("author", 4),
                ("published", 3), ("comment", 3), ("share", 2),
                ("read more", 3), ("subscribe", 3), ("newsletter", 4),
                ("category", 2), ("tag", 2), ("archive", 3),
                ("by ", 2), ("posted", 3)
            ],
            "patterns": [
                r"read more",
                r"posted (on|by|in)",
                r"\d+ comments?",
                r"share (this|on)"
            ]
        },
        
        "saas": {
            "keywords": [
                ("pricing", 5), ("plan", 4), ("subscription", 5),
                ("api", 4), ("integration", 4), ("feature", 3),
                ("dashboard", 4), ("trial", 4), ("demo", 3),
                ("free trial", 5), ("per month", 4), ("upgrade", 3),
                ("analytics", 3), ("saas", 5), ("software", 3),
                ("platform", 3), ("cloud", 3)
            ],
            "patterns": [
                r"free trial",
                r"\$\d+/mo(nth)?",
                r"(api|rest) (documentation|docs)",
                r"integrat(e|ion)"
            ]
        },
        
        "professional_services": {
            "keywords": [
                ("service", 3), ("client", 3), ("portfolio", 5),
                ("project", 3), ("consultation", 4), ("expert", 3),
                ("testimonial", 4), ("case study", 5), ("hire", 3),
                ("contact us", 3), ("get quote", 4), ("our work", 3),
                ("agency", 4), ("consulting", 4), ("strategy", 3)
            ],
            "patterns": [
                r"our (clients?|work|portfolio)",
                r"case stud(y|ies)",
                r"get (a )?quote",
                r"contact (us|our team)"
            ]
        },
        
        "realestate": {
            "keywords": [
                ("property", 5), ("real estate", 5), ("listing", 5),
                ("bedrooms", 4), ("bathroom", 4), ("sqft", 5),
                ("rent", 4), ("sale", 3), ("apartment", 4),
                ("house", 3), ("condo", 4), ("tour", 3),
                ("agent", 3), ("location", 2), ("neighborhood", 3)
            ],
            "patterns": [
                r"\d+\s*(bed|br|bedroom)",
                r"\d+\s*(bath|bathroom)",
                r"\d+\s*sq\.?\s*ft",
                r"schedule (a )?tour"
            ]
        },
        
        "education": {
            "keywords": [
                ("course", 5), ("learn", 4), ("student", 4),
                ("instructor", 4), ("lesson", 4), ("enroll", 5),
                ("curriculum", 4), ("class", 3), ("training", 4),
                ("certificate", 4), ("degree", 4), ("tuition", 4),
                ("admission", 4), ("campus", 3), ("education", 3)
            ],
            "patterns": [
                r"enroll now",
                r"cours(e|es) (catalog|list)",
                r"student (portal|login)",
                r"learn (more|online)"
            ]
        },
        
        "portfolio": {
            "keywords": [
                ("portfolio", 5), ("work", 3), ("project", 4),
                ("design", 3), ("creative", 3), ("showcase", 4),
                ("gallery", 4), ("freelance", 5), ("hire me", 5),
                ("about me", 3), ("skills", 3), ("contact", 2)
            ],
            "patterns": [
                r"my (work|portfolio|projects)",
                r"hire me",
                r"view (project|work)",
                r"(ui|ux|graphic) design"
            ]
        },
        
        "healthcare": {
            "keywords": [
                ("doctor", 5), ("patient", 5), ("appointment", 5),
                ("medical", 4), ("clinic", 5), ("hospital", 5),
                ("health", 3), ("treatment", 4), ("care", 2),
                ("physician", 4), ("dental", 4), ("insurance", 3),
                ("emergency", 4), ("schedule", 3)
            ],
            "patterns": [
                r"book (an? )?appointment",
                r"medical (care|service)",
                r"patient (portal|care)",
                r"emergency (care|service)"
            ]
        }
    }
    
    def detect_industry(self, content: str) -> Tuple[str, float, Dict[str, float]]:
        """
        Detect the industry type of a website from its content.
        
        Args:
            content: HTML or text content from the website
            
        Returns:
            Tuple of (industry_name, confidence_score, all_scores)
        """
        content_lower = content.lower()
        
        # Calculate scores for each industry
        industry_scores = {}
        
        for industry, signature in self.INDUSTRY_SIGNATURES.items():
            score = 0
            
            # Keyword matching
            for keyword, weight in signature["keywords"]:
                count = content_lower.count(keyword.lower())
                if count > 0:
                    # Logarithmic scoring to avoid overweighting frequent words
                    score += min(weight * count, weight * 3)
            
            # Pattern matching
            for pattern in signature["patterns"]:
                matches = len(re.findall(pattern, content_lower))
                if matches > 0:
                    score += min(matches * 5, 15)  # Max 15 points per pattern
            
            industry_scores[industry] = score
        
        # Find the industry with highest score
        if not industry_scores or max(industry_scores.values()) == 0:
            return "general", 0.0, industry_scores
        
        top_industry = max(industry_scores, key=industry_scores.get)
        top_score = industry_scores[top_industry]
        
        # Calculate confidence (0-1)
        total_score = sum(industry_scores.values())
        confidence = top_score / total_score if total_score > 0 else 0
        
        # Normalize confidence to 0-1 range with minimum threshold
        # If top score is very low, reduce confidence
        if top_score < 20:
            confidence *= 0.5
        
        return top_industry, confidence, industry_scores
    
    def get_industry_details(self, industry: str) -> Dict:
        """
        Get details about a detected industry.
        
        Args:
            industry: Industry name
            
        Returns:
            Dictionary with industry metadata
        """
        industry_metadata = {
            "ecommerce": {
                "name": "E-commerce",
                "description": "Online retail and shopping",
                "key_features": ["Payment options", "Delivery", "Shopping cart", "Product listings"]
            },
            "restaurant": {
                "name": "Restaurant/Food Service",
                "description": "Food and beverage services",
                "key_features": ["Menu", "Reservations", "Online ordering", "Delivery"]
            },
            "blog": {
                "name": "Blog/Content",
                "description": "Content publishing and blogging",
                "key_features": ["Articles", "Comments", "Sharing", "Newsletter"]
            },
            "saas": {
                "name": "SaaS/Software",
                "description": "Software as a service platform",
                "key_features": ["Pricing plans", "Integrations", "API", "Free trial"]
            },
            "professional_services": {
                "name": "Professional Services",
                "description": "Consulting and service businesses",
                "key_features": ["Portfolio", "Case studies", "Testimonials", "Contact forms"]
            },
            "realestate": {
                "name": "Real Estate",
                "description": "Property listings and real estate",
                "key_features": ["Property listings", "Virtual tours", "Agent contact", "Search filters"]
            },
            "education": {
                "name": "Education/E-learning",
                "description": "Online courses and education",
                "key_features": ["Course catalog", "Enrollment", "Student portal", "Certificates"]
            },
            "portfolio": {
                "name": "Portfolio/Personal",
                "description": "Personal portfolio and showcase",
                "key_features": ["Project gallery", "About", "Contact", "Skills showcase"]
            },
            "healthcare": {
                "name": "Healthcare/Medical",
                "description": "Medical and healthcare services",
                "key_features": ["Appointments", "Patient portal", "Services", "Insurance"]
            },
            "general": {
                "name": "General/Other",
                "description": "General purpose website",
                "key_features": ["Content", "Navigation", "Contact", "About"]
            }
        }
        
        return industry_metadata.get(industry, industry_metadata["general"])


# Global instance
industry_detector = IndustryDetector()
