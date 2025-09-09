"""
LangChain AI Chain Service

This module provides a reusable LangChain pipeline that integrates with Google Gemini API.
It includes conversation memory, system prompts, and structured conversation handling
for the law firm's pre-sales assistant (AI Closer).

The chain is designed to be modular and extensible for future integrations with
tools like database queries, CRM systems, or other external services.
"""

import os
import logging
from typing import Dict, Any, Optional
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_google_genai import ChatGoogleGenerativeAI
from fastapi import HTTPException, status

# Configure logging
logger = logging.getLogger(__name__)

class AIChainManager:
    """
    Manages LangChain pipeline with Google Gemini integration.
    
    This class handles:
    - LLM initialization with Gemini API
    - Conversation memory management
    - System prompt configuration
    - Chain execution and error handling
    """
    
    def __init__(self):
        self.llm = None
        self.chain = None
        self.memory = None
        self._initialize_chain()
    
    def _initialize_chain(self):
        """Initialize the LangChain pipeline with Gemini LLM."""
        try:
            # Get API key from environment
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                logger.error("GEMINI_API_KEY environment variable not set")
                raise ValueError("Gemini API key not configured")
            
            # Get system prompt from environment
            system_prompt = os.getenv("AI_SYSTEM_PROMPT", self._get_default_system_prompt())
            
            # Initialize Google Gemini LLM
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",
                google_api_key=api_key,
                temperature=0.7,
                max_output_tokens=300,
                convert_system_message_to_human=True  # Gemini compatibility
            )
            
            # Initialize conversation memory
            self.memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True,
                input_key="user_input",
                output_key="response"
            )
            
            # Create prompt template
            prompt_template = PromptTemplate(
                input_variables=["user_input", "chat_history"],
                template=f"""
{system_prompt}

Conversation History:
{{chat_history}}

User: {{user_input}}
Assistant:"""
            )
            
            # Create LLM chain
            self.chain = LLMChain(
                llm=self.llm,
                prompt=prompt_template,
                memory=self.memory,
                output_key="response",
                verbose=False
            )
            
            logger.info("LangChain pipeline initialized successfully with Gemini")
            
        except Exception as e:
            logger.error(f"Failed to initialize LangChain pipeline: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"AI chain initialization failed: {str(e)}"
            )
    
    def _get_default_system_prompt(self) -> str:
        """Get default system prompt if not provided in environment."""
        return """You are a digital pre-sales assistant (AI Closer) for a law firm in Brazil.
Your purpose is to engage leads, understand their legal concerns, and smoothly guide them to schedule a consultation on WhatsApp.

Behavior Rules:
- Always respond in Brazilian Portuguese (PT-BR).
- Keep answers short, clear, and human-like (maximum 3 sentences).
- Use a warm, persuasive, and professional tone.
- Ask open-ended questions to understand the lead's situation.
- Do not provide detailed legal advice → instead, highlight the firm's experience and reliability.
- If the user shows interest → invite them to continue the conversation on WhatsApp.
- If the user hesitates → reinforce credibility (e.g., years of experience, quick support, personalized service).
- Always sound empathetic and supportive, never robotic.

Final Objective:
- Qualify the lead (understand their situation).
- Warm up the conversation (build trust).
- Guide them to WhatsApp to schedule a consultation."""
    
    async def process_message(self, user_message: str, session_id: Optional[str] = None) -> str:
        """
        Process user message through the LangChain pipeline.
        
        Args:
            user_message (str): The user's input message
            session_id (Optional[str]): Session ID for conversation tracking
            
        Returns:
            str: The AI-generated response
            
        Raises:
            HTTPException: If processing fails
        """
        try:
            if not self.chain:
                self._initialize_chain()
            
            logger.info(f"Processing message through LangChain: {user_message[:50]}...")
            
            # Run the chain
            result = await self.chain.arun(user_input=user_message)
            
            # Extract response text
            if isinstance(result, dict):
                response = result.get("response", str(result))
            else:
                response = str(result)
            
            logger.info(f"LangChain response generated: {response[:50]}...")
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error processing message through LangChain: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process message through AI chain"
            )
    
    def clear_memory(self, session_id: Optional[str] = None):
        """
        Clear conversation memory for a fresh start.
        
        Args:
            session_id (Optional[str]): Session ID (for future session-specific memory)
        """
        try:
            if self.memory:
                self.memory.clear()
                logger.info("Conversation memory cleared")
        except Exception as e:
            logger.error(f"Error clearing memory: {str(e)}")
    
    def get_conversation_history(self, session_id: Optional[str] = None) -> list:
        """
        Get current conversation history.
        
        Args:
            session_id (Optional[str]): Session ID (for future session-specific memory)
            
        Returns:
            list: Conversation history messages
        """
        try:
            if self.memory and hasattr(self.memory, 'chat_memory'):
                return self.memory.chat_memory.messages
            return []
        except Exception as e:
            logger.error(f"Error getting conversation history: {str(e)}")
            return []
    
    def get_chain_status(self) -> Dict[str, Any]:
        """
        Get current status of the LangChain pipeline.
        
        Returns:
            Dict[str, Any]: Status information
        """
        try:
            api_key_configured = bool(os.getenv("GEMINI_API_KEY"))
            system_prompt_configured = bool(os.getenv("AI_SYSTEM_PROMPT"))
            
            return {
                "service": "langchain_ai_chain",
                "status": "active" if self.chain and api_key_configured else "configuration_required",
                "llm_model": "gemini-2.0-flash",
                "temperature": 0.7,
                "max_output_tokens": 300,
                "memory_type": "ConversationBufferMemory",
                "api_key_configured": api_key_configured,
                "system_prompt_configured": system_prompt_configured,
                "chain_initialized": bool(self.chain),
                "memory_initialized": bool(self.memory),
                "conversation_messages": len(self.get_conversation_history()),
                "features": [
                    "conversation_memory",
                    "system_prompt_support",
                    "gemini_integration",
                    "extensible_for_tools"
                ],
                "configuration_notes": [
                    "Set GEMINI_API_KEY in environment variables",
                    "Set AI_SYSTEM_PROMPT for custom behavior (optional)",
                    "Memory persists during session for context"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting chain status: {str(e)}")
            return {
                "service": "langchain_ai_chain",
                "status": "error",
                "error": str(e)
            }

# Global AI chain manager instance
ai_chain_manager = AIChainManager()

# Convenience functions for external use
async def process_with_langchain(user_message: str, session_id: Optional[str] = None) -> str:
    """
    Process message through LangChain pipeline.
    
    Args:
        user_message (str): User's message
        session_id (Optional[str]): Session identifier
        
    Returns:
        str: AI response
    """
    return await ai_chain_manager.process_message(user_message, session_id)

def clear_conversation_memory(session_id: Optional[str] = None):
    """Clear conversation memory."""
    ai_chain_manager.clear_memory(session_id)

def get_langchain_status() -> Dict[str, Any]:
    """Get LangChain service status."""
    return ai_chain_manager.get_chain_status()