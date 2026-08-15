"""
story_llm.py
------------
Turns an already-selected log pool into text via an LLM call through
OpenRouter, in one of two modes:
  - "narrative": a short prose chronicle (the original/default mode).
  - "dialogue": dialogue-only output (PLACEHOLDER PROMPT -- see
    PROMPTS["dialogue"] below; drop in the real prompt before using
    this mode).

SECURITY NOTE: the original code had a live OpenRouter API key
hardcoded in source. That's now read from the OPENROUTER_API_KEY
environment variable instead -- set it before running, e.g. (PowerShell):

    $env:OPENROUTER_API_KEY = "sk-or-v1-..."
    python testing.py

If you already committed/shared the old hardcoded key anywhere, treat
it as compromised and rotate it in your OpenRouter dashboard.
"""

import os

import requests

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = "openai/gpt-oss-20b:free"
REQUEST_TIMEOUT_SECONDS = 120


NARRATIVE_PROMPT = """### Context ###
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
Your primary goal is to write a compelling narrative summary of the provided logs in under 120 words, prioritizing story cohesion and atmosphere over exhaustive coverage.

Guidelines:
- Highlight low-count events (e.g., [x1]).
- High-count events should be condensed into background context unless considered important.
- For events tagged [NV], you may be more creative, describing unseen causes or off-screen consequences, as long as they remain consistent with the logs.
- Avoid breaking the fourth wall: avoid mentioning logs, tags, visibility or counts explicitly.
- Only include colonist details when they meaningfully contribute to the narrative.
- Avoid listing events; weave them into a continuous story with cause and effect.

Tone:
- Cinematic and grounded, as if recounting a chapter from a colony's history rather than a gameplay summary."""


# PLACEHOLDER -- drop in the real dialogue-only prompt here. Kept as an
# explicit, loud placeholder (rather than silently reusing
# NARRATIVE_PROMPT) so it's obvious in testing if this mode is invoked
# before the real prompt is filled in.
DIALOGUE_PROMPT = """### Context ###
You are a narrative chronicler that transforms raw game logs from a sci-fi colony simulator into immersive dialogues.

You will be given logs from a sci-fi game world.
The logs are ordered in a temporal sequence and follow this format:

Event description. [xCount] [V/NV]

[V/NV] are visibility tags:
- [V]: Event was visible to the player.
- [NV]: Event was not visible to the player.

[xCount] indicates how many times a similar event occurred.

Information regarding the player’s colonists is provided in the following format:

Name: First Name 'Nickname' Last Name -> full name of the colonist.
Gender: Male/Female - gender of the colonist.
Age: 0-99 - age of the colonist
Backstory: Backstory 1; Backstory 2; (…) - backstories from the colonist’s past as a child/teen/young adult.
Incapable of: Type of Work 1; Type of Work 2; (...) - types of work that the colonist is incapable of doing.
Traits: Trait 1; Trait 2; (...) - the colonist’s personality traits.
Relations: Relation 1; Relation 2; (...) - active relationships with other colonists/characters/animals.

### Instructions ###
Output a JSON array of 2-4 short lines colonists might say referencing these events, each under 15 words. Each entry must be a JSON object with exactly two fields:
- colonist: the full colonist name
- line: the spoken dialogue

Guidelines:
- Highlight low-count events (e.g., [x1]).
- High-count events should be seen as background context unless considered important.
- For events tagged [NV], you may be more creative, describing unseen causes or off-screen consequences, as long as they remain consistent with the logs.
- Avoid breaking the fourth wall: avoid mentioning logs, tags, visibility, or counts explicitly.
- Only include colonist details when they meaningfully contribute to the narrative.\n- Use the colonist's biographical details to ground the dialogue generation.

### Tone ###
Natural, concise, and character-driven. Each line should sound like something a real colonist would say in the moment, reflecting their personality, emotions, and recent experiences. Avoid exposition, narration, or overly poetic language."""


PROMPTS = {
    "narrative": NARRATIVE_PROMPT,
    "dialogue": DIALOGUE_PROMPT,
}


def _get_api_key():
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENROUTER_API_KEY is not set. Set it as an environment variable "
            "before running the app (see story_llm.py for details)."
        )
    return api_key


def generate_story_llm(characters_bios, selected_descriptions, mode="narrative"):
    """
    Call the LLM with the current character bios + selected log
    descriptions and return the generated text.

    Parameters
    ----------
    characters_bios : str
        Raw character bios text.
    selected_descriptions : list[str]
        Labels of the logs currently selected in the "Final Log Pool".
    mode : "narrative" | "dialogue"
        Which system prompt (see PROMPTS above) to use.
    """
    if mode not in PROMPTS:
        raise ValueError(f"Unknown generation mode {mode!r}. Valid modes: {list(PROMPTS)}")

    system_prompt = PROMPTS[mode]
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
                {"role": "system", "content": system_prompt},
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


def load_final_log_pool(path):
    """
    Read a final-log-pool file as written by the C# side (WriteFinalLogsToFiles):
    one formatted log line per line, e.g. "{log}[x{count}][{V/NV}]". Returns
    the lines as-is (stripped, blanks dropped) -- these are exactly what
    generate_story_llm() expects as `selected_descriptions`.
    """
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return [line.strip() for line in f if line.strip()]