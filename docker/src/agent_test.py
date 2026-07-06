import os
import argparse
import subprocess

from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai import Agent

def bash(command: str) -> str:
    result = subprocess.run(command, shell=True, capture_output=True, text=True, env={})
    return result.stdout if result.returncode == 0 else result.stderr

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--user-prompt",
        required=True,
        help="Prompt to send to the agent",
    )
    args = parser.parse_args()

    model = OpenAIChatModel(
        "openai/gpt-4o-mini",
        provider=OpenAIProvider(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.environ["OPENROUTER_API_KEY"],
        ),
    )

    plain_agent = Agent(model, tools=[bash])

    result = plain_agent.run_sync(args.user_prompt)
    print(result.output)

if __name__ == "__main__":
    main()