# Sifting and Support Framework

A compression-based log analysis, hierarchical clustering, and LLM narrative generation framework. This repository processes raw game logs using Normalized Compression Distance (NCD), builds hierarchical dendrograms, selects representative log subsets via configurable tree-traversal strategies, and generates stories or dialogue using an LLM.

---

## Table of Contents

- [Overview](#overview)
- [Repository Structure & Key Modules](#repository-structure--key-modules)
- [Configuration & Settings (`config.py`)](#configuration--settings-configpy)
  - [Game Host Integration (`RUNNING_WITHIN_GAME`)](#game-host-integration-running_within_game)
  - [Pre-configured Example Scenarios](#pre-configured-example-scenarios)
- [Environment Setup & API Key](#environment-setup--api-key)
- [Configuring LLM Settings & Prompts (`story_llm.py`)](#configuring-llm-settings--prompts-story_llmpy)
  - [Endpoint URL & Model Configuration](#endpoint-url--model-configuration)
  - [Customizing System Prompts & Generation Modes](#customizing-system-prompts--generation-modes)
- [Core Pipeline & Main Python Functions](#core-pipeline--main-python-functions)
  - [1. Preprocessing (`pipeline.py`)](#1-preprocessing-pipelinepy)
  - [2. Log Selection & Tree Traversal (`log_selection.py`)](#2-log-selection--tree-traversal-log_selectionpy)
  - [3. LLM Narrative Generation (`story_llm.py`)](#3-llm-narrative-generation-story_llmpy)
  - [4. Dashboard & Server (`dashboard.py` & `server.py`)](#4-dashboard--server-dashboardpy--serverpy)
- [Live Interactive Demo (`main_demo.py`)](#live-interactive-demo-main_demopy)
- [Building an Isolated Executable with PyInstaller](#building-an-isolated-executable-with-pyinstaller)

---

## Overview

The **Log Dendrogram Explorer** provides both an interactive web dashboard and a headless CLI framework for analyzing log data. It uses string compression algorithms (zlib Deflate) to measure information-theoretic similarity between log entries without relying on domain-specific parsers.

Key capabilities:
- **NCD Distance Calculation**: Computes pairwise Normalized Compression Distance across log entries.
- **Hierarchical Clustering**: Constructs a canonical dendrogram tree using average linkage.
- **Dynamic Tree Zooming**: Collapses subtrees below an NCD threshold using medoid-based representative selection.
- **Traversal Strategies**: Selects representative log pools via random walk or least-frequent branch descent.
- **LLM Narrative Synthesis**: Transforms selected log pools and character bios into stories or character dialogues.

---

## Repository Structure & Key Modules

| Module / File | Description |
| :--- | :--- |
| `config.py` | Static configuration: `RUNNING_WITHIN_GAME` flag, NCD thresholds (`INITIAL_NCD_THRESHOLD = 0.5`), example scenario paths, CSS styling, and backup story fallbacks. |
| `compression_algorithms.py` | Compression wrappers (`zlib` Deflate) returning compressed payload sizes in bytes. |
| `ncd_data.py` | In-memory NCD calculations, log line normalization, deduplication, and timestamp extraction. |
| `tree_utils.py` | Structural tree operations: node depth assignment, subtree frequency aggregation, medoid calculation, and NCD threshold collapsing. |
| `traversal_strategies.py` | Branch selection algorithms (`Random` vs. `Least Frequent` branch descent). |
| `pipeline.py` | Main end-to-end processing pipeline (log ingestion -> NCD matrix -> SciPy linkage tree). |
| `log_selection.py` | Headless log selection wrapper and chronological reordering of selected log pools. |
| `story_llm.py` | LLM client, prompt templates, and generation modes for OpenRouter / OpenAI-compatible API endpoints. |
| `dashboard.py` | Panel UI construction and Plotly dendrogram visualization callbacks. |
| `dendrogram_plot.py` | Custom Plotly dendrogram renderer with zoom bounds and red traversal path highlighting. |
| `server.py` | Local web server launcher for Panel with port detection and auto-shutdown logic. |
| `main_demo.py` | Central entry point supporting both interactive GUI and headless JSON CLI modes. |
| `main_demo.spec` | PyInstaller spec file for bundling the framework into a standalone binary. |

---

## Configuration & Settings (`config.py`)

### Game Host Integration (`RUNNING_WITHIN_GAME`)

`config.py` includes a hard-coded flag that controls whether the framework is operating as an embedded module within an external game host process (e.g., a C# enabler/mod host):

```python
# In config.py:
RUNNING_WITHIN_GAME = True  # Set to True when running inside the game enabler (C# host process)
```

- **Set to `True`**: Keep this as `True` if you plan to access the Python code or compiled `.exe` from within a game or C# host process.
- **Set to `False`**: Change to `False` if running standalone, during local CLI debugging, or when executing outside the game environment.

### Pre-configured Example Scenarios

`config.py` also defines pre-configured example scenarios and default input file paths (referencing sample datasets in `Test Scenarios/`, such as `demo_all_events_complete.txt` and `demo_all_events_charactersbios.txt`). You can utilize these built-in scenario configurations to test pipeline execution without supplying custom log files.

---

## Environment Setup & API Key

The LLM narrative generator (`story_llm.py`) connects to an external OpenRouter or OpenAI-compatible endpoint. To authenticate, you must set the `OPENROUTER_API_KEY` environment variable in your terminal before running the script.

### Setting the Environment Variable

#### Windows (PowerShell)
```powershell
$env:OPENROUTER_API_KEY = "sk-or-v1-your-api-key-here"
python main_demo.py
```

#### Windows (Command Prompt)
```cmd
set OPENROUTER_API_KEY=sk-or-v1-your-api-key-here
python main_demo.py
```

#### Linux / macOS (Bash / Zsh)
```bash
export OPENROUTER_API_KEY="sk-or-v1-your-api-key-here"
python main_demo.py
```

*Note: If `OPENROUTER_API_KEY` is not detected, `story_llm.py` will raise a `RuntimeError` on generation requests.*

---

## Configuring LLM Settings & Prompts (`story_llm.py`)

### Endpoint URL & Model Configuration

If you want to route requests to a custom LLM endpoint (e.g., local server like LM Studio, Ollama, vLLM, or another API provider), you can manually change the hard-coded endpoint settings directly in `story_llm.py`:

```python
# In story_llm.py:

# 1. Base URL for chat completions
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"  # Modify this URL if using a custom server

# 2. Model Identifier
OPENROUTER_MODEL = "qwen/qwen3.8-27b:free"  # Change to your target model ID

# 3. Request Timeout
REQUEST_TIMEOUT_SECONDS = 120
```

To switch endpoints, edit `OPENROUTER_URL` to point to your target server (e.g., `http://localhost:1234/v1/chat/completions`).

### Customizing System Prompts & Generation Modes

You can customize the LLM's output style, formatting, and behavioral constraints by editing the prompt templates in `story_llm.py`. The framework supports three distinct prompt modes:

1. **Generating a Narrative from Logs (`mode="narrative"`)**:
   Synthesizes pre-selected log events and character biographies into an atmospheric prose chronicle.
2. **Generating Dialogue from Logs (`mode="dialogue"`)**:
   Transforms pre-selected log events and character bios directly into character-driven dialogue exchanges (returned in structured JSON or text format).
3. **Generating Dialogue from Narrative (`mode="dialogue_from_narrative"`)**:
   Takes a previously generated prose narrative as input and converts it into character dialogue.

---

## Core Pipeline & Main Python Functions

You can import and call the framework's core modules directly in your own Python scripts.

### 1. Preprocessing (`pipeline.py`)
Loads raw log files, deduplicates entries, computes the NCD pairwise distance matrix, and builds the canonical hierarchical clustering tree.

```python
import pipeline

# Run preprocessing pipeline
pipeline_state = pipeline.run_preprocessing(
    full_log="Test Scenarios/demo_all_events_complete.txt",
    characters_bios_log="Test Scenarios/demo_all_events_charactersbios.txt",
    seed=42
)

# Inspect output dictionary
unique_logs = pipeline_state["unique_logs"]
distance_matrix = pipeline_state["distance_matrix"]
root_0 = pipeline_state["root_0"]  # Canonical SciPy ClusterNode tree
```

### 2. Log Selection & Tree Traversal (`log_selection.py`)
Zooms into the canonical tree at a given NCD threshold and applies traversal strategies to pick a representative log pool.

```python
from log_selection import select_final_log_pool

selection = select_final_log_pool(
    pipeline_state=pipeline_state,
    ncd_threshold=0.5,        # Merge logs below this NCD similarity distance
    control="fixed_depth",    # Options: "fixed_depth" or "target_count"
    strategy="random",         # Options: "random" or "least_frequent"
    depth=1,                  # Traversal depth
    target_count=2,           # Desired log pool size (if control="target_count")
    seed=42
)

print("Selected Log Pool:", selection["final_log_pool_short"])
```

### 3. LLM Narrative Generation (`story_llm.py`)
Sends selected logs and character bios to the LLM using one of the three supported prompt modes.

```python
from story_llm import generate_story_llm

bios_text = "Name: Ava 'Farmer' Smith..."
log_descriptions = "Colonist Ava planted crops.[x5][NV]\nA meteor shower struck the base.[x1][V]"

# Mode 1: Generate narrative story from log pool
narrative = generate_story_llm(
    characters_bios=bios_text,
    supporting_content=log_descriptions,
    mode="narrative"
)

# Mode 2: Generate dialogue directly from log pool
dialogue = generate_story_llm(
    characters_bios=bios_text,
    supporting_content=log_descriptions,
    mode="dialogue"
)

# Mode 3: Generate dialogue from an existing narrative chronicle
dialogue_from_story = generate_story_llm(
    characters_bios=bios_text,
    supporting_content=narrative,  # Pass the generated narrative story as input
    mode="dialogue_from_narrative"
)
```

### 4. Dashboard & Server (`dashboard.py` & `server.py`)
Builds the Panel UI layout and serves it locally.

```python
from dashboard import build_dashboard
import server

dashboard = build_dashboard(pipeline_state)
server.serve_dashboard(dashboard, title="Log Dendrogram Explorer")
```

---

## Live Interactive Demo (`main_demo.py`)

The primary live demo interface is implemented in `main_demo.py`. You can use this to visually explore how compression filtering and tree traversal select representative log events.

### Running the Interactive UI

```bash
python main_demo.py
```
*(or explicitly: `python main_demo.py demo`)*

This command:
1. Runs log preprocessing.
2. Constructs the interactive Panel dashboard with dynamic Plotly dendrograms.
3. Opens a browser window showing the interactive controls (NCD slider, depth selector, strategy options, and story generator).

### Headless CLI Modes

`main_demo.py` also provides headless JSON CLI modes (used for automated pipelines or C# game client integration):

```bash
# Headless preprocessing JSON output
python main_demo.py preprocess --full-log "logs.txt" --bios-log "bios.txt"

# Headless selection JSON output
python main_demo.py select --ncd-threshold 0.5 --control fixed_depth --strategy random

# Headless story generation from pre-selected log pool file
python main_demo.py generate_from_logs --final-log-pool "selected_logs.txt" --bios-log "bios.txt" --generation-mode narrative
```

---

## Building an Isolated Executable with PyInstaller

To bundle the entire framework into a standalone binary that can be deployed or called by an external application (such as a C# host process or game mod) without requiring a Python environment:

Run the following command in the repository root:

```bash
python -m PyInstaller main_demo.spec
```

### Output
This will build a self-contained executable bundle inside the `dist/` directory:
- Executable location: `dist/main_demo/main_demo.exe` (Windows) or `dist/main_demo/main_demo` (Linux/macOS)

You can distribute this executable as an isolated, zero-dependency module for external integrations.
