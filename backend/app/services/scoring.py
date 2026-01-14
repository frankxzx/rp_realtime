from app.core.config import settings
from typing import Dict, List
import random


class ScoringService:
    """Service for scoring conversation performance"""
    
    def __init__(self):
        self.dimensions = settings.scoring_dimensions_list
    
    async def score_response(
        self,
        user_input: str,
        ideal_answer: str,
        scenario_context: str
    ) -> Dict[str, float]:
        """
        Score the user's response across multiple dimensions
        
        Args:
            user_input: User's spoken response
            ideal_answer: Ideal answer for comparison
            scenario_context: Context of the conversation
            
        Returns:
            Dictionary mapping dimension names to scores (0-10)
        """
        scores = {}
        
        for dimension in self.dimensions:
            score = await self._score_dimension(
                dimension, 
                user_input, 
                ideal_answer,
                scenario_context
            )
            scores[dimension] = round(score, 2)
        
        return scores
    
    async def _score_dimension(
        self,
        dimension: str,
        user_input: str,
        ideal_answer: str,
        scenario_context: str
    ) -> float:
        """
        Score a specific dimension
        This is a simplified scoring - in production, you'd use ML models
        """
        user_length = len(user_input.split())
        ideal_length = len(ideal_answer.split())
        
        # Base score on length comparison
        base_score = 5.0
        
        if dimension == "fluency":
            # Fluency based on response length and completeness
            if user_length > 10:
                base_score = 7.0 + min(3.0, user_length / 20)
            else:
                base_score = 5.0
        
        elif dimension == "accuracy":
            # Accuracy based on keyword overlap with ideal answer
            user_words = set(user_input.lower().split())
            ideal_words = set(ideal_answer.lower().split())
            overlap = len(user_words & ideal_words) / max(len(ideal_words), 1)
            base_score = 5.0 + (overlap * 5.0)
        
        elif dimension == "relevance":
            # Relevance based on context keywords
            context_keywords = scenario_context.lower().split()
            user_words = user_input.lower().split()
            relevance = sum(1 for word in user_words if word in context_keywords)
            base_score = 5.0 + min(5.0, relevance)
        
        elif dimension == "confidence":
            # Confidence based on response length and structure
            has_examples = "for example" in user_input.lower() or "such as" in user_input.lower()
            base_score = 6.0 if user_length > 15 else 5.0
            if has_examples:
                base_score += 1.0
        
        elif dimension == "engagement":
            # Engagement based on response enthusiasm indicators
            enthusiasm_markers = ["!", "really", "very", "excited", "passionate"]
            engagement_count = sum(1 for marker in enthusiasm_markers if marker in user_input.lower())
            base_score = 6.0 + min(2.0, engagement_count)
        
        else:
            # Default scoring for custom dimensions
            base_score = 6.0 + random.uniform(-1.0, 2.0)
        
        # Add some variance
        score = base_score + random.uniform(-0.5, 0.5)
        
        # Ensure score is between 0 and 10
        return max(0.0, min(10.0, score))
    
    async def calculate_overall_scores(
        self,
        turn_scores: List[Dict[str, float]]
    ) -> Dict[str, float]:
        """Calculate overall scores by averaging across all turns"""
        if not turn_scores:
            return {dim: 0.0 for dim in self.dimensions}
        
        overall = {}
        for dimension in self.dimensions:
            scores = [turn.get(dimension, 0.0) for turn in turn_scores]
            overall[dimension] = round(sum(scores) / len(scores), 2)
        
        return overall


scoring_service = ScoringService()
