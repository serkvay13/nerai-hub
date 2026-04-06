# ══════════════════════════════════════════════════════════════════
# NERAI — REPLACEMENT render_home() FUNCTION
# ══════════════════════════════════════════════════════════════════
#
# INSTRUCTIONS:
# 1. Open gdelt_dashboard.py on GitHub
# 2. Find the existing render_home() function (starts at line ~1753)
# 3. DELETE everything from "def render_home():" until the NEXT
#    function definition (line ~2007)
# 4. PASTE this entire function in its place
# 5. Commit & deploy
#
# This replaces:
#   - Old Three.js 3D globe → new AI+Geopolitical canvas hero
#   - Plain text KPIs → premium glassmorphism KPI cards
#   - Basic module cards → premium styled cards
#   - All navigation buttons are PRESERVED exactly as before
# ══════════════════════════════════════════════════════════════════

def render_home():
    """Home page — Premium world-class hero + KPIs + module navigation."""

    # ── 1. HERO: AI + Geopolitical Network Visualization ──
    # (from nerai_premium_css.py — replaces old Three.js globe)
    nerai_premium_css.inject_home_hero()

    # ── 2. PREMIUM KPI SECTION ──
    st.markdown("""
    <div style="
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin: -0.5rem 0 2rem 0;
        padding: 0 4px;
    ">
        <div style="
            background: linear-gradient(135deg, rgba(0,212,255,0.06) 0%, rgba(10,14,23,0.95) 100%);
            border: 1px solid rgba(0,212,255,0.12);
            border-radius: 14px;
            padding: 24px 20px;
            text-align: center;
            backdrop-filter: blur(12px);
            position: relative;
            overflow: hidden;
        ">
            <div style="position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,rgba(0,212,255,0.25),transparent);"></div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:2rem;font-weight:700;color:#00d4ff;margin-bottom:4px;text-shadow:0 0 20px rgba(0,212,255,0.15);">60</div>
            <div style="font-family:'Inter',sans-serif;font-size:0.65rem;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:#6b7f99;">Countries</div>
        </div>
        <div style="
            background: linear-gradient(135deg, rgba(0,212,255,0.06) 0%, rgba(10,14,23,0.95) 100%);
            border: 1px solid rgba(0,212,255,0.12);
            border-radius: 14px;
            padding: 24px 20px;
            text-align: center;
            backdrop-filter: blur(12px);
            position: relative;
            overflow: hidden;
        ">
            <div style="position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,rgba(0,212,255,0.25),transparent);"></div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:2rem;font-weight:700;color:#00d4ff;margin-bottom:4px;text-shadow:0 0 20px rgba(0,212,255,0.15);">40</div>
            <div style="font-family:'Inter',sans-serif;font-size:0.65rem;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:#6b7f99;">Risk Topics</div>
        </div>
        <div style="
            background: linear-gradient(135deg, rgba(0,212,255,0.06) 0%, rgba(10,14,23,0.95) 100%);
            border: 1px solid rgba(0,212,255,0.12);
            border-radius: 14px;
            padding: 24px 20px;
            text-align: center;
            backdrop-filter: blur(12px);
            position: relative;
            overflow: hidden;
        ">
            <div style="position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,rgba(0,212,255,0.25),transparent);"></div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:2rem;font-weight:700;color:#00d4ff;margin-bottom:4px;text-shadow:0 0 20px rgba(0,212,255,0.15);">354</div>
            <div style="font-family:'Inter',sans-serif;font-size:0.65rem;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:#6b7f99;">Days of Data</div>
        </div>
        <div style="
            background: linear-gradient(135deg, rgba(0,212,255,0.06) 0%, rgba(10,14,23,0.95) 100%);
            border: 1px solid rgba(0,212,255,0.12);
            border-radius: 14px;
            padding: 24px 20px;
            text-align: center;
            backdrop-filter: blur(12px);
            position: relative;
            overflow: hidden;
        ">
            <div style="position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,rgba(0,212,255,0.25),transparent);"></div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:2rem;font-weight:700;color:#00d4ff;margin-bottom:4px;text-shadow:0 0 20px rgba(0,212,255,0.15);">2,400</div>
            <div style="font-family:'Inter',sans-serif;font-size:0.65rem;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:#6b7f99;">Data Points</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Status bar ──
    st.markdown("""
    <div style="
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 20px;
        padding: 10px 24px;
        margin: 0 auto 2rem auto;
        max-width: 600px;
        background: rgba(17,24,39,0.6);
        border: 1px solid rgba(0,212,255,0.08);
        border-radius: 30px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.65rem;
        letter-spacing: 1.5px;
        color: #6b7f99;
    ">
        <span style="color:#00e676;font-weight:600;">● LIVE</span>
        <span style="color:rgba(0,212,255,0.15);">│</span>
        <span>GDELT PROJECT</span>
        <span style="color:rgba(0,212,255,0.15);">│</span>
        <span>LAST UPDATE: RECENT</span>
        <span style="color:rgba(0,212,255,0.15);">│</span>
        <span style="color:#00e676;">✓ ONLINE</span>
    </div>
    """, unsafe_allow_html=True)

    # ── 3. MODULE NAVIGATION SECTION ──
    st.markdown("""
    <div style="
        display: flex;
        align-items: center;
        gap: 16px;
        margin: 1.5rem 0 1.2rem 0;
    ">
        <div style="flex:1;height:1px;background:linear-gradient(90deg,transparent,rgba(0,212,255,0.2));"></div>
        <span style="
            font-family:'Inter',sans-serif;
            font-size:0.7rem;
            font-weight:600;
            letter-spacing:3px;
            text-transform:uppercase;
            color:rgba(0,212,255,0.5);
            white-space:nowrap;
        ">SELECT A MODULE TO BEGIN</span>
        <div style="flex:1;height:1px;background:linear-gradient(90deg,rgba(0,212,255,0.2),transparent);"></div>
    </div>
    """, unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.markdown("""
        <div style="text-align:center;padding:8px 0;">
            <div style="font-size:1.6rem;margin-bottom:10px;">📊</div>
            <div style="font-family:'Inter',sans-serif;font-size:1rem;font-weight:700;color:#e8edf4;margin-bottom:6px;">Indices</div>
            <div style="font-family:'Inter',sans-serif;font-size:0.75rem;color:#6b7f99;line-height:1.5;">
                Topic-based geopolitical risk indices across 60 countries.<br>
                Time series, heatmaps, world maps, correlations.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("→ Open Indices", key="home_to_indices", use_container_width=True):
            st.session_state.page = "indices"
            st.rerun()

    with m2:
        st.markdown("""
        <div style="text-align:center;padding:8px 0;">
            <div style="font-size:1.6rem;margin-bottom:10px;">🎯</div>
            <div style="font-family:'Inter',sans-serif;font-size:1rem;font-weight:700;color:#e8edf4;margin-bottom:6px;">Country Profile</div>
            <div style="font-family:'Inter',sans-serif;font-size:0.75rem;color:#6b7f99;line-height:1.5;">
                Deep-dive into any country: top risk scores, active alarms, bilateral relations worst & best partners.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("→ Open Profile", key="home_to_profile", use_container_width=True):
            st.session_state.page = "profile"
            st.rerun()

    with m3:
        st.markdown("""
        <div style="text-align:center;padding:8px 0;">
            <div style="font-size:1.6rem;margin-bottom:10px;">📰</div>
            <div style="font-family:'Inter',sans-serif;font-size:1rem;font-weight:700;color:#e8edf4;margin-bottom:6px;">News</div>
            <div style="font-family:'Inter',sans-serif;font-size:0.75rem;color:#6b7f99;line-height:1.5;">
                Live GDELT headlines across 28 topic categories.<br>
                Real-time global news intelligence feed.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("→ Open News", key="home_to_news", use_container_width=True):
            st.session_state.page = "news"
            st.rerun()

    with m4:
        st.markdown("""
        <div style="text-align:center;padding:8px 0;">
            <div style="font-size:1.6rem;margin-bottom:10px;">🔮</div>
            <div style="font-family:'Inter',sans-serif;font-size:1rem;font-weight:700;color:#e8edf4;margin-bottom:6px;">Predictions</div>
            <div style="font-family:'Inter',sans-serif;font-size:0.75rem;color:#6b7f99;line-height:1.5;">
                N-HiTS deep learning 12-month forecasts<br>
                for 2,400 topic × country risk series.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("→ Open Predictions", key="home_to_predictions", use_container_width=True):
            st.session_state.page = "predictions"
            st.rerun()

    # ── Footer tagline ──
    st.markdown("""
    <div style="
        text-align: center;
        margin: 2.5rem 0 1rem 0;
        padding: 16px 0;
        border-top: 1px solid rgba(0,212,255,0.06);
    ">
        <div style="
            font-family:'Inter',sans-serif;
            font-size:0.7rem;
            font-weight:600;
            letter-spacing:3px;
            text-transform:uppercase;
            color:#4a5d75;
            margin-bottom:12px;
        ">TRANSFORMING GLOBAL DATA INTO ACTIONABLE INTELLIGENCE</div>
        <div style="
            display:flex;
            justify-content:center;
            gap:10px;
            flex-wrap:wrap;
        ">
            <span style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;padding:5px 12px;border:1px solid rgba(0,212,255,0.12);border-radius:20px;color:#6b7f99;letter-spacing:0.5px;">Deep Learning</span>
            <span style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;padding:5px 12px;border:1px solid rgba(0,212,255,0.12);border-radius:20px;color:#6b7f99;letter-spacing:0.5px;">NLP</span>
            <span style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;padding:5px 12px;border:1px solid rgba(0,212,255,0.12);border-radius:20px;color:#6b7f99;letter-spacing:0.5px;">GDELT</span>
            <span style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;padding:5px 12px;border:1px solid rgba(0,212,255,0.12);border-radius:20px;color:#6b7f99;letter-spacing:0.5px;">Predictive Analytics</span>
            <span style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;padding:5px 12px;border:1px solid rgba(0,212,255,0.12);border-radius:20px;color:#6b7f99;letter-spacing:0.5px;">Risk Modeling</span>
            <span style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;padding:5px 12px;border:1px solid rgba(0,212,255,0.12);border-radius:20px;color:#6b7f99;letter-spacing:0.5px;">Neural Networks</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
