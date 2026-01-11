"""
Industry-Adaptive NLP Feature Discovery

Dynamically discovers features based on detected website industry:
- Auto-detects industry type (e-commerce, restaurant, blog, SaaS, etc.)
- Loads industry-specific feature rules
- Discovers features relevant to that industry
- Falls back to general feature detection if industry unknown
"""

import re
from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass
from collections import Counter
from industry_detector import industry_detector
from dynamic_feature_rules import dynamic_rules


@dataclass
class NLPFeature:
    feature_name: str
    category: str
    confidence: float
    evidence: List[str]
    discovery_method: str  # 'keyword', 'pattern', 'template'
    industry: str = "general"  # Industry context


class IndustryAdaptiveNLPDiscovery:
    """Industry-adaptive feature discovery using NLP techniques."""
    
    def __init__(self):
        self.detected_industry = None
        self.industry_confidence = 0.0
    
    def discover_features(self, page_content: str, page_type: str = "unknown",
                         force_industry: Optional[str] = None) -> List[NLPFeature]:
        """
        Discover features from page content using industry-adaptive NLP.
        
        Args:
            page_content: HTML or text content from the page
            page_type: Type of page (homepage, product, etc.)
            force_industry: Force a specific industry (skip detection)
            
        Returns:
            List of discovered features
        """
        # Step 1: Detect industry (or use forced industry)
        if force_industry:
            industry = force_industry
            confidence = 1.0
        else:
            industry, confidence, _ = industry_detector.detect_industry(page_content)
        
        self.detected_industry = industry
        self.industry_confidence = confidence
        
        print(f"[NLP_DISCOVERY] Detected industry: {industry} (confidence: {confidence:.2f})")
        
        # Step 2: Get industry-specific rules
        rules = dynamic_rules.get_rules_for_industry(industry)
        
        # Step 3: Discover features using industry-specific keywords
        discovered = []
        
        # Clean and prepare text
        text = self._extract_text(page_content)
        sentences = self._split_sentences(text)
        
        # Method 1: Keyword-based discovery (industry-specific)
        keyword_features = self._discover_by_keywords(
            sentences, rules["keywords"], industry
        )
        discovered.extend(keyword_features)
        
        # Method 2: Pattern-based extraction (generic patterns)
        pattern_features = self._discover_generic_patterns(text, industry)
        discovered.extend(pattern_features)
        
        # Deduplicate and merge
        unique_features = self._deduplicate_features(discovered)
        
        print(f"[NLP_DISCOVERY] Found {len(unique_features)} features for {industry} industry")
        
        return unique_features
    
    def _extract_text(self, html_content: str) -> str:
        """Extract clean text from HTML content."""
        # Remove script and style tags
        text = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', text)
        
        # Decode HTML entities
        text = re.sub(r'&nbsp;', ' ', text)
        text = re.sub(r'&amp;', '&', text)
        text = re.sub(r'&lt;', '<', text)
        text = re.sub(r'&gt;', '>', text)
        
        # Clean whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        sentences = re.split(r'[.!?\n]+', text)
        return [s.strip() for s in sentences if len(s.strip()) > 10]
    
    def _discover_by_keywords(self, sentences: List[str], 
                             category_keywords: Dict[str, List[str]],
                             industry: str) -> List[NLPFeature]:
        """
        Discover features based on industry-specific keywords.
        
        Args:
            sentences: List of sentences from content
            category_keywords: Dict of category -> keywords for this industry
            industry: Detected industry name
            
        Returns:
            List of discovered features
        """
        features = []
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            
            for category, keywords in category_keywords.items():
                # Count matching keywords
                keyword_matches = sum(1 for kw in keywords if kw in sentence_lower)
                
                if keyword_matches >= 2:  # At least 2 keywords for confidence
                    # Extract potential feature name
                    feature_name = self._extract_feature_name(sentence, category, keywords)
                    
                    if feature_name:
                        confidence = min(0.9, 0.4 + keyword_matches * 0.1)
                        features.append(NLPFeature(
                            feature_name=feature_name,
                            category=category,
                            confidence=confidence,
                            evidence=[sentence],
                            discovery_method="keyword",
                            industry=industry
                        ))
        
        return features
    
    def _discover_generic_patterns(self, text: str, industry: str) -> List[NLPFeature]:
        """
        Discover features using generic patterns that work across industries.
        
        Args:
            text: Full text content
            industry: Detected industry
            
        Returns:
            List of discovered features
        """
        features = []
        
        # Generic patterns that indicate features
        generic_patterns = {
            "Service": [
                r"(24/7|24x7)\s+(\w+\s+){0,2}(support|service|help)",
                r"(free|complimentary)\s+(\w+)",
                r"(instant|immediate|quick)\s+(\w+)",
            ],
            "Feature": [
                r"(advanced|premium|pro)\s+(\w+)",
                r"(unlimited|unrestricted)\s+(\w+)",
                r"(easy|simple|quick)\s+(\w+)",
            ],
            "Benefit": [
                r"(100%|fully?)\s+(guaranteed?|secure|safe)",
                r"(certified?|verified?)\s+(\w+)",
            ]
        }
        
        for category, patterns in generic_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                
                for match in matches:
                    # Get context around match
                    start = max(0, match.start() - 100)
                    end = min(len(text), match.end() + 100)
                    context = text[start:end].strip()
                    
                    # Extract feature name from match
                    matched_text = match.group(0)
                    feature_name = self._normalize_feature_name(matched_text)
                    
                    if feature_name:
                        features.append(NLPFeature(
                            feature_name=feature_name,
                            category=category,
                            confidence=0.7,
                            evidence=[context],
                            discovery_method="pattern",
                            industry=industry
                        ))
        
        return features
    
    def _extract_feature_name(self, sentence: str, category: str, 
                             keywords: List[str]) -> str:
        """
        Extract a meaningful feature name from sentence.
        
        Args:
            sentence: Sentence containing feature mention
            category: Feature category
            keywords: Keywords that triggered detection
            
        Returns:
            Extracted feature name
        """
        sentence = sentence.strip()
        
        # Try to find capitalized multi-word phrases
        caps_phrases = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', sentence)
        if caps_phrases:
            return caps_phrases[0]
        
        # Try to find keyword-containing phrases
        for keyword in keywords:
            # Find phrase containing keyword
            pattern = rf'\b(\w+\s+){{0,2}}{re.escape(keyword)}(\s+\w+){{0,2}}\b'
            match = re.search(pattern, sentence, re.IGNORECASE)
            if match:
                phrase = match.group(0).strip()
                if 3 < len(phrase) < 50:
                    return self._normalize_feature_name(phrase)
        
        # Fall back to first few words
        words = sentence.split()
        if len(words) <= 5:
            return sentence.title()
        else:
            return ' '.join(words[:4]).title()
    
    def _normalize_feature_name(self, name: str) -> str:
        """Normalize feature name to consistent format."""
        # Clean up
        name = name.strip()
        name = re.sub(r'\s+', ' ', name)
        
        # Title case
        name = name.title()
        
        # Remove invalid characters
        name = re.sub(r'[^\w\s&-]', '', name)
        
        # Must be reasonable length
        if len(name) < 3 or len(name) > 50:
            return ""
        
        return name
    
    def _deduplicate_features(self, features: List[NLPFeature]) -> List[NLPFeature]:
        """Remove duplicate features and merge evidence."""
        feature_map = {}
        
        for feature in features:
            key = (feature.feature_name.lower(), feature.category)
            
            if key in feature_map:
                # Merge with existing
                existing = feature_map[key]
                existing.evidence.extend(feature.evidence)
                existing.confidence = max(existing.confidence, feature.confidence)
            else:
                feature_map[key] = feature
        
        # Sort by confidence
        unique_features = sorted(feature_map.values(), 
                                key=lambda f: f.confidence, 
                                reverse=True)
        
        return unique_features
    
    def get_complementary_features(self, nlp_features: List[NLPFeature], 
                                   rule_features: List) -> List[NLPFeature]:
        """
        Get NLP-discovered features that complement (don't overlap with) rule-based features.
        
        Args:
            nlp_features: Features discovered by NLP
            rule_features: Features discovered by rule-based detector
            
        Returns:
            NLP features that are truly new discoveries
        """
        rule_names = {f.feature_name.lower() for f in rule_features}
        
        complementary = []
        for nlp_feat in nlp_features:
            # Check if this is a new discovery
            if nlp_feat.feature_name.lower() not in rule_names:
                # Check for partial matches (avoid very similar features)
                is_new = True
                for rule_name in rule_names:
                    if self._are_similar(nlp_feat.feature_name, rule_name):
                        is_new = False
                        break
                
                if is_new:
                    complementary.append(nlp_feat)
        
        return complementary
    
    def _are_similar(self, name1: str, name2: str, threshold: float = 0.7) -> bool:
        """Check if two feature names are similar."""
        name1_lower = name1.lower()
        name2_lower = name2.lower()
        
        # Check for substring match
        if name1_lower in name2_lower or name2_lower in name1_lower:
            return True
        
        # Simple word overlap similarity
        words1 = set(name1_lower.split())
        words2 = set(name2_lower.split())
        
        if not words1 or not words2:
            return False
        
        overlap = len(words1 & words2)
        total = len(words1 | words2)
        
        similarity = overlap / total if total > 0 else 0
        
        return similarity >= threshold
    
    def get_detected_industry(self) -> Tuple[str, float]:
        """
        Get the detected industry from last analysis.
        
        Returns:
            Tuple of (industry_name, confidence_score)
        """
        return self.detected_industry or "general", self.industry_confidence


# Global instance
nlp_discoverer = IndustryAdaptiveNLPDiscovery()
