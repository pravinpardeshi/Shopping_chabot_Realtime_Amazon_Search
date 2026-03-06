"""
Central Shopping Agent — focuses on autonomous reasoning and tool orchestration.
"""
import ollama
import json
import logging
from tools import TOOL_SCHEMAS, execute_tool
from config import config

logger = logging.getLogger(__name__)

class ShoppingAgent:
    def __init__(self, model: str = None):
        self.model = model or config.OLLAMA_MODEL
        self.max_iterations = config.MAX_AGENT_ITERATIONS

    def chat(self, user_message: str, history: list[dict]) -> dict:
        """
        Executes the reasoning loop for a single user interaction.
        """
        messages = [{"role": "system", "content": config.AGENT_SYSTEM_PROMPT}]
        messages.extend(history)
        
        # Track start of current turn for new_messages extraction
        turn_start_idx = len(messages)
        messages.append({"role": "user", "content": user_message})

        thinking_steps = []
        state = {
            "offer_details": None,
            "search_results": [],
            "trigger_checkout": False,
        }

        for iteration in range(self.max_iterations):
            logger.info(f"Agent turn {iteration + 1}")
            try:
                response = ollama.chat(
                    model=self.model,
                    messages=messages,
                    tools=TOOL_SCHEMAS,
                )
            except Exception as e:
                logger.error(f"Ollama error: {e}")
                return self._error_response("I encountered a thinking error. Please try again.")

            msg = response["message"]

            if not msg.get("tool_calls"):
                final_reply = msg.get("content", "I'm not sure how to help.")
                messages.append({"role": "assistant", "content": final_reply})
                break

            # Handle tool calls
            messages.append(msg) # role: assistant with tool_calls
            
            for tool_call in msg["tool_calls"]:
                name = tool_call["function"]["name"]
                args = tool_call["function"]["arguments"]
                
                thinking_steps.append(f"🔍 Executing **{name}**...")
                result = execute_tool(name, args)
                
                # Update agent state based on tool results
                self._update_state(state, name, result)

                messages.append({
                    "role": "tool",
                    "content": json.dumps(result),
                })

        return {
            "reply": messages[-1]["content"],
            "thinking_steps": thinking_steps,
            "new_messages": messages[turn_start_idx:],
            **state
        }

    def _update_state(self, state, name, result):
        if name == "search_products" and result.get("found"):
            state["search_results"] = result.get("products", [])
        elif name == "get_best_offer" and result.get("found"):
            state["offer_details"] = result.get("best_offer")
        elif name == "initiate_checkout" and result.get("success"):
            # Include offer details from initiate_checkout if available
            if result.get("offer_details"):
                state["offer_details"] = result.get("offer_details")
            state["trigger_checkout"] = True

    def _error_response(self, message: str) -> dict:
        return {
            "reply": message,
            "thinking_steps": [],
            "new_messages": [],
            "offer_details": None,
            "search_results": [],
            "trigger_checkout": False,
        }

# Global singleton for easy use in main.py
agent = ShoppingAgent()
