import json
from typing import Any

from sqlalchemy.orm import Session

from app.services.llm.client import (
    client,
    NVIDIA_MODEL,
)

from app.services.llm.agent_tools import (
    inspect_recovery_case,
    execute_bounded_recovery,
)

from app.services.llm.message_safety import (
    make_safe_customer_message,
)


SYSTEM_PROMPT = """
You are the RecoveryOS Revenue Recovery Agent.

Your job is to reason about revenue recovery cases
and use the available RecoveryOS tools when appropriate.

You are an agent operating inside a financial recovery
system.

IMPORTANT SAFETY RULES:

1. You may inspect recovery cases.
2. You may request a recovery action only when the
   deterministic RecoveryOS policy permits it.
3. Never invent payment facts.
4. Never invent customer information.
5. Never invent recovery outcomes.
6. Never bypass the deterministic recovery policy.
7. Never directly execute payments.
8. Never request an action that is not supported
   by the available tools.
9. If RecoveryOS blocks an action, accept the decision.
10. If a case is already recovered, do not attempt
    another recovery.
11. Respect maximum recovery attempts.
12. The ML prediction is advisory only.
13. The deterministic policy is authoritative.
14. Do not repeatedly call the same tool without
    a reason.
15. Stop once the case has been successfully handled.

Your workflow should normally be:

1. Inspect the recovery case.
2. Understand the payment failure.
3. Review the ML prediction.
4. Review the deterministic recovery policy.
5. If policy permits recovery, request the approved
   recovery action.
6. If policy blocks recovery, do not attempt execution.
7. Report the final result clearly.

When reporting the final result:

- Keep the explanation factual.
- Do not expose unnecessary internal system details
  to the customer.
- If a customer-facing message is included, keep it
  concise and professional.
- Do not request passwords, OTPs, PINs, CVVs or other
  sensitive authentication information.

The system, not you, controls whether a financial
action is actually executed.
"""


# ============================================================
# TOOL DEFINITIONS
# ============================================================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "inspect_recovery_case",
            "description": (
                "Inspect the authoritative RecoveryOS "
                "state for a recovery case, including "
                "payment information, recovery status, "
                "latest action, ML prediction and "
                "deterministic recovery policy."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "recovery_case_id": {
                        "type": "integer",
                        "description": (
                            "RecoveryOS recovery case ID."
                        ),
                    },
                },
                "required": [
                    "recovery_case_id"
                ],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "execute_bounded_recovery",
            "description": (
                "Request execution of an approved "
                "RecoveryOS recovery action. The action "
                "is always validated by the deterministic "
                "policy before execution."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "recovery_case_id": {
                        "type": "integer",
                        "description": (
                            "RecoveryOS recovery case ID."
                        ),
                    },
                    "action": {
                        "type": "string",
                        "enum": [
                            "alternate_payment_method"
                        ],
                        "description": (
                            "Approved recovery action."
                        ),
                    },
                },
                "required": [
                    "recovery_case_id",
                    "action",
                ],
            },
        },
    },
]


# ============================================================
# TOOL EXECUTION
# ============================================================


def _execute_tool(
    db: Session,
    name: str,
    arguments: dict[str, Any],
) -> dict:

    if name == "inspect_recovery_case":

        return inspect_recovery_case(
            db=db,
            recovery_case_id=arguments[
                "recovery_case_id"
            ],
        )

    if name == "execute_bounded_recovery":

        return execute_bounded_recovery(
            db=db,
            recovery_case_id=arguments[
                "recovery_case_id"
            ],
            action=arguments["action"],
        )

    return {
        "error": (
            f"Unknown RecoveryOS tool: {name}"
        )
    }


# ============================================================
# AGENT
# ============================================================


def run_recovery_agent(
    db: Session,
    recovery_case_id: int,
    max_iterations: int = 5,
) -> dict:

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": (
                "Handle RecoveryOS recovery case "
                f"{recovery_case_id}.\n\n"
                "Inspect the case first. "
                "Use the available tools when necessary. "
                "Follow all deterministic policy constraints."
            ),
        },
    ]

    tool_calls_made = []

    for _ in range(max_iterations):

        response = client.chat.completions.create(
            model=NVIDIA_MODEL,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            temperature=1.0,
            top_p=0.95,
            max_tokens=2048,
            extra_body={
                "chat_template_kwargs": {
                    "enable_thinking": False,
                },
            },
        )

        message = response.choices[0].message

        # ----------------------------------------------------
        # MODEL FINISHED
        # ----------------------------------------------------

        if not message.tool_calls:

            original_message = (
                message.content or ""
            )

            # ------------------------------------------------
            # CONTENT SAFETY GATE
            # ------------------------------------------------

            safety_result = (
                make_safe_customer_message(
                    original_message
                )
            )

            return {
                "status": "completed",

                # Safe message that can be exposed
                # to the customer.
                "message": safety_result[
                    "message"
                ],
                "agent_assessment": (
                    original_message
                    if safety_result["safe"]
                    else safety_result["message"]
                ),

                # Keep the safety decision visible
                # to the application layer.
                "content_safety": {
                    "safe": safety_result[
                        "safe"
                    ],
                    "reason": safety_result[
                        "reason"
                    ],
                    "fallback_used": (
                        safety_result[
                            "fallback_used"
                        ]
                    ),
                },

                # Preserve the model output for
                # internal inspection/auditing.
                "original_message": (
                    original_message
                ),

                "tool_calls": tool_calls_made,
            }

        # ----------------------------------------------------
        # PRESERVE ASSISTANT TOOL-CALL MESSAGE
        # ----------------------------------------------------

        assistant_message = {
            "role": "assistant",
            "content": message.content or "",
            "tool_calls": [],
        }

        for tool_call in message.tool_calls:

            assistant_message[
                "tool_calls"
            ].append(
                {
                    "id": tool_call.id,
                    "type": "function",
                    "function": {
                        "name": tool_call.function.name,
                        "arguments": (
                            tool_call.function.arguments
                        ),
                    },
                }
            )

        messages.append(
            assistant_message
        )

        # ----------------------------------------------------
        # EXECUTE REQUESTED TOOLS
        # ----------------------------------------------------

        for tool_call in message.tool_calls:

            tool_name = (
                tool_call.function.name
            )

            try:

                arguments = json.loads(
                    tool_call.function.arguments
                )

            except json.JSONDecodeError:

                tool_result = {
                    "error": (
                        "Invalid JSON arguments "
                        "returned by the model."
                    )
                }

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(
                            tool_result
                        ),
                    }
                )

                continue

            # ------------------------------------------------
            # HARD TOOL ALLOWLIST
            # ------------------------------------------------

            allowed_tools = {
                "inspect_recovery_case",
                "execute_bounded_recovery",
            }

            if tool_name not in allowed_tools:

                tool_result = {
                    "error": (
                        "Tool is not permitted."
                    )
                }

            else:

                tool_result = _execute_tool(
                    db=db,
                    name=tool_name,
                    arguments=arguments,
                )

            tool_calls_made.append(
                {
                    "tool": tool_name,
                    "arguments": arguments,
                    "result": tool_result,
                }
            )

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(
                        tool_result,
                        default=str,
                    ),
                }
            )

    return {
        "status": "max_iterations_reached",
        "message": (
            "Recovery agent stopped after reaching "
            "the maximum number of iterations."
        ),
        "agent_assessment": (
            "Recovery agent stopped after reaching "
            "the maximum number of iterations."
        ),
        "tool_calls": tool_calls_made,
    }