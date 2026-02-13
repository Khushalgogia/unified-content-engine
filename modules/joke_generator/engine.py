"""
V11 Logic Engine - Core Engine
Refactored for Unified Content Engine — uses relative imports.
"""

from typing import Dict, Optional
from .gemini_client import classify_joke_type, call_gemini


def generate_v11_joke(reference_joke: str, new_topic: str) -> Dict:
    """
    V11 Enhanced Pipeline: Analyze → Brainstorm → Select → Draft
    """
    try:
        result = classify_joke_type(reference_joke, new_topic)

        required_keys = ["engine_selected", "reasoning", "brainstorming", "selected_strategy", "draft_joke"]

        if isinstance(result, dict):
            if "error" in result:
                return {
                    "success": False,
                    "error": result.get("error"),
                    "raw": result.get("raw", "")
                }

            missing = [k for k in required_keys if k not in result]
            if missing:
                for key in missing:
                    if key == "brainstorming":
                        result[key] = ["N/A"]
                    elif key == "selected_strategy":
                        result[key] = "N/A"
                    else:
                        return {
                            "success": False,
                            "error": f"Missing keys in response: {missing}",
                            "partial_result": result
                        }

            result["success"] = True
            return result
        else:
            return {
                "success": False,
                "error": "Unexpected response type",
                "raw": str(result)
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def regenerate_joke(
    reference_joke: str,
    new_topic: str,
    engine_type: str,
    previous_draft: str
) -> Dict:
    """
    Regenerate a joke with the same engine type but different approach.
    """
    system_instruction = f"""You are a Comedy Writer. You have already classified this joke as {engine_type}.

Now generate a DIFFERENT version. Brainstorm 3 NEW angles (different from before).

PREVIOUS DRAFT (DO NOT REPEAT):
"{previous_draft}"

Generate a fresh take using the same {engine_type} logic engine."""

    prompt = f"""REFERENCE JOKE:
"{reference_joke}"

NEW TOPIC:
"{new_topic}"

FORCED ENGINE TYPE: {engine_type}

Create 3 NEW mapping options and select a different one from before.

OUTPUT JSON:
{{
  "engine_selected": "{engine_type}",
  "brainstorming": [
    "New Option 1: [Trait/Angle] -> [Scenario]",
    "New Option 2: [Trait/Angle] -> [Scenario]",
    "New Option 3: [Trait/Angle] -> [Scenario]"
  ],
  "selected_strategy": "The new selected approach",
  "draft_joke": "The new joke (max 40 words, different from previous)"
}}"""

    try:
        result = call_gemini(
            prompt=prompt,
            system_instruction=system_instruction,
            model_stage="generation",
            temperature=0.7,
            json_output=True
        )

        if isinstance(result, dict) and "draft_joke" in result:
            result["success"] = True
            return result
        else:
            return {
                "success": False,
                "error": "Failed to regenerate",
                "result": result
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
