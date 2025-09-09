"""
Conversation Flow Service

This module manages the guided conversation flow for law firm client intake.
It handles step-by-step questions, user responses, and transitions to AI chat.

The conversation flow is stored in Firebase and can be updated by lawyers
without modifying the code.
"""

import logging
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
from app.services.firebase_service import (
    get_conversation_flow,
    save_lead_data,
    get_user_session,
    save_user_session
)
from app.services.ai_service import process_chat_message

# Configure logging
logger = logging.getLogger(__name__)

class ConversationManager:
    """
    Manages conversation flow state and progression for users.
    
    This class handles:
    - Step-by-step guided questions
    - User response collection
    - Lead data compilation
    - Transition to AI chat mode
    """
    
    def __init__(self):
        self.flow_cache = None
        self.cache_timestamp = None
    
    async def get_flow(self) -> Dict[str, Any]:
        """Get conversation flow, with caching for performance."""
        # Cache flow for 5 minutes to reduce Firebase calls
        if (self.flow_cache is None or 
            (datetime.now() - self.cache_timestamp).seconds > 300):
            self.flow_cache = await get_conversation_flow()
            self.cache_timestamp = datetime.now()
        
        return self.flow_cache
    
    async def start_conversation(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Start a new conversation flow.
        
        Args:
            session_id (Optional[str]): Session ID, generates new if None
            
        Returns:
            Dict[str, Any]: Initial conversation state with first question
        """
        try:
            if not session_id:
                session_id = str(uuid.uuid4())
            
            flow = await self.get_flow()
            
            # Initialize session data
            session_data = {
                "session_id": session_id,
                "current_step": 1,
                "responses": {},
                "flow_completed": False,
                "ai_mode": False,
                "started_at": datetime.now()
            }
            
            await save_user_session(session_id, session_data)
            
            # Get first question
            first_step = next((step for step in flow["steps"] if step["id"] == 1), None)
            
            if not first_step:
                raise ValueError("No first step found in conversation flow")
            
            logger.info(f"Started conversation for session: {session_id}")
            
            return {
                "session_id": session_id,
                "question": first_step["question"],
                "step_id": first_step["id"],
                "is_final_step": len(flow["steps"]) == 1,
                "flow_completed": False,
                "ai_mode": False
            }
            
        except Exception as e:
            logger.error(f"Error starting conversation: {str(e)}")
            raise
    
    async def process_response(self, session_id: str, user_response: str) -> Dict[str, Any]:
        """
        Process user response and return next question or AI response.
        
        Args:
            session_id (str): The session identifier
            user_response (str): User's response to current question
            
        Returns:
            Dict[str, Any]: Next question or AI response with conversation state
        """
        try:
            # Get current session
            session_data = await get_user_session(session_id)
            if not session_data:
                # Session not found, start new conversation
                return await self.start_conversation(session_id)
            
            # If already in AI mode, use Gemini
            if session_data.get("ai_mode", False):
                ai_response = await process_chat_message(user_response)
                return {
                    "session_id": session_id,
                    "response": ai_response,
                    "ai_mode": True,
                    "flow_completed": True
                }
            
            flow = await self.get_flow()
            current_step = session_data.get("current_step", 1)
            
            # Find current step in flow
            current_step_data = next(
                (step for step in flow["steps"] if step["id"] == current_step), 
                None
            )
            
            if not current_step_data:
                logger.error(f"Step {current_step} not found in flow")
                return await self._switch_to_ai_mode(session_id, user_response)
            
            # Save user response
            field_name = current_step_data.get("field", f"step_{current_step}")
            session_data["responses"][field_name] = user_response.strip()
            
            # Check if this was the last step
            next_step = current_step + 1
            next_step_data = next(
                (step for step in flow["steps"] if step["id"] == next_step), 
                None
            )
            
            if next_step_data:
                # Move to next step
                session_data["current_step"] = next_step
                await save_user_session(session_id, session_data)
                
                is_final_step = next_step == len(flow["steps"])
                
                return {
                    "session_id": session_id,
                    "question": next_step_data["question"],
                    "step_id": next_step_data["id"],
                    "is_final_step": is_final_step,
                    "flow_completed": False,
                    "ai_mode": False
                }
            else:
                # Flow completed, save lead and switch to AI mode
                return await self._complete_flow(session_id, session_data, flow)
                
        except Exception as e:
            logger.error(f"Error processing response for session {session_id}: {str(e)}")
            # Fallback to AI mode on error
            return await self._switch_to_ai_mode(session_id, user_response)
    
    async def _complete_flow(self, session_id: str, session_data: Dict[str, Any], flow: Dict[str, Any]) -> Dict[str, Any]:
        """
        Complete the guided flow and save lead data.
        
        Args:
            session_id (str): Session identifier
            session_data (Dict[str, Any]): Current session data
            flow (Dict[str, Any]): Conversation flow configuration
            
        Returns:
            Dict[str, Any]: Completion message and AI mode activation
        """
        try:
            # Prepare lead data
            responses = session_data.get("responses", {})
            lead_data = {
                "name": responses.get("name", "Unknown"),
                "area_of_law": responses.get("area_of_law", "Not specified"),
                "situation": responses.get("situation", "Not provided"),
                "wants_meeting": responses.get("wants_meeting", "Not specified"),
                "session_id": session_id,
                "completed_at": datetime.now()
            }
            
            # Save lead to Firebase
            lead_id = await save_lead_data(lead_data)
            
            # Update session to AI mode
            session_data.update({
                "flow_completed": True,
                "ai_mode": True,
                "lead_id": lead_id,
                "completed_at": datetime.now()
            })
            
            await save_user_session(session_id, session_data)
            
            completion_message = flow.get(
                "completion_message", 
                "Thank you! Your information has been recorded. Do you have any other questions?"
            )
            
            logger.info(f"Completed flow for session {session_id}, created lead {lead_id}")
            
            return {
                "session_id": session_id,
                "response": completion_message,
                "flow_completed": True,
                "ai_mode": True,
                "lead_saved": True,
                "lead_id": lead_id
            }
            
        except Exception as e:
            logger.error(f"Error completing flow: {str(e)}")
            return await self._switch_to_ai_mode(session_id, "Thank you for your information.")
    
    async def _switch_to_ai_mode(self, session_id: str, user_message: str) -> Dict[str, Any]:
        """
        Switch to AI mode and process user message.
        
        Args:
            session_id (str): Session identifier
            user_message (str): User's message
            
        Returns:
            Dict[str, Any]: AI response
        """
        try:
            # Update session to AI mode
            session_data = await get_user_session(session_id) or {}
            session_data.update({
                "ai_mode": True,
                "switched_to_ai_at": datetime.now()
            })
            await save_user_session(session_id, session_data)
            
            # Get AI response
            ai_response = await process_chat_message(user_message)
            
            return {
                "session_id": session_id,
                "response": ai_response,
                "ai_mode": True,
                "flow_completed": True
            }
            
        except Exception as e:
            logger.error(f"Error switching to AI mode: {str(e)}")
            return {
                "session_id": session_id,
                "response": "I'm here to help with any questions you have about our legal services.",
                "ai_mode": True,
                "flow_completed": True
            }
    
    async def get_conversation_status(self, session_id: str) -> Dict[str, Any]:
        """
        Get current conversation status for a session.
        
        Args:
            session_id (str): Session identifier
            
        Returns:
            Dict[str, Any]: Current conversation state
        """
        try:
            session_data = await get_user_session(session_id)
            if not session_data:
                return {"exists": False}
            
            flow = await self.get_flow()
            current_step = session_data.get("current_step", 1)
            
            return {
                "exists": True,
                "session_id": session_id,
                "current_step": current_step,
                "total_steps": len(flow["steps"]),
                "flow_completed": session_data.get("flow_completed", False),
                "ai_mode": session_data.get("ai_mode", False),
                "responses_collected": len(session_data.get("responses", {})),
                "started_at": session_data.get("started_at"),
                "last_updated": session_data.get("last_updated")
            }
            
        except Exception as e:
            logger.error(f"Error getting conversation status: {str(e)}")
            return {"exists": False, "error": str(e)}

# Global conversation manager instance
conversation_manager = ConversationManager()