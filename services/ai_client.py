"""Reusable Ollama client for project management summaries."""

import json
import ollama


class ProjectAIClient:
  """Generate project summaries using a local Ollama model."""

  def __init__(self, model_name="llama3.2:3b"):
    self.model_name = model_name

  def summarize_project(self, project_data):
    """Generate a summary, risks, and next-step recommendations."""
    if not isinstance(project_data, dict) or not project_data:
      raise ValueError("Project data is required.")

    structured_data = json.dumps(
      project_data,
      indent=2
    )

    prompt = f"""
You are a project management assistant.

Analyze the project information below.

Provide a clear, concise response with these sections:

1. Project Summary
2. Current Progress
3. Risk Notes
4. Recommended Next Steps

Use only the provided project information.
Do not invent project details.
Clearly identify unknown information.

Project Information:
{structured_data}
""".strip()

    try:
      response = ollama.chat(
        model=self.model_name,
        messages=[
          {
            "role": "user",
            "content": prompt
          }
        ]
      )

      if isinstance(response, dict):
        message = response.get("message")
      else:
        message = getattr(response, "message", None)

      if isinstance(message, dict):
        content = message.get("content")
      else:
        content = getattr(message, "content", None)

      if not isinstance(content, str) or not content.strip():
        raise ValueError("AI returned an empty response.")

      return content.strip()

    except Exception as error:
      raise RuntimeError(
        f"AI service request failed: {error}"
      ) from error