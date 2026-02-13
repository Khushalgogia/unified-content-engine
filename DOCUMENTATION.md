# 🎭 Unified Content Engine — Full Documentation

> **One dashboard to Ideate, Produce, and Distribute Instagram comedy Reels.**
> Built with Streamlit, powered by Gemini + OpenAI + Supabase, and automated with the Instagram Graph API.

---

## Table of Contents

1. [What Is This?](#1-what-is-this)
2. [Architecture Overview](#2-architecture-overview)
3. [Directory Structure](#3-directory-structure)
4. [The Three Modules](#4-the-three-modules)
   - [Module 1: Joke Generator (Ideation)](#module-1-joke-generator--ideation)
   - [Module 2: Video Studio (Production)](#module-2-video-studio--production)
   - [Module 3: Instagram Uploader (Distribution)](#module-3-instagram-uploader--distribution)
5. [End-to-End Workflow](#5-end-to-end-workflow)
6. [All Prompts Used](#6-all-prompts-used)
7. [Environment Variables Reference](#7-environment-variables-reference)
8. [Setup & Replication Guide](#8-setup--replication-guide)
9. [Troubleshooting](#9-troubleshooting)

---

## 1. What Is This?

The **Unified Content Engine** is a Streamlit-based dashboard that automates the entire pipeline of creating and posting Instagram comedy Reels:

1. **Ideation** — You type a topic (e.g., "IPL Auction"). The app searches a Supabase database of reference jokes using semantic "Bridge Embeddings," then uses **Gemini AI** to generate new jokes by transplanting the *logic structure* of matching jokes onto your topic.
2. **Production** — You select your favorite generated jokes. The app renders them as Instagram Reels (9:16 vertical video) by overlaying styled text onto a background video with music, using **MoviePy** and **Pillow**.
3. **Distribution** — You click "Post" and the app uploads the finished Reel directly to your Instagram Business account via the **Instagram Graph API** (Resumable Upload Protocol).

**In short:** Topic → AI Jokes → Video Reels → Posted to Instagram. All from one screen.

---

## 2. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      Streamlit Dashboard (app.py)               │
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐   │
│  │  Section 1   │ →  │  Section 2   │ →  │    Section 3     │   │
│  │  🧠 Ideation │    │  🎬 Production│    │  📤 Distribution │   │
│  └──────┬───────┘    └──────┬───────┘    └────────┬─────────┘   │
│         │                   │                     │             │
│         ▼                   ▼                     ▼             │
│  joke_generator/     video_studio/         video_studio/        │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐   │
│  │campaign_gen  │    │  studio.py   │    │   uploader.py    │   │
│  │  engine.py   │    │  (MoviePy +  │    │ (Graph API +     │   │
│  │  bridge_mgr  │    │   Pillow)    │    │  Resumable UL)   │   │
│  │   db_mgr     │    └──────────────┘    └──────────────────┘   │
│  └──────────────┘                                               │
│         │                                                       │
│    ┌────┴────┐                                                  │
│    ▼         ▼                                                  │
│  OpenAI   Gemini    Supabase              Instagram             │
│ (Embed +  (Joke     (Bridge DB)           (Graph API)           │
│  Bridge)  Engine)                                               │
└─────────────────────────────────────────────────────────────────┘
```

**Tech Stack:**

| Layer | Technology |
|---|---|
| Frontend | Streamlit (Python) |
| Joke AI — Classification & Generation | Google Gemini (`gemini-3-flash-preview`) |
| Joke AI — Bridge Creation & Theme Expansion | OpenAI GPT-4o-mini |
| Joke AI — Embeddings | OpenAI `text-embedding-3-small` |
| Joke Database | Supabase (PostgreSQL + pgvector) |
| Video Rendering | MoviePy 2.x + Pillow |
| Instagram Upload | Instagram Graph API v22.0 (Resumable Upload) |
| Config | `.env` file via `python-dotenv` |

---

## 3. Directory Structure

```
Unified_Content_Engine/
├── app.py                          # Main Streamlit dashboard (553 lines)
├── .env                            # All API keys & credentials
├── .gitignore                      # Ignores .env
├── requirements.txt                # Python dependencies
├── temp/                           # Generated video output (reel_1.mp4, etc.)
│
└── modules/
    ├── __init__.py
    │
    ├── joke_generator/             # MODULE 1: Ideation
    │   ├── __init__.py             # Exports: generate_campaign, generate_campaign_json
    │   ├── campaign_generator.py   # Orchestrator: headline → themes → search → generate
    │   ├── engine.py               # Core V11 logic: classify → brainstorm → draft
    │   ├── gemini_client.py        # Gemini API wrapper (classification + generation)
    │   ├── openai_client.py        # OpenAI API wrapper (bridge creation + themes)
    │   ├── bridge_manager.py       # Bridge string creation + headline theme expansion
    │   └── db_manager.py           # Supabase client: embeddings, search, CRUD
    │
    └── video_studio/               # MODULE 2 & 3: Production + Distribution
        ├── __init__.py             # Exports: generate_reel, upload_reel
        ├── studio.py               # Video rendering engine (MoviePy + Pillow)
        ├── uploader.py             # Instagram Graph API uploader
        └── assets/
            ├── fonts/              # .ttf font files (Arial, Georgia, Verdana, etc.)
            ├── music/              # Background audio tracks (.mp3)
            └── templates/          # Background video templates (.mp4) + config.json
                └── config.json     # Per-template text styling config
```

---

## 4. The Three Modules

---

### Module 1: Joke Generator — Ideation

**What it does:** Takes a headline/topic and generates relevant comedy jokes using AI.

**The Secret Sauce: "Bridge Embeddings" (V12)**

The system doesn't just "ask AI to write a joke." Instead, it uses a **structure-first approach**:

1. There is a **database of ~hundreds of reference jokes** stored in Supabase (table: `comic_segments`).
2. Each reference joke has a **"Bridge"** — a 1-sentence abstract description of the joke's *mechanism* (e.g., "A joke about extreme procrastination where a high-stakes timeline is ignored for comfort").
3. These bridges are **embedded** using OpenAI's `text-embedding-3-small` and stored as vectors in Supabase (pgvector).
4. When you enter a new topic, the system:
   - **Expands** the topic into abstract themes (using OpenAI GPT-4o-mini)
   - **Embeds** those themes into a vector
   - **Searches** the bridge embeddings for the most structurally similar jokes
   - **Generates** new jokes by having Gemini "transplant" each reference joke's logic onto your topic

**File-by-file breakdown:**

#### `campaign_generator.py` — The Orchestrator

The main entry point. Called by `app.py` when you click "Generate Jokes."

```
Input:  headline="Bangalore Traffic", top_k=10
Output: List of joke dicts with {joke, engine, similarity, strategy, ...}
```

**Flow:**
1. Calls `expand_headline_to_themes(headline)` → gets abstract themes
2. Calls `get_embedding(themes)` → creates a search vector
3. Calls `search_by_bridge(embedding, top_k)` → gets top-K matching reference jokes
4. For each match, calls `generate_v11_joke(reference_joke, headline)` → gets a new joke

#### `bridge_manager.py` — Bridge Creation & Theme Expansion

Two functions, both powered by **OpenAI GPT-4o-mini**:

- **`create_joke_bridge(joke_text)`** — Analyzes a joke and writes a 1-sentence abstract description of its mechanism. Used when *populating* the database (not during generation).
- **`expand_headline_to_themes(headline)`** — Expands a user's topic into 5 abstract themes for semantic search.

#### `db_manager.py` — Database Layer

Talks to **Supabase** (PostgreSQL + pgvector). Key functions:

- `get_embedding(text)` — Calls OpenAI `text-embedding-3-small` to create a 1536-dim vector.
- `search_by_bridge(query_embedding, match_count)` — Calls the Supabase RPC function `match_joke_bridges` to find the most similar bridge embeddings using cosine similarity.
- `get_all_jokes()`, `update_joke_bridge()` — CRUD operations on `comic_segments` table.

**Database Schema (Supabase):**

| Column | Type | Description |
|---|---|---|
| `id` | int | Primary key |
| `searchable_text` | text | The original joke text |
| `bridge_content` | text | Abstract 1-sentence bridge description |
| `bridge_embedding` | vector(1536) | OpenAI embedding of the bridge |

**SQL Function (must exist in Supabase):**

```sql
CREATE OR REPLACE FUNCTION match_joke_bridges(
  query_embedding vector(1536),
  match_count int DEFAULT 10
)
RETURNS TABLE (
  id bigint,
  searchable_text text,
  bridge_content text,
  similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    cs.id,
    cs.searchable_text,
    cs.bridge_content,
    1 - (cs.bridge_embedding <=> query_embedding) AS similarity
  FROM comic_segments cs
  WHERE cs.bridge_embedding IS NOT NULL
  ORDER BY cs.bridge_embedding <=> query_embedding
  LIMIT match_count;
END;
$$;
```

#### `engine.py` — The V11 Logic Engine

The core classification + generation pipeline. Takes a reference joke and a new topic, and calls Gemini to:

1. **Classify** the reference joke into one of 3 "Logic Engines" (Type A, B, or C)
2. **Brainstorm** 3 mapping angles for the new topic
3. **Select** the funniest angle
4. **Draft** the final joke (max 40 words)

Also has `regenerate_joke()` for creating alternative versions with the same engine type.

#### `gemini_client.py` — Gemini API Wrapper

Handles all communication with Google's Gemini API. Uses the `google-genai` SDK.

- **Model used:** `gemini-3-flash-preview` (for all stages: classification, extraction, generation)
- **Output format:** JSON (with robust fallback parsing for truncated responses)
- Contains the **main classification prompt** — the core "Comedy Architect" system instruction (see [Section 6](#6-all-prompts-used)).

#### `openai_client.py` — OpenAI API Wrapper

Simple wrapper for OpenAI's chat completions API. Used by `bridge_manager.py`.

- **Model used:** `gpt-4o-mini`
- Single function: `generate_content(prompt, model, max_tokens, temperature)`

---

### Module 2: Video Studio — Production

**What it does:** Takes a joke text string and renders it as a 9:16 Instagram Reel (`.mp4`) with background video, text overlay, and music.

**File: `studio.py`**

**Key function: `generate_reel(joke_text, output_filename, duration, video_path, audio_path)`**

**How it works:**

1. **Load background video** from `assets/templates/` (e.g., `cat.mp4`, `jerry.mp4`)
2. **Loop or trim** the video to the desired duration (default: 15 seconds)
3. **Resize** to 1080×1920 (9:16 portrait) — auto-crops if necessary
4. **Create text overlay** as a transparent PNG using Pillow:
   - Loads per-template config from `config.json` (position, font, size, color, alignment)
   - Word-wraps text to fit the configured text area
   - Auto-scales font size down if text overflows
   - Applies text shadow if configured
5. **Load background music** from `assets/music/` — loops or trims to match duration
6. **Composite** video + text overlay + audio using MoviePy
7. **Export** as `.mp4` (H.264 + AAC) to the `temp/` folder

**Template Config (`config.json`):**

Each video template can have custom text styling:

```json
{
  "cat1.mp4": {
    "text_area": { "x": 37, "y": 1048, "width": 999, "height": 483 },
    "font": "Mulish-Regular.ttf",
    "font_size": 70,
    "color": "#000000",
    "shadow": null,
    "alignment": "left",
    "font_weight": "regular",
    "padding": 20
  }
}
```

| Field | Description |
|---|---|
| `text_area` | Pixel coordinates and dimensions where text is placed |
| `font` | Font filename (from `assets/fonts/`) |
| `font_size` | Base font size in pixels (auto-scales down if overflow) |
| `color` | Text color (hex) |
| `shadow` | Shadow color (hex) or `null` for no shadow |
| `alignment` | `"left"`, `"center"`, or `"right"` |
| `font_weight` | `"regular"`, `"bold"`, `"medium"`, etc. |
| `padding` | Inner padding in pixels |

**Available Fonts:** Arial, Georgia, TrebuchetMS, Verdana (Regular + Bold variants), Mulish.

---

### Module 3: Instagram Uploader — Distribution

**What it does:** Uploads a generated `.mp4` Reel to Instagram using the Graph API's Resumable Upload Protocol.

**File: `uploader.py`**

**The 4-Step Upload Pipeline:**

```
initialize_upload() → upload_file() → check_status() → publish()
         │                  │                │              │
   Create media       Upload binary     Poll until      Publish to
   container on       to Instagram's    "FINISHED"       Instagram
   Graph API          rupload server    (max 5 min)       feed
```

**Step 1: `initialize_upload(access_token, ig_user_id, file_path, caption)`**
- `POST https://graph.facebook.com/v22.0/{ig_user_id}/media`
- Parameters: `media_type=REELS`, `upload_type=resumable`, `caption`, `access_token`
- Returns: `container_id`

**Step 2: `upload_file(access_token, container_id, file_path)`**
- `POST https://rupload.facebook.com/ig-api-upload/{container_id}`
- Sends the raw `.mp4` binary as `application/octet-stream`
- Headers include `Authorization: OAuth {token}`, `offset: 0`, `file_size: {bytes}`

**Step 3: `check_status(access_token, container_id)`**
- `GET https://graph.facebook.com/v22.0/{container_id}?fields=status_code,status`
- Polls every 5 seconds, up to 60 retries (5 minutes max)
- Waits for `status_code == "FINISHED"`

**Step 4: `publish(access_token, ig_user_id, container_id)`**
- `POST https://graph.facebook.com/v22.0/{ig_user_id}/media_publish`
- Parameters: `creation_id={container_id}`, `access_token`
- Returns: `media_id`

**Bonus: `get_permalink(access_token, media_id)`** — Fetches the public URL of the posted Reel.

---

## 5. End-to-End Workflow

Here's exactly what happens when you use the app:

### Step 1: Launch the App

```bash
streamlit run app.py
```

The Streamlit dashboard opens with 3 sections.

### Step 2: Ideation — Generate Jokes

1. Type a topic (e.g., "Australia lost the series")
2. Set the number of jokes (1–15)
3. Click **"🔥 Generate Jokes"**

**Behind the scenes:**
- `expand_headline_to_themes("Australia lost the series")` → `"Defeat, Disappointment, Underperformance, Humiliation, Unexpected Outcome"`
- `get_embedding("Defeat, Disappointment, ...")` → 1536-dim vector
- `search_by_bridge(vector, top_k=10)` → Top 10 semantically similar reference jokes
- For each match: `generate_v11_joke(reference_joke, headline)` → Gemini classifies, brainstorms, drafts

### Step 3: Select & Edit

- Checkboxes appear next to each generated joke
- Select your favorites
- Optionally edit the text in text areas

### Step 4: Production — Generate Videos

1. Choose a **video template** (dropdown of `.mp4` files from `assets/templates/`)
2. Choose a **music track** (dropdown of `.mp3` files from `assets/music/`)
3. Set **duration** (5–60 seconds)
4. Click **"🎬 Generate Videos"**

**Behind the scenes:**
- For each selected joke: `generate_reel(joke_text, "reel_1.mp4", duration, video_path, audio_path)`
- Videos saved to `temp/reel_1.mp4`, `temp/reel_2.mp4`, etc.
- Video previews appear in the dashboard

### Step 5: Distribution — Post to Instagram

1. Edit the **caption** for each Reel (pre-filled with the joke text)
2. Click **"📤 Post Reel #1"**

**Behind the scenes:**
- `upload_reel(access_token, ig_user_id, file_path, caption)`
- Goes through the 4-step resumable upload pipeline
- On success: shows ✅ with a permalink to the posted Reel

---

## 6. All Prompts Used

### Prompt 1: Bridge Creation (OpenAI GPT-4o-mini)

**Used in:** `bridge_manager.py → create_joke_bridge()`
**Purpose:** Create a 1-sentence abstract description of a joke's mechanism for embedding.

```
Analyze this joke: "{joke_text}"

Write a 1-sentence "Search Description" for this joke.

RULES:
1. Do NOT mention specific nouns (e.g., don't say 'Coma', say 'Long Delay').
2. Focus on the EMOTION and the MECHANISM.
3. Use keywords that describe what kind of topics this joke fits.

Example Output: "A joke about extreme procrastination where a high-stakes
timeline is ignored for comfort."

OUTPUT: Just the description, nothing else.
```

---

### Prompt 2: Theme Expansion (OpenAI GPT-4o-mini)

**Used in:** `bridge_manager.py → expand_headline_to_themes()`
**Purpose:** Expand a user's topic into abstract search themes.

```
Topic: "{headline}"

List 5 abstract themes or concepts associated with this topic.

Example: If topic is 'Traffic', themes are 'Waiting', 'Frustration',
'Wasting Time', 'Trapped'.

OUTPUT: Just the comma-separated themes, nothing else.
```

---

### Prompt 3: The Comedy Architect — Classification + Generation (Gemini)

**Used in:** `gemini_client.py → classify_joke_type()`
**Purpose:** The core joke generation engine. Classifies a reference joke into one of 3 "Logic Engines," brainstorms 3 angles, and drafts a new joke.

**System Instruction:**

```
You are a Comedy Architect. You reverse-engineer the logic of a reference joke
and transplant it into a new topic.

YOUR PROCESS:
1. Analyze the 'Reference Joke' to find the Engine (A, B, or C).
2. BRAINSTORM 3 distinct mapping angles for the New Topic.
3. Select the funniest angle.
4. Draft the final joke.

---
THE ENGINES:

TYPE A: The "Word Trap" (Semantic/Pun)
- Logic: A trigger word bridges two unrelated contexts.
- Mapping: Find a word in the New Topic that has a double meaning.
  If none exists, FAIL and switch to Type C.

TYPE B: The "Behavior Trap" (Scenario/Character)
- Logic: Character applies a [Mundane Habit] to a [High-Stakes Situation],
  trivializing it.
- Mapping:
  1. Identify the Abstract Behavior (e.g. "Being Cheap", "Being Lazy",
     "Professional Deformation").
  2. You may SWAP the specific trait if a better one exists for the New Topic.
  3. Apply the Trait to the New Context. DO NOT PUN.

TYPE C: The "Hyperbole Engine" (Roast/Exaggeration)
- Logic: A physical trait is exaggerated until it breaks physics/social norms.
- Mapping:
  1. Identify the Scale (e.g. Size, Weight, Wealth).
  2. Constraint: Conservation of Failure.
  3. Format: Statement ("He is so X..."), NOT a scene.

---
OUTPUT FORMAT (JSON ONLY):
{
  "engine_selected": "Type A/B/C",
  "reasoning": "Explain why this engine fits.",
  "brainstorming": [
    "Option 1: [Trait/Angle] -> [Scenario]",
    "Option 2: [Trait/Angle] -> [Scenario]",
    "Option 3: [Trait/Angle] -> [Scenario]"
  ],
  "selected_strategy": "The best option from above",
  "draft_joke": "The final joke text. Max 40 words. NO FILLER.
                  Start directly with the setup."
}
```

**User Prompt:**

```
REFERENCE JOKE:
"{reference_joke}"

NEW TOPIC:
"{new_topic}"

Analyze the reference joke, brainstorm 3 mapping angles, select the funniest,
and draft the final joke.
```

---

### Prompt 4: Joke Regeneration (Gemini)

**Used in:** `engine.py → regenerate_joke()`
**Purpose:** Generate a different version of a joke using the same logic engine.

**System Instruction:**

```
You are a Comedy Writer. You have already classified this joke as {engine_type}.

Now generate a DIFFERENT version. Brainstorm 3 NEW angles (different from before).

PREVIOUS DRAFT (DO NOT REPEAT):
"{previous_draft}"

Generate a fresh take using the same {engine_type} logic engine.
```

---

## 7. Environment Variables Reference

All credentials are stored in `.env` at the project root. The app loads them via `python-dotenv`.

```env
# ─── Joke Generator (Version_12) ─────────────────────────────
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key_here

# ─── Video Studio (Studio_AutoPost) ──────────────────────────
INSTAGRAM_ACCESS_TOKEN=your_instagram_long_lived_token_here
INSTAGRAM_BUSINESS_ACCOUNT_ID=your_instagram_business_account_id
```

| Variable | Service | How to Get It |
|---|---|---|
| `GEMINI_API_KEY` | Google AI Studio | [aistudio.google.com](https://aistudio.google.com/) → Get API Key |
| `OPENAI_API_KEY` | OpenAI | [platform.openai.com/api-keys](https://platform.openai.com/api-keys) |
| `SUPABASE_URL` | Supabase | Project Settings → API → URL |
| `SUPABASE_KEY` | Supabase | Project Settings → API → `anon` `public` key |
| `INSTAGRAM_ACCESS_TOKEN` | Meta Graph API | Graph API Explorer → Generate User Token (select `instagram_content_publish` + `instagram_basic` scopes) → Exchange for Long-Lived Token |
| `INSTAGRAM_BUSINESS_ACCOUNT_ID` | Meta Graph API | Graph API Explorer → `GET /me/accounts` → get Page ID → `GET /{page_id}?fields=instagram_business_account` → use the `id` |

---

## 8. Setup & Replication Guide

### Prerequisites

- Python 3.10+
- A Supabase project with the `comic_segments` table and `match_joke_bridges` SQL function (see [Module 1](#module-1-joke-generator--ideation))
- Reference jokes populated in Supabase with bridge embeddings
- An Instagram Business or Creator account connected to a Facebook Page
- A Meta Developer App (in Development mode is fine — add yourself as a Tester)

### Step-by-Step Setup

```bash
# 1. Clone/copy the project
cd /path/to/your/workspace

# 2. Create and activate virtual environment
python -m venv workflow
source workflow/bin/activate  # macOS/Linux
# workflow\Scripts\activate   # Windows

# 3. Install dependencies
pip install -r Unified_Content_Engine/requirements.txt

# 4. Create your .env file
cp Unified_Content_Engine/.env.example Unified_Content_Engine/.env
# Edit .env and fill in your API keys (see Section 7)

# 5. Add video templates
# Place your background .mp4 files in:
#   Unified_Content_Engine/modules/video_studio/assets/templates/

# 6. Add music
# Place your .mp3 files in:
#   Unified_Content_Engine/modules/video_studio/assets/music/

# 7. Add fonts (optional — defaults are included)
# Place .ttf files in:
#   Unified_Content_Engine/modules/video_studio/assets/fonts/

# 8. Configure text styling per template (optional)
# Edit: Unified_Content_Engine/modules/video_studio/assets/templates/config.json
# Add an entry for each video template with text position, font, size, etc.

# 9. Run the app!
streamlit run Unified_Content_Engine/app.py
```

### Setting Up the Instagram Token

1. Go to [developers.facebook.com/apps](https://developers.facebook.com/apps/)
2. Create an app (or use existing) → Type: **Business**
3. Add the **Instagram Graph API** product
4. Go to **App Roles** → Add yourself as a **Tester** → Accept the invitation
5. Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
6. Select your app
7. Click **Generate Access Token** → grant `instagram_basic`, `instagram_content_publish`, `pages_show_list`, `pages_read_engagement`
8. **Exchange for Long-Lived Token** (valid 60 days):

```bash
curl -X GET "https://graph.facebook.com/v22.0/oauth/access_token?\
grant_type=fb_exchange_token&\
client_id=YOUR_APP_ID&\
client_secret=YOUR_APP_SECRET&\
fb_exchange_token=YOUR_SHORT_LIVED_TOKEN"
```

9. Copy the returned `access_token` into your `.env` file
10. Get your Instagram Business Account ID:

```bash
# First get your Page ID
curl "https://graph.facebook.com/v22.0/me/accounts?access_token=YOUR_TOKEN"

# Then get the Instagram Business Account ID
curl "https://graph.facebook.com/v22.0/PAGE_ID?fields=instagram_business_account&access_token=YOUR_TOKEN"
```

11. Copy the `instagram_business_account.id` into your `.env`

### Setting Up Supabase

1. Create a project at [supabase.com](https://supabase.com/)
2. Create the `comic_segments` table:

```sql
CREATE TABLE comic_segments (
  id BIGSERIAL PRIMARY KEY,
  searchable_text TEXT NOT NULL,
  bridge_content TEXT,
  bridge_embedding vector(1536)
);
```

3. Enable the `vector` extension:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

4. Create the search function:

```sql
CREATE OR REPLACE FUNCTION match_joke_bridges(
  query_embedding vector(1536),
  match_count int DEFAULT 10
)
RETURNS TABLE (
  id bigint,
  searchable_text text,
  bridge_content text,
  similarity float
)
LANGUAGE plpgsql AS $$
BEGIN
  RETURN QUERY
  SELECT
    cs.id,
    cs.searchable_text,
    cs.bridge_content,
    1 - (cs.bridge_embedding <=> query_embedding) AS similarity
  FROM comic_segments cs
  WHERE cs.bridge_embedding IS NOT NULL
  ORDER BY cs.bridge_embedding <=> query_embedding
  LIMIT match_count;
END;
$$;
```

5. Populate with reference jokes and generate bridges:
   - Insert jokes into `searchable_text`
   - Use `bridge_manager.create_joke_bridge()` to generate `bridge_content`
   - Use `db_manager.get_embedding()` to generate `bridge_embedding`
   - Use `db_manager.update_joke_bridge()` to store them

---

## 9. Troubleshooting

| Issue | Cause | Fix |
|---|---|---|
| "API access blocked" on Instagram upload | Meta security checkpoint on new app/activity | Log into [developers.facebook.com](https://developers.facebook.com/), verify your identity, try again from a different browser |
| Token expires after 1 hour | Using a short-lived token | Exchange for a long-lived token (see Section 8) |
| Token expires after 60 days | Long-lived tokens aren't permanent | Refresh it: `GET /oauth/access_token?grant_type=fb_exchange_token&fb_exchange_token=YOUR_CURRENT_LONG_TOKEN&client_id=APP_ID&client_secret=APP_SECRET` |
| `ModuleNotFoundError: moviepy` | Dependencies not installed | `pip install -r requirements.txt` |
| "No fonts found" warning | Missing font files | Add `.ttf` fonts to `modules/video_studio/assets/fonts/` |
| Text too small / overflows | Config mismatch | Edit `config.json` text_area dimensions or use the template editor HTML tool |
| Supabase RPC error | Missing SQL function | Create the `match_joke_bridges` function (see Section 8) |
| `GEMINI_API_KEY not found` | `.env` not loaded | Make sure `.env` is in the `Unified_Content_Engine/` root directory |

---

*Built with ❤️ as the Unified Content Engine — Joke Generator (V12) × Video Studio × Instagram Publisher*
