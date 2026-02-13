"""
V12 Campaign Generator
Refactored for Unified Content Engine — uses relative imports, no sys.path hack.
"""

from typing import List, Dict

from .bridge_manager import expand_headline_to_themes
from .db_manager import get_embedding, search_by_bridge
from .engine import generate_v11_joke


def find_matching_structures(headline: str, top_k: int = 10) -> List[Dict]:
    """
    1. Expands headline into Themes.
    2. Searches the DB's 'Bridge Vectors'.
    """
    print(f"🔍 Expanding headline to themes...")

    search_query = expand_headline_to_themes(headline)
    print(f"   Themes: {search_query}")

    print(f"🧮 Creating embedding...")
    query_embedding = get_embedding(search_query)

    if not query_embedding:
        print("   ❌ Failed to create query embedding")
        return []

    print(f"🔎 Searching bridge embeddings...")
    matches = search_by_bridge(query_embedding, match_count=top_k)

    print(f"   Found {len(matches)} matches")

    return matches


def generate_campaign(headline: str, top_k: int = 10) -> List[Dict]:
    """
    Master loop that generates joke variations based on a headline.
    """
    print()
    print("=" * 60)
    print(f"🔥 GENERATING CAMPAIGN")
    print(f"   Headline: {headline}")
    print("=" * 60)
    print()

    matches = find_matching_structures(headline, top_k=top_k)

    if not matches:
        print("❌ No matching structures found!")
        return []

    results = []

    for i, match in enumerate(matches):
        reference_joke = match.get('searchable_text', '')
        joke_id = match.get('id')
        similarity = match.get('similarity', 0)
        bridge = match.get('bridge_content', '')

        print()
        print(f"[{i+1}/{len(matches)}] ────────────────────────────────")
        print(f"📌 Reference ID: {joke_id}")
        print(f"📊 Similarity: {similarity:.3f}")
        print(f"🌉 Bridge: {bridge[:60]}..." if bridge else "   No bridge")
        print(f"📝 Joke: {reference_joke[:80]}...")
        print()

        try:
            generated = generate_v11_joke(reference_joke, headline)

            if generated.get('success'):
                result = {
                    "original_id": joke_id,
                    "searchable_text": reference_joke,
                    "bridge_content": bridge,
                    "similarity": similarity,
                    "engine": generated.get('engine_selected'),
                    "selected_strategy": generated.get('selected_strategy'),
                    "joke": generated.get('draft_joke'),
                    "brainstorming": generated.get('brainstorming', [])
                }
                results.append(result)

                print(f"✅ Engine: {result['engine']}")
                print(f"💡 Strategy: {result['selected_strategy']}")
                print(f"🎭 Joke: {result['joke']}")
            else:
                print(f"❌ Generation failed: {generated.get('error')}")

        except Exception as e:
            print(f"❌ Error: {e}")
            continue

    print()
    print("=" * 60)
    print("CAMPAIGN COMPLETE")
    print("=" * 60)
    print(f"✅ Generated: {len(results)} jokes")

    return results


def generate_campaign_json(headline: str, top_k: int = 10) -> Dict:
    """Generate campaign and return as JSON-serializable dict."""
    results = generate_campaign(headline, top_k)

    return {
        "success": True,
        "headline": headline,
        "total_generated": len(results),
        "jokes": results
    }
