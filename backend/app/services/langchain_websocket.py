"""
LangChain WebSocket service for streaming responses from Azure OpenAI
"""
from langchain_openai import AzureChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from app.core.config import settings
from app.models.schemas import ScenarioConfig
from typing import List, Dict, AsyncIterator
import json


class LangChainWebSocketService:
    """Service for streaming Azure OpenAI responses using LangChain with WebSocket"""
    
    def __init__(self):
        self.llm = AzureChatOpenAI(
            azure_endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
            azure_deployment=settings.azure_openai_deployment_name,
            temperature=0.7,
            streaming=True
        )
    
    def _build_system_message(self, scenario: ScenarioConfig) -> str:
        """
        Build system prompt from scenario configuration
        
        Args:
            scenario: ScenarioConfig with context, audience, purpose, etc.
            
        Returns:
            Formatted system prompt string for the AI assistant
        """
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
    
    async def stream_response(
        self,
        user_input: str,
        scenario: ScenarioConfig,
        conversation_history: List[Dict] = None
    ) -> AsyncIterator[str]:
        """
        Stream AI response using LangChain
        
        Args:
            user_input: User's input message
            scenario: Scenario configuration
            conversation_history: Previous conversation turns
            
        Yields:
            Chunks of AI response text
        """
        # Build messages
        messages = []
        
        # System message
        system_content = self._build_system_message(scenario)
        messages.append(SystemMessage(content=system_content))
        
        # Add conversation history
        if conversation_history:
            for turn in conversation_history:
                messages.append(HumanMessage(content=turn.get("user", "")))
                messages.append(AIMessage(content=turn.get("assistant", "")))
        
        # Add current user input
        messages.append(HumanMessage(content=user_input))
        
        # Stream response
        async for chunk in self.llm.astream(messages):
            if chunk.content:
                yield chunk.content
    
    async def generate_complete_response(
        self,
        user_input: str,
        scenario: ScenarioConfig,
        conversation_history: List[Dict] = None
    ) -> str:
        """
        Generate complete response (non-streaming version)
        
        Args:
            user_input: User's input message
            scenario: Scenario configuration
            conversation_history: Previous conversation turns
            
        Returns:
            Complete AI response
        """
        # Build messages
        messages = []
        
        # System message
        system_content = self._build_system_message(scenario)
        messages.append(SystemMessage(content=system_content))
        
        # Add conversation history
        if conversation_history:
            for turn in conversation_history:
                messages.append(HumanMessage(content=turn.get("user", "")))
                messages.append(AIMessage(content=turn.get("assistant", "")))
        
        # Add current user input
        messages.append(HumanMessage(content=user_input))
        
        # Generate response
        response = await self.llm.ainvoke(messages)
        return response.content


langchain_websocket_service = LangChainWebSocketService()
