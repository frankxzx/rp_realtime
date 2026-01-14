"""
Sample Q&A data for generating ideal answers.
This can be extended or replaced with a database.
"""

QA_DATA = {
    "job_interview": [
        {
            "question": "Tell me about yourself",
            "ideal_answer": "I'd start with a brief professional summary highlighting my relevant experience, key achievements, and how they align with this role. I'd keep it concise, under 2 minutes, focusing on what makes me a strong fit.",
            "keywords": ["experience", "achievements", "fit", "professional"]
        },
        {
            "question": "What are your strengths",
            "ideal_answer": "I'd choose 2-3 specific strengths relevant to the job, provide concrete examples of how I've demonstrated them, and explain how they'd benefit this role.",
            "keywords": ["strengths", "examples", "relevant", "benefit"]
        },
        {
            "question": "Why do you want to work here",
            "ideal_answer": "I'd mention specific aspects of the company that align with my career goals, demonstrate my research about their mission and values, and explain how my skills can contribute to their objectives.",
            "keywords": ["company research", "alignment", "contribution", "values"]
        }
    ],
    "customer_service": [
        {
            "question": "I have a complaint about my order",
            "ideal_answer": "I'd start by empathizing with the customer, acknowledging their concern, asking specific questions to understand the issue, and offering a clear solution or next steps.",
            "keywords": ["empathy", "acknowledge", "solution", "listen"]
        },
        {
            "question": "Can you help me with this product",
            "ideal_answer": "I'd confirm what specific help they need, ask clarifying questions, provide clear step-by-step guidance, and ensure they understand before concluding.",
            "keywords": ["clarify", "guide", "patient", "helpful"]
        }
    ],
    "sales_pitch": [
        {
            "question": "Why should I buy this product",
            "ideal_answer": "I'd focus on understanding their specific needs first, then highlight 2-3 key benefits that directly address those needs, provide evidence or examples, and create urgency without being pushy.",
            "keywords": ["needs", "benefits", "value", "evidence"]
        }
    ],
    "presentation": [
        {
            "question": "What is your main message",
            "ideal_answer": "I'd state a clear, concise main message, support it with 3 key points, use specific examples or data, and relate it back to the audience's interests.",
            "keywords": ["clear", "concise", "evidence", "audience"]
        }
    ]
}


def get_ideal_answer(scenario_context: str, user_input: str) -> str:
    """
    Find ideal answer based on scenario context and user input.
    Uses simple keyword matching - can be enhanced with embeddings.
    """
    # Convert scenario context to lowercase for matching
    context_lower = scenario_context.lower()
    
    # Determine scenario category
    category = "job_interview"  # default
    if "customer" in context_lower or "service" in context_lower:
        category = "customer_service"
    elif "sales" in context_lower or "pitch" in context_lower:
        category = "sales_pitch"
    elif "presentation" in context_lower or "present" in context_lower:
        category = "presentation"
    
    # Get Q&A for category
    qa_list = QA_DATA.get(category, QA_DATA["job_interview"])
    
    # Simple keyword matching to find most relevant ideal answer
    user_input_lower = user_input.lower()
    best_match = None
    best_score = 0
    
    for qa in qa_list:
        score = sum(1 for keyword in qa["keywords"] if keyword in user_input_lower)
        if score > best_score:
            best_score = score
            best_match = qa
    
    if best_match:
        return best_match["ideal_answer"]
    
    # Default response if no match
    return "Focus on being clear, concise, and addressing the key points directly. Use specific examples to support your statements."
