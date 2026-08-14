"""
story_llm.py
------------
Turns the currently selected log pool into a short narrative via an
LLM call through OpenRouter.

SECURITY NOTE: do not have a live OpenRouter API key
hardcoded in source. Read from the OPENROUTER_API_KEY
environment variable instead -- set it before running, e.g. (PowerShell):

    $env:OPENROUTER_API_KEY = "sk-or-v1-..."
    python main_demo.py

If you already committed/shared the old hardcoded key anywhere, treat
it as compromised and rotate it in your OpenRouter dashboard.
"""

import os

import requests

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
#OPENROUTER_MODEL = "nvidia/nemotron-3-ultra-550b-a55b:free"
OPENROUTER_MODEL = "nvidia/nemotron-3-nano-30b-a3b:free"
REQUEST_TIMEOUT_SECONDS = 120


SYSTEM_PROMPT = """### Context ###
You are a narrative chronicler that transforms raw game logs from a sci-fi colony simulator into an immersive short story.

You will be given logs from a sci-fi game world.

The logs are ordered in a temporal sequence and follow this format:

Event description. [xCount] [V/NV]

[V/NV] are visibility tags:
- [V]: Event was visible to the player.
- [NV]: Event was not visible to the player.

[xCount] indicates how many times a similar event occurred.

Information regarding the player's colonists is provided in the following format:
Name: First Name "Nickname" Last Name -> full name of the colonist.
Gender: Male/Female -> gender of the colonist.
Age: 0-99 -> age of the colonist
Backstory: Backstory 1; Backstory 2; (...) -> backstories from the colonist's past as a child/teen/young adult.
Incapable of: Type of Work 1; Type of Work 2; (...) -> types of work that the colonist is incapable of doing.
Traits: Trait 1; Trait 2; (...) -> the colonist's personality traits.
Relations: Relation 1; Relation 2; (...) -> active relationships with other colonists/characters/animals.

### Instructions ###
Your primary goal is to write a compelling narrative summary of the provided logs in less than 200 words.

Guidelines:
- Highlight low-count events (e.g., [x1]).
- High-count events should be condensed into background context unless considered important.
- For events tagged [NV], you may be more creative, describing unseen causes or off-screen consequences, as long as they remain consistent with the logs.
- Avoid breaking the fourth wall: avoid mentioning logs, tags, visibility or counts explicitly.
- Only include colonist details when they meaningfully contribute to the narrative.
- Avoid listing events; weave them into a continuous story with cause and effect.

Tone:
- Cinematic and grounded, as if recounting a chapter from a colony's history rather than a gameplay summary."""


def _get_api_key():

    api_key = os.environ.get("OPENROUTER_API_KEY")

    if not api_key:
        raise RuntimeError(
            "OPENROUTER_API_KEY is not set. Set it as an environment variable "
            "before running the app (see story_llm.py for details)."
        )
    return api_key


def generate_story_llm(characters_bios, selected_descriptions):
    """
    Call the LLM with the current character bios + selected log
    descriptions and return the generated story text.

    Parameters
    ----------
    characters_bios : str
        Raw character bios text.
    selected_descriptions : list[str]
        Labels of the logs currently selected in the "Final Log Pool".
    """
    log_descriptions = "\n\n".join(selected_descriptions)

    prompt = f"""### Player's Colonists ###
{characters_bios}

### Input Logs ###
{log_descriptions}
"""

    response = requests.post(
        OPENROUTER_URL,
        headers={
            "Authorization": f"Bearer {_get_api_key()}",
            "Content-Type": "application/json",
        },
        json={
            "model": OPENROUTER_MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        },
        timeout=REQUEST_TIMEOUT_SECONDS,
    )

    response.raise_for_status()
    data = response.json()

    if "choices" not in data:
        raise RuntimeError(f"OpenRouter error: {data}")

    return data["choices"][0]["message"]["content"]
