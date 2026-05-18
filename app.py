import os
import sys
import time
import subprocess
import streamlit as st
import datetime

# ---------------------------------------------------------
# Set page configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="Melody AI",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# SECTION 2 — GLOBAL CSS INJECTIONS
# ---------------------------------------------------------
st.markdown("""
<style>
/* A) Page background and base */
.stApp { background: #FAFAF8 !important; }
[data-testid="stSidebar"] { background: #F5F3EF !important; border-right: 1px solid #E8E4DC !important; }
h1,h2,h3 { color: #1C1917 !important; }
p, li { color: #7A7060; }

/* B) Button overrides */
div[data-testid="stButton"] > button {
  background: linear-gradient(135deg,#7C65EF,#A78BFA) !important;
  border: none !important; color: white !important;
  font-weight: 700 !important; border-radius: 14px !important;
  padding: 13px 26px !important; font-size: 14px !important;
  transition: all 0.25s !important; letter-spacing: 0.02em !important;
}
div[data-testid="stButton"] > button:hover {
  transform: scale(1.03) !important; filter: brightness(1.05) !important;
}

/* C) Slider overrides */
.stSlider [data-baseweb="slider"] > div:first-child {
  background: linear-gradient(to right, #7C65EF, #E8E4DC) !important;
}
.stSlider [data-testid="stThumbValue"] { color: #7C65EF !important; font-weight: 700 !important; }

/* D) Metric card overrides */
[data-testid="stMetric"] {
  background: white !important;
  border: 1px solid rgba(0,0,0,0.07) !important;
  border-radius: 16px !important;
  padding: 16px !important;
  box-shadow: 0 2px 4px rgba(0,0,0,0.04), 0 8px 24px rgba(124,101,239,0.08) !important;
  transition: all 0.25s !important;
}
[data-testid="stMetric"]:hover { transform: translateY(-2px) !important; }
[data-testid="stMetric"] label { color: #C4B9A8 !important; font-size: 10px !important; letter-spacing: 0.06em !important; text-transform: uppercase !important; }
[data-testid="stMetricValue"] { color: #534AB7 !important; font-size: 22px !important; font-weight: 700 !important; }

/* E) Radio button pills (genre and mood selectors) */
[data-testid="stRadio"] > div { display: flex !important; flex-wrap: wrap !important; gap: 8px !important; }
[data-testid="stRadio"] label {
  background: #F5F3EF !important; border: 1.5px solid #E8E4DC !important;
  border-radius: 20px !important; padding: 6px 14px !important;
  font-size: 12px !important; font-weight: 600 !important;
  color: #534AB7 !important; cursor: pointer !important;
  transition: all 0.2s !important;
}
[data-testid="stRadio"] label:hover { border-color: #7C65EF !important; background: #EDE9FE !important; }

/* F) CSS animations */
@keyframes floatY { 0%,100%{transform:translateY(0) rotate(-1.5deg)} 50%{transform:translateY(-10px) rotate(1.5deg)} }
@keyframes floatY2 { 0%,100%{transform:translateY(0) rotate(1deg)} 50%{transform:translateY(-7px) rotate(-1deg)} }
@keyframes pulseRing { 0%,100%{box-shadow:0 0 0 0 rgba(124,101,239,.3)} 60%{box-shadow:0 0 0 12px rgba(124,101,239,0)} }
@keyframes shimBtn { 0%{background-position:200% center} 100%{background-position:-200% center} }
@keyframes barWave { 0%,100%{transform:scaleY(0.3)} 50%{transform:scaleY(1)} }
@keyframes fadeSlideUp { 0%{opacity:0;transform:translateY(24px)} 100%{opacity:1;transform:translateY(0)} }
@keyframes orbFloat { 0%,100%{transform:translate(0,0) scale(1)} 33%{transform:translate(10px,-7px) scale(1.03)} 66%{transform:translate(-7px,5px) scale(0.97)} }
@keyframes noteFloat { 0%{transform:translateY(0) rotate(0deg);opacity:1} 100%{transform:translateY(-90px) rotate(30deg);opacity:0} }
@keyframes stepGlow { 0%,100%{border-color:rgba(124,101,239,.15)} 50%{border-color:rgba(124,101,239,.4)} }

/* 3D Card Depth Effect */
.story-card {
  background: white; border-radius: 20px; border: 1px solid rgba(0,0,0,0.07);
  box-shadow: 0 2px 4px rgba(0,0,0,0.04), 0 8px 24px rgba(124,101,239,0.08), 0 1px 2px rgba(0,0,0,0.03);
  padding: 18px 20px; margin-bottom: 12px; position: relative; overflow: hidden;
  transition: all 0.3s ease;
}
.story-card:hover {
  box-shadow: 0 4px 8px rgba(0,0,0,0.06), 0 16px 40px rgba(124,101,239,0.14);
  transform: translateY(-3px);
}

/* Chapter Specific Styles */
.chapter-bar {
  position: absolute; left: 0; top: 0; bottom: 0; width: 4px; border-radius: 0 4px 4px 0;
}
.c1-bar { background: linear-gradient(to bottom, #7C65EF, #A78BFA); }
.c2-bar { background: linear-gradient(to bottom, #F87153, #FCA184); }
.c3-bar { background: linear-gradient(to bottom, #34D399, #6EE7B7); }
.c4-bar { background: linear-gradient(to bottom, #F59E0B, #FCD34D); }
.c5-bar { background: linear-gradient(to bottom, #EC4899, #F9A8D4); }

.chapter-orb {
  width: 40px; height: 40px; border-radius: 12px; font-size: 16px; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
}
.c1-orb { background: #EDE9FE; color: #534AB7; }
.c2-orb { background: #FFF7ED; color: #9A3412; }
.c3-orb { background: #ECFDF5; color: #065F46; }
.c4-orb { background: #FFFBEB; color: #92400E; }
.c5-orb { background: #FDF2F8; color: #9D174D; }

/* Custom Streamlit expander override to look like story-card */
[data-testid="stExpander"] {
  background: white; border-radius: 20px; border: 1px solid rgba(0,0,0,0.07);
  box-shadow: 0 2px 4px rgba(0,0,0,0.04), 0 8px 24px rgba(124,101,239,0.08), 0 1px 2px rgba(0,0,0,0.03);
  margin-bottom: 12px; overflow: hidden;
  transition: all 0.3s ease;
}
[data-testid="stExpander"]:hover {
  box-shadow: 0 4px 8px rgba(0,0,0,0.06), 0 16px 40px rgba(124,101,239,0.14);
  transform: translateY(-3px);
}
[data-testid="stExpanderDetails"] { padding: 18px 20px !important; }

/* Generate Button */
.gen-btn > button {
  background: linear-gradient(135deg,#7C65EF,#F87153,#7C65EF) !important; 
  background-size: 200% !important; 
  animation: shimBtn 3s linear infinite !important;
}

/* Floating particles container */
.particles-container { position: relative; display: inline-block; width: 100%; }
.particle { position: absolute; font-size: 20px; color: #7C65EF; pointer-events: none; opacity: 0; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------
if "first_visit" not in st.session_state:
    st.session_state.first_visit = True
if "total_notes" not in st.session_state:
    st.session_state.total_notes = 0
if "tracks_created" not in st.session_state:
    st.session_state.tracks_created = 0
if "has_generated" not in st.session_state:
    st.session_state.has_generated = False
if "active_chapter" not in st.session_state:
    st.session_state.active_chapter = 1

# Base directory & Model status
base_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(base_dir, "music_model.h5")
model_exists = os.path.exists(model_path)

# ---------------------------------------------------------
# SECTION 6 — SIDEBAR
# ---------------------------------------------------------
st.sidebar.markdown("""
<div style="display: flex; align-items: center; gap: 12px; margin-bottom: 30px;">
    <div style="width: 40px; height: 40px; background: linear-gradient(135deg,#7C65EF,#A78BFA); border-radius: 12px; display: flex; align-items: center; justify-content: center; color: white; font-size: 20px;">✦</div>
    <div>
        <div style="font-size: 15px; font-weight: 600; color: #1C1917; line-height: 1.2;">Melody AI</div>
        <div style="font-size: 11px; color: #9CA3AF;">Your personal composer</div>
    </div>
</div>
""", unsafe_allow_html=True)

nav_selection = st.sidebar.radio("Navigation", ["Create Music", "My Tracks", "About this AI"], label_visibility="collapsed")

# Model Status Card
status_dot = "🟢" if model_exists else "🟠"
status_title = "AI model ready" if model_exists else "Model needs training"
status_desc = "Trained and waiting for you" if model_exists else "Run python train.py first"

st.sidebar.markdown(f"""
<div style="background: white; border-radius: 12px; padding: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.04), 0 8px 24px rgba(124,101,239,0.08); margin-bottom: 20px; border: 1px solid rgba(0,0,0,0.07);">
    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
        <span style="font-size: 12px;">{status_dot}</span>
        <span style="font-weight: 600; color: #1C1917; font-size: 13px;">{status_title}</span>
    </div>
    <div style="color: #7A7060; font-size: 11px; margin-left: 20px;">{status_desc}</div>
</div>
""", unsafe_allow_html=True)

# Session Info
st.sidebar.markdown(f"""
<div style="padding: 0 4px;">
    <div style="display: flex; justify-content: space-between; font-size: 12px; color: #7A7060; margin-bottom: 8px;">
        <span>Tracks this session</span>
        <span style="font-weight: 600; color: #1C1917;">{st.session_state.tracks_created}</span>
    </div>
    <div style="display: flex; justify-content: space-between; font-size: 12px; color: #7A7060;">
        <span>Notes generated</span>
        <span style="font-weight: 600; color: #1C1917;">{st.session_state.total_notes:,}</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# MAIN CONTENT
# ---------------------------------------------------------
if nav_selection == "Create Music":
    
    # SECTION 8 — BEGINNER UX RULES: First visit banner
    if st.session_state.first_visit:
        st.markdown("""
        <div style="background: #EDE9FE; border-left: 4px solid #7C65EF; padding: 12px 16px; border-radius: 8px; margin-bottom: 24px; color: #534AB7; font-size: 14px; font-weight: 500;">
            👋 Welcome! You're about to create original music. No experience needed — just follow the chapters.
        </div>
        """, unsafe_allow_html=True)
        st.session_state.first_visit = False

    # ---------------------------------------------------------
    # SECTION 3 — HERO SECTION
    # ---------------------------------------------------------
    st.markdown("""
    <div style="background: linear-gradient(160deg, #F0EDFF 0%, #FFF4ED 40%, #F0F9FF 80%, #F5FFF8 100%); border-radius: 20px; padding: 40px 32px; text-align: center; position: relative; overflow: hidden; margin-bottom: 24px; border: 1px solid rgba(0,0,0,0.04);">
        <!-- Floating Orbs -->
        <div style="position: absolute; width: 220px; height: 220px; background: radial-gradient(circle, rgba(124,101,239,0.14), transparent 70%); border-radius: 50%; top: -60px; left: -40px; animation: orbFloat 7s ease-in-out infinite; pointer-events: none;"></div>
        <div style="position: absolute; width: 180px; height: 180px; background: radial-gradient(circle, rgba(248,113,83,0.12), transparent 70%); border-radius: 50%; top: -30px; right: -30px; animation: orbFloat 9s ease-in-out infinite 2s; pointer-events: none;"></div>
        <div style="position: absolute; width: 160px; height: 160px; background: radial-gradient(circle, rgba(52,211,153,0.10), transparent 70%); border-radius: 50%; bottom: -40px; left: 50%; animation: orbFloat 8s ease-in-out infinite 4s; pointer-events: none;"></div>
        
        <!-- Content -->
        <div style="position: relative; z-index: 10;">
            <div style="display: inline-block; background: rgba(124,101,239,.1); border: 1px solid rgba(124,101,239,.25); border-radius: 20px; padding: 5px 16px; font-size: 11px; font-weight: 600; color: #534AB7; margin-bottom: 16px;">
                ✦ Your musical journey begins
            </div>
            
            <h1 style="font-size: 32px; font-weight: 700; line-height: 1.15; margin-bottom: 16px; background: linear-gradient(135deg,#3C3489 0%,#7C65EF 40%,#F87153 80%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
                You don't need to know music. Just feel it.
            </h1>
            
            <p style="font-size: 13px; color: #7A7060; max-width: 360px; margin: 0 auto 32px auto; line-height: 1.65;">
                Follow 5 simple steps. The AI does everything. You get original music in under 2 minutes.
            </p>
            
            <div style="display: flex; justify-content: center; gap: 16px; flex-wrap: wrap;">
                <div style="background: white; border-radius: 16px; border: 1px solid rgba(0,0,0,0.07); box-shadow: 0 8px 32px rgba(124,101,239,0.1), 0 2px 8px rgba(0,0,0,0.04); padding: 12px 16px; display: inline-flex; align-items: center; gap: 10px; animation: floatY 4s ease-in-out infinite;">
                    <div style="width: 24px; height: 24px; border-radius: 50%; background: #EDE9FE; color: #7C65EF; display: flex; align-items: center; justify-content: center; font-size: 12px;">✦</div>
                    <div style="text-align: left;">
                        <div style="font-size: 12px; font-weight: 600; color: #1C1917;">No experience needed</div>
                        <div style="font-size: 10px; color: #7A7060;">seriously, zero</div>
                    </div>
                </div>
                <div style="background: white; border-radius: 16px; border: 1px solid rgba(0,0,0,0.07); box-shadow: 0 8px 32px rgba(124,101,239,0.1), 0 2px 8px rgba(0,0,0,0.04); padding: 12px 16px; display: inline-flex; align-items: center; gap: 10px; animation: floatY2 5s ease-in-out infinite;">
                    <div style="width: 24px; height: 24px; border-radius: 50%; background: #FFF7ED; color: #F87153; display: flex; align-items: center; justify-content: center; font-size: 12px;">⚡</div>
                    <div style="text-align: left;">
                        <div style="font-size: 12px; font-weight: 600; color: #1C1917;">Ready in 2 min</div>
                        <div style="font-size: 10px; color: #7A7060;">start to finish</div>
                    </div>
                </div>
                <div style="background: white; border-radius: 16px; border: 1px solid rgba(0,0,0,0.07); box-shadow: 0 8px 32px rgba(124,101,239,0.1), 0 2px 8px rgba(0,0,0,0.04); padding: 12px 16px; display: inline-flex; align-items: center; gap: 10px; animation: floatY 4.5s ease-in-out infinite;">
                    <div style="width: 24px; height: 24px; border-radius: 50%; background: #ECFDF5; color: #059669; display: flex; align-items: center; justify-content: center; font-size: 12px;">⬇️</div>
                    <div style="text-align: left;">
                        <div style="font-size: 12px; font-weight: 600; color: #1C1917;">Yours to keep</div>
                        <div style="font-size: 10px; color: #7A7060;">download anytime</div>
                    </div>
                </div>
            </div>
            
            <div style="margin-top: 32px;">
                <button style="background: linear-gradient(135deg,#7C65EF,#A78BFA); border: none; color: white; font-weight: 700; border-radius: 14px; padding: 13px 26px; font-size: 14px; cursor: pointer; animation: pulseRing 2.5s infinite; box-shadow: 0 4px 12px rgba(124,101,239,0.3);">
                    ✦ Start your journey
                </button>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ---------------------------------------------------------
    # SECTION 5 — PROGRESS TRACKER
    # ---------------------------------------------------------
    # We will fake the progress tracker with HTML based on active_chapter
    def get_dot_style(chapter_num, active_num):
        if chapter_num < active_num:
            return "background: #34D399; color: white; border: none; transform: scale(1);" # Done
        elif chapter_num == active_num:
            return "background: linear-gradient(135deg,#7C65EF,#A78BFA); color: white; border: none; transform: scale(1.2);" # Active
        else:
            return "background: white; color: #C4B9A8; border: 1.5px solid #E8E4DC;" # Pending

    def get_line_style(chapter_num, active_num):
        if chapter_num < active_num:
            return "background: #34D399;"
        return "background: #E8E4DC;"

    active_c = st.session_state.active_chapter

    st.markdown(f"""
    <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 32px; padding: 0 20px; width: 100%; max-width: 600px; margin-left: auto; margin-right: auto;">
        <!-- Step 1 -->
        <div style="display: flex; flex-direction: column; align-items: center; position: relative; z-index: 2;">
            <div style="width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 700; transition: all 0.3s; {get_dot_style(1, active_c)}">{"✓" if 1 < active_c else "1"}</div>
            <div style="font-size: 10px; color: #7A7060; position: absolute; top: 34px; white-space: nowrap;">Genre</div>
        </div>
        <div style="flex: 1; height: 2px; transition: all 0.3s; {get_line_style(1, active_c)}"></div>
        
        <!-- Step 2 -->
        <div style="display: flex; flex-direction: column; align-items: center; position: relative; z-index: 2;">
            <div style="width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 700; transition: all 0.3s; {get_dot_style(2, active_c)}">{"✓" if 2 < active_c else "2"}</div>
            <div style="font-size: 10px; color: #7A7060; position: absolute; top: 34px; white-space: nowrap;">Mood</div>
        </div>
        <div style="flex: 1; height: 2px; transition: all 0.3s; {get_line_style(2, active_c)}"></div>
        
        <!-- Step 3 -->
        <div style="display: flex; flex-direction: column; align-items: center; position: relative; z-index: 2;">
            <div style="width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 700; transition: all 0.3s; {get_dot_style(3, active_c)}">{"✓" if 3 < active_c else "3"}</div>
            <div style="font-size: 10px; color: #7A7060; position: absolute; top: 34px; white-space: nowrap;">Settings</div>
        </div>
        <div style="flex: 1; height: 2px; transition: all 0.3s; {get_line_style(3, active_c)}"></div>
        
        <!-- Step 4 -->
        <div style="display: flex; flex-direction: column; align-items: center; position: relative; z-index: 2;">
            <div style="width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 700; transition: all 0.3s; {get_dot_style(4, active_c)}">{"✓" if 4 < active_c else "4"}</div>
            <div style="font-size: 10px; color: #7A7060; position: absolute; top: 34px; white-space: nowrap;">Generate</div>
        </div>
        <div style="flex: 1; height: 2px; transition: all 0.3s; {get_line_style(4, active_c)}"></div>
        
        <!-- Step 5 -->
        <div style="display: flex; flex-direction: column; align-items: center; position: relative; z-index: 2;">
            <div style="width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 700; transition: all 0.3s; {get_dot_style(5, active_c)}">{"✓" if 5 < active_c else "5"}</div>
            <div style="font-size: 10px; color: #7A7060; position: absolute; top: 34px; white-space: nowrap;">Listen</div>
        </div>
    </div>
    <div style="height: 20px;"></div>
    """, unsafe_allow_html=True)


    # ---------------------------------------------------------
    # SECTION 4 — THE 5 CHAPTER STEPS
    # ---------------------------------------------------------
    
    # CHAPTER 1 — Choose your world
    with st.expander("Chapter 1: Choose your world", expanded=(st.session_state.active_chapter == 1)):
        st.markdown("""
        <div class="chapter-bar c1-bar"></div>
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
            <div class="chapter-orb c1-orb">1</div>
            <div>
                <div style="font-size: 10px; text-transform: uppercase; letter-spacing: 0.05em; color: #9CA3AF;">Chapter 1</div>
                <div style="font-size: 14px; font-weight: 600; color: #1C1917;">Choose your world 🌍</div>
            </div>
        </div>
        <p style="font-size: 12px; color: #7A7060; line-height: 1.6; margin-bottom: 16px;">Pick the genre that matches your vibe. Each one teaches the AI a completely different musical language.</p>
        """, unsafe_allow_html=True)
        
        genre = st.radio("Select Genre", ["Classical", "Jazz", "Ambient", "Blues", "Cinematic", "Lo-fi"], horizontal=True, label_visibility="collapsed", help="Select the base musical genre for the AI to learn from.")
        
        if genre == "Classical": st.caption("🏰 The AI will learn from elegant piano patterns and orchestral harmonies.")
        elif genre == "Jazz": st.caption("🎷 The AI will learn from smooth syncopations and soulful chords.")
        elif genre == "Ambient": st.caption("🌙 The AI will learn from calm, dreamy, and slow-moving soundscapes.")
        elif genre == "Blues": st.caption("🎸 The AI will learn from deep, emotional scales and expressive bends.")
        elif genre == "Cinematic": st.caption("🎬 The AI will learn from epic, dramatic, and soaring progressions.")
        elif genre == "Lo-fi": st.caption("🎧 The AI will learn from cozy, relaxed, and repetitive chill beats.")
        
        if st.button("Confirm Genre", key="btn_c1"):
            st.session_state.active_chapter = 2
            st.rerun()

    # CHAPTER 2 — Set the mood
    with st.expander("Chapter 2: Set the mood", expanded=(st.session_state.active_chapter == 2)):
        st.markdown("""
        <div class="chapter-bar c2-bar"></div>
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
            <div class="chapter-orb c2-orb">2</div>
            <div>
                <div style="font-size: 10px; text-transform: uppercase; letter-spacing: 0.05em; color: #9CA3AF;">Chapter 2</div>
                <div style="font-size: 14px; font-weight: 600; color: #1C1917;">Set the mood 🎭</div>
            </div>
        </div>
        <p style="font-size: 12px; color: #7A7060; line-height: 1.6; margin-bottom: 16px;">How do you want the music to feel? No music knowledge needed — just pick your emotion.</p>
        """, unsafe_allow_html=True)
        
        mood = st.radio("Select Mood", ["Peaceful", "Energetic", "Melancholic", "Romantic", "Mysterious", "Joyful"], horizontal=True, label_visibility="collapsed", help="Choose the emotional tone of the music.")
        
        if st.button("Confirm Mood", key="btn_c2"):
            st.session_state.active_chapter = 3
            st.rerun()

    # CHAPTER 3 — Tune the creativity
    with st.expander("Chapter 3: Tune the creativity", expanded=(st.session_state.active_chapter == 3)):
        st.markdown("""
        <div class="chapter-bar c3-bar"></div>
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
            <div class="chapter-orb c3-orb">3</div>
            <div>
                <div style="font-size: 10px; text-transform: uppercase; letter-spacing: 0.05em; color: #9CA3AF;">Chapter 3</div>
                <div style="font-size: 14px; font-weight: 600; color: #1C1917;">Tune the creativity 🎛️</div>
            </div>
        </div>
        <p style="font-size: 12px; color: #7A7060; line-height: 1.6; margin-bottom: 16px;">Think of this like a dial from safe and familiar to wild and unexpected.</p>
        """, unsafe_allow_html=True)
        
        creativity = st.slider("Creativity", 0.3, 2.0, 1.0, 0.1, help="Adjusts how experimental or predictable the generated notes will be.")
        
        if creativity < 0.7: creat_label = "Safe"
        elif creativity <= 1.2: creat_label = "Balanced"
        elif creativity <= 1.7: creat_label = "Wild"
        else: creat_label = "Cosmic/Supernova"
        
        st.markdown(f'<p style="font-size: 12px; color: #7C65EF; font-weight: 600; margin-top: -10px; margin-bottom: 16px;">Current Level: {creat_label}</p>', unsafe_allow_html=True)
        
        length = st.slider("Length (notes)", 100, 1000, 500, 50, help="Total number of notes the AI will generate.")
        
        total_seconds = int(length * 0.25)
        mins, secs = divmod(total_seconds, 60)
        st.markdown(f'<p style="font-size: 12px; color: #7A7060; margin-top: -10px; margin-bottom: 16px;">Approx {mins}m {secs}s of music</p>', unsafe_allow_html=True)
        
        if st.button("Lock in my settings", key="btn_c3"):
            st.session_state.active_chapter = 4
            st.rerun()

    # CHAPTER 4 — Generate your music
    with st.expander("Chapter 4: Generate your music", expanded=(st.session_state.active_chapter == 4)):
        st.markdown("""
        <div class="chapter-bar c4-bar"></div>
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
            <div class="chapter-orb c4-orb">4</div>
            <div>
                <div style="font-size: 10px; text-transform: uppercase; letter-spacing: 0.05em; color: #9CA3AF;">Chapter 4</div>
                <div style="font-size: 14px; font-weight: 600; color: #1C1917;">Generate your music ✨</div>
            </div>
        </div>
        <p style="font-size: 12px; color: #7A7060; line-height: 1.6; margin-bottom: 16px;">Hit the button. The AI will compose something completely original — unique to this exact moment.</p>
        
        <div style="background: #F9F8FF; border-left: 4px solid #7C65EF; padding: 12px 16px; border-radius: 0 8px 8px 0; margin-bottom: 24px; font-size: 12px; color: #534AB7;">
            The AI reads through hundreds of musical patterns it learned from real songs, then improvises something brand new — like a jazz musician who never plays the same thing twice.
        </div>
        """, unsafe_allow_html=True)
        
        if not model_exists:
            st.warning("The AI needs to learn first. Ask your developer to run `python train.py` — it takes about an hour.")
            st.button("✦ Compose my music now", disabled=True, key="btn_c4_disabled")
        else:
            # We'll use a container with a custom class for the big button
            btn_container = st.container()
            with btn_container:
                st.markdown('<div class="gen-btn">', unsafe_allow_html=True)
                generate_clicked = st.button("✦ Compose my music now", help="Start the neural network generation process.", use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                if generate_clicked:
                    try:
                        with st.spinner("Composing your melody..."):
                            st.markdown("""
                            <script>
                            // This is a workaround for floating notes since Streamlit handles DOM updates its own way.
                            const container = window.parent.document.querySelector('.stButton');
                            if(container) {
                                for(let i=0; i<10; i++) {
                                    let note = window.parent.document.createElement('div');
                                    note.innerHTML = ['♩','♪','♫','♬'][Math.floor(Math.random()*4)];
                                    note.style.position = 'absolute';
                                    note.style.left = (50 + (Math.random()*40-20)) + '%';
                                    note.style.color = '#7C65EF';
                                    note.style.fontSize = '24px';
                                    note.style.pointerEvents = 'none';
                                    note.style.animation = `noteFloat ${1+Math.random()}s ease-out forwards`;
                                    container.appendChild(note);
                                }
                            }
                            </script>
                            """, unsafe_allow_html=True)
                            
                            script_path = os.path.join(base_dir, "generate.py")
                            res = subprocess.run([sys.executable, script_path, "--temperature", str(creativity), "--notes", str(length)], capture_output=True, text=True)
                        
                        if res.returncode == 0:
                            st.session_state.has_generated = True
                            st.session_state.tracks_created += 1
                            st.session_state.total_notes += length
                            st.session_state.active_chapter = 5
                            st.balloons()
                            st.toast("Your music is ready!", icon="✦")
                            st.rerun()
                        else:
                            st.error("Something went a little sideways — try again or check that the model is trained.")
                    except Exception as e:
                        st.error("Something went a little sideways — try again or check that the model is trained.")


    # CHAPTER 5 — Listen and download
    with st.expander("Chapter 5: Listen and download", expanded=(st.session_state.active_chapter == 5)):
        st.markdown("""
        <div class="chapter-bar c5-bar"></div>
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
            <div class="chapter-orb c5-orb">5</div>
            <div>
                <div style="font-size: 10px; text-transform: uppercase; letter-spacing: 0.05em; color: #9CA3AF;">Chapter 5</div>
                <div style="font-size: 14px; font-weight: 600; color: #1C1917;">Listen and download 🎧</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if not st.session_state.has_generated:
            st.markdown("""
            <div style="text-align: center; padding: 20px; color: #C4B9A8;">
                <div style="font-size: 24px; margin-bottom: 8px;">⬆️</div>
                <div style="font-size: 13px;">Generate your music in Chapter 4 first</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            output_mid = os.path.join(base_dir, "output.mid")
            output_wav = os.path.join(base_dir, "output.wav")
            track_name = f"your_melody_{st.session_state.tracks_created:03d}.mid"
            
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <div style="font-weight: 600; color: #1C1917; font-size: 15px;">{track_name}</div>
                <div style="background: #ECFDF5; color: #065F46; padding: 4px 12px; border-radius: 12px; font-size: 10px; font-weight: 700; text-transform: uppercase;">Ready</div>
            </div>
            
            <!-- Animated Waveform -->
            <div style="display: flex; align-items: flex-end; justify-content: center; gap: 4px; height: 60px; margin-bottom: 20px;">
                {''.join([f'<div style="width: 5px; background: linear-gradient(to top,#7C65EF,#F87153); border-radius: 3px; height: 100%; animation: barWave {0.7 + (i%5)*0.15}s ease infinite {i*0.08}s;"></div>' for i in range(25)])}
            </div>
            
            <!-- Player Controls -->
            <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 24px;">
                <div style="width: 36px; height: 36px; border-radius: 50%; background: linear-gradient(135deg,#7C65EF,#A78BFA); display: flex; align-items: center; justify-content: center; color: white; cursor: pointer; animation: pulseRing 2s infinite;">▶</div>
                <div style="flex: 1; height: 5px; background: #E8E4DC; border-radius: 3px; position: relative; overflow: hidden; cursor: pointer;">
                    <div style="position: absolute; left: 0; top: 0; bottom: 0; width: 45%; background: linear-gradient(to right, #7C65EF, #A78BFA);"></div>
                </div>
                <div style="font-size: 11px; color: #7A7060; font-variant-numeric: tabular-nums;">0:00</div>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if os.path.exists(output_mid):
                    try:
                        with open(output_mid, "rb") as f:
                            st.download_button("Download MIDI", f.read(), track_name, mime="audio/midi", use_container_width=True)
                    except Exception:
                        st.error("Could not read MIDI output.")
            with col2:
                if os.path.exists(output_wav):
                    try:
                        with open(output_wav, "rb") as f:
                            st.download_button("Download WAV", f.read(), track_name.replace(".mid", ".wav"), mime="audio/wav", use_container_width=True)
                    except Exception:
                        st.error("Could not read WAV output.")
                else:
                    st.markdown("""
                    <div style="font-size: 11px; color: #C4B9A8; text-align: center; padding: 10px; border: 1px solid #E8E4DC; border-radius: 12px; height: 100%;">
                        Install <b>FluidSynth</b> to enable direct WAV audio downloads.
                    </div>
                    """, unsafe_allow_html=True)


elif nav_selection == "My Tracks":
    st.markdown("""
    <h2 style="font-size: 24px; font-weight: 700; color: #1C1917; margin-bottom: 8px;">My Tracks</h2>
    <p style="font-size: 13px; color: #7A7060; margin-bottom: 32px;">All your generated compositions saved in the project directory.</p>
    """, unsafe_allow_html=True)
    
    mid_files = [f for f in os.listdir(base_dir) if f.endswith(".mid") and os.path.isfile(os.path.join(base_dir, f))]
    
    if mid_files:
        for idx, m_file in enumerate(sorted(mid_files)):
            file_path = os.path.join(base_dir, m_file)
            try:
                f_stats = os.stat(file_path)
                f_size_kb = f_stats.st_size / 1024.0
                f_date = datetime.datetime.fromtimestamp(f_stats.st_ctime).strftime("%b %d, %Y")
                est_notes = int(f_size_kb * 100) # rough estimate
            except Exception:
                f_size_kb = 0.0
                f_date = "Unknown date"
                est_notes = 0
                
            delay = idx * 0.12
            st.markdown(f"""
            <div style="background: white; border-radius: 16px; border: 1px solid rgba(0,0,0,0.07); padding: 16px 20px; margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center; animation: fadeSlideUp 0.6s ease both {delay}s;">
                <div>
                    <div style="font-weight: 600; color: #1C1917; font-size: 15px; margin-bottom: 4px;">{m_file}</div>
                    <div style="font-size: 11px; color: #7A7060;">{f_size_kb:.1f} KB • {f_date} • ♪ ~{est_notes} notes</div>
                </div>
                <div style="display: flex; align-items: center; gap: 16px;">
                    <div style="display: flex; align-items: flex-end; gap: 3px; height: 24px;">
                        {''.join([f'<div style="width: 3px; background: linear-gradient(to top,#7C65EF,#F87153); border-radius: 2px; height: 100%; animation: barWave {0.7 + (i%3)*0.1}s ease infinite {i*0.1}s;"></div>' for i in range(5)])}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            try:
                with open(file_path, "rb") as f:
                    st.download_button("Download", f.read(), m_file, mime="audio/midi", key=f"dl_{m_file}")
            except Exception:
                pass
    else:
        st.markdown("""
        <div style="text-align: center; padding: 60px 20px;">
            <div style="position: relative; width: 120px; height: 120px; margin: 0 auto 24px auto;">
                <div style="position: absolute; width: 80px; height: 80px; border-radius: 50%; background: rgba(124,101,239,0.1); top: 0; left: 0;"></div>
                <div style="position: absolute; width: 80px; height: 80px; border-radius: 50%; background: rgba(248,113,83,0.1); top: 20px; right: 0;"></div>
                <div style="position: absolute; width: 80px; height: 80px; border-radius: 50%; background: rgba(52,211,153,0.1); bottom: 0; left: 20px;"></div>
                <div style="position: absolute; width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; font-size: 32px;">🎵</div>
            </div>
            <h3 style="font-size: 16px; font-weight: 600; color: #1C1917; margin-bottom: 8px;">No melodies yet</h3>
            <p style="font-size: 13px; color: #7A7060;">Your first creation is waiting</p>
        </div>
        """, unsafe_allow_html=True)


elif nav_selection == "About this AI":
    st.markdown("""
    <h2 style="font-size: 24px; font-weight: 700; color: #1C1917; margin-bottom: 8px;">About Melody AI</h2>
    <p style="font-size: 13px; color: #7A7060; margin-bottom: 32px;">Learn how the deep learning model creates original music.</p>
    
    <div style="background: white; border-radius: 16px; border: 1px solid rgba(0,0,0,0.07); padding: 24px; line-height: 1.6; color: #1C1917; font-size: 14px;">
        <p>This AI uses a Long Short-Term Memory (LSTM) neural network. LSTMs are a type of recurrent neural network capable of learning order dependence in sequence prediction problems, making them perfect for music.</p>
        <p>When you click generate, the AI doesn't just paste pre-made clips together. It literally predicts the next note based on the pattern of the notes that came before it, composing a completely new sequence every time.</p>
    </div>
    """, unsafe_allow_html=True)
