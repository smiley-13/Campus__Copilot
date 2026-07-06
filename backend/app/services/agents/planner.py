import logging
from app.services.agents.base import BaseAgent, AgentContext
from app.schemas.agent import AgentRequest, AgentResponse, PlannerClassification
from app.services.agents.registry import AgentRegistry
from app.core.llm import generate_structured_data

# Import all agents so they register themselves
import app.services.agents.study
import app.services.agents.attendance
import app.services.agents.assignment
import app.services.agents.career
import app.services.agents.general

from app.services.memory_service import MemoryService
import app.services.agents.memory_agent # Import memory agent
from app.services.context.conversation_manager import ConversationManager
from app.services.context.decision_engine import DecisionEngine
from app.core.prompts import PLANNER_CLASSIFICATION_PROMPT
import time
from app.core.llm import reset_gemini_calls, get_gemini_calls

import logging
logger = logging.getLogger(__name__)

class PlannerAgent(BaseAgent):
    """
    The main orchestrator.
    Receives all requests, determines multiple intents via Gemini, 
    routes to the correct specialized agents, and merges responses.
    """
    @property
    def name(self) -> str:
        return "planner_agent"
        
    @property
    def description(self) -> str:
        return "Central orchestrator that detects intent and routes requests to specialized agents."

    def _classify_intents(self, message: str) -> PlannerClassification:
        logger.info(f"[PlannerAgent] Classifying intent for message: '{message}'")
        
        classification_prompt = PLANNER_CLASSIFICATION_PROMPT.format(message=message)
        
        try:
            classification = generate_structured_data(classification_prompt, PlannerClassification)
            
            # Log detected intents as requested
            intents_str = ", ".join(classification.intents)
            logger.info(f"Detected Intent: {intents_str}")
            
            # Ensure general_agent is used if empty
            if not classification.target_agents:
                classification.target_agents = ["general_agent"]
                classification.intents = ["general_conversation"]
            return classification
        except Exception as e:
            logger.error(f"[PlannerAgent] Classification failed: {e}", exc_info=True)
            # Do NOT default to General Agent silently unless it's truly a greeting
            raise e

    def process(self, request: AgentRequest, context: AgentContext) -> AgentResponse:
        start_time = time.time()
        reset_gemini_calls()
        self._log_processing("Orchestrating request")
        
        # 1. Intent Classification
        decision_method = "Rule-Based"
        classification, extracted_params, conf = DecisionEngine.classify(request.message)
        
        if not classification or conf < 0.90:
            decision_method = "Gemini"
            classification = self._classify_intents(request.message)
            
        logger.info(f"[PlannerAgent] Classification ({decision_method}): {classification.model_dump()}")
        
        # Inject intents and extracted params into context
        context.set("detected_intents", classification.intents)
        if extracted_params:
            context.set("extracted_params", extracted_params)
        
        # Update Conversation State
        ConversationManager.update_state(
            user_id=request.user_id,
            role="user",
            content=request.message,
            topic=classification.intents[0] if classification.intents else "general",
            agent=classification.target_agents[0] if classification.target_agents else "general_agent"
        )
        
        sub_responses = []
        
        # 3. Delegation to Specialized Agents
        for agent_name in classification.target_agents:
            target_agent = AgentRegistry.get_agent(agent_name)
            if not target_agent:
                logger.error(f"[PlannerAgent] Unknown agent '{agent_name}'.")
                continue
                
            logger.info(f"[PlannerAgent] Delegating to {target_agent.name}")
            try:
                response = target_agent.process(request, context)
                sub_responses.append(response)
            except Exception as e:
                logger.error(f"[PlannerAgent] Agent {agent_name} failed: {e}")
                sub_responses.append(AgentResponse(
                    agent_name=agent_name,
                    content=f"Sorry, {agent_name} encountered an error.",
                    confidence=0.0
                ))
                
        # 4. Merge Responses
        if len(sub_responses) == 1:
            content = sub_responses[0].content
            data = sub_responses[0].data
            used_tools = sub_responses[0].used_tools
            cache_status = getattr(sub_responses[0], "cache_status", "Miss")
        else:
            content = "Here is what I found for your requests:"
            data = {}
            used_tools = []
            cache_status = "Miss"
            for sr in sub_responses:
                used_tools.extend(sr.used_tools)
                if getattr(sr, "cache_status", "Miss") == "Hit":
                    cache_status = "Partial Hit"
            
        execution_time_ms = (time.time() - start_time) * 1000
            
        return AgentResponse(
            agent_name=self.name,
            content=content,
            data=data,
            sub_responses=sub_responses,
            detected_intents=classification.intents,
            decision_method=decision_method,
            gemini_calls=get_gemini_calls(),
            cache_status=cache_status,
            used_tools=used_tools,
            total_execution_time_ms=round(execution_time_ms, 2)
        )
