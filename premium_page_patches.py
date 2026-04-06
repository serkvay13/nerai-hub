# ══════════════════════════════════════════════════════════════════════════
# NERAI — PREMIUM PAGE REDESIGN: ALL PATCHES FOR gdelt_dashboard.py
# ══════════════════════════════════════════════════════════════════════════
#
#  HOW TO APPLY:
#  Open gdelt_dashboard.py on GitHub and apply each patch below using
#  Find & Replace. Each patch shows EXACTLY what to find and what to
#  replace it with.
#
#  ALSO: Upload the updated nerai_premium_css.py (duplicate
#  inject_section_header removed).
#
# ══════════════════════════════════════════════════════════════════════════


# ┌─────────────────────────────────────────────────────────────────────────┐
# │  PATCH 1: FIX INDENTATION ERROR in render_indices()                     │
# │  Location: ~Lines 2069–2086                                             │
# │  ERROR: inject_section_header calls are at 4sp instead of 8sp           │
# └─────────────────────────────────────────────────────────────────────────┘
#
# ── FIND THIS ── (exact text):
"""
    # ── Heatmap ──────────────────────────────────────────────
    try:
    # (divider handled by inject_section_header)
    nerai_premium_css.inject_section_header("Risk Heatmap \u2014 Top Countries", icon="\U0001f5fa\ufe0f")
        _fig_hm = chart_heatmap(df_norm, heatmap_n, norm_method)
        if _fig_hm is not None:
            st.plotly_chart(_fig_hm, use_container_width=True)
    except Exception:
        pass

    # ── Global Risk Map ────────────────────────────────────────
    try:
    nerai_premium_css.inject_section_header("Global Risk Map", icon="\U0001f30d")
        _fig_wm = chart_world(df_norm, map_date)
        if _fig_wm is not None:
            st.plotly_chart(_fig_wm, use_container_width=True)
    except Exception:
        pass

    _render_footer()
"""

# ── REPLACE WITH THIS ──
PATCH_1 = '''
    # ── Heatmap ──────────────────────────────────────────────
    try:
        nerai_premium_css.inject_section_header("Risk Heatmap — Top Countries", icon="🗺️")
        _fig_hm = chart_heatmap(df_norm, heatmap_n, norm_method)
        if _fig_hm is not None:
            st.plotly_chart(_fig_hm, use_container_width=True)
    except Exception:
        pass

    # ── Global Risk Map ────────────────────────────────────────
    try:
        nerai_premium_css.inject_section_header("Global Risk Map", icon="🌍")
        _fig_wm = chart_world(df_norm, map_date)
        if _fig_wm is not None:
            st.plotly_chart(_fig_wm, use_container_width=True)
    except Exception:
        pass

    _render_footer()
'''


# ┌─────────────────────────────────────────────────────────────────────────┐
# │  PATCH 2: ADD PREMIUM HEADER to render_profile()                        │
# │  Location: ~Line 2093                                                   │
# └─────────────────────────────────────────────────────────────────────────┘
#
# ── FIND THIS ──
"""
def render_profile():
"""
# (the first line of the function)
#
# ── ADD THIS right after the function def and any existing docstring/comments,
#    BEFORE the "# ── Profile Header" comment ──
#
PATCH_2 = '''
    nerai_premium_css.inject_page_header(
        title="Country Intel",
        subtitle="Deep-dive risk analysis, bilateral relations & alarm monitoring",
        badge="INTEL",
        icon="🌏"
    )
'''
# ── ALSO FIND (around line 2239): ──
# "    # ── Bilateral Analyzer ────────────────────────────────────"
# ── ADD THIS LINE right before it: ──
PATCH_2B = '''
    nerai_premium_css.inject_section_header("Bilateral Relations Analyzer", icon="🤝")
'''


# ┌─────────────────────────────────────────────────────────────────────────┐
# │  PATCH 3: ADD PREMIUM HEADER to render_news()                           │
# │  Location: ~Line 2338                                                   │
# └─────────────────────────────────────────────────────────────────────────┘
#
# ── ADD THIS as the FIRST lines inside render_news() ──
#
PATCH_3 = '''
    nerai_premium_css.inject_page_header(
        title="Signal Feed",
        subtitle="Live GDELT headlines across 28 topic categories — real-time intelligence",
        badge="LIVE",
        icon="📰"
    )
'''


# ┌─────────────────────────────────────────────────────────────────────────┐
# │  PATCH 4: ADD PREMIUM HEADER to render_predictions()                    │
# │  Location: ~Line 2425                                                   │
# └─────────────────────────────────────────────────────────────────────────┘
#
# ── ADD THIS as the FIRST lines inside render_predictions() ──
#
PATCH_4 = '''
    nerai_premium_css.inject_page_header(
        title="Forecast Engine",
        subtitle="N-HiTS deep learning 12-month forecasts for 2,400 risk series",
        badge="AI",
        icon="🔮"
    )
'''


# ┌─────────────────────────────────────────────────────────────────────────┐
# │  PATCH 5: ADD PREMIUM HEADER to render_insights()                       │
# │  Location: ~Line 3407                                                   │
# └─────────────────────────────────────────────────────────────────────────┘
#
# ── ADD THIS as the FIRST lines inside render_insights() ──
#
PATCH_5 = '''
    nerai_premium_css.inject_page_header(
        title="AI Insights",
        subtitle="Machine-generated intelligence briefings & natural language Q&A",
        badge="AI",
        icon="🧠"
    )
'''


# ┌─────────────────────────────────────────────────────────────────────────┐
# │  PATCH 6: ADD PREMIUM HEADER + REPLACE SUBHEADERS in render_causality() │
# │  Location: ~Line 3974                                                   │
# └─────────────────────────────────────────────────────────────────────────┘
#
# ── ADD THIS as the FIRST lines inside render_causality() ──
#
PATCH_6 = '''
    nerai_premium_css.inject_page_header(
        title="Causal Network",
        subtitle="Discover causal links between geopolitical risk factors",
        badge="NETWORK",
        icon="🔗"
    )
'''
# ── ALSO REPLACE these 3 subheaders: ──
#
# Line ~4127:  st.subheader(_net_title)
#   REPLACE → nerai_premium_css.inject_section_header(_net_title, icon="🕸️")
#
# Line ~4165:  st.subheader(_inf_title)
#   REPLACE → nerai_premium_css.inject_section_header(_inf_title, icon="📊")
#
# Line ~4221-4222:
#   DELETE → # (divider handled by inject_section_header)
#   REPLACE → st.subheader("Recent News Evidence")
#   WITH   → nerai_premium_css.inject_section_header("Recent News Evidence", icon="📰")


# ┌─────────────────────────────────────────────────────────────────────────┐
# │  PATCH 7: ADD PREMIUM HEADER to render_briefing_room()                  │
# │  Location: ~Line 4433                                                   │
# └─────────────────────────────────────────────────────────────────────────┘
#
# ── ADD THIS as the FIRST lines inside render_briefing_room() ──
#
PATCH_7 = '''
    nerai_premium_css.inject_page_header(
        title="Briefing Room",
        subtitle="Automated intelligence reports & downloadable risk assessments",
        badge="REPORTS",
        icon="📋"
    )
'''


# ┌─────────────────────────────────────────────────────────────────────────┐
# │  PATCH 8: ADD PREMIUM HEADER + REPLACE SUBHEADERS in render_scenarios() │
# │  Location: ~Line 4822                                                   │
# └─────────────────────────────────────────────────────────────────────────┘
#
# ── ADD THIS as the FIRST lines inside render_scenarios() ──
#
PATCH_8 = '''
    nerai_premium_css.inject_page_header(
        title="What-If Scenarios",
        subtitle="Simulate geopolitical shocks and analyze cascading risk impacts",
        badge="SIM",
        icon="⚡"
    )
'''
# ── ALSO REPLACE these 4 subheaders: ──
#
# Line ~4835:  st.subheader("Pre-Built Scenarios")
#   REPLACE → nerai_premium_css.inject_section_header("Pre-Built Scenarios", icon="📦")
#
# Line ~4873:  st.subheader("▶️ Run Pre-Built Scenario")
#   REPLACE → nerai_premium_css.inject_section_header("Run Pre-Built Scenario", icon="▶️")
#
# Line ~4892:  st.subheader("🔧 Build a Custom Scenario")
#   REPLACE → nerai_premium_css.inject_section_header("Build a Custom Scenario", icon="🔧")
#
# Line ~4926:  st.subheader("📊 Scenario Results")
#   REPLACE → nerai_premium_css.inject_section_header("Scenario Results", icon="📊")


# ┌─────────────────────────────────────────────────────────────────────────┐
# │  PATCH 9: ADD PREMIUM HEADER to render_threat_radar()                   │
# │  Location: ~Line 5114                                                   │
# └─────────────────────────────────────────────────────────────────────────┘
#
# ── ADD THIS as the FIRST lines inside render_threat_radar() ──
#
PATCH_9 = '''
    nerai_premium_css.inject_page_header(
        title="Threat Radar",
        subtitle="Real-time anomaly detection & risk escalation monitoring",
        badge="ALERT",
        icon="🎯"
    )
'''


# ┌─────────────────────────────────────────────────────────────────────────┐
# │  PATCH 10: ADD PREMIUM HEADER to render_api()                           │
# │  Location: ~Line 5015                                                   │
# └─────────────────────────────────────────────────────────────────────────┘
#
# ── ADD THIS as the FIRST lines inside render_api() ──
#
PATCH_10 = '''
    nerai_premium_css.inject_page_header(
        title="API Access",
        subtitle="Programmatic access to NERAI risk data & intelligence feeds",
        badge="DEV",
        icon="🔌"
    )
'''


# ══════════════════════════════════════════════════════════════════════════
# QUICK REFERENCE — TOTAL CHANGES:
# ══════════════════════════════════════════════════════════════════════════
#
#  FILE: nerai_premium_css.py
#   → Remove duplicate inject_section_header at line ~1714 (DONE in file)
#
#  FILE: gdelt_dashboard.py
#   → PATCH 1:  Fix indentation in render_indices heatmap/map sections
#   → PATCH 2:  render_profile — add page header + bilateral section header
#   → PATCH 3:  render_news — add page header
#   → PATCH 4:  render_predictions — add page header
#   → PATCH 5:  render_insights — add page header
#   → PATCH 6:  render_causality — add page header + replace 3 subheaders
#   → PATCH 7:  render_briefing_room — add page header
#   → PATCH 8:  render_scenarios — add page header + replace 4 subheaders
#   → PATCH 9:  render_threat_radar — add page header
#   → PATCH 10: render_api — add page header
#
# ══════════════════════════════════════════════════════════════════════════
