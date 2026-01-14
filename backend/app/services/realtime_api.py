from openai import AzureOpenAI
from app.core.config import settings
from app.models.schemas import ScenarioConfig
from typing import List, Dict
import json


class RealtimeAPIService:
    """Service for Azure OpenAI Realtime API"""
    
    def __init__(self):
        self.client = AzureOpenAI(
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
            azure_endpoint=settings.azure_openai_endpoint
        )
        self.deployment_name = settings.azure_openai_deployment_name
    
    async def generate_response(
        self, 
        user_input: str, 
        scenario: ScenarioConfig,
        conversation_history: List[Dict] = None
    ) -> str:
        """
        Generate AI response using Azure OpenAI
        
        Args:
            user_input: User's spoken input
            scenario: Scenario configuration
            conversation_history: Previous conversation turns
            
        Returns:
            AI response text
        """
        # Build messages
        messages = []
        
        # System message with scenario context
        system_message = self._build_system_prompt(scenario)
        messages.append({"role": "system", "content": system_message})
        
        # Add conversation history
        if conversation_history:
            for turn in conversation_history:
                messages.append({"role": "user", "content": turn.get("user")})
                messages.append({"role": "assistant", "content": turn.get("assistant")})
        
        # Add current user input
        messages.append({"role": "user", "content": user_input})
        
        # Generate response
        response = self.client.chat.completions.create(
            model=self.deployment_name,
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content
    
    async def generate_suggestions(
        self,
        user_input: str,
        ideal_answer: str,
        scenario: ScenarioConfig
    ) -> List[str]:
        """Generate conversation improvement suggestions"""
        prompt = f"""Based on the conversation scenario and the user's response, provide 3 specific suggestions for improvement.

Scenario Context: {scenario.context}
Purpose: {scenario.purpose}
Target Language: {scenario.target_language}

Ideal Answer: {ideal_answer}
User's Response: {user_input}

Provide 3 concrete, actionable suggestions to improve the response. Return as a JSON array of strings."""

        response = self.client.chat.completions.create(
            model=self.deployment_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=300
        )
        
        try:
            suggestions = json.loads(response.choices[0].message.content)
            if isinstance(suggestions, list):
                return suggestions[:3]
        except:
            pass
        
        # Fallback
        return [
            "Focus on clarity and conciseness",
            "Use more specific examples",
            "Maintain professional tone"
        ]
    
    async def generate_insights(
        self,
        user_input: str,
        scenario: ScenarioConfig
    ) -> List[str]:
        """Generate insights about the user's performance"""
        prompt = f"""Analyze this response in the context of {scenario.purpose} practice.

User's Response: {user_input}

Provide 2-3 brief insights about strengths or areas for improvement. Return as a JSON array of strings."""

        response = self.client.chat.completions.create(
            model=self.deployment_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=200
        )
        
        try:
            insights = json.loads(response.choices[0].message.content)
            if isinstance(insights, list):
                return insights[:3]
        except:
            pass
        
        return ["Keep practicing to improve fluency"]
    
    async def generate_direction(
        self,
        user_input: str,
        scenario: ScenarioConfig
    ) -> str:
        """Generate direction for next steps"""
        prompt = f"""Based on this response in a {scenario.purpose} practice session, what should the user focus on next?

User's Response: {user_input}

Provide one clear, actionable direction (1-2 sentences)."""

        response = self.client.chat.completions.create(
            model=self.deployment_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=100
        )
        
        return response.choices[0].message.content.strip()
    
    async def analyze_visual(self, image_urls: List[str]) -> Dict:
        """
        Analyze facial expressions and body language from images
        
        Args:
            image_urls: List of image URLs to analyze
            
        Returns:
            Dictionary with visual analysis
        """
        # Note: This requires GPT-4 Vision API
        # For now, returning placeholder data
        # In production, you'd use the vision API to analyze the images
        
        prompt = f"""Analyze the facial expressions and body language from {len(image_urls)} snapshots taken during a conversation practice session.

Provide analysis of:
1. Overall facial expression (confident, nervous, engaged, etc.)
2. Body language indicators
3. Confidence level
4. Engagement indicators

Return as JSON with keys: facial_expression, body_language, confidence_level, engagement_indicators (array)"""

        # Placeholder response since vision analysis requires specific API setup
        return {
            "facial_expression": "engaged and attentive",
            "body_language": "open posture with good eye contact",
            "confidence_level": "moderate to high",
            "engagement_indicators": [
                "maintained eye contact",
                "appropriate facial expressions",
                "steady posture"
            ]
        }
    
    def _build_system_prompt(self, scenario: ScenarioConfig) -> str:
        """Build system prompt from scenario configuration"""
        prompt = f"""You are a conversation practice partner for role-playing scenarios.

Scenario Context: {scenario.context}
Target Audience: {scenario.target_audience}
Purpose: {scenario.purpose}
Language: {scenario.target_language}

Your role is to:
1. Respond naturally as the {scenario.target_audience}
2. Help the user practice {scenario.purpose}
3. Keep responses conversational and realistic
4. Speak in {scenario.target_language}
"""
        
        if scenario.custom_prompt:
            prompt += f"\n\nAdditional Instructions: {scenario.custom_prompt}"
        
        return prompt


realtime_api_service = RealtimeAPIService()
