#!/usr/bin/env python3
"""
NERAI — Otomatik Premium Patch Uygulayıcı
==========================================
Bu script'i gdelt_dashboard.py ile aynı klasörde çalıştırın:

    python apply_premium_patches.py

Yapacağı değişiklikler:
  1. render_indices — IndentationError düzeltmesi (heatmap + global risk map)
  2. render_profile — Premium page header + bilateral section header
  3. render_news — Premium page header
  4. render_predictions — Premium page header
  5. render_insights — Premium page header
  6. render_causality — Premium page header + 3 subheader → section_header
  7. render_briefing_room — Premium page header
  8. render_scenarios — Premium page header + 4 subheader → section_header
  9. render_threat_radar — Premium page header
  10. render_api — Premium page header

Orijinal dosya gdelt_dashboard.py.bak olarak yedeklenir.
"""

import re
import shutil
import sys
import os

FILENAME = "gdelt_dashboard.py"

def main():
    if not os.path.exists(FILENAME):
        print(f"HATA: {FILENAME} bulunamadı. Script'i repo klasöründe çalıştırın.")
        sys.exit(1)

    # Yedekle
    shutil.copy2(FILENAME, FILENAME + ".bak")
    print(f"Yedek oluşturuldu: {FILENAME}.bak")

    with open(FILENAME, "r", encoding="utf-8") as f:
        code = f.read()

    changes = 0

    # ══════════════════════════════════════════════════════════════
    # PATCH 1: Fix IndentationError in render_indices heatmap/map
    # ══════════════════════════════════════════════════════════════
    old_heatmap = (
        '    try:\n'
        '    # (divider handled by inject_section_header)\n'
        '    nerai_premium_css.inject_section_header("Risk Heatmap \u2014 Top Countries", icon="\U0001f5fa\ufe0f")\n'
        '        _fig_hm = chart_heatmap(df_norm, heatmap_n, norm_method)\n'
        '        if _fig_hm is not None:\n'
        '            st.plotly_chart(_fig_hm, use_container_width=True)\n'
        '    except Exception:\n'
        '        pass'
    )
    new_heatmap = (
        '    try:\n'
        '        nerai_premium_css.inject_section_header("Risk Heatmap \u2014 Top Countries", icon="\U0001f5fa\ufe0f")\n'
        '        _fig_hm = chart_heatmap(df_norm, heatmap_n, norm_method)\n'
        '        if _fig_hm is not None:\n'
        '            st.plotly_chart(_fig_hm, use_container_width=True)\n'
        '    except Exception:\n'
        '        pass'
    )
    if old_heatmap in code:
        code = code.replace(old_heatmap, new_heatmap, 1)
        changes += 1
        print("  ✓ PATCH 1a: Heatmap indentation düzeltildi")
    else:
        # Try alternative: maybe comment is not there
        alt_old = (
            '    try:\n'
            '    nerai_premium_css.inject_section_header("Risk Heatmap \u2014 Top Countries", icon="\U0001f5fa\ufe0f")\n'
            '        _fig_hm = chart_heatmap(df_norm, heatmap_n, norm_method)'
        )
        alt_new = (
            '    try:\n'
            '        nerai_premium_css.inject_section_header("Risk Heatmap \u2014 Top Countries", icon="\U0001f5fa\ufe0f")\n'
            '        _fig_hm = chart_heatmap(df_norm, heatmap_n, norm_method)'
        )
        if alt_old in code:
            code = code.replace(alt_old, alt_new, 1)
            changes += 1
            print("  ✓ PATCH 1a (alt): Heatmap indentation düzeltildi")
        else:
            print("  ⚠ PATCH 1a: Heatmap bloğu bulunamadı — zaten düzeltilmiş olabilir")

    old_map = (
        '    try:\n'
        '    nerai_premium_css.inject_section_header("Global Risk Map", icon="\U0001f30d")\n'
        '        _fig_wm = chart_world(df_norm, map_date)'
    )
    new_map = (
        '    try:\n'
        '        nerai_premium_css.inject_section_header("Global Risk Map", icon="\U0001f30d")\n'
        '        _fig_wm = chart_world(df_norm, map_date)'
    )
    if old_map in code:
        code = code.replace(old_map, new_map, 1)
        changes += 1
        print("  ✓ PATCH 1b: Global Risk Map indentation düzeltildi")
    else:
        print("  ⚠ PATCH 1b: Global Risk Map bloğu bulunamadı — zaten düzeltilmiş olabilir")

    # ══════════════════════════════════════════════════════════════
    # PATCH 2: render_profile — Premium page header
    # ══════════════════════════════════════════════════════════════
    profile_header_code = (
        '    nerai_premium_css.inject_page_header(\n'
        '        title="Country Intel",\n'
        '        subtitle="Deep-dive risk analysis, bilateral relations & alarm monitoring",\n'
        '        badge="INTEL",\n'
        '        icon="\\U0001f30f"\n'
        '    )\n\n'
    )

    # Insert after "def render_profile():" line
    marker = '    # ── Profile Header'
    if marker in code and 'inject_page_header' not in code.split('def render_profile')[1].split('def render_news')[0][:200]:
        code = code.replace(marker, profile_header_code + marker, 1)
        changes += 1
        print("  ✓ PATCH 2a: render_profile page header eklendi")
    else:
        # Try alternative: insert right after def render_profile(): and its first line
        pat = re.search(r'(def render_profile\(\):.*?\n)', code)
        if pat and 'inject_page_header' not in code[pat.end():pat.end()+300]:
            # Find the first non-empty, non-comment line after the def
            insert_pos = pat.end()
            code = code[:insert_pos] + profile_header_code + code[insert_pos:]
            changes += 1
            print("  ✓ PATCH 2a (alt): render_profile page header eklendi")
        else:
            print("  ⚠ PATCH 2a: render_profile header zaten var veya bulunamadı")

    # Bilateral section header
    bilateral_marker = '    # ── Bilateral Analyzer'
    bilateral_header = '    nerai_premium_css.inject_section_header("Bilateral Relations Analyzer", icon="\\U0001f91d")\n\n'
    if bilateral_marker in code and 'Bilateral Relations Analyzer' not in code:
        code = code.replace(bilateral_marker, bilateral_header + bilateral_marker, 1)
        changes += 1
        print("  ✓ PATCH 2b: Bilateral section header eklendi")
    else:
        print("  ⚠ PATCH 2b: Bilateral header zaten var veya marker bulunamadı")

    # ══════════════════════════════════════════════════════════════
    # PATCH 3: render_news — Premium page header
    # ══════════════════════════════════════════════════════════════
    news_header = (
        '    nerai_premium_css.inject_page_header(\n'
        '        title="Signal Feed",\n'
        '        subtitle="Live GDELT headlines across 28 topic categories — real-time intelligence",\n'
        '        badge="LIVE",\n'
        '        icon="\\U0001f4f0"\n'
        '    )\n\n'
    )
    pat = re.search(r'(def render_news\(\):.*?\n)', code)
    if pat and 'inject_page_header' not in code[pat.end():pat.end()+300]:
        code = code[:pat.end()] + news_header + code[pat.end():]
        changes += 1
        print("  ✓ PATCH 3: render_news page header eklendi")
    else:
        print("  ⚠ PATCH 3: render_news header zaten var veya bulunamadı")

    # ══════════════════════════════════════════════════════════════
    # PATCH 4: render_predictions — Premium page header
    # ══════════════════════════════════════════════════════════════
    pred_header = (
        '    nerai_premium_css.inject_page_header(\n'
        '        title="Forecast Engine",\n'
        '        subtitle="N-HiTS deep learning 12-month forecasts for 2,400 risk series",\n'
        '        badge="AI",\n'
        '        icon="\\U0001f52e"\n'
        '    )\n\n'
    )
    pat = re.search(r'(def render_predictions\(\):.*?\n)', code)
    if pat and 'inject_page_header' not in code[pat.end():pat.end()+300]:
        code = code[:pat.end()] + pred_header + code[pat.end():]
        changes += 1
        print("  ✓ PATCH 4: render_predictions page header eklendi")
    else:
        print("  ⚠ PATCH 4: render_predictions header zaten var veya bulunamadı")

    # ══════════════════════════════════════════════════════════════
    # PATCH 5: render_insights — Premium page header
    # ══════════════════════════════════════════════════════════════
    insights_header = (
        '    nerai_premium_css.inject_page_header(\n'
        '        title="AI Insights",\n'
        '        subtitle="Machine-generated intelligence briefings & natural language Q&A",\n'
        '        badge="AI",\n'
        '        icon="\\U0001f9e0"\n'
        '    )\n\n'
    )
    pat = re.search(r'(def render_insights\(\):.*?\n)', code)
    if pat and 'inject_page_header' not in code[pat.end():pat.end()+300]:
        code = code[:pat.end()] + insights_header + code[pat.end():]
        changes += 1
        print("  ✓ PATCH 5: render_insights page header eklendi")
    else:
        print("  ⚠ PATCH 5: render_insights header zaten var veya bulunamadı")

    # ══════════════════════════════════════════════════════════════
    # PATCH 6: render_causality — Premium page header + subheaders
    # ══════════════════════════════════════════════════════════════
    causal_header = (
        '    nerai_premium_css.inject_page_header(\n'
        '        title="Causal Network",\n'
        '        subtitle="Discover causal links between geopolitical risk factors",\n'
        '        badge="NETWORK",\n'
        '        icon="\\U0001f517"\n'
        '    )\n\n'
    )
    pat = re.search(r'(def render_causality\(\):.*?\n)', code)
    if pat and 'inject_page_header' not in code[pat.end():pat.end()+300]:
        code = code[:pat.end()] + causal_header + code[pat.end():]
        changes += 1
        print("  ✓ PATCH 6a: render_causality page header eklendi")
    else:
        print("  ⚠ PATCH 6a: render_causality header zaten var veya bulunamadı")

    # Replace subheaders in causality
    if '    st.subheader(_net_title)' in code:
        code = code.replace(
            '    st.subheader(_net_title)',
            '    nerai_premium_css.inject_section_header(_net_title, icon="\\U0001f578\\ufe0f")',
            1
        )
        changes += 1
        print("  ✓ PATCH 6b: _net_title subheader → section_header")

    if '    st.subheader(_inf_title)' in code:
        code = code.replace(
            '    st.subheader(_inf_title)',
            '    nerai_premium_css.inject_section_header(_inf_title, icon="\\U0001f4ca")',
            1
        )
        changes += 1
        print("  ✓ PATCH 6c: _inf_title subheader → section_header")

    if '    st.subheader("Recent News Evidence")' in code:
        code = code.replace(
            '    st.subheader("Recent News Evidence")',
            '    nerai_premium_css.inject_section_header("Recent News Evidence", icon="\\U0001f4f0")',
            1
        )
        changes += 1
        print("  ✓ PATCH 6d: Recent News Evidence subheader → section_header")

    # Remove orphaned comment
    code = code.replace('    # (divider handled by inject_section_header)\n    nerai_premium_css.inject_section_header("Recent News Evidence',
                         '    nerai_premium_css.inject_section_header("Recent News Evidence', 1)

    # ══════════════════════════════════════════════════════════════
    # PATCH 7: render_briefing_room — Premium page header
    # ══════════════════════════════════════════════════════════════
    briefing_header = (
        '    nerai_premium_css.inject_page_header(\n'
        '        title="Briefing Room",\n'
        '        subtitle="Automated intelligence reports & downloadable risk assessments",\n'
        '        badge="REPORTS",\n'
        '        icon="\\U0001f4cb"\n'
        '    )\n\n'
    )
    pat = re.search(r'(def render_briefing_room\(\):.*?\n)', code)
    if pat and 'inject_page_header' not in code[pat.end():pat.end()+300]:
        code = code[:pat.end()] + briefing_header + code[pat.end():]
        changes += 1
        print("  ✓ PATCH 7: render_briefing_room page header eklendi")
    else:
        print("  ⚠ PATCH 7: render_briefing_room header zaten var veya bulunamadı")

    # ══════════════════════════════════════════════════════════════
    # PATCH 8: render_scenarios — Premium page header + subheaders
    # ══════════════════════════════════════════════════════════════
    scenarios_header = (
        '    nerai_premium_css.inject_page_header(\n'
        '        title="What-If Scenarios",\n'
        '        subtitle="Simulate geopolitical shocks and analyze cascading risk impacts",\n'
        '        badge="SIM",\n'
        '        icon="\\u26a1"\n'
        '    )\n\n'
    )
    pat = re.search(r'(def render_scenarios\(\):.*?\n)', code)
    if pat and 'inject_page_header' not in code[pat.end():pat.end()+300]:
        code = code[:pat.end()] + scenarios_header + code[pat.end():]
        changes += 1
        print("  ✓ PATCH 8a: render_scenarios page header eklendi")
    else:
        print("  ⚠ PATCH 8a: render_scenarios header zaten var veya bulunamadı")

    # Replace scenario subheaders
    scenario_replacements = [
        ('    st.subheader("Pre-Built Scenarios")',
         '    nerai_premium_css.inject_section_header("Pre-Built Scenarios", icon="\\U0001f4e6")'),
        ('    st.subheader("▶️ Run Pre-Built Scenario")',
         '    nerai_premium_css.inject_section_header("Run Pre-Built Scenario", icon="▶️")'),
        ('    st.subheader("🔧 Build a Custom Scenario")',
         '    nerai_premium_css.inject_section_header("Build a Custom Scenario", icon="🔧")'),
        ('    st.subheader("📊 Scenario Results")',
         '    nerai_premium_css.inject_section_header("Scenario Results", icon="📊")'),
    ]
    for old, new in scenario_replacements:
        if old in code:
            code = code.replace(old, new, 1)
            changes += 1
            print(f"  ✓ PATCH 8: subheader → section_header")

    # ══════════════════════════════════════════════════════════════
    # PATCH 9: render_threat_radar — Premium page header
    # ══════════════════════════════════════════════════════════════
    threat_header = (
        '    nerai_premium_css.inject_page_header(\n'
        '        title="Threat Radar",\n'
        '        subtitle="Real-time anomaly detection & risk escalation monitoring",\n'
        '        badge="ALERT",\n'
        '        icon="\\U0001f3af"\n'
        '    )\n\n'
    )
    pat = re.search(r'(def render_threat_radar\(\):.*?\n)', code)
    if pat and 'inject_page_header' not in code[pat.end():pat.end()+300]:
        code = code[:pat.end()] + threat_header + code[pat.end():]
        changes += 1
        print("  ✓ PATCH 9: render_threat_radar page header eklendi")
    else:
        print("  ⚠ PATCH 9: render_threat_radar header zaten var veya bulunamadı")

    # ══════════════════════════════════════════════════════════════
    # PATCH 10: render_api — Premium page header
    # ══════════════════════════════════════════════════════════════
    api_header = (
        '    nerai_premium_css.inject_page_header(\n'
        '        title="API Access",\n'
        '        subtitle="Programmatic access to NERAI risk data & intelligence feeds",\n'
        '        badge="DEV",\n'
        '        icon="\\U0001f50c"\n'
        '    )\n\n'
    )
    pat = re.search(r'(def render_api\(\):.*?\n)', code)
    if pat and 'inject_page_header' not in code[pat.end():pat.end()+300]:
        code = code[:pat.end()] + api_header + code[pat.end():]
        changes += 1
        print("  ✓ PATCH 10: render_api page header eklendi")
    else:
        print("  ⚠ PATCH 10: render_api header zaten var veya bulunamadı")

    # ══════════════════════════════════════════════════════════════
    # WRITE OUTPUT
    # ══════════════════════════════════════════════════════════════
    with open(FILENAME, "w", encoding="utf-8") as f:
        f.write(code)

    print(f"\n{'='*60}")
    print(f"  TOPLAM: {changes} değişiklik uygulandı")
    print(f"  Dosya: {FILENAME}")
    print(f"  Yedek: {FILENAME}.bak")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
