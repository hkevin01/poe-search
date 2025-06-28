"""Categorization worker for auto-categorizing conversations."""

import logging
from typing import Dict, Any, List, Optional
import re

from PyQt6.QtCore import QThread, pyqtSignal

from poe_search.client import PoeSearchClient

logger = logging.getLogger(__name__)


class CategoryRule:
    """Represents a categorization rule."""
    
    def __init__(self, name: str, category: str, keywords: List[str], 
                 pattern: Optional[str] = None, confidence: float = 0.7):
        """Initialize category rule.
        
        Args:
            name: Rule name
            category: Category to assign
            keywords: Keywords to match
            pattern: Optional regex pattern
            confidence: Confidence threshold (0.0-1.0)
        """
        self.name = name
        self.category = category
        self.keywords = [k.lower() for k in keywords]
        self.pattern = re.compile(pattern, re.IGNORECASE) if pattern else None
        self.confidence = confidence
    
    def matches(self, text: str) -> float:
        """Check if rule matches text and return confidence score.
        
        Args:
            text: Text to check
            
        Returns:
            Confidence score (0.0-1.0)
        """
        if not text:
            return 0.0
        
        text_lower = text.lower()
        
        # Check pattern first (higher priority)
        if self.pattern and self.pattern.search(text):
            return min(1.0, self.confidence + 0.2)
        
        # Check keywords
        matches = sum(1 for keyword in self.keywords if keyword in text_lower)
        
        if matches == 0:
            return 0.0
        
        # Calculate confidence based on keyword density
        word_count = len(text_lower.split())
        keyword_density = matches / max(word_count, 1)
        
        # Scale confidence based on matches and density
        base_confidence = min(matches / len(self.keywords), 1.0)
        density_bonus = min(keyword_density * 2, 0.3)
        
        return min(base_confidence + density_bonus, 1.0)


class CategoryWorker(QThread):
    """Worker thread for categorizing conversations."""
    
    # Signals
    progress_updated = pyqtSignal(int, str)  # Progress percentage, status message
    conversation_categorized = pyqtSignal(str, str, float)  # ID, category, confidence
    categorization_complete = pyqtSignal(dict)  # Statistics
    error_occurred = pyqtSignal(str)  # Error message
    
    def __init__(self, client: PoeSearchClient, rules: Optional[List[CategoryRule]] = None,
                 conversation_ids: Optional[List[str]] = None):
        """Initialize categorization worker.
        
        Args:
            client: Poe Search client
            rules: Categorization rules (uses default if None)
            conversation_ids: Specific conversation IDs to categorize
        """
        super().__init__()
        
        self.client = client
        self.rules = rules or self.get_default_rules()
        self.conversation_ids = conversation_ids
        self.should_stop = False
    
    def get_default_rules(self) -> List[CategoryRule]:
        """Get default categorization rules.
        
        Returns:
            List of default rules
        """
        return [
            CategoryRule(
                "Technical",
                "Technical",
                ["programming", "code", "software", "development", "python", "javascript", 
                 "algorithm", "database", "api", "framework", "debug", "error", "function",
                 "variable", "class", "method", "library", "package", "git", "github"],
                r"\b(def|class|import|from|function|var|let|const|SELECT|UPDATE|INSERT)\b"
            ),
            CategoryRule(
                "Medical",
                "Medical",
                ["health", "medical", "doctor", "medicine", "symptom", "treatment", "therapy",
                 "diagnosis", "hospital", "clinic", "patient", "disease", "illness", "medication",
                 "prescription", "surgery", "anatomy", "physiology", "psychology"],
                r"\b(mg|ml|dosage|prescription|diagnosis|symptoms?)\b"
            ),
            CategoryRule(
                "Spiritual",
                "Spiritual", 
                ["spiritual", "meditation", "mindfulness", "religion", "faith", "prayer",
                 "god", "divine", "soul", "enlightenment", "consciousness", "buddhism",
                 "christianity", "islam", "judaism", "hinduism", "yoga", "chakra"],
                r"\b(meditation|prayer|enlightenment|consciousness|divine)\b"
            ),
            CategoryRule(
                "Political",
                "Political",
                ["politics", "government", "policy", "election", "democracy", "republican",
                 "democrat", "conservative", "liberal", "vote", "legislation", "congress",
                 "senate", "president", "political", "economy", "economic", "tax"],
                r"\b(election|congress|senate|legislation|policy|democrat|republican)\b"
            ),
            CategoryRule(
                "Entertainment",
                "Entertainment",
                ["movie", "film", "music", "song", "game", "gaming", "book", "novel",
                 "tv", "television", "show", "series", "actor", "artist", "celebrity",
                 "entertainment", "fun", "hobby", "sport", "sports"],
                r"\b(movie|film|music|game|book|tv show|series)\b"
            ),
            CategoryRule(
                "Education",
                "Education",
                ["education", "learning", "study", "school", "university", "college",
                 "student", "teacher", "course", "lesson", "homework", "assignment",
                 "research", "academic", "science", "math", "history", "literature"],
                r"\b(study|learn|education|school|university|research|academic)\b"
            ),
            CategoryRule(
                "Business",
                "Business",
                ["business", "company", "corporate", "management", "marketing", "sales",
                 "profit", "revenue", "strategy", "investment", "finance", "money",
                 "career", "job", "work", "professional", "industry", "market"],
                r"\b(business|company|marketing|sales|investment|finance|career)\b"
            ),
            CategoryRule(
                "Creative",
                "Creative",
                ["creative", "art", "design", "writing", "poetry", "painting", "drawing",
                 "photography", "music", "composition", "creative writing", "artistic",
                 "inspiration", "imagination", "craft", "make", "create"],
                r"\b(creative|art|design|writing|poetry|painting|artistic|inspiration)\b"
            )
        ]
    
    def stop(self):
        """Stop the categorization operation."""
        self.should_stop = True
    
    def run(self):
        """Run the categorization operation."""
        try:
            logger.info("Starting conversation categorization")
            
            stats = {
                'categorized': 0,
                'unchanged': 0,
                'failed': 0,
                'total': 0
            }
            
            # Get conversations to categorize
            if self.conversation_ids:
                conversations = []
                for conv_id in self.conversation_ids:
                    conv = self.client.database.get_conversation(conv_id)
                    if conv:
                        conversations.append(conv)
            else:
                # Get all conversations without categories
                conversations = self.client.database.get_conversations(
                    filter_uncategorized=True
                )
            
            total_conversations = len(conversations)
            stats['total'] = total_conversations
            
            logger.info(f"Found {total_conversations} conversations to categorize")
            
            if total_conversations == 0:
                self.progress_updated.emit(100, "No conversations to categorize")
                self.categorization_complete.emit(stats)
                return
            
            # Categorize each conversation
            for i, conversation in enumerate(conversations):
                if self.should_stop:
                    break
                
                try:
                    # Update progress
                    progress = int((i / total_conversations) * 100)
                    self.progress_updated.emit(
                        progress, 
                        f"Categorizing conversation {i+1}/{total_conversations}"
                    )
                    
                    # Extract text content for categorization
                    content = self.extract_conversation_text(conversation)
                    
                    # Find best matching category
                    best_category, confidence = self.categorize_text(content)
                    
                    if best_category and confidence >= 0.5:  # Minimum confidence threshold
                        # Update conversation category
                        conversation_id = conversation.get('id')
                        current_category = conversation.get('category')
                        
                        if current_category != best_category:
                            self.client.database.update_conversation_category(
                                conversation_id, best_category
                            )
                            
                            self.conversation_categorized.emit(
                                conversation_id, best_category, confidence
                            )
                            stats['categorized'] += 1
                            
                            logger.debug(f"Categorized conversation {conversation_id} as {best_category} (confidence: {confidence:.2f})")
                        else:
                            stats['unchanged'] += 1
                    else:
                        stats['unchanged'] += 1
                        logger.debug(f"No suitable category found for conversation {conversation.get('id')} (best confidence: {confidence:.2f})")
                
                except Exception as e:
                    stats['failed'] += 1
                    logger.error(f"Error categorizing conversation {conversation.get('id', 'unknown')}: {e}")
                    continue
            
            # Final progress update
            self.progress_updated.emit(100, "Categorization completed")
            
            logger.info(f"Categorization completed: {stats['categorized']} categorized, {stats['unchanged']} unchanged, {stats['failed']} failed")
            
            # Emit completion signal
            self.categorization_complete.emit(stats)
            
        except Exception as e:
            logger.error(f"Categorization worker error: {e}")
            self.error_occurred.emit(str(e))
    
    def extract_conversation_text(self, conversation: Dict[str, Any]) -> str:
        """Extract text content from conversation for categorization.
        
        Args:
            conversation: Conversation data
            
        Returns:
            Combined text content
        """
        text_parts = []
        
        # Add title if available
        if conversation.get('title'):
            text_parts.append(conversation['title'])
        
        # Add messages
        messages = conversation.get('messages', [])
        for message in messages:
            if isinstance(message, dict):
                content = message.get('content', message.get('text', ''))
                if content:
                    text_parts.append(content)
            elif isinstance(message, str):
                text_parts.append(message)
        
        # Add any additional text fields
        for field in ['description', 'summary', 'tags']:
            if conversation.get(field):
                text_parts.append(str(conversation[field]))
        
        return ' '.join(text_parts)
    
    def categorize_text(self, text: str) -> tuple[Optional[str], float]:
        """Categorize text using rules.
        
        Args:
            text: Text to categorize
            
        Returns:
            Tuple of (category, confidence)
        """
        if not text:
            return None, 0.0
        
        best_category = None
        best_confidence = 0.0
        
        # Test all rules
        for rule in self.rules:
            confidence = rule.matches(text)
            
            if confidence > best_confidence:
                best_category = rule.category
                best_confidence = confidence
        
        return best_category, best_confidence
