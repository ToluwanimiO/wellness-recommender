
from pathlib import Path
import html
import pandas as pd
import streamlit as st

# =========================================================
# CONFIGURATION
# =========================================================
BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "recipes.csv"

st.set_page_config(
    page_title="Nourish — Find your next favourite",
    page_icon="🍋",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =========================================================
# DATA
# =========================================================
@st.cache_data
def load_recipes():
    if not DATA_FILE.exists():
        return pd.DataFrame()

    df = pd.read_csv(DATA_FILE).fillna("")

    required = {
        "recipe_id",
        "recipe_title",
        "ingredients",
        "directions",
        "image_path",
    }

    if not required.issubset(df.columns):
        return pd.DataFrame()

    df["recipe_id"] = df["recipe_id"].astype(str)
    for column in ["recipe_title", "ingredients", "directions", "image_path"]:
        df[column] = df[column].astype(str)

    df["search_text"] = (
        df["recipe_title"] + " " + df["ingredients"]
    ).str.lower()

    return df


recipes = load_recipes()

if recipes.empty:
    st.error(
        "Recipe data could not be loaded. Check that data/recipes.csv "
        "exists and contains recipe_id, recipe_title, ingredients, "
        "directions, and image_path."
    )
    st.stop()

# =========================================================
# SESSION STATE
# =========================================================
defaults = {
    "page": "Discover",
    "selected_recipe_id": "",
    "last_surprise_id": "",
    "surprise_result_id": "",
    "saved_recipes": [],
    "search_query": "",
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# HELPERS
# =========================================================
def safe_text(value):
    return html.escape(str(value))


def image_for(row):
    relative = str(row.get("image_path", "")).strip()
    if not relative:
        return None

    path = (BASE_DIR / relative).resolve()

    try:
        path.relative_to(BASE_DIR.resolve())
    except ValueError:
        return None

    return str(path) if path.is_file() else None


def parse_list(value):
    """Parse a list stored as JSON/Python-list text or plain text."""
    value = str(value).strip()
    if not value:
        return []

    if value.startswith("[") and value.endswith("]"):
        import ast
        try:
            result = ast.literal_eval(value)
            if isinstance(result, list):
                return [str(item).strip() for item in result if str(item).strip()]
        except (ValueError, SyntaxError):
            pass

    if "\n" in value:
        return [item.strip(" -•\t") for item in value.splitlines() if item.strip()]

    if ";" in value:
        return [item.strip() for item in value.split(";") if item.strip()]

    return [value]


def go_to(page, recipe_id=None):
    st.session_state["page"] = page
    print(f"Navigating to {page} page.")
    if recipe_id is not None:
        print(f"Selecting recipe ID: {recipe_id}")
        st.session_state["selected_recipe_id"] = str(recipe_id)
    st.rerun()


def get_recipe(recipe_id):
    if recipe_id is None or str(recipe_id).strip() == "":
        return None

    matches = recipes[
        recipes["recipe_id"].astype(str) == str(recipe_id)
    ]

    return None if matches.empty else matches.iloc[0]


def recipe_card(row, key_prefix="card"):
    rid = str(row["recipe_id"])
    img = image_for(row)

    with st.container(border=True):
        if img:
            st.image(img, width='stretch')
        else:
            st.markdown( 
                '<div class="no-photo">🍲<br><span>Something delicious</span></div>',
                unsafe_allow_html=True,
            )

        st.markdown(
            f'<div class="recipe-title">{safe_text(row["recipe_title"])}</div>',
            unsafe_allow_html=True,
        )
        st.caption("Recipe inspiration")

        left, right = st.columns([3, 1])

        with left:
            print(f"Navigating to Recipe page for recipe ID: {rid}")
            if st.button(
                "View recipe ↗",
                key=f"{key_prefix}_view_{rid}",
                width='stretch',
            ):
                print(f"Navigating to Recipe page for recipe ID: {rid}")
                go_to("Recipe", rid)

        # with right:
        #     saved = rid in st.session_state["saved_recipes"]

        #     if st.button(
        #         "♥" if saved else "♡",
        #         key=f"{key_prefix}_save_{rid}",
        #         help="Remove from saved" if saved else "Save recipe",
        #     ):
        #         if saved:
        #             st.session_state["saved_recipes"].remove(rid)
        #         else:
        #             st.session_state["saved_recipes"].append(rid)
        #         st.rerun()


# =========================================================
# STYLING
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@500;600;700;800&display=swap');

:root {
    --cream: #faf8f1;
    --green: #254b36;
    --green-light: #e5ecdf;
    --yellow: #f4d66e;
    --ink: #25352b;
    --muted: #788075;
}

.stApp {
    background: var(--cream);
    color: var(--ink);
    font-family: 'DM Sans', sans-serif;
}

.block-container {
    max-width: 1320px;
    padding-top: 1.2rem;
    padding-bottom: 4rem;
}

h1, h2, h3 {
    color: var(--green);
    font-family: 'Playfair Display', Georgia, serif !important;
}

h1 { letter-spacing: -1.5px; }

[data-testid="stHeader"] { background: transparent; }

.brand {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 2rem;
    font-weight: 800;
    color: var(--green);
    letter-spacing: -1.2px;
}

.brand span { color: #d77b5c; }

.brand-sub {
    color: var(--muted);
    font-size: .77rem;
    margin-top: -5px;
}

.eyebrow {
    font-size: .72rem;
    font-weight: 700;
    letter-spacing: 2.2px;
    text-transform: uppercase;
    color: #54734e;
}

.hero {
    background: var(--green-light);
    border-radius: 28px;
    padding: clamp(24px, 4vw, 54px);
    margin: 18px 0 28px;
}

.hero h1 {
    font-size: clamp(2.5rem, 5.5vw, 4.5rem);
    line-height: 1.04;
    margin: 15px 0;
}

.hero p {
    font-size: 1rem;
    color: #596c5b;
    max-width: 450px;
    line-height: 1.8;
}

.hero-art {
    background: var(--yellow);
    border-radius: 48% 52% 45% 55%;
    min-height: 245px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 15px;
}

.hero-art .food-emoji {
    font-size: clamp(5rem, 10vw, 8rem);
    line-height: 1.2;
}

.hero-art p {
    color: var(--green);
    font-weight: 700;
    margin: 8px 0 0;
}

.section-heading {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: clamp(1.7rem, 3vw, 2.4rem);
    font-weight: 700;
    color: var(--green);
    letter-spacing: -.7px;
}

.section-note {
    color: var(--muted);
    margin-top: -6px;
    margin-bottom: 18px;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    border-color: #e9e5da;
    border-radius: 20px;
    background: #fffefb;
}

div[data-testid="stImage"] img {
    border-radius: 14px;
    object-fit: cover;
}

.recipe-title {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--green);
    line-height: 1.3;
    min-height: 3rem;
    margin: 8px 0;
}

.no-photo {
    min-height: 160px;
    border-radius: 14px;
    background: var(--green-light);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    font-size: 3rem;
    text-align: center;
}

.no-photo span {
    font-size: .8rem;
    color: #536354;
}

div.stButton > button {
    border-radius: 999px;
    min-height: 42px;
    border: 1px solid #dfe4d8;
    background: #fffefb;
    color: var(--green);
    font-weight: 600;
    transition: all .15s ease;
}

div.stButton > button:hover {
    border-color: var(--green);
    background: var(--green);
    color: white;
}

div.stButton > button[kind="primary"] {
    background: var(--green);
    color: white;
    border: none;
}

div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div {
    border-radius: 14px;
    border-color: #e1dfd5;
    background: #fffefb;
}

.footer {
    text-align: center;
    color: #818579;
    font-size: .8rem;
    padding-top: 28px;
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# NAVIGATION
# =========================================================
nav1, nav2, nav3, nav4 = st.columns([2, 1, 1, 1])

with nav1:
    st.markdown(
        '<div class="brand">nourish<span>.</span></div>'
        '<div class="brand-sub">A little inspiration for your plate</div>',
        unsafe_allow_html=True,
    )

with nav2:
    if st.button("Discover", width='stretch'):
        go_to("Discover")

with nav3:
    if st.button("Explore all", width='stretch'):
        go_to("Explore")

# with nav4:
#     if st.button(
#         f"♡ Saved ({len(st.session_state['saved_recipes'])})",
#         width='stretch',
#     ):
#         go_to("Saved")

# st.markdown("---")


# =========================================================
# DISCOVER
# =========================================================
if st.session_state["page"] == "Discover":
    left, right = st.columns([1.5, 1], gap="large")

    with left:
        st.markdown("""
        <div class="hero">
            <div class="eyebrow">Good food, new discoveries</div>
            <h1>Your next favourite meal is out there.</h1>
            <p>
                Craving something comforting? Curious about another cuisine?
                Find a recipe that makes you excited to get into the kitchen.
            </p>
        </div>
        """, unsafe_allow_html=True)

        search = st.text_input(
            "Search recipes",
            value=st.session_state["search_query"],
            placeholder="Try pasta, tomatoes, chicken...",
            label_visibility="collapsed",
        )
        st.session_state["search_query"] = search

        if st.button("Explore recipes →", type="primary"):
            go_to("Explore")

    with right:
        st.markdown("""
        <div class="hero-art">
            <div class="food-emoji">🥗 🍜 🍓</div>
            <p>Something delicious is waiting.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### A little adventure?")
        st.write("Let chance choose what you cook next.")

        if st.button("🎲 Pick something for me", type="primary",
                     width='stretch'):
            go_to("Surprise Me")

#     st.markdown(
#         '<div class="section-heading">A little inspiration</div>',
#         unsafe_allow_html=True,
#     )
#     st.markdown(
#         '<div class="section-note">A few dishes to get you thinking.</div>',
#         unsafe_allow_html=True,
#     )

#     # Show a new random selection on each page rerun.
# if "featured_recipe_ids" not in st.session_state:
#     st.session_state["featured_recipe_ids"] = (
#         recipes.sample(n=min(4, len(recipes)))["recipe_id"].tolist()
#     )

#     featured = (
#         recipes.set_index("recipe_id")
#         .loc[st.session_state["featured_recipe_ids"]]
#         .reset_index()
#     )
#     cols = st.columns(4, gap="medium")
#     for i, (_, row) in enumerate(featured.iterrows()):
#         with cols[i]:
#             recipe_card(row, "featured")

#     st.markdown("")
#     promo_left, promo_right = st.columns([1.5, 1], gap="medium")

#     with promo_left:
#         st.markdown("""
#         <div style="background:#254b36;color:#fffefb;padding:28px;border-radius:22px;">
#             <div style="font-size:.72rem;letter-spacing:2px;text-transform:uppercase;color:#d6e5c9;">
#                 The joy of trying something new
#             </div>
#             <div style="font-family:'Playfair Display',serif;font-size:2rem;margin:12px 0;">
#                 Same kitchen.<br>New possibilities.
#             </div>
#             <div style="color:#e3eadf;">
#                 You don't need a special occasion to discover a new favourite.
#             </div>
#         </div>
#         """, unsafe_allow_html=True)

#     with promo_right:
#         st.markdown("""
#         <div style="background:#f4d66e;padding:28px;border-radius:22px;min-height:160px;">
#             <div style="font-size:2.5rem;">🎲</div>
#             <div style="font-family:'Playfair Display',serif;font-size:1.6rem;color:#254b36;">
#                 Can't decide?
#             </div>
#             <div style="color:#536354;">Leave dinner to fate.</div>
#         </div>
#         """, unsafe_allow_html=True)

#         if st.button("Surprise me →", width='stretch'):
#             go_to("Surprise Me")


# =========================================================
# EXPLORE
# =========================================================
elif st.session_state["page"] == "Explore":
    st.markdown(
        '<div class="eyebrow">Browse the collection</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-heading">Find something delicious.</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-note">Search by dish or ingredient.</div>',
        unsafe_allow_html=True,
    )

    query = st.text_input(
        "Search recipes",
        value=st.session_state["search_query"],
        placeholder="e.g. tomato, noodles, chocolate",
    )
    st.session_state["search_query"] = query

    sort_order = st.selectbox(
        "Sort recipes",
        ["Random discovery", "A–Z", "Z–A"],
    )
    image_filter = st.checkbox("Only show recipes with photos")

    results = recipes.copy()

    if query.strip():
        results = results[
            results["search_text"].str.contains(
                query.strip().lower(), regex=False, na=False
            )
        ]

    if image_filter:
        results = results[
            results["image_path"].apply(
                lambda x: bool(x.strip()) and (BASE_DIR / x).is_file()
            )
        ]

    if sort_order == "A–Z":
        results = results.sort_values("recipe_title")
    elif sort_order == "Z–A":
        results = results.sort_values("recipe_title", ascending=False)
    elif len(results) > 1:
        results = results.sample(frac=1, random_state=42)

    st.caption(f"{len(results):,} recipes to explore")

    if results.empty:
        st.info("No recipes found. Try another search.")
    else:
        page_size = 24
        page_count = max(1, (len(results) + page_size - 1) // page_size)

        page_num = st.number_input(
            "Gallery page",
            min_value=1,
            max_value=page_count,
            value=1,
            step=1,
        )

        start = (int(page_num) - 1) * page_size
        current = results.iloc[start:start + page_size]

        cols = st.columns(4, gap="medium")
        for i, (_, row) in enumerate(current.iterrows()):
            with cols[i % 4]:
                recipe_card(row, f"explore_{page_num}")


# =========================================================
# SURPRISE ME
# =========================================================
elif st.session_state["page"] == "Surprise Me":
    st.markdown(
        '<div class="eyebrow">A little culinary adventure</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-heading">Let fate pick your next meal.</div>',
        unsafe_allow_html=True,
    )
    st.write(
        "No endless scrolling. No overthinking. Just a recipe you might "
        "never have picked yourself."
    )

    with st.container(border=True):
        query = st.text_input(
            "Optional: include a dish or ingredient",
            placeholder="e.g. rice, beans, tomato",
            key="surprise_query",
        )
        require_image = st.checkbox(
            "Only show recipes with a photo",
            value=True,
        )

        if st.button(
            "🎲 Surprise me!",
            type="primary",
            width='stretch',
        ):
            candidates = recipes.copy()

            if query.strip():
                candidates = candidates[
                    candidates["search_text"].str.contains(
                        query.strip().lower(), regex=False, na=False
                    )
                ]

            if require_image:
                candidates = candidates[
                    candidates["image_path"].apply(
                        lambda x: bool(x.strip())
                        and (BASE_DIR / x).is_file()
                    )
                ]

            previous = st.session_state["last_surprise_id"]

            if len(candidates) > 1:
                candidates = candidates[
                    candidates["recipe_id"] != previous
                ]

            if candidates.empty:
                st.session_state["surprise_result_id"] = ""
                st.warning(
                    "No recipes match those preferences. Try removing a filter."
                )
            else:
                picked = candidates.sample(n=1).iloc[0]
                st.session_state["last_surprise_id"] = picked["recipe_id"]
                st.session_state["surprise_result_id"] = picked["recipe_id"]

    picked_id = st.session_state["surprise_result_id"]
    picked = get_recipe(picked_id) if picked_id else None

    if picked is not None:
        st.markdown("")
        st.markdown("## ✨ Your surprise recipe")

        left, right = st.columns([1.1, 1], gap="large")

        with left:
            img = image_for(picked)
            if img:
                st.image(img, width='stretch')
            else:
                st.markdown("### 🍲 Image unavailable")

        with right:
            st.markdown(
                '<div class="eyebrow">Your next kitchen adventure</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div class="section-heading">{safe_text(picked["recipe_title"])}</div>',
                unsafe_allow_html=True,
            )
            if st.button("Open full recipe →", type="primary"):
                go_to("Recipe", picked["recipe_id"])

            if st.button("Try another one ↻"):
                st.session_state["surprise_result_id"] = ""
                st.rerun()


# =========================================================
# RECIPE DETAILS
# =========================================================
elif st.session_state["page"] == "Recipe":
    row = get_recipe(st.session_state["selected_recipe_id"])

    if row is None:
        st.warning("Choose a recipe from Discover or Explore.")
        if st.button("Back to Discover"):
            go_to("Discover")
    else:
        if st.button("← Back to Discover"):
            go_to("Discover")

        left, right = st.columns([1.1, 1], gap="large")

        with left:
            img = image_for(row)
            if img:
                st.image(img, width='stretch')
            else:
                st.markdown("### 🍲 Image unavailable")

        with right:
            st.markdown(
                '<div class="eyebrow">Something worth making</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div class="section-heading">{safe_text(row["recipe_title"])}</div>',
                unsafe_allow_html=True,
            )

            rid = str(row["recipe_id"])
            is_saved = rid in st.session_state["saved_recipes"]

            # if st.button(
            #     "♥ Remove from saved" if is_saved else "♡ Save this recipe",
            #     type="primary",
            # ):
            #     if is_saved:
            #         st.session_state["saved_recipes"].remove(rid)
            #     else:
            #         st.session_state["saved_recipes"].append(rid)
            #     st.rerun()

        st.markdown("---")
        ingredient_col, instruction_col = st.columns([.8, 1.2], gap="large")

        with ingredient_col:
            st.markdown("## 🥬 Ingredients")
            items = parse_list(row["ingredients"])

            if items:
                for item in items:
                    st.markdown(f"- {item}")
            else:
                st.write("No ingredient list available.")

        with instruction_col:
            st.markdown("## 👩🏽‍🍳 Let's make it")
            steps = parse_list(row["directions"])

            if steps:
                for index, step in enumerate(steps, start=1):
                    st.markdown(f"**Step {index}**")
                    st.write(step)
            else:
                st.write("No cooking instructions available.")


# =========================================================
# SAVED RECIPES
# =========================================================
elif st.session_state["page"] == "Saved":
    st.markdown(
        '<div class="eyebrow">Your personal collection</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-heading">Recipes to come back to. ♡</div>',
        unsafe_allow_html=True,
    )

    saved_ids = st.session_state["saved_recipes"]
    saved = recipes[recipes["recipe_id"].isin(saved_ids)]

    if saved.empty:
        st.info(
            "Your collection is waiting to be filled. "
            "Browse recipes and tap ♡ to save the ones you love."
        )
        if st.button("Find recipes →", type="primary"):
            go_to("Explore")
    else:
        cols = st.columns(4, gap="medium")
        for i, (_, row) in enumerate(saved.iterrows()):
            with cols[i % 4]:
                recipe_card(row, "saved")


# =========================================================
# FOOTER
# =========================================================
st.markdown("---")
st.markdown(
    '<div class="footer">'
    'Made for curious appetites. 🍋<br>'
    'Recipe content and images come from the imported dataset. '
    'Check source licensing and attribution before publishing.'
    '</div>',
    unsafe_allow_html=True,
)
