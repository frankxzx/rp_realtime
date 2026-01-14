"""
LangChain prompt templates for conversation scenarios
"""

from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain.prompts.chat import SystemMessagePromptTemplate, HumanMessagePromptTemplate


def get_scenario_prompt_template():
    """Get the main scenario prompt template"""
    system_template = """You are a conversation practice partner for role-playing scenarios.

Scenario Context: {context}
Target Audience: {target_audience}
Purpose: {purpose}
Language: {target_language}

Your role is to:
1. Respond naturally as the {target_audience}
2. Help the user practice {purpose}
3. Keep responses conversational and realistic
4. Speak in {target_language}
5. Ask follow-up questions to keep the conversation flowing
6. Provide realistic reactions based on the scenario

{custom_instructions}

Remember to stay in character and maintain the scenario context throughout the conversation.
"""
    
    return SystemMessagePromptTemplate.from_template(system_template)


def get_feedback_prompt_template():
    """Get prompt template for generating feedback"""
    template = """Analyze the user's response in the context of this conversation practice scenario.

Scenario: {scenario_context}
Purpose: {purpose}
Ideal Answer: {ideal_answer}
User's Response: {user_response}

Provide specific, actionable feedback in the following format:
1. What was done well
2. What could be improved
3. Specific suggestions for better performance

Keep feedback constructive and encouraging.
"""
    
    return PromptTemplate(
        input_variables=["scenario_context", "purpose", "ideal_answer", "user_response"],
        template=template
    )


def get_suggestion_prompt_template():
    """Get prompt template for generating improvement suggestions"""
    template = """Based on the conversation scenario and the user's response, provide 3 specific suggestions for improvement.

Scenario Context: {context}
Purpose: {purpose}
Target Language: {target_language}

Ideal Answer: {ideal_answer}
User's Response: {user_input}

Provide 3 concrete, actionable suggestions to improve the response. Return as a JSON array of strings.
Each suggestion should be specific to this scenario and response.
"""
    
    return PromptTemplate(
        input_variables=["context", "purpose", "target_language", "ideal_answer", "user_input"],
        template=template
    )


def get_insight_prompt_template():
    """Get prompt template for generating insights"""
    template = """Analyze this response in the context of {purpose} practice.

User's Response: {user_input}
Scenario: {context}

Provide 2-3 brief insights about:
- Communication strengths demonstrated
- Areas that need development
- Patterns to be aware of

Return as a JSON array of strings. Be specific and actionable.
"""
    
    return PromptTemplate(
        input_variables=["purpose", "user_input", "context"],
        template=template
    )


def get_direction_prompt_template():
    """Get prompt template for next direction"""
    template = """Based on this response in a {purpose} practice session, what should the user focus on next?

User's Response: {user_input}
Context: {context}

Provide one clear, actionable direction (1-2 sentences) for the next step in their practice.
Focus on what would have the most impact on their improvement.
"""
    
    return PromptTemplate(
        input_variables=["purpose", "user_input", "context"],
        template=template
    )


def get_visual_analysis_prompt_template():
    """Get prompt template for visual analysis"""
    template = """Analyze the facial expressions and body language from {num_snapshots} snapshots taken during a conversation practice session.

Scenario: {scenario_context}
Purpose: {purpose}

Based on typical patterns in {purpose} scenarios, provide analysis of:
1. Overall facial expression (confident, nervous, engaged, etc.)
2. Body language indicators
3. Confidence level
4. Engagement indicators

Return as JSON with keys: facial_expression, body_language, confidence_level, engagement_indicators (array).
Be constructive and specific.
"""
    
    return PromptTemplate(
        input_variables=["num_snapshots", "scenario_context", "purpose"],
        template=template
    )


def get_assessment_summary_prompt_template():
    """Get prompt template for final assessment summary"""
    template = """Generate a comprehensive summary for a conversation practice session.

Scenario: {scenario_context}
Purpose: {purpose}
Number of Turns: {num_turns}
Overall Score: {avg_score}/10

Dimension Scores:
{dimension_scores}

Visual Analysis: {visual_summary}
Audio Analysis: {audio_summary}

Create a detailed but concise summary (3-4 sentences) that:
1. Acknowledges overall performance
2. Highlights key strengths
3. Identifies primary areas for improvement
4. Provides encouragement for continued practice

Be specific, constructive, and professional.
"""
    
    return PromptTemplate(
        input_variables=[
            "scenario_context", "purpose", "num_turns", "avg_score",
            "dimension_scores", "visual_summary", "audio_summary"
        ],
        template=template
    )
