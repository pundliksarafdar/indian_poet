"""Multilingual poem agents using a Sarvam-compatible chat completion.

This script orchestrates two poet agents (Marathi and Kannada) that alternate
adding stanzas to a poem, and a translator agent that translates the final
poem into Hindi. It targets the `sarvam-m` model via a chat-completion HTTP API.

Configuration via environment variables:
- SARVAM_API_URL: Chat completion endpoint (required)
- SARVAM_API_KEY: Authorization key (required)

The script is intentionally simple and framework-agnostic so you can adapt it
to your LangGraph setup (if you have a specific SDK you want integrated,
I can update this to use it).
"""

import os
import json
import time
from typing import List, Dict
import argparse

import requests
from dotenv import load_dotenv

# Load .env from the project directory (same folder as this script)
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=env_path)


class ChatClient:
    def __init__(self, api_url: str, api_key: str, timeout: int = 30):
        self.api_url = api_url
        self.api_key = api_key
        self.timeout = timeout

    def chat_completion(self, messages: List[Dict[str, str]], model: str = "sarvam-m") -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {"model": model, "messages": messages}
        resp = requests.post(self.api_url, headers=headers, json=payload, timeout=self.timeout)
        resp.raise_for_status()
        data = resp.json()
        # Expecting OpenAI-style response: choices[0].message.content
        try:
            return data["choices"][0]["message"]["content"].strip()
        except Exception:
            # Fallback: try top-level text
            return data.get("text") or json.dumps(data, ensure_ascii=False)


class Agent:
    def __init__(self, name: str, language: str, system_prompt: str, client: ChatClient):
        self.name = name
        self.language = language
        self.system_prompt = system_prompt
        self.client = client

    def produce(self, context: str) -> str:
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": context},
        ]
        return self.client.chat_completion(messages, model="sarvam-m")


def orchestrate_poem(topic: str = "Nature", turns: int = 6, out_path: str = "outputs/poem_multilingual.txt") -> Dict[str, str]:
    # Support either a full chat endpoint URL or a base URL.
    # Prefer `SARVAM_API_URL`, fall back to `SARVAM_API_BASE_URL` and append the chat path.
    api_url = os.getenv("SARVAM_API_URL") or os.getenv("SARVAM_API_BASE_URL")
    api_key = os.getenv("SARVAM_API_KEY")
    if not api_url or not api_key:
        raise RuntimeError("Set SARVAM_API_URL (or SARVAM_API_BASE_URL) and SARVAM_API_KEY environment variables.")

    # If a base URL was provided (not including chat path), append the expected chat completions path.
    if api_url and not api_url.endswith("/chat/completions"):
        api_url = api_url.rstrip("/") + "/chat/completions"

    client = ChatClient(api_url, api_key)

    marathi = Agent(
        name="agent_marathi",
        language="Marathi",
        system_prompt=(
            "You are a Marathi poet. Write a short stanza (1-2 lines) continuing the poem. "
            "Keep it poetic and in Marathi. Do NOT translate other languages."
        ),
        client=client,
    )

    kannada = Agent(
        name="agent_kannada",
        language="Kannada",
        system_prompt=(
            "You are a Kannada poet. Write a short stanza (1-2 lines) continuing the poem. "
            "Keep it poetic and in Kannada. Do NOT translate other languages."
        ),
        client=client,
    )

    translator = Agent(
        name="agent_translator",
        language="Hindi",
        system_prompt=(
            "You are a translator. Translate the provided entire poem into Hindi. "
            "Preserve poetic sense and line breaks. Do not add extra commentary."
        ),
        client=client,
    )

    agents = [marathi, kannada]
    poem_lines: List[str] = []

    # Prepare output file and write header
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("--- Poem (with language tags) ---\n")

    for i in range(turns):
        active = agents[i % 2]
        current_poem = "\n".join(poem_lines) if poem_lines else ""
        # Provide the topic and current poem context to the agent.
        context = (
            "Topic: " + topic + "\n\n"
            "Continue the poem below. Only output the stanza you are adding in your language.\n\n"
            f"Current poem so far:\n{current_poem}"
        )
        try:
            stanza = active.produce(context)
        except Exception as e:
            stanza = f"[{active.name} error: {e}]"
        # Add a language tag so we know who wrote what
        line = f"[{active.language}] {stanza}"
        poem_lines.append(line)
        # Print each agent's stanza to console
        print("\n" + f"{active.name} ({active.language}) produced:")
        print(stanza)
        # Append stanza to output file incrementally
        with open(out_path, "a", encoding="utf-8") as f:
            f.write(line + "\n")
        # small pause to avoid rate limits
        time.sleep(0.1)

    full_poem = "\n".join(poem_lines)

    # Translator step
    try:
        translation = translator.produce(
            f"Translate the following poem into Hindi (keep line breaks). Topic: {topic}\n\n{full_poem}"
        )
    except Exception as e:
        translation = f"[translator error: {e}]"

    # Print and append translation
    print("\nTranslator (Hindi) produced:")
    print(translation)
    with open(out_path, "a", encoding="utf-8") as f:
        f.write("\n--- Hindi Translation ---\n")
        f.write(translation + "\n")

    return {"poem": full_poem, "hindi_translation": translation}


def save_outputs(outputs: Dict[str, str], out_path: str = "outputs/poem_multilingual.txt") -> None:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("--- Poem (with language tags) ---\n")
        f.write(outputs["poem"] + "\n\n")
        f.write("--- Hindi Translation ---\n")
        f.write(outputs["hindi_translation"] + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Multilingual poem agents (Marathi/Kannada + Hindi translator)")
    parser.add_argument("--topic", "-t", help="Poem topic", default=None)
    parser.add_argument("--turns", "-n", "--lines", "-l", type=int, help="Number of alternating stanzas (total turns)", default=None)
    args = parser.parse_args()

    # If no CLI input provided, accept interactive input from the user.
    if args.topic is None:
        try:
            user_topic = input("Enter poem topic (default: Nature): ").strip()
            args.topic = user_topic if user_topic else "Nature"
        except Exception:
            args.topic = "Nature"

    if args.turns is None:
        try:
            user_lines = input("Enter number of lines/turns (default: 6): ").strip()
            args.turns = int(user_lines) if user_lines else 6
        except Exception:
            args.turns = 6

    print(f"Orchestrating multilingual poem on topic: '{args.topic}' ({args.turns} turns)...")
    result = orchestrate_poem(topic=args.topic, turns=args.turns)
    save_outputs(result)
    print("Done. Output saved to outputs/poem_multilingual.txt")
