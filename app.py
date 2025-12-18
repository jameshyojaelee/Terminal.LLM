import streamlit as st
import json
from datetime import datetime
from html import escape
import sys
from typing import Optional
from data_fetcher import get_market_data

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Terminal.LLM",
    page_icon="⚡", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- STYLE ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=JetBrains+Mono:wght@400;700&display=swap');

    /* Global Theme Overrides */
    .stApp {
        background-color: #050505;
        background-image: 
            radial-gradient(circle at 15% 50%, rgba(76, 29, 149, 0.08), transparent 25%),
            radial-gradient(circle at 85% 30%, rgba(6, 182, 212, 0.08), transparent 25%);
        font-family: 'Outfit', sans-serif;
    }

    h1, h2, h3, h4, h5, h6, .stMarkdown, .stButton, div {
        font-family: 'Outfit', sans-serif !important;
    }
    
    code, .stCodeBlock {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0a0a0a;
        border-right: 1px solid rgba(255,255,255,0.08);
    }
    
    /* Block Spacing */
    .block-container { 
        padding-top: 2rem; 
        padding-bottom: 4rem; 
        max-width: 1200px;
    }

    /* HERO SECTION */
    .tllm-hero {
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        padding: 2.5rem;
        border-radius: 24px;
        background: linear-gradient(135deg, rgba(255,255,255,0.03) 0%, rgba(255,255,255,0.01) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 20px 40px -10px rgba(0,0,0,0.5);
        backdrop-filter: blur(12px);
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
    }
    
    .tllm-hero::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
    }

    .tllm-title { 
        font-size: 3.5rem; 
        font-weight: 800; 
        letter-spacing: -0.04em; 
        background: linear-gradient(120deg, #fff, #94a3b8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1.1;
        margin-bottom: 0.5rem;
    }
    
    .tllm-subtitle { 
        font-size: 1.1rem; 
        color: #94a3b8; 
        font-weight: 400;
        max-width: 600px;
        line-height: 1.6;
    }
    
    .tllm-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 999px;
        background: rgba(124, 58, 237, 0.2);
        color: #c4b5fd;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-bottom: 1rem;
        border: 1px solid rgba(124, 58, 237, 0.3);
    }

    /* FRESHNESS CHIPS */
    .freshness-container {
        display: flex;
        flex-wrap: wrap;
        gap: 0.75rem;
        margin-top: 1rem;
        align-items: center;
    }
    
    .status-pill {
        display: flex;
        align-items: center;
        gap: 6px;
        padding: 6px 12px;
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px;
        font-size: 0.8rem;
        color: #94a3b8;
        transition: all 0.2s ease;
    }
    
    .status-pill:hover {
        background: rgba(255,255,255,0.06);
        border-color: rgba(255,255,255,0.1);
    }
    
    .status-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background-color: #10b981;
        box-shadow: 0 0 8px rgba(16, 185, 129, 0.4);
    }

    /* MARKET TAPE CARDS */
    .market-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
        gap: 1rem;
        margin: 1.5rem 0 2.5rem 0;
    }
    
    .ticker-card {
        background: rgba(20, 20, 22, 0.6);
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 16px;
        padding: 1rem;
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        transition: transform 0.2s, background 0.2s;
        cursor: default;
    }
    
    .ticker-card:hover {
        transform: translateY(-2px);
        background: rgba(255,255,255,0.04);
        border-color: rgba(255,255,255,0.1);
    }
    
    .ticker-name {
        font-size: 0.9rem;
        font-weight: 700;
        color: #e2e8f0;
        margin-bottom: 0.25rem;
    }
    
    .ticker-val {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.95rem;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 6px;
    }
    
    .val-up { color: #4ade80; background: rgba(74, 222, 128, 0.1); }
    .val-down { color: #f87171; background: rgba(248, 113, 113, 0.1); }
    .val-flat { color: #94a3b8; background: rgba(148, 163, 184, 0.1); }

    /* Buttons */
    div.stButton > button {
        border-radius: 12px;
        font-weight: 600;
        height: 3.2rem;
        background: linear-gradient(135deg, #4f46e5 0%, #3b82f6 100%);
        border: none;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
        transition: all 0.3s ease;
    }
    
    div.stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(79, 70, 229, 0.4);
    }

    /* LLM Report Typography */
    .report-container {
        background: #0a0a0a;
        padding: 2rem;
        border-radius: 16px;
        border: 1px solid rgba(255,255,255,0.06);
    }
    </style>
    """,
    unsafe_allow_html=True,
	)

# --- MODEL LISTING HELPERS ---
GEMINI_FALLBACK_MODELS = [
    "gemini-3-flash-preview",
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-2.0-flash-exp",
    "gemini-flash-latest",
    "gemini-pro-latest",
]

OPENAI_FALLBACK_MODELS = [
    "gpt-4o",
    "gpt-4o-mini",
]


def _dedupe_keep_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            out.append(item)
    return out


def _normalize_gemini_model_name(name: str) -> str:
    return name.removeprefix("models/").strip()


def _list_gemini_models(api_key: str) -> list[str]:
    import google.generativeai as genai

    genai.configure(api_key=api_key)
    models: list[str] = []
    for m in genai.list_models():
        supported = getattr(m, "supported_generation_methods", []) or []
        if "generateContent" not in supported:
            continue
        model_name = getattr(m, "name", None)
        if isinstance(model_name, str) and model_name.strip():
            models.append(_normalize_gemini_model_name(model_name))
    return _dedupe_keep_order(models)


def _list_openai_models(api_key: str) -> list[str]:
    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    page = client.models.list()
    data = getattr(page, "data", None)
    if data is None:
        data = list(page)

    model_ids: list[str] = []
    for m in data:
        model_id = getattr(m, "id", None)
        if isinstance(model_id, str) and model_id.strip():
            model_ids.append(model_id)
    return _dedupe_keep_order(sorted(model_ids))


def _safe_index(options: list[str], preferred: str) -> int:
    try:
        return options.index(preferred)
    except ValueError:
        return 0


# --- SIDEBAR (Settings) ---
with st.sidebar:
    st.markdown("### ⚡ Terminal.LLM")
    st.caption("Live Market Intelligence")
    st.divider()
    st.markdown("#### ⚙️ Configuration")

    provider = st.radio(
        "Intelligence Provider",
        ["Gemini", "OpenAI"],
        horizontal=True,
        help="Choose your AI backend.",
    )

    provider_ready = True
    if provider == "Gemini":
        try:
            import google.generativeai  # noqa: F401
        except ModuleNotFoundError:
            provider_ready = False
            st.warning(
                "Gemini SDK not installed. Install it with:\n"
                f"  {sys.executable} -m pip install -U google-generativeai",
                icon="⚠️",
            )
    else:
        try:
            from openai import OpenAI  # noqa: F401
        except Exception:
            provider_ready = False
            st.warning(
                "OpenAI SDK not installed (or too old). Install/upgrade it with:\n"
                f"  {sys.executable} -m pip install -U openai",
                icon="⚠️",
            )

    # API Key Input (Secure)
    if provider == "Gemini":
        api_key = st.text_input("AI Studio Key", type="password", key="gemini_api_key")
        if "gemini_models" not in st.session_state:
            st.session_state.gemini_models = []

        if st.button(
            "🔎 Load Gemini models",
            use_container_width=True,
            disabled=(not api_key) or (not provider_ready),
            help="Fetches your currently available Gemini models and populates the dropdowns.",
        ):
            with st.spinner("Loading Gemini models..."):
                try:
                    st.session_state.gemini_models = _list_gemini_models(api_key)
                except Exception as e:
                    st.error(f"Could not load Gemini models: {e}")

        preferred_debrief = st.session_state.get("gemini_debrief_model", "gemini-2.5-flash")
        preferred_chat = st.session_state.get("gemini_chat_model", "gemini-2.5-flash")
        model_options = _dedupe_keep_order(
            [preferred_debrief, preferred_chat]
            + (st.session_state.gemini_models or [])
            + GEMINI_FALLBACK_MODELS
        )

        st.session_state.gemini_debrief_model = st.selectbox(
            "Model (Debrief)",
            options=model_options,
            index=_safe_index(model_options, preferred_debrief),
        )
        st.session_state.gemini_chat_model = st.selectbox(
            "Model (Chat)",
            options=model_options,
            index=_safe_index(model_options, preferred_chat),
        )

        debrief_model = st.session_state.gemini_debrief_model
        chat_model = st.session_state.gemini_chat_model
    else:
        api_key = st.text_input("OpenAI Key", type="password", key="openai_api_key")
        if "openai_models" not in st.session_state:
            st.session_state.openai_models = []

        show_all_openai_models = st.checkbox(
            "Show all OpenAI models",
            value=False,
            help="If off, the list is filtered to common chat-capable models (gpt-* and o*).",
        )

        if st.button(
            "🔎 Load OpenAI models",
            use_container_width=True,
            disabled=(not api_key) or (not provider_ready),
            help="Fetches your currently available OpenAI models and populates the dropdowns.",
        ):
            with st.spinner("Loading OpenAI models..."):
                try:
                    st.session_state.openai_models = _list_openai_models(api_key)
                except Exception as e:
                    st.error(f"Could not load OpenAI models: {e}")

        preferred_debrief = st.session_state.get("openai_debrief_model", "gpt-4o")
        preferred_chat = st.session_state.get("openai_chat_model", "gpt-4o-mini")
        loaded = st.session_state.openai_models or []
        if not show_all_openai_models and loaded:
            loaded = [m for m in loaded if m.startswith(("gpt-", "o", "chatgpt"))]

        model_options = _dedupe_keep_order([preferred_debrief, preferred_chat] + loaded + OPENAI_FALLBACK_MODELS)

        st.session_state.openai_debrief_model = st.selectbox(
            "Model (Debrief)",
            options=model_options,
            index=_safe_index(model_options, preferred_debrief),
        )
        st.session_state.openai_chat_model = st.selectbox(
            "Model (Chat)",
            options=model_options,
            index=_safe_index(model_options, preferred_chat),
        )

        debrief_model = st.session_state.openai_debrief_model
        chat_model = st.session_state.openai_chat_model

    # Watchlist Input
    default_tickers = "NVDA, TSLA, PLTR, AAPL"
    watchlist_input = st.text_area("Watchlist", value=default_tickers, height=100)
    watchlist = [x.strip().upper() for x in watchlist_input.split(",") if x.strip()]

    # Risk Profile
    risk_profile = st.select_slider(
        "Risk Appetite",
        options=["Conservative", "Balanced", "Aggressive", "YOLO"],
        value="Balanced",
    )

    st.divider()
    analyze_clicked = st.button(
        "Generate Briefing",
        type="primary",
        use_container_width=True,
        disabled=(not api_key) or (not provider_ready),
    )
    st.caption(f"v1.2.0 • {provider} Backend")

# --- MAIN LAYOUT ---

# Hero
st.markdown(
    """
<div class="tllm-hero">
  <div class="tllm-badge">Market Intelligence Unit</div>
  <div class="tllm-title">Terminal<span style="opacity:0.4">.LLM</span></div>
  <div class="tllm-subtitle">Real-time executive summary of US equities, crypto, and macro movements. Powered by generative AI.</div>
</div>
""",
    unsafe_allow_html=True,
)

if not api_key:
    st.warning("⚠️ Access Restricted: Please provide a valid API key in the sidebar to initialize the terminal.")

def _format_iso_local(ts: Optional[str]) -> Optional[str]:
    if not ts:
        return None
    try:
        dt = datetime.fromisoformat(ts)
        return dt.astimezone().strftime("%H:%M %p")
    except Exception:
        return ts

def _render_data_freshness(ctx: dict) -> None:
    retrieved_at = _format_iso_local(ctx.get("retrieved_at"))
    source_as_of = ctx.get("source_as_of") or {}
    prices_as_of = _format_iso_local(source_as_of.get("prices_as_of"))
    news_as_of = _format_iso_local(source_as_of.get("news_as_of"))

    parts = []
    if retrieved_at: parts.append(f"Retrieved: {retrieved_at}")
    if prices_as_of: parts.append(f"Prices: {prices_as_of}")
    if news_as_of: parts.append(f"News: {news_as_of}")
    
    if not parts: return

    # HTML Generator for pills
    pills_html = "".join(
        f'<div class="status-pill"><div class="status-dot"></div>{p}</div>' 
        for p in parts
    )
    st.markdown(f'<div class="freshness-container">{pills_html}</div>', unsafe_allow_html=True)

def _render_market_tape(ctx: dict) -> None:
    market_context = ctx.get("market_context") or {}
    user_profile = ctx.get("user_profile") or {}
    watchlist = user_profile.get("watchlist") or []
    if not isinstance(watchlist, list):
        watchlist = []

    # Priority Tickers + Watchlist
    tape_tickers = ["SPY", "QQQ", "BTC-USD"] + [t for t in watchlist if isinstance(t, str)]
    # Unique only (preserve order)
    seen = set()
    unique_tape = [x for x in tape_tickers if not (x in seen or seen.add(x))]

    cards_html = ""
    for ticker in unique_tape:
        val_str = market_context.get(ticker, "0.00%")
        
        # Determine color based on value
        color_class = "val-flat"
        try:
            val_float = float(val_str.replace("%", "").replace("+", ""))
            if val_float > 0: color_class = "val-up"
            elif val_float < 0: color_class = "val-down"
        except:
            pass
            
        cards_html += (
            f'<div class="ticker-card">'
            f'<div class="ticker-name">{ticker}</div>'
            f'<div class="ticker-val {color_class}">{val_str}</div>'
            f'</div>'
        )
        
    st.markdown(f'<div class="market-grid">{cards_html}</div>', unsafe_allow_html=True)

def _call_llm(provider: str, api_key: str, model: str, *, instructions: str, user_input: str) -> str:
    if provider == "Gemini":
        try:
            import google.generativeai as genai
        except ModuleNotFoundError:
            st.error(
                "Gemini SDK not found in this Python environment.\n"
                "Install it with:\n"
                f"  {sys.executable} -m pip install -U google-generativeai"
            )
            return ""

        genai.configure(api_key=api_key)
        response = genai.GenerativeModel(model).generate_content(f"SYSTEM: {instructions}\n\n{user_input}")
        return response.text or ""

    if provider == "OpenAI":
        try:
            from openai import OpenAI
        except ModuleNotFoundError:
            st.error(
                "OpenAI SDK not found in this Python environment.\n"
                "Install/upgrade it with:\n"
                f"  {sys.executable} -m pip install -U openai"
            )
            return ""

        client = OpenAI(api_key=api_key)
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": instructions},
                    {"role": "user", "content": user_input}
                ]
            )
        except Exception as e:
            raise RuntimeError(f"OpenAI Error: {e}")
            
        return response.choices[0].message.content or ""

    raise RuntimeError(f"Unsupported provider: {provider}")

# Session State
if "debrief" not in st.session_state:
    st.session_state.debrief = None
if "context_data" not in st.session_state:
    st.session_state.context_data = None
if "provider" not in st.session_state:
    st.session_state.provider = provider
elif st.session_state.provider != provider:
    st.session_state.provider = provider
    st.session_state.debrief = None

# Slots for live updates
freshness_slot = st.empty()
tape_slot = st.empty()

# Render existing state
if st.session_state.context_data:
    with freshness_slot.container():
        _render_data_freshness(st.session_state.context_data)
    with tape_slot.container():
        _render_market_tape(st.session_state.context_data)

# Logic
if analyze_clicked:
    with st.spinner("📡 Establishing secure link to market feeds..."):
        # 1. GET DATA
        raw_data = get_market_data(watchlist)
        st.session_state.context_data = raw_data
        
        # Render updates
        with freshness_slot.container():
            _render_data_freshness(raw_data)
        with tape_slot.container():
            _render_market_tape(raw_data)
        
        # 2. PROMPT MODEL
        system_instruction = f"""
        ROLE: Wall Street Chief Market Strategist.
        TASK: Synthesize a high-precision morning briefing from the provided data.
        USER PROFILE: Risk Profile = {risk_profile}
        
        FORMAT GUIDELINES:
        - Style: Bloomberg Terminal / Axios Pro.
        - Tone: Professional, direct, actionable. No fluff.
        - Structure:
          1. 🚨 **Market Signal** (One sentence mood summary)
          2. 🌍 **Macro & Big Tech** (SPY, QQQ, Key Drivers)
          3. 🎯 **Watchlist Alpha** (Significant moves in user's list)
          4. 🔮 **Forward Outlook** (What to watch next 24h)
        """
        try:
            st.session_state.debrief = _call_llm(
                provider,
                api_key,
                debrief_model,
                instructions=system_instruction,
                user_input=f"DATA: {json.dumps(raw_data)}",
            )
        except Exception as e:
            st.error(f"Analysis Failed: {str(e)}")

# Display Report
if st.session_state.debrief:
    st.markdown('<div class="report-container">', unsafe_allow_html=True)
    st.markdown("### 📝 Executive Briefing")
    st.markdown(st.session_state.debrief)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("💬 Analyst Chat")
    st.caption("Ask follow-up questions on specific tickers or macro trends.")
    
    user_q = st.chat_input("E.g., 'Why is NVDA down?' or 'Correlation between BTC and SPY?'")
    
    if user_q:
        with st.chat_message("user", avatar="👤"):
            st.write(user_q)
            
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Analyzing..."):
                followup_instruction = f"""
                ROLE: Senior Analyst.
                TASK: Answer the client's question based on the market data and prior brief.
                CONTEXT: Risk={risk_profile}.
                Keep it concise and data-backed.
                """
                try:
                    answer_text = _call_llm(
                        provider,
                        api_key,
                        chat_model,
                        instructions=followup_instruction,
                        user_input=(
                            f"DATA: {json.dumps(st.session_state.context_data)}\n"
                            f"BRIEF: {st.session_state.debrief}\n"
                            f"Q: {user_q}"
                        ),
                    )
                    st.write(answer_text)
                except Exception as e:
                    st.error(str(e))
