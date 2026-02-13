"""
Unified Content Engine — Streamlit Dashboard
Workflow: Ideation (joke gen) → Production (video gen) → Distribution (Instagram post)

Run:  streamlit run app.py
"""

import streamlit as st
import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

# ─── Bootstrap ────────────────────────────────────────────────────────────────
# Load .env for local development (gracefully ignored if file is absent)
load_dotenv(Path(__file__).parent / ".env")

# Ensure project root is on sys.path so `modules` can be imported
PROJECT_ROOT = str(Path(__file__).parent)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# ─── Page Config (MUST be the first Streamlit command) ────────────────────────
st.set_page_config(
    page_title="Unified Content Engine",
    page_icon="🎭",
    layout="wide",
)

# ─── Bridge Streamlit Cloud Secrets → os.environ ─────────────────────────────
# On Streamlit Cloud, secrets are in st.secrets; locally they come from .env.
# We inject them into os.environ so modules using os.getenv() work everywhere.
try:
    for key, value in st.secrets.items():
        if isinstance(value, str) and key not in os.environ:
            os.environ[key] = value
except Exception:
    pass  # No secrets.toml found (local dev with .env — that's fine)


# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Import premium font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    * { font-family: 'Inter', sans-serif; }

    /* Hero title */
    .hero-title {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.6rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin-bottom: 0;
    }
    .hero-sub {
        color: #94a3b8;
        font-size: 1rem;
        font-weight: 400;
        margin-top: -8px;
        margin-bottom: 20px;
    }

    /* Section headers */
    .section-header {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 12px 0 8px 0;
    }
    .section-header .icon {
        font-size: 1.5rem;
    }
    .section-header .label {
        font-size: 1.2rem;
        font-weight: 700;
        color: #e2e8f0;
    }
    .section-header .desc {
        font-size: 0.85rem;
        color: #64748b;
        font-weight: 400;
    }

    /* Joke card */
    .joke-card {
        background: rgba(30, 30, 46, 0.7);
        border: 1px solid rgba(100, 116, 139, 0.2);
        border-radius: 12px;
        padding: 16px 20px;
        margin: 8px 0;
        transition: all 0.2s ease;
    }
    .joke-card:hover {
        border-color: rgba(102, 126, 234, 0.5);
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.1);
    }
    .joke-text {
        color: #e2e8f0;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    .joke-meta {
        display: flex;
        gap: 16px;
        margin-top: 8px;
        font-size: 0.75rem;
        color: #64748b;
    }
    .joke-meta .badge {
        background: rgba(102, 126, 234, 0.15);
        color: #818cf8;
        padding: 2px 10px;
        border-radius: 20px;
        font-weight: 600;
    }

    /* Status badges */
    .status-ok {
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    .status-warn {
        background: rgba(251, 191, 36, 0.15);
        color: #fbbf24;
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        border: 1px solid rgba(251, 191, 36, 0.3);
    }
    .status-error {
        background: rgba(239, 68, 68, 0.15);
        color: #f87171;
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }

    /* Pipeline arrow */
    .pipeline {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 8px;
        padding: 12px 0;
        font-size: 0.85rem;
        color: #64748b;
    }
    .pipeline .step {
        padding: 6px 16px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.8rem;
    }
    .pipeline .step.active {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
    }
    .pipeline .step.done {
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    .pipeline .step.pending {
        background: rgba(100, 116, 139, 0.1);
        color: #64748b;
        border: 1px solid rgba(100, 116, 139, 0.2);
    }
    .pipeline .arrow {
        color: #475569;
        font-size: 1rem;
    }

    /* Make primary buttons glow */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        padding: 0.6rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
    }

    /* Dividers */
    .divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(100, 116, 139, 0.3), transparent);
        margin: 24px 0;
    }
</style>
""", unsafe_allow_html=True)


# ─── Session State Defaults ───────────────────────────────────────────────────

defaults = {
    "bridge_matches": [],         # Raw semantic search results
    "selected_bridge_indices": [],# Which bridges the user picked
    "bridge_selection_done": False,
    "jokes": [],              # List[dict] from campaign_generator
    "selected_indices": [],   # Indices of selected jokes
    "edited_texts": {},       # {index: edited_text}
    "video_paths": {},        # {index: path_to_mp4}
    "upload_results": {},     # {index: upload_result_dict}
    "generation_done": False,
    "videos_done": False,
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val


# ─── Helpers ──────────────────────────────────────────────────────────────────

def scan_assets(subfolder, extensions):
    """Scan assets directory for files."""
    from modules.video_studio.studio import ASSETS_DIR
    target = os.path.join(ASSETS_DIR, subfolder)
    if not os.path.exists(target):
        return []
    return sorted([
        f for f in os.listdir(target)
        if f.lower().endswith(extensions) and not f.startswith(".")
    ])


def get_pipeline_html():
    """Render the pipeline status bar."""
    s1 = "done" if st.session_state.generation_done else "active"
    s2_class = "done" if st.session_state.videos_done else ("active" if st.session_state.generation_done else "pending")
    s3 = "active" if st.session_state.videos_done else "pending"
    return f"""
    <div class="pipeline">
        <span class="step {s1}">🧠 Ideation</span>
        <span class="arrow">→</span>
        <span class="step {s2_class}">🎬 Production</span>
        <span class="arrow">→</span>
        <span class="step {s3}">📤 Distribution</span>
    </div>
    """


# ─── Header ──────────────────────────────────────────────────────────────────

st.markdown('<p class="hero-title">Unified Content Engine</p>', unsafe_allow_html=True)
st.markdown('<p class="hero-sub">Ideate → Produce → Distribute — all from one dashboard</p>', unsafe_allow_html=True)
st.markdown(get_pipeline_html(), unsafe_allow_html=True)
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SECTION 1: IDEATION — The Brain
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

st.markdown("""
<div class="section-header">
    <span class="icon">🧠</span>
    <span class="label">Section 1 — Ideation</span>
    <span class="desc">Search bridge structures → Select the best ones → Generate jokes</span>
</div>
""", unsafe_allow_html=True)

# ─── Topic Input + Search ─────────────────────────────────────────────────────

topic = st.text_input(
    "Topic / Headline",
    placeholder="e.g. Bangalore Traffic, IPL Auction, Inflation...",
    label_visibility="collapsed",
)

col_search, col_reset = st.columns([4, 1])

with col_search:
    search_btn = st.button(
        "🔍 Search Bridges",
        type="primary",
        use_container_width=True,
        disabled=not topic.strip(),
    )
with col_reset:
    reset_btn = st.button("🔄 New Search", use_container_width=True)

# ─── Reset Handler ────────────────────────────────────────────────────────────

if reset_btn:
    for key, val in defaults.items():
        st.session_state[key] = val
    st.rerun()

# ─── Phase 1: Bridge Search ──────────────────────────────────────────────────

if search_btn and topic.strip():
    with st.spinner("🔍 Expanding themes and searching bridge embeddings..."):
        try:
            from modules.joke_generator.campaign_generator import search_bridges
            matches = search_bridges(topic.strip(), top_k=30)
            st.session_state.bridge_matches = matches
            st.session_state.selected_bridge_indices = []
            st.session_state.bridge_selection_done = False
            # Clear downstream state
            st.session_state.jokes = []
            st.session_state.selected_indices = []
            st.session_state.edited_texts = {}
            st.session_state.video_paths = {}
            st.session_state.upload_results = {}
            st.session_state.generation_done = False
            st.session_state.videos_done = False
            st.rerun()
        except Exception as e:
            st.error(f"❌ Bridge search failed: {e}")

# ─── Phase 1 Results: Show Bridge Matches for Selection ──────────────────────

if st.session_state.bridge_matches and not st.session_state.generation_done:
    st.markdown(
        f"**{len(st.session_state.bridge_matches)} bridge structures found** — "
        f"select the ones you want to generate jokes from:"
    )

    # Select All / Deselect All
    col_sel_all, col_desel_all, _ = st.columns([1, 1, 4])
    with col_sel_all:
        if st.button("✅ Select All", use_container_width=True):
            st.session_state.selected_bridge_indices = list(
                range(len(st.session_state.bridge_matches))
            )
            st.rerun()
    with col_desel_all:
        if st.button("❎ Deselect All", use_container_width=True):
            st.session_state.selected_bridge_indices = []
            st.rerun()

    # Display each bridge match as a selectable card
    for i, match in enumerate(st.session_state.bridge_matches):
        col_check, col_bridge = st.columns([0.05, 0.95])

        with col_check:
            selected = st.checkbox(
                "sel",
                key=f"bridge_sel_{i}",
                value=i in st.session_state.selected_bridge_indices,
                label_visibility="collapsed",
            )
            if selected and i not in st.session_state.selected_bridge_indices:
                st.session_state.selected_bridge_indices.append(i)
            elif not selected and i in st.session_state.selected_bridge_indices:
                st.session_state.selected_bridge_indices.remove(i)

        with col_bridge:
            joke_text = match.get("searchable_text", "N/A")
            bridge = match.get("bridge_content", "")
            similarity = match.get("similarity", 0)

            # Truncate long joke text for the card display
            display_text = joke_text[:200] + "..." if len(joke_text) > 200 else joke_text

            st.markdown(f"""
            <div class="joke-card">
                <div class="joke-text">{display_text}</div>
                <div class="joke-meta">
                    <span class="badge">#{i + 1}</span>
                    <span>Similarity: {similarity:.3f}</span>
                    <span>🌉 {bridge[:80]}{'...' if len(bridge) > 80 else ''}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Generate button (only if bridges are selected)
    st.markdown("")
    num_selected = len(st.session_state.selected_bridge_indices)

    generate_btn = st.button(
        f"🔥 Generate {num_selected} Joke{'s' if num_selected != 1 else ''}"
        if num_selected > 0 else "🔥 Select bridges above first",
        type="primary",
        use_container_width=True,
        disabled=num_selected == 0,
    )

    if generate_btn and num_selected > 0:
        selected_matches = [
            st.session_state.bridge_matches[i]
            for i in sorted(st.session_state.selected_bridge_indices)
        ]
        with st.spinner(f"🔥 Generating {num_selected} jokes via Gemini..."):
            try:
                from modules.joke_generator.campaign_generator import generate_from_selected
                results = generate_from_selected(topic.strip(), selected_matches)
                st.session_state.jokes = results
                st.session_state.generation_done = True
                st.session_state.bridge_selection_done = True
                st.session_state.selected_indices = []
                st.session_state.edited_texts = {}
                st.session_state.video_paths = {}
                st.session_state.upload_results = {}
                st.session_state.videos_done = False
                st.rerun()
            except Exception as e:
                st.error(f"❌ Generation failed: {e}")

# ─── Generated Jokes Display (same as before) ────────────────────────────────

if st.session_state.jokes:
    st.markdown(f"**{len(st.session_state.jokes)} jokes generated** — select the ones you want to turn into Reels:")

    for i, joke_data in enumerate(st.session_state.jokes):
        col_check, col_joke = st.columns([0.05, 0.95])

        with col_check:
            selected = st.checkbox(
                "sel",
                key=f"joke_sel_{i}",
                value=i in st.session_state.selected_indices,
                label_visibility="collapsed"
            )
            if selected and i not in st.session_state.selected_indices:
                st.session_state.selected_indices.append(i)
            elif not selected and i in st.session_state.selected_indices:
                st.session_state.selected_indices.remove(i)

        with col_joke:
            engine = joke_data.get("engine", "?")
            similarity = joke_data.get("similarity", 0)

            st.markdown(f"""
            <div class="joke-card">
                <div class="joke-text">{joke_data.get('joke', 'N/A')}</div>
                <div class="joke-meta">
                    <span class="badge">{engine}</span>
                    <span>Similarity: {similarity:.2f}</span>
                    <span>Strategy: {joke_data.get('selected_strategy', 'N/A')[:60]}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Editable text fields for selected jokes
    if st.session_state.selected_indices:
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown("**✏️ Edit selected jokes** (optional — tweak before generating videos):")

        for idx in sorted(st.session_state.selected_indices):
            joke_data = st.session_state.jokes[idx]
            original = joke_data.get("joke", "")
            current = st.session_state.edited_texts.get(idx, original)

            edited = st.text_area(
                f"Joke #{idx + 1}",
                value=current,
                key=f"edit_{idx}",
                height=80,
            )
            st.session_state.edited_texts[idx] = edited

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SECTION 2: PRODUCTION — The Studio
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

st.markdown("""
<div class="section-header">
    <span class="icon">🎬</span>
    <span class="label">Section 2 — Production</span>
    <span class="desc">Turn your jokes into Instagram Reels with video templates + music</span>
</div>
""", unsafe_allow_html=True)

# Scan assets for dropdowns
templates = scan_assets("templates", (".mp4", ".mov"))
# Filter out config.json
templates = [t for t in templates if not t.endswith(".json")]
music_files = scan_assets("music", (".mp3", ".wav", ".m4a"))

col_template, col_music, col_duration = st.columns([2, 2, 1])

with col_template:
    selected_template = st.selectbox(
        "🎥 Video Template",
        templates if templates else ["No templates found"],
        help="Background video for the Reel"
    )

with col_music:
    selected_music = st.selectbox(
        "🎵 Music Track",
        music_files if music_files else ["No music found"],
        help="Background audio track"
    )

with col_duration:
    duration = st.number_input("⏱ Duration (s)", min_value=5, max_value=60, value=15, step=5)

# Generate Videos button
can_produce = (
    st.session_state.generation_done
    and st.session_state.selected_indices
    and templates
    and music_files
)

produce_btn = st.button(
    "🎬 Generate Videos",
    type="primary",
    use_container_width=True,
    disabled=not can_produce
)

if not can_produce and st.session_state.generation_done and not st.session_state.selected_indices:
    st.info("☝️ Select at least one joke above to generate videos.")

if produce_btn:
    from modules.video_studio.studio import generate_reel, ASSETS_DIR

    progress = st.progress(0, text="Preparing...")
    total = len(st.session_state.selected_indices)

    for count, idx in enumerate(sorted(st.session_state.selected_indices)):
        joke_text = st.session_state.edited_texts.get(
            idx,
            st.session_state.jokes[idx].get("joke", "")
        )

        progress.progress(
            (count) / total,
            text=f"🎬 Rendering video {count + 1}/{total}..."
        )

        try:
            video_path = os.path.join(ASSETS_DIR, "templates", selected_template)
            audio_path = os.path.join(ASSETS_DIR, "music", selected_music)

            output_name = f"reel_{idx + 1}.mp4"
            result_path = generate_reel(
                joke_text,
                output_filename=output_name,
                duration=duration,
                video_path=video_path,
                audio_path=audio_path
            )
            st.session_state.video_paths[idx] = result_path
        except Exception as e:
            st.error(f"❌ Video {count + 1} failed: {e}")

    progress.progress(1.0, text="✅ All videos generated!")
    st.session_state.videos_done = True
    time.sleep(0.5)
    st.rerun()

# Display generated video previews
if st.session_state.video_paths:
    st.markdown("### 🎞️ Generated Reels")

    cols = st.columns(min(len(st.session_state.video_paths), 3))

    for col_idx, (joke_idx, vpath) in enumerate(sorted(st.session_state.video_paths.items())):
        with cols[col_idx % len(cols)]:
            joke_text = st.session_state.edited_texts.get(
                joke_idx,
                st.session_state.jokes[joke_idx].get("joke", "")
            )
            st.markdown(f"**Reel #{joke_idx + 1}**")
            st.caption(joke_text[:80] + "..." if len(joke_text) > 80 else joke_text)

            if os.path.exists(vpath):
                st.video(vpath)
            else:
                st.warning(f"Video file not found: {vpath}")

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SECTION 3: DISTRIBUTION — The Publisher
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

st.markdown("""
<div class="section-header">
    <span class="icon">📤</span>
    <span class="label">Section 3 — Distribution</span>
    <span class="desc">Post your Reels directly to Instagram via the Graph API</span>
</div>
""", unsafe_allow_html=True)

# Check credentials
ig_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
ig_account = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID")
creds_ok = bool(ig_token and ig_account)

if creds_ok:
    st.markdown('<span class="status-ok">✅ Instagram Credentials OK</span>', unsafe_allow_html=True)
else:
    st.markdown(
        '<span class="status-error">❌ Missing Instagram credentials in .env</span>',
        unsafe_allow_html=True
    )

if st.session_state.video_paths:
    for joke_idx, vpath in sorted(st.session_state.video_paths.items()):
        already_posted = joke_idx in st.session_state.upload_results

        col_caption, col_post = st.columns([3, 1])

        with col_caption:
            joke_text = st.session_state.edited_texts.get(
                joke_idx,
                st.session_state.jokes[joke_idx].get("joke", "")
            )
            caption = st.text_input(
                f"Caption for Reel #{joke_idx + 1}",
                value=joke_text,
                key=f"caption_{joke_idx}",
                disabled=already_posted,
            )

        with col_post:
            st.markdown("<br>", unsafe_allow_html=True)  # vertical spacer

            if already_posted:
                result = st.session_state.upload_results[joke_idx]
                permalink = result.get("permalink", "")
                if permalink:
                    st.markdown(f'<span class="status-ok">✅ Posted</span> [View →]({permalink})', unsafe_allow_html=True)
                else:
                    st.markdown('<span class="status-ok">✅ Posted</span>', unsafe_allow_html=True)
            else:
                post_btn = st.button(
                    f"📤 Post Reel #{joke_idx + 1}",
                    key=f"post_{joke_idx}",
                    disabled=not creds_ok,
                    type="primary",
                )

                if post_btn:
                    with st.spinner(f"📤 Uploading Reel #{joke_idx + 1} to Instagram..."):
                        try:
                            from modules.video_studio.uploader import upload_reel
                            result = upload_reel(
                                access_token=ig_token,
                                ig_user_id=ig_account,
                                file_path=vpath,
                                caption=caption,
                            )
                            st.session_state.upload_results[joke_idx] = result
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Upload failed: {e}")
else:
    st.info("Generate videos in Section 2 to unlock posting.")


# ─── Footer ──────────────────────────────────────────────────────────────────
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown(
    '<p style="text-align: center; color: #475569; font-size: 0.8rem;">'
    'Unified Content Engine — Joke Generator (V12) × Video Studio × Instagram Publisher'
    '</p>',
    unsafe_allow_html=True,
)
