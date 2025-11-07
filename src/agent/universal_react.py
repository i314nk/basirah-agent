"""
Universal ReAct Loop Implementation

Provides tool calling capability for ANY LLM (Claude, OpenAI, Gemini, etc.)
using JSON-based function calling instead of native tool APIs.

This enables future LLM providers to perform full Deep Dive analyses
with multi-year research, tool use, and autonomous investigation.
"""

import json
import re
import logging
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)


class UniversalReActLoop:
    """
    Universal ReAct (Reasoning + Acting) loop for any LLM.

    Uses JSON-based tool calling that works with:
    - Claude (Anthropic)
    - OpenAI models (future)
    - Google Gemini (future)
    - Any model that can generate JSON
    """

    def __init__(self, llm_client, tools: Dict[str, Any], max_iterations: int = 30):
        """
        Initialize universal ReAct loop.

        Args:
            llm_client: LLMClient instance from Phase 7
            tools: Dict of tool name -> tool object
            max_iterations: Maximum ReAct iterations
        """
        self.llm = llm_client
        self.tools = tools
        self.max_iterations = max_iterations

        # Tool descriptions for prompt
        self.tool_descriptions = self._build_tool_descriptions()

    def _build_tool_descriptions(self) -> str:
        """Build tool descriptions in JSON schema format."""
        descriptions = []

        for tool_name, tool in self.tools.items():
            # Get tool info
            if hasattr(tool, 'get_info'):
                info = tool.get_info()
            else:
                info = {
                    "name": tool_name,
                    "description": f"Tool: {tool_name}",
                    "parameters": {}
                }

            schema = {
                "name": tool_name,
                "description": info.get("description", f"Tool: {tool_name}"),
                "parameters": info.get("parameters", {})
            }
            descriptions.append(json.dumps(schema, indent=2))

        return "\n\n".join(descriptions)

    def _build_system_prompt(self, task_prompt: str) -> str:
        """Build system prompt with tool calling instructions."""
        return f"""{task_prompt}

## TOOL USAGE

You have access to these tools:

{self.tool_descriptions}

To use a tool, output EXACTLY this format:

```json
{{
  "thought": "Why I need to use this tool",
  "tool": "tool_name",
  "parameters": {{
    "param1": "value1",
    "param2": "value2"
  }}
}}
```

After receiving tool results, continue your analysis or use more tools as needed.

When you have enough information to complete your analysis, output your final answer WITHOUT any tool call JSON.

IMPORTANT:
- Use tools to gather information before making conclusions
- Always explain your reasoning in "thought"
- Output ONLY the JSON block when calling a tool, nothing else
- Output ONLY your final analysis when done, no JSON
"""

    def _parse_tool_call(self, response: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        """
        Parse tool call from LLM response.

        Returns:
            Tuple of (tool_name, parameters) or None if no tool call found
        """
        # Look for JSON code block
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
        if not json_match:
            # Try without code block
            json_match = re.search(r'(\{[^{}]*"tool"[^{}]*\})', response, re.DOTALL)

        if not json_match:
            return None

        try:
            tool_call = json.loads(json_match.group(1))

            if "tool" not in tool_call:
                return None

            tool_name = tool_call["tool"]
            parameters = tool_call.get("parameters", {})
            thought = tool_call.get("thought", "")

            logger.info(f"[Tool Call] {tool_name}")
            logger.info(f"[Thought] {thought}")

            return (tool_name, parameters)

        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse tool call JSON: {e}")
            return None

    def _execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> str:
        """Execute a tool and return formatted results."""
        if tool_name not in self.tools:
            return f"ERROR: Tool '{tool_name}' not found. Available tools: {list(self.tools.keys())}"

        try:
            tool = self.tools[tool_name]
            result = tool.execute(**parameters)

            # Format result
            if isinstance(result, dict):
                if result.get("success"):
                    return f"SUCCESS:\n{json.dumps(result.get('data', result), indent=2)}"
                else:
                    return f"ERROR: {result.get('error', 'Unknown error')}"
            else:
                return f"RESULT:\n{result}"

        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            return f"ERROR: Tool execution failed: {str(e)}"

    def run(self, initial_prompt: str, system_prompt: str) -> Dict[str, Any]:
        """
        Run ReAct loop with universal tool calling.

        Args:
            initial_prompt: User's initial request
            system_prompt: System prompt defining agent personality/task

        Returns:
            Dict with analysis results and metadata
        """
        logger.info("Starting Universal ReAct loop")
        logger.info(f"Max iterations: {self.max_iterations}")

        # Build enhanced system prompt with tool instructions
        full_system_prompt = self._build_system_prompt(system_prompt)

        # Initialize conversation
        messages = [
            {"role": "system", "content": full_system_prompt},
            {"role": "user", "content": initial_prompt}
        ]

        iteration = 0
        tool_calls_made = 0

        while iteration < self.max_iterations:
            iteration += 1
            logger.info(f"\n--- Iteration {iteration}/{self.max_iterations} ---")

            try:
                # Generate response from LLM
                response = self.llm.generate(
                    messages=messages,
                    max_tokens=4000,
                    temperature=1.0
                )

                content = response.content
                logger.info(f"[LLM Response] {len(content)} characters")

                # Check for tool call
                tool_call = self._parse_tool_call(content)

                if tool_call is None:
                    # No tool call - agent is done
                    logger.info("[Agent] No tool call detected - analysis complete")

                    return {
                        "success": True,
                        "content": content,
                        "metadata": {
                            "iterations": iteration,
                            "tool_calls": tool_calls_made,
                            "model": response.model,
                            "provider": response.provider,
                            "tokens_input": response.tokens_input,
                            "tokens_output": response.tokens_output,
                            "cost": response.cost
                        }
                    }

                # Execute tool
                tool_name, parameters = tool_call
                tool_calls_made += 1

                logger.info(f"[Executing] {tool_name} with {len(parameters)} parameters")
                tool_result = self._execute_tool(tool_name, parameters)
                logger.info(f"[Tool Result] {len(tool_result)} characters")

                # Add to conversation
                messages.append({"role": "assistant", "content": content})
                messages.append({
                    "role": "user",
                    "content": f"Tool Result:\n{tool_result}\n\nContinue your analysis or use more tools if needed."
                })

            except Exception as e:
                logger.error(f"Error in ReAct loop: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "content": None,
                    "metadata": {
                        "iterations": iteration,
                        "tool_calls": tool_calls_made
                    }
                }

        # Max iterations reached
        logger.warning(f"Reached max iterations ({self.max_iterations})")
        return {
            "success": False,
            "error": "Max iterations reached",
            "content": "Analysis incomplete - reached maximum iteration limit",
            "metadata": {
                "iterations": iteration,
                "tool_calls": tool_calls_made
            }
        }


__all__ = ["UniversalReActLoop"]
