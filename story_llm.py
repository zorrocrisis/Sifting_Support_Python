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

PROVIDER_URL = ""
MODEL_URL = ""
REQUEST_TIMEOUT_SECONDS = 120

# Retry policy for 429 (rate limited) responses specifically -- see
# _post_with_retry() below. Other HTTP errors (401 bad key, 400 bad
# request, 5xx) are NOT retried, since retrying those wouldn't help
# and would just delay an unavoidable failure.
MAX_RETRIES = 5
INITIAL_BACKOFF_SECONDS = 1.0
MAX_BACKOFF_SECONDS = 30.0


# Example of a provider URL (see get_provider_url() below for how the actual URL is loaded from models/provider_URL.txt)
#PROVIDER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Examples of model URLs (see get_model_url() below for how the actual URL is loaded from models/model_URL.txt)
#MODEL_URL = "poolside/laguna-xs-2.1:free"
#MODEL_URL = "stealth/space-bunny-alpha"
#MODEL_URL = "qwen/qwen3.8-27b:free" # not free anymore
#MODEL_URL = "google/gemma-4-31b-it:free" # not free anymore


PROMPT_MODES = ("narrative", "dialogue", "dialogue_from_narrative")

def _models_dirs():
    """Folders to search for model files, in priority order."""
    dirs = []

    # 1. Explicit override, useful for A/B testing prompt versions.
    override = os.environ.get("MODELS_DIR")
    if override:
        dirs.append(override)

    if getattr(sys, "frozen", False):  # running as a PyInstaller exe
        # 2. A "models" folder next to the exe: editable without rebuilding.
        dirs.append(os.path.join(os.path.dirname(sys.executable), "models"))
        # 3. Copy bundled inside the exe (see --add-data below).
        if getattr(sys, "_MEIPASS", None):
            dirs.append(os.path.join(sys._MEIPASS, "models"))

    # 4. Plain `python main_demo.py` during development.
    dirs.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "models"))
    return dirs

def get_model_url():
    """Load the model URL for `mode` from models/model_URL.txt."""

    searched = []
    for directory in _models_dirs():
        path = os.path.join(directory, f"model_URL.txt")
        searched.append(path)
        if os.path.isfile(path):
            # utf-8-sig tolerates the BOM that Windows Notepad adds.
            with open(path, "r", encoding="utf-8-sig") as f:
                return f.read().strip()

    raise FileNotFoundError(f"No model URL file found. Looked in: {searched}")

def get_provider_url():
    """Load the provider URL for `mode` from models/provider_URL.txt."""

    searched = []
    for directory in _models_dirs():
        path = os.path.join(directory, f"provider_URL.txt")
        searched.append(path)
        if os.path.isfile(path):
            # utf-8-sig tolerates the BOM that Windows Notepad adds.
            with open(path, "r", encoding="utf-8-sig") as f:
                return f.read().strip()

    raise FileNotFoundError(f"No provider URL file found. Looked in: {searched}")



def _prompt_dirs():
    """Folders to search for prompt files, in priority order."""
    dirs = []

    # 1. Explicit override, useful for A/B testing prompt versions.
    override = os.environ.get("STORY_PROMPTS_DIR")
    if override:
        dirs.append(override)

    if getattr(sys, "frozen", False):  # running as a PyInstaller exe
        # 2. A "prompts" folder next to the exe: editable without rebuilding.
        dirs.append(os.path.join(os.path.dirname(sys.executable), "prompts"))
        # 3. Copy bundled inside the exe (see --add-data below).
        if getattr(sys, "_MEIPASS", None):
            dirs.append(os.path.join(sys._MEIPASS, "prompts"))

    # 4. Plain `python main_demo.py` during development.
    dirs.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "prompts"))
    return dirs


def get_prompt(mode):
    """Load the system prompt for `mode` from prompts/<mode>.txt."""
    if mode not in PROMPT_MODES:
        raise ValueError(f"Unknown generation mode {mode!r}. Valid modes: {list(PROMPT_MODES)}")

    searched = []
    for directory in _prompt_dirs():
        path = os.path.join(directory, f"{mode}.txt")
        searched.append(path)
        if os.path.isfile(path):
            # utf-8-sig tolerates the BOM that Windows Notepad adds.
            with open(path, "r", encoding="utf-8-sig") as f:
                return f.read().strip()

    raise FileNotFoundError(f"No prompt file for mode {mode!r}. Looked in: {searched}")


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
    system_prompt = get_prompt(mode)   # also validates the mode
    MODEL_URL = get_model_url()
    PROVIDER_URL = get_provider_url()


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
        PROVIDER_URL,
        headers={
            "Authorization": f"Bearer {_get_api_key()}",
            "Content-Type": "application/json",
        },
        json_payload={
            "model": MODEL_URL,
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
    usage["model"] = data.get("model", MODEL_URL)  # actual serving model, if OpenRouter reports one
 
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