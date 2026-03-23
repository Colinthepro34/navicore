import streamlit as st
import pandas as pd
import io
import os
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ── NO osmnx import at module level — only used lazily if needed ──
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from GPS import MumbaiData, Router

# ──────────────────────────────────────────────────────────────────────────────
# 1. PAGE CONFIG & STYLES
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="NaviCore", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=DM+Sans:wght@400;500;700&display=swap');

    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding-top: 0rem !important; }
    body { color: black; background-color: white; }

    /* ── NAVBAR ── */
    .ub-nav {
        display: flex; align-items: center; justify-content: space-between;
        padding: 20px 60px;
        background: var(--bg-primary);
        border-bottom: 1px solid var(--border);
        position: sticky; top: 0; z-index: 999;
    }
    .ub-logo {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 28px; font-weight: 800;
        color: var(--text-primary); letter-spacing: -1px;
    }
    .ub-nav-links { display: flex; gap: 36px; list-style: none; margin: 0; padding: 0; }
    .ub-nav-links li a { color: var(--text-muted); text-decoration: none; font-size: 14px; font-weight: 500; }
    .ub-nav-links li a:hover { color: var(--text-primary); }
    .ub-nav-actions { display: flex; gap: 16px; align-items: center; }
    .ub-btn-ghost {
        background: transparent; border: 1px solid var(--border);
        color: var(--text-primary); padding: 9px 22px;
        border-radius: 500px; font-size: 14px; font-weight: 500; cursor: pointer;
    }
    .ub-btn-solid {
        background: var(--btn-bg); border: none; color: var(--btn-text);
        padding: 9px 22px; border-radius: 500px; font-size: 14px; font-weight: 700; cursor: pointer;
    }

    /* ── PRIMARY BUTTON ── */
    div.stButton > button[kind="primary"] {
        background-color: black; color: white; border: none;
        padding: 0.55rem 1.2rem; font-weight: 600; border-radius: 8px;
        font-family: 'DM Sans', sans-serif;
    }
    div.stButton > button[kind="primary"]:hover { background-color: #222; border: none; color: white; }

    /* ── BLACK SECTION ── */
    .black-section-container {
        background-color: black; color: white;
        padding: 4rem; border-radius: 16px; margin: 2rem 0;
    }
    .black-section-title { font-size: 3rem; font-weight: 700; margin-bottom: 1rem; letter-spacing: -0.5px; }
    .black-section-text { font-size: 1.1rem; line-height: 1.7; color: #aaaaaa; margin-bottom: 2rem; }
    .white-btn {
        background-color: white; color: black; padding: 11px 24px;
        text-decoration: none; font-weight: 700; border-radius: 8px;
        display: inline-block; font-size: 0.9rem;
    }
    .white-btn:hover { background-color: #f0f0f0; color: black; }

    /* ── STICKY BOTTOM ── */
    .sticky-bottom {
        position: fixed; bottom: 0; left: 0; width: 100%;
        background-color: white; padding: 15px;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.1); text-align: center; z-index: 999;
    }
    .sticky-btn {
        background-color: black; color: white; padding: 12px 24px;
        border-radius: 8px; font-weight: bold; font-size: 16px;
        border: none; cursor: pointer; width: 100%; max-width: 400px;
    }
    .sticky-btn:hover { background-color: #333; }

    /* ── INPUTS ── */
    .stTextInput > div > div > input {
        border-radius: 8px; border: 1.5px solid #e0e0e0;
        padding: 0.5rem 0.75rem; font-family: 'DM Sans', sans-serif;
    }
    .stTextInput > div > div > input:focus { border-color: #111; box-shadow: none; }

    /* ── LEG CARDS ── */
    .leg-card {
        background: #111d35; border-radius: 10px; border-left: 5px solid #ccc;
        padding: 14px 16px; margin-bottom: 12px; color: #e8eaf6;
    }
    .leg-header {
        font-family: 'Space Grotesk', sans-serif; font-size: 1rem; font-weight: 700;
        display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;
    }
    .leg-route { color: #9aa7c4; font-size: 0.85rem; }
    .leg-stats { font-size: 0.8rem; color: #9aa7c4; background: #1c2d4a; border-radius: 6px; padding: 2px 8px; }
    .stop-chip {
        display: inline-block; border-radius: 12px; padding: 2px 9px;
        font-size: 0.78rem; margin: 2px; font-weight: 600;
    }

    /* ── FEATURE CARDS ── */
    .feature-card {
        background: linear-gradient(145deg, #1a2540, #0f1d35);
        border: 1px solid #2a3a60; border-radius: 12px;
        padding: 20px; height: 100%; transition: transform 0.2s;
    }
    .feature-card:hover { transform: translateY(-3px); }
    .feature-icon { font-size: 2rem; margin-bottom: 8px; }
    .feature-title { font-family: 'Space Grotesk', sans-serif; font-size: 1.1rem; font-weight: 700; margin: 0 0 6px; }
    .feature-desc  { font-size: 0.9rem; color: #9aa7c4; margin: 0; }

    /* ── PROGRESS BAR ── */
    .progress-bar-wrap { border-radius: 8px; overflow: hidden; display: flex; height: 14px; margin: 8px 0 16px; }
    .progress-segment  { height: 100%; }

    /* ── MAP LEGEND ── */
    .map-legend {
        display: flex; flex-wrap: wrap; gap: 10px;
        padding: 8px 12px; background: #0e1a30;
        border-radius: 8px; margin-top: 8px; font-size: 0.82rem; color: #e8eaf6;
    }
    .legend-item { display: flex; align-items: center; gap: 5px; }
    .legend-dot  { width: 12px; height: 12px; border-radius: 3px; flex-shrink: 0; }

    /* ── MOBILE ── */
    @media (max-width: 768px) {
        .ub-nav { padding: 12px 16px; justify-content: flex-start; gap: 0; }
        .ub-logo { font-size: 22px; flex: 1; text-align: left; }
        .ub-nav-links { display: none; }
        .ub-nav-actions { gap: 8px; flex-shrink: 0; }
        .ub-btn-ghost, .ub-btn-solid { padding: 7px 13px; font-size: 12px; }
        .block-container { padding-left: 0.75rem !important; padding-right: 0.75rem !important; }
        .black-section-container { padding: 2rem 1.2rem; border-radius: 12px; }
        .black-section-title { font-size: 2rem; }
        .black-section-text { font-size: 0.95rem; }
        .feature-card { margin-bottom: 12px; }
        .sticky-btn { font-size: 14px; padding: 10px 20px; }
        .leg-card { padding: 10px 12px; }
        .leg-header { font-size: 0.9rem; flex-direction: column; align-items: flex-start; gap: 4px; }
        .leg-stats { font-size: 0.75rem; }
        .stop-chip { font-size: 0.72rem; padding: 2px 7px; }
    }
    </style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# 2. DATA LOADING  (cached — loaded once, never reloaded)
# ──────────────────────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner="Loading Mumbai transport data…")
def load_core_data():
    """
    Load MumbaiData + Router once and keep them alive for the whole session.
    IMPORTANT: We do NOT store G_road as a module-level variable — it stays
    inside the cached MumbaiData object so Streamlit can manage its lifetime.
    """
    try:
        data   = MumbaiData()
        router = Router(data)
        return data, router
    except Exception as e:
        st.error(f"Failed to load Mumbai transport data: {e}")
        return None, None


@st.cache_data(show_spinner=False)
def get_landmark_list():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Mumbai Landmarks.csv")
    if not os.path.exists(path):
        st.error("Mumbai Landmarks.csv not found.")
        return pd.DataFrame()
    df = pd.read_csv(path)
    df = df.dropna(subset=["latitude", "longitude", "name"])
    df["label"] = df.apply(
        lambda r: f"{r['name']} — {str(r.get('category', '')).replace('_', ' ')}",
        axis=1,
    )
    return df.sort_values("name")


# ── Run once at startup ──
data, router   = load_core_data()
landmarks_df   = get_landmark_list()

if not landmarks_df.empty:
    landmark_labels = ["📍 Custom coordinates..."] + landmarks_df["label"].tolist()
    landmark_map    = {
        row["label"]: (row["latitude"], row["longitude"])
        for _, row in landmarks_df.iterrows()
    }
else:
    landmark_labels = ["📍 Custom coordinates..."]
    landmark_map    = {}

# ──────────────────────────────────────────────────────────────────────────────
# 3. CONSTANTS
# ──────────────────────────────────────────────────────────────────────────────
MODE_HEX = {
    "train":    "#ff3333",
    "metro":    "#00e5c0",
    "monorail": "#ff9800",
    "bus":      "#1e90ff",
    "walk":     "#aaaaaa",
    "car":      "#ffd700",
}
MODE_EMOJI = {
    "walk":     "🚶",
    "train":    "🚆",
    "metro":    "🚇",
    "monorail": "🚝",
    "bus":      "🚌",
    "car":      "🚖",
}
MODE_OPTIONS = [
    "earliest_arrival",
    "least_interchange",
    "public_transport",
    "train",
    "metro",
    "bus",
    "car",
]
MODE_LABELS = {
    "earliest_arrival":  "⚡ Earliest Arrival",
    "least_interchange": "🔄 Least Interchange",
    "public_transport":  "🚏 Public Transport Only",
    "train":             "🚆 Local Train",
    "metro":             "🚇 Metro & Monorail",
    "bus":               "🚌 Bus",
    "car":               "🚖 Cab",
}


# ──────────────────────────────────────────────────────────────────────────────
# 4. HELPERS
# ──────────────────────────────────────────────────────────────────────────────
def friendly_node(node_id: str, data: MumbaiData) -> str:
    if node_id == "start":  return "📍 Start"
    if node_id == "end":    return "🏁 Destination"
    if node_id.startswith("train_"):
        return node_id[len("train_"):].split("__")[0].title()
    if node_id.startswith("bus_"):
        stop_id = node_id[len("bus_"):]
        rows = data.bus_df[data.bus_df["stop_id"] == stop_id]["stop_name"]
        return rows.iloc[0].title() if not rows.empty else stop_id
    return node_id


def group_into_legs(steps):
    legs = []
    for step in steps:
        mode  = step["mode"]
        route = step.get("route", "")
        if legs and legs[-1]["mode"] == mode and legs[-1]["route"] == route:
            legs[-1]["steps"].append(step)
            legs[-1]["distance_km"] += step["distance_km"]
            legs[-1]["time_min"]    += step["time_min"]
        else:
            legs.append({
                "mode": mode, "route": route, "steps": [step],
                "distance_km": step["distance_km"], "time_min": step["time_min"],
            })
    return legs


def render_progress_bar(legs, total_time):
    segments = ""
    for leg in legs:
        pct   = (leg["time_min"] / total_time * 100) if total_time else 0
        color = MODE_HEX.get(leg["mode"], "#888")
        title = f"{leg['mode'].title()}: {leg['time_min']:.1f} min"
        segments += (
            f'<div class="progress-segment" '
            f'style="width:{pct:.1f}%;background:{color};" title="{title}"></div>'
        )
    st.markdown(f'<div class="progress-bar-wrap">{segments}</div>', unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# 5. LIGHTWEIGHT MAP  (no ox.plot_graph — memory-safe for Streamlit Cloud)
# ──────────────────────────────────────────────────────────────────────────────
def render_map_lightweight(steps, start_coords, end_coords) -> io.BytesIO:
    """
    Draw the route on a plain dark canvas WITHOUT loading the full OSMnx road
    graph into memory.  This is the deployment-safe version for Streamlit Cloud.

    Visual quality is preserved:
      • Dark navy background matching the original aesthetic
      • Glow + solid lines per mode with correct colours
      • Dashed yellow walk legs
      • Coloured stop dots with white outlines
      • Cyan ★ START  /  Red ★ END  markers with labels
      • Station name annotations for rail stops
      • Bounding-box zoom with padding
    """
    # ── Collect all coordinates ──────────────────────────────────────────────
    all_lats = [start_coords[0], end_coords[0]]
    all_lons = [start_coords[1], end_coords[1]]
    for s in steps:
        for key in ("seg_start", "seg_end"):
            c = s.get(key)
            if c:
                all_lats.append(c[0])
                all_lons.append(c[1])

    PAD     = 0.015
    min_lat = min(all_lats) - PAD
    max_lat = max(all_lats) + PAD
    min_lon = min(all_lons) - PAD
    max_lon = max(all_lons) + PAD

    # ── Figure setup ────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(7, 9))
    fig.patch.set_facecolor("#0a1628")
    ax.set_facecolor("#0a1628")
    ax.set_xlim(min_lon, max_lon)
    ax.set_ylim(min_lat, max_lat)
    ax.set_aspect("equal")
    ax.axis("off")

    # ── Draw a subtle grid to hint at street structure ───────────────────────
    lon_range = max_lon - min_lon
    lat_range = max_lat - min_lat
    grid_step = max(lon_range, lat_range) / 10
    for g in [i * grid_step + min_lon for i in range(12)]:
        ax.axvline(g, color="#1a2a45", lw=0.4, zorder=0)
    for g in [i * grid_step + min_lat for i in range(12)]:
        ax.axhline(g, color="#1a2a45", lw=0.4, zorder=0)

    # ── Draw route segments ──────────────────────────────────────────────────
    for s in steps:
        seg_s = s.get("seg_start")
        seg_e = s.get("seg_end")
        if not seg_s or not seg_e:
            continue
        if s.get("is_snap"):
            continue

        mode  = s["mode"]
        color = MODE_HEX.get(mode, "white")
        xs = [seg_s[1], seg_e[1]]
        ys = [seg_s[0], seg_e[0]]

        if mode == "walk":
            # Dashed yellow walk leg
            ax.plot(xs, ys, color="#f5c518", lw=2.5,
                    linestyle="--", dash_capstyle="round", zorder=5)
        else:
            # Glow halo
            ax.plot(xs, ys, color=color, lw=9, alpha=0.18,
                    solid_capstyle="round", zorder=3)
            # Core line
            lw = 4 if mode in ("train", "metro", "monorail") else 3
            ax.plot(xs, ys, color=color, lw=lw,
                    solid_capstyle="round", zorder=4)

    # ── Stop dots + labels ───────────────────────────────────────────────────
    seen_coords: set = set()
    for s in steps:
        if s["mode"] not in ("train", "metro", "monorail", "bus"):
            continue
        for coord_key, node_key in [("seg_start", "from"), ("seg_end", "to")]:
            c    = s.get(coord_key)
            node = s.get(node_key)
            if not c or c in seen_coords:
                continue
            seen_coords.add(c)
            color = MODE_HEX.get(s["mode"], "#ccc")
            ax.plot(c[1], c[0], "o",
                    color=color, markersize=6,
                    markeredgecolor="white", markeredgewidth=0.8, zorder=7)
            label = friendly_node(node, data) if node else ""
            if label and label not in ("📍 Start", "🏁 Destination"):
                ax.annotate(
                    label, xy=(c[1], c[0]),
                    xytext=(5, 4), textcoords="offset points",
                    fontsize=5.5, color="white", alpha=0.85,
                    zorder=8, fontfamily="monospace",
                )

    # ── START marker ────────────────────────────────────────────────────────
    ax.plot(start_coords[1], start_coords[0],
            marker="*", color="#00e5c0", markersize=20,
            markeredgecolor="white", markeredgewidth=0.8, zorder=10)
    ax.annotate(
        " START", (start_coords[1], start_coords[0]),
        fontsize=9, fontweight="bold", color="#00e5c0",
        xytext=(7, 5), textcoords="offset points",
        zorder=11, fontfamily="monospace",
    )

    # ── END marker ──────────────────────────────────────────────────────────
    ax.plot(end_coords[1], end_coords[0],
            marker="*", color="#ff3333", markersize=20,
            markeredgecolor="white", markeredgewidth=0.8, zorder=10)
    ax.annotate(
        " END", (end_coords[1], end_coords[0]),
        fontsize=9, fontweight="bold", color="#ff3333",
        xytext=(7, 5), textcoords="offset points",
        zorder=11, fontfamily="monospace",
    )

    plt.tight_layout(pad=0)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150,
                bbox_inches="tight", facecolor="#0a1628")
    plt.close(fig)
    buf.seek(0)
    return buf


# ──────────────────────────────────────────────────────────────────────────────
# 6. ROUTE POPUP
# ──────────────────────────────────────────────────────────────────────────────
@st.dialog("Route Details", width="large")
def show_route_popup(start_coords, end_coords, mode_choice):
    with st.status("Analyzing routes…", expanded=True) as status:
        st.write("Optimizing transport path…")
        try:
            result = router.route(start_coords, end_coords, mode_choice)
        except Exception as e:
            status.update(label="Routing failed.", state="error")
            st.error(f"Routing error: {e}")
            return

        if not result or result[0] is None:
            status.update(label="No route found.", state="error")
            # Mode-specific hints
            hints = {
                "metro":            "Metro/monorail may not serve these locations. Try Earliest Arrival.",
                "train":            "Local train lines may not connect these points. Try Earliest Arrival.",
                "bus":              "No BEST bus routes connect these points. Try Earliest Arrival.",
                "public_transport": "Too far from any transit stop to walk. Try Earliest Arrival.",
            }
            st.warning(hints.get(mode_choice, "No path found. Try Earliest Arrival."))
            if result and result[3]:
                for adv in result[3]:
                    st.info(adv)
            return

        path, steps, total_time, advisories, G_multi = result
        legs       = group_into_legs(steps)
        total_dist = sum(s["distance_km"] for s in steps)

        st.write("Rendering map…")
        map_buf = render_map_lightweight(steps, start_coords, end_coords)

        status.update(label="Route ready!", state="complete", expanded=False)

    # ── Summary bar ─────────────────────────────────────────────────────────
    st.subheader(f"⏱ {total_time:.1f} min  |  📏 {total_dist:.2f} km")

    # Mode breakdown
    mode_times: dict = {}
    for s in steps:
        mode_times[s["mode"]] = mode_times.get(s["mode"], 0) + s["time_min"]
    if len(mode_times) > 1:
        bcols = st.columns(len(mode_times))
        for i, (m, t) in enumerate(mode_times.items()):
            bcols[i].metric(
                f"{MODE_EMOJI.get(m, '')} {m.title()}",
                f"{t:.1f} min",
                f"{t / total_time * 100:.0f}%",
            )

    # Progress bar
    render_progress_bar(legs, total_time)

    # Advisories
    if advisories:
        unique_adv = list(dict.fromkeys(advisories))
        with st.expander(f"⚠️ Advisories ({len(unique_adv)})", expanded=False):
            for a in unique_adv:
                st.warning(a)

    # ── Two-column layout: map | steps ──────────────────────────────────────
    col_map, col_list = st.columns([1.2, 1])

    with col_map:
        st.image(map_buf, use_container_width=True)
        # Map legend
        legend_items = "".join(
            f"<div class='legend-item'>"
            f"<div class='legend-dot' style='background:{c};'></div>"
            f"<span>{m}</span></div>"
            for m, c in {
                "Walk": "#aaaaaa", "Train": "#ff3333", "Metro": "#00e5c0",
                "Monorail": "#ff9800", "Bus": "#1e90ff", "Cab": "#ffd700",
            }.items()
        )
        legend_items += (
            "<div class='legend-item'>"
            "<div class='legend-dot' style='background:#00e5c0;border-radius:50%;'></div>"
            "<span>Start</span></div>"
            "<div class='legend-item'>"
            "<div class='legend-dot' style='background:#ff3333;border-radius:50%;'></div>"
            "<span>End</span></div>"
        )
        st.markdown(f"<div class='map-legend'>{legend_items}</div>",
                    unsafe_allow_html=True)

    with col_list:
        st.markdown("### 📋 Journey Breakdown")
        # Filter out trivial walk legs (< 100 m) from display only
        display_legs = [l for l in legs
                        if not (l["mode"] == "walk" and l["distance_km"] < 0.1)]
        for leg in display_legs:
            color = MODE_HEX.get(leg["mode"], "#888")
            emoji = MODE_EMOJI.get(leg["mode"], "•")
            stops = [friendly_node(s["from"], data) for s in leg["steps"]]
            stops.append(friendly_node(leg["steps"][-1]["to"], data))
            unique_stops = list(dict.fromkeys(stops))
            chips = "".join([
                f"<span class='stop-chip' "
                f"style='background:{color}33;color:{color};border:1px solid {color}55;'>"
                f"{s}</span>"
                for s in unique_stops
            ])
            route_badge = f"— {leg['route']}" if leg.get("route") else ""
            st.markdown(f"""
            <div class="leg-card" style="border-left-color:{color};">
              <div class="leg-header">
                <span>{emoji} {leg['mode'].title()}
                  <span class="leg-route">{route_badge}</span>
                </span>
                <span class="leg-stats">
                  {leg['distance_km']:.2f} km | {leg['time_min']:.1f} min
                </span>
              </div>
              <div class="leg-body">
                <div>
                  <strong style="color:{color};">{unique_stops[0]}</strong>
                  <span style="color:#667;"> → </span>
                  <strong style="color:{color};">{unique_stops[-1]}</strong>
                </div>
                <div style="margin-top:8px;">{chips}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# 7. MAIN UI
# ──────────────────────────────────────────────────────────────────────────────
def main():
    # ── Navbar ───────────────────────────────────────────────────────────────
    st.markdown("""
    <nav class="ub-nav">
      <div class="ub-logo">NaviCore</div>
      <div class="ub-nav-actions">
        <button class="ub-btn-ghost">Log in</button>
        <button class="ub-btn-solid">Sign up</button>
      </div>
    </nav>
    """, unsafe_allow_html=True)

    # ── Hero section ─────────────────────────────────────────────────────────
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.title("Find the smartest route now")

        s_name = st.selectbox("Start Point", options=landmark_labels)
        e_name = st.selectbox(
            "Destination", options=landmark_labels,
            index=min(10, len(landmark_labels) - 1),
        )
        mode_option = st.selectbox(
            "Preferred Mode",
            options=MODE_OPTIONS,
            format_func=lambda m: MODE_LABELS.get(m, m),
        )

        if st.button("Calculate Route", type="primary", use_container_width=True):
            s_coords = landmark_map.get(s_name, (19.0760, 72.8777))
            e_coords = landmark_map.get(e_name, (19.1972, 72.9780))
            show_route_popup(s_coords, e_coords, mode_option)

    with col_right:
        st.image(
            "https://cn-geo1.uber.com/image-proc/crop/resizecrop/udam/format=auto"
            "/width=552/height=552/srcb64=aHR0cHM6Ly90Yi1zdGF0aWMudWJlci5jb20vcHJvZC91ZGFtLWFzc2V0cy80MmEyOTE0Ny1lMDQzLTQyZjktODU0NC1lY2ZmZmUwNTMyZTkucG5n"
        )

    # ── PAT.ai black section ─────────────────────────────────────────────────
    st.markdown("""
    <div class="black-section-container">
        <div style="display:flex;flex-wrap:wrap;gap:2rem;align-items:center;">
            <div style="flex:1;min-width:300px;">
                <div class="black-section-title">PAT.ai</div>
                <div class="black-section-text">
                    PAT.ai (Perform • Analyze • Transform) is a smart data assistant that
                    lets users upload a dataset and analyze it using simple natural language
                    commands. It automatically interprets prompts to perform statistical
                    analysis, visualization, data cleaning, and predictions.
                </div>
                <a href="https://pat-ai-maf6edxnuysrl84qfmjgwt.streamlit.app/" class="white-btn">Try it</a>
            </div>
            <div style="flex:1;min-width:300px;text-align:center;">
                <img src="https://cn-geo1.uber.com/image-proc/crop/resizecrop/udam/format=auto/width=552/height=368/srcb64=aHR0cHM6Ly90Yi1zdGF0aWMudWJlci5jb20vcHJvZC91ZGFtLWFzc2V0cy9jNjQyNWRmNC0zMTkwLTRmZTEtODY2Ni02YTVhZjJjMGEwNDkucG5n"
                     style="max-width:100%;height:auto;border-radius:12px;">
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── How it works ─────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    col3, col4 = st.columns([1, 1], gap="large")

    with col3:
        st.image(
            "https://cn-geo1.uber.com/image-proc/crop/resizecrop/udam/format=auto"
            "/width=552/height=311/srcb64=aHR0cHM6Ly90Yi1zdGF0aWMudWJlci5jb20vcHJvZC91ZGFtLWFzc2V0cy9kNjQ4ZjViNi1iYjVmLTQ1MGUtODczMy05MGFlZmVjYmQwOWUuanBn"
        )
    with col4:
        st.title("How it works")
        st.markdown("""
        NaviCore is a multimodal transit engine for Mumbai that solves the "last-mile"
        problem by merging road data with local train, metro, monorail, and BEST bus
        networks. A weighted Dijkstra algorithm evaluates millions of combinations to
        find the most efficient path — minimising time, transfers, or both.

        The system uses a dynamic speed model: walking at 12 min/km, buses at 4 min/km,
        cabs at 3 min/km — with fixed rail timetables and snap logic ensuring every
        route is realistic and navigable.
        """)

    # ── Feature cards ────────────────────────────────────────────────────────
    st.subheader("Choose your routing strategy")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class='feature-card'>
          <div class='feature-icon'>⚡</div>
          <div class='feature-title'>Earliest Arrival</div>
          <p class='feature-desc'>Dijkstra across all modes — local train, metro,
          monorail, bus, cab and walk — minimising total journey time.</p>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class='feature-card'>
          <div class='feature-icon'>🔄</div>
          <div class='feature-title'>Least Interchange</div>
          <p class='feature-desc'>Uses all modes but penalises every line or mode
          change heavily, so you transfer as few times as possible.</p>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class='feature-card'>
          <div class='feature-icon'>🚏</div>
          <div class='feature-title'>Public Transport Only</div>
          <p class='feature-desc'>All transit systems, walk-only access — no cabs.
          Forces the route to stay on trains, metro, monorail and buses.</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br><br><br><br>", unsafe_allow_html=True)

    # ── Sticky bottom bar ────────────────────────────────────────────────────
    st.markdown("""
        <div class="sticky-bottom">
            <button class="sticky-btn" onclick="window.scrollTo(0,0);">
                Calculate Route
            </button>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
