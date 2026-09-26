"""
story_llm.py
------------
Turns an already-selected log pool into text via an LLM call through
OpenRouter, in one of two modes:
  - "narrative": a short prose chronicle (the original/default mode).
  - "dialogue": dialogue-only output (PLACEHOLDER PROMPT -- see
    PROMPTS["dialogue"] below; drop in the real prompt before using
    this mode).

SECURITY NOTE: the OpenRouter API key is read from the OPENROUTER_API_KEY
environment variable instead -- set it before running, e.g. (PowerShell):

    $env:OPENROUTER_API_KEY = "sk-or-v1-..."
    python testing.py
"""

import os

import requests
import random
import sys
import time

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
#OPENROUTER_MODEL = "poolside/laguna-xs-2.1:free"
#OPENROUTER_MODEL = "stealth/space-bunny-alpha"
OPENROUTER_MODEL = "qwen/qwen3.8-27b:free"
REQUEST_TIMEOUT_SECONDS = 120

# Retry policy for 429 (rate limited) responses specifically -- see
# _post_with_retry() below. Other HTTP errors (401 bad key, 400 bad
# request, 5xx) are NOT retried, since retrying those wouldn't help
# and would just delay an unavoidable failure.
MAX_RETRIES = 5
INITIAL_BACKOFF_SECONDS = 1.0
MAX_BACKOFF_SECONDS = 30.0


NARRATIVE_PROMPT = """### Context ###
You are a narrative chronicler that transforms raw game logs from a sci-fi colony simulator into an immersive short story.

You will be given logs from a sci-fi game world.

The logs are ordered in a temporal sequence and follow this format:

Event description. [xCount] [V/NV]

[V/NV] are visibility tags:
- [V]: Event was visible to the player.
- [NV]: Event was not visible to the player.

[xCount] indicates how many times a similar event occurred.

Information regarding the colonists is provided in the following format:

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


DIALOGUE_PROMPT = """### Context ###
You are a narrative chronicler that transforms raw game logs from a sci-fi colony simulator into immersive dialogues.

You will be given logs from a sci-fi game world.
The logs are ordered in a temporal sequence and follow this format:

Event description. [xCount] [V/NV]

[V/NV] are visibility tags:
- [V]: Event was visible to the player.
- [NV]: Event was not visible to the player.

[xCount] indicates how many times a similar event occurred.

Information regarding the colonists is provided in the following format:

Name: First Name 'Nickname' Last Name -> full name of the colonist.
Gender: Male/Female - gender of the colonist.
Age: 0-99 - age of the colonist
Backstory: Backstory 1; Backstory 2; (…) - backstories from the colonist’s past as a child/teen/young adult.
Incapable of: Type of Work 1; Type of Work 2; (...) - types of work that the colonist is incapable of doing.
Traits: Trait 1; Trait 2; (...) - the colonist’s personality traits.
Relations: Relation 1; Relation 2; (...) - active relationships with other colonists/characters/animals.

### Instructions ###
Output a JSON array of dialogue lines colonists might say referencing the events of these logs, each under 15 words. Each entry must be a JSON object with exactly two fields:
- colonist: the full colonist name
- line: the spoken dialogue
Generate 3 lines per colonist, with 2 variations of each line.

Guidelines:
- Highlight low-count events (e.g., [x1]).
- High-count events should be seen as background context unless considered important.
- For events tagged [NV], you may be more creative, describing unseen causes or off-screen consequences, as long as they remain consistent with the logs.
- Avoid breaking the fourth wall: avoid mentioning logs, tags, visibility, or counts explicitly.
- Use the colonist's biographical details to ground the dialogue generation.

### Tone ###
Natural, concise, and character-driven. Each line should sound like something a real colonist would say in the moment, reflecting their personality, emotions, and recent experiences. Avoid exposition, narration, or overly poetic language."""


DIALOGUE_FROM_NARRATIVE_PROMPT = """### Context ###
You convert narratives from a sci-fi game world into short, believable spoken lines from the colonists involved.

Information regarding the colonists is provided in the following format:

Name: First Name 'Nickname' Last Name -> full name of the colonist.
Gender: Male/Female - gender of the colonist.
Age: 0-99 - age of the colonist
Backstory: Backstory 1; Backstory 2; (…) - backstories from the colonist’s past as a child/teen/young adult.
Incapable of: Type of Work 1; Type of Work 2; (...) - types of work that the colonist is incapable of doing.
Traits: Trait 1; Trait 2; (...) - the colonist’s personality traits.
Relations: Relation 1; Relation 2; (...) - active relationships with other colonists/characters/animals.

### Instructions ###
Output a JSON array of dialogue lines colonists might say referencing the events of this narrative.

Each dialogue line should be under 20 words.

Generate 3 lines per colonist.

Each entry must be a JSON object with exactly two fields:
- colonist: the full colonist name
- line: the spoken dialogue

### Spoken Dialogue Rules ###
- All dialogue lines should begin with 'Hey [N],'. Example: 'Hey [N], [generated line].'. Do not replace [N] with the colonist's name; it will be replaced later in the game engine.
- Write dialogue as something the colonist could plausibly say aloud.
- Characters should speak retrospectively - the dialogue happens after the narrated events.
- Prefer ordinary conversational phrasing over polished prose.
- Use the character's biographical details as influences on how the colonist speaks.
- Prefer concrete observations, reactions, questions, warnings, complaints, requests, and short remarks.
- Avoid narration disguised as dialogue.
- Avoid describing symbolism, metaphors, themes, or the "meaning" of events.
- Avoid poetic language, literary metaphors, dramatic declarations, and philosophical statements.
- Avoid inventing information that the narrative does not establish.
- Avoid breaking the fourth wall: avoid mentioning mentions of the game or the narrative itself.
"""


PROMPTS = {
    "narrative": NARRATIVE_PROMPT,
    "dialogue": DIALOGUE_PROMPT,
    "dialogue_from_narrative": DIALOGUE_FROM_NARRATIVE_PROMPT
}


def _get_api_key():
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENROUTER_API_KEY is not set. Set it as an environment variable "
            "before running the app (see story_llm.py for details)."
        )
    return api_key


def _post_with_retry(url, headers, json_payload, timeout):
    """
    POST with exponential backoff, specifically for 429 (rate limited)
    responses -- other status codes (401 bad key, 400 bad request, 5xx
    server errors) are returned immediately with no retry, since
    retrying those wouldn't help and would just delay an unavoidable
    failure reaching the caller.
 
    Honors OpenRouter's `Retry-After` response header when present
    (more accurate than a fixed schedule); falls back to computed
    exponential backoff with jitter otherwise. Retries a bounded number
    of times (MAX_RETRIES) rather than indefinitely -- an unbounded
    retry loop could hang `generate` mode for a very long time during a
    sustained rate-limit window, which is worse than failing fast into
    the existing backup-story fallback.
    """
    response = None
 
    for attempt in range(MAX_RETRIES + 1):
        response = requests.post(url, headers=headers, json=json_payload, timeout=timeout)
 
        if response.status_code != 429:
            return response
 
        if attempt == MAX_RETRIES:
            return response  # out of retries -- let the caller's raise_for_status() handle it
 
        retry_after = response.headers.get("Retry-After")
        wait_seconds = None
        if retry_after is not None:
            try:
                wait_seconds = float(retry_after)
            except ValueError:
                wait_seconds = None  # header present but not a plain number of seconds
 
        if wait_seconds is None:
            wait_seconds = min(INITIAL_BACKOFF_SECONDS * (2 ** attempt), MAX_BACKOFF_SECONDS)
            wait_seconds += random.uniform(0, wait_seconds * 0.25)  # jitter, avoids retry storms
 
        print(
            f"[story_llm] 429 rate limited, retrying in {wait_seconds:.1f}s "
            f"(attempt {attempt + 1}/{MAX_RETRIES})...",
            file=sys.stderr,
        )
        time.sleep(wait_seconds)
 
    return response
 

def generate_story_llm(characters_bios, supporting_content, mode="narrative", return_usage=False):
    """
    Call the LLM with the current character bios + selected log
    descriptions and return the generated text.

    Parameters
    ----------
    characters_bios : str
        Raw character bios text.
    supporting_content : str
        Labels of the logs currently selected in the "Final Log Pool" ("narrative" and "dialogue" modes)
        OR a narrative based on the final logs ("dialogue_from_narrative" mode)
    mode : "narrative" | "dialogue" | "dialogue_from_narrative"
        Which system prompt (see PROMPTS above) to use.
    return_usage : bool
        If False (default -- unchanged from before), returns just the
        generated text, same as always. If True, returns a
        (text, usage) tuple instead, where `usage` is a dict with
        prompt_tokens/completion_tokens/total_tokens (as reported by
        OpenRouter) plus the actual `model` that served the request --
        useful for cost/performance logging. Kept opt-in and
        keyword-only so existing callers (e.g. dashboard.py, which just
        does `story = generate_story_llm(bios, descriptions)`) don't
        need to change.
    """
    if mode not in PROMPTS:
        raise ValueError(f"Unknown generation mode {mode!r}. Valid modes: {list(PROMPTS)}")

    system_prompt = PROMPTS[mode]

    if(mode == "narrative" or mode == "dialogue"):
        log_descriptions = supporting_content

        prompt = f"""### Player's Colonists ###
                {characters_bios}

                ### Input Logs ###
                {log_descriptions}
                """
    elif(mode == "dialogue_from_narrative"):
        prompt = f"""### Player's Colonists ###
                {characters_bios}

                ### Input Narrative ###
                {supporting_content}
                """

    response = _post_with_retry(
        OPENROUTER_URL,
        headers={
            "Authorization": f"Bearer {_get_api_key()}",
            "Content-Type": "application/json",
        },
        json_payload={
            "model": OPENROUTER_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
        },
        timeout=REQUEST_TIMEOUT_SECONDS,)
 
    response.raise_for_status()
    data = response.json()
 
    if "choices" not in data:
        raise RuntimeError(f"OpenRouter error: {data}")
 
    story = data["choices"][0]["message"]["content"]
 
    if not return_usage:
        return story
 
    # OpenRouter follows the OpenAI-compatible schema: data["usage"] =
    # {"prompt_tokens": ..., "completion_tokens": ..., "total_tokens": ...}.
    # .get(..., {}) rather than indexing directly, since some providers/
    # models routed through OpenRouter omit usage entirely -- this
    # shouldn't ever crash the caller just because usage reporting was
    # unavailable for a particular request.
    usage = dict(data.get("usage", {}))
    usage["model"] = data.get("model", OPENROUTER_MODEL)  # actual serving model, if OpenRouter reports one
 
    return story, usage


def load_final_log_pool(path):
    """
    Read a final-log-pool file as written by the C# side (WriteFinalLogsToFiles):
    one formatted log line per line, e.g. "{log}[x{count}][{V/NV}]". Returns
    the lines as-is (stripped, blanks dropped) -- these are exactly what
    generate_story_llm() expects as `selected_descriptions`.
    """
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return [line.strip() for line in f if line.strip()]