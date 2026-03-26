"""Intent router module: uses LLM to route natural language queries to API tools.

This module implements the tool-calling loop that:
1. Sends user messages to the LLM with available tool definitions
2. Executes tools when the LLM requests them
3. Feeds results back to the LLM for final response generation
"""

import sys
from typing import Any

from config import configuration
from services.api_client import LMSAPIClient
from services.llm_client import LLMClient


# System prompt for the LLM
SYSTEM_PROMPT = """You are an assistant for a Learning Management System (LMS). You have access to tools that fetch data about labs, learners, and scores.

Your job is to:
1. Understand the user's question
2. Decide which tool(s) to call to get the data needed
3. After receiving tool results, analyze the data and provide a helpful answer

Tool calling rules:
- Always call tools when you need data - don't guess or make up numbers
- If the user asks about multiple labs, call the tool for each lab
- If the user asks a vague question, ask for clarification
- For greetings or simple messages, respond directly without tools

When you have tool results:
- Analyze the actual data returned
- Provide specific numbers and comparisons when relevant
- If data is missing or empty, tell the user honestly

Be helpful, accurate, and data-driven in your responses."""


async def dispatch_intent(user_message: str, debug: bool = False) -> str:
    """
    Route a user message through the LLM to generate a response.

    This implements the tool-calling loop:
    1. Send message + tools to LLM
    2. If LLM calls tools, execute them
    3. Feed results back to LLM
    4. Return final response

    Args:
        user_message: The user's natural language message
        debug: If True, print debug info to stderr

    Returns:
        The LLM's final response text
    """

    def debug_log(msg: str) -> None:
        if debug:
            print(msg, file=sys.stderr)

    # Initialize clients
    api_client = LMSAPIClient(
        base_url=configuration.lms_api_base_url,
        api_key=configuration.lms_api_key,
    )
    llm_client = LLMClient(
        base_url=configuration.llm_api_base_url,
        api_key=configuration.llm_api_key,
        model=configuration.llm_api_model,
    )

    try:
        # Build conversation history
        messages: list[dict] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ]

        # Get tool definitions
        tools = llm_client._build_tool_definitions()

        # Tool calling loop (max iterations to prevent infinite loops)
        max_iterations = 5
        iteration = 0

        while iteration < max_iterations:
            iteration += 1
            debug_log(f"[iteration {iteration}] Sending message to LLM...")

            # Call LLM
            result = await llm_client.chat(messages, tools=tools)

            if not result["ok"]:
                return f"LLM error: {result['error']}"

            # Check for tool calls
            tool_calls = result.get("tool_calls")
            llm_response = result.get("response")

            if tool_calls:
                debug_log(f"[tool] LLM called {len(tool_calls)} tool(s)")

                # Execute each tool call
                tool_results = []
                for tool_call in tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call.get("arguments", {})

                    debug_log(f"[tool] Calling {tool_name}({tool_args})")

                    # Execute the tool
                    try:
                        api_result = await _execute_tool(api_client, tool_name, tool_args)
                        debug_log(f"[tool] Result: {str(api_result)[:100]}...")

                        # Add tool result to conversation
                        tool_results.append({
                            "role": "tool",
                            "name": tool_name,
                            "content": str(api_result),
                        })
                    except Exception as e:
                        debug_log(f"[tool] Error: {e}")
                        tool_results.append({
                            "role": "tool",
                            "name": tool_name,
                            "content": f"Error: {e}",
                        })

                # Add assistant's tool call to messages
                messages.append({
                    "role": "assistant",
                    "tool_calls": [
                        {
                            "id": f"call_{i}",
                            "type": "function",
                            "function": {
                                "name": tc["name"],
                                "arguments": str(tc.get("arguments", {})),
                            },
                        }
                        for i, tc in enumerate(tool_calls)
                    ],
                })

                # Add tool results to messages
                messages.extend(tool_results)

                debug_log(f"[summary] Feeding {len(tool_results)} tool result(s) back to LLM")

                # Continue loop - LLM will process results and respond
                continue

            elif llm_response:
                # LLM provided a final response
                debug_log(f"[response] LLM responded with text")
                return llm_response

            else:
                # No tool calls and no response - something went wrong
                debug_log("[error] LLM returned neither tool calls nor response")
                return "I'm having trouble processing that. Could you rephrase?"

        # Max iterations reached
        debug_log(f"[error] Max iterations ({max_iterations}) reached")
        return "I'm still working on that. Let me summarize: I called several tools but haven't finished processing. Could you try a simpler question?"

    finally:
        await api_client.close()
        await llm_client.close()


async def _execute_tool(
    api_client: LMSAPIClient,
    tool_name: str,
    arguments: dict[str, Any],
) -> Any:
    """
    Execute a tool by calling the appropriate API method.

    Args:
        api_client: The LMS API client instance
        tool_name: Name of the tool to invoke
        arguments: Tool arguments from the LLM

    Returns:
        The API result dict (without 'ok' and 'error' keys for cleaner output)
    """
    tool_methods = {
        "get_items": lambda: api_client.get_items(),
        "get_learners": lambda: api_client.get_learners(),
        "get_pass_rates": lambda: api_client.get_pass_rates(arguments.get("lab", "")),
        "get_timeline": lambda: api_client.get_timeline(arguments.get("lab", "")),
        "get_groups": lambda: api_client.get_groups(arguments.get("lab", "")),
        "get_top_learners": lambda: api_client.get_top_learners(
            arguments.get("lab", ""),
            arguments.get("limit", 10),
        ),
        "get_completion_rate": lambda: api_client.get_completion_rate(arguments.get("lab", "")),
        "trigger_sync": lambda: api_client.trigger_sync(),
    }

    if tool_name not in tool_methods:
        return {"error": f"Unknown tool: {tool_name}"}

    result = await tool_methods[tool_name]()

    # Return just the data portion for cleaner LLM consumption
    if result.get("ok"):
        # Return the main data key
        data_keys = ["items", "learners", "labs", "pass_rates", "timeline",
                     "groups", "top_learners", "completion_rate", "status", "scores"]
        for key in data_keys:
            if key in result:
                return result[key]
        return result
    else:
        return {"error": result.get("error", "Unknown error")}
