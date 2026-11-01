"""Boréal Marché V4 — visual, explainable grocery recommendation storefront.
Run from project root: streamlit run app/streamlit_app.py
Uses offline JSON rules; never runs Apriori in the web app.
"""
from __future__ import annotations
import json
import re
from pathlib import Path
from html import escape
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
st.set_page_config(page_title="Boréal Marché | Smart Grocery", page_icon="🥬", layout="wide", initial_sidebar_state="collapsed")

st.markdown('''<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito+Sans:wght@400;500;600;700;800;900&display=swap');
html,body,[data-testid="stApp"] {font-family:'Nunito Sans',sans-serif;color:#183c31}
.stApp {background:linear-gradient(125deg,#f7fff8,#f5fbf7 60%,#fefcf3)}
.block-container {max-width:1850px;padding:1rem 1.5rem 4rem}
[data-testid="stHeader"] {background:transparent}
h1,h2,h3 {color:#0b5639!important}
.hero {background:linear-gradient(105deg,#e6fff0 0%,#fff8d7 47%,#d9f8e5 100%);border:1px solid #ccead8;border-radius:24px;padding:22px 30px;box-shadow:0 8px 28px #1a6d3d12;margin-bottom:14px;display:flex;align-items:center;justify-content:space-between;gap:15px}
.hero-title {font-size:2.6rem;font-weight:900;color:#075637;line-height:1.1}
.hero-tag {font-size:.78rem;letter-spacing:.14em;font-weight:900;color:#258355}
.hero-desc {color:#486a56;font-size:.91rem;margin-top:7px}
.hero-art {font-size:3.7rem;letter-spacing:.07em;white-space:nowrap}
.kpi {background:white;border:1px solid #dceee2;border-radius:16px;padding:13px 17px;box-shadow:0 3px 12px #1a59320c}
.kpi-num {font-size:1.65rem;font-weight:900;color:#087449;line-height:1.3}
.kpi-label {font-size:.76rem;color:#5a7668}
.section-head {font-size:1.22rem;font-weight:900;color:#0b5c3c;margin:18px 0 9px}
.sidebox {background:#fff;border:1px solid #d7eee1;border-radius:17px;padding:15px;margin:7px 0 13px;box-shadow:0 4px 16px #246f3d0c}
.howbox {background:#e7faeb;border-radius:16px;padding:15px;line-height:2;color:#205c40;font-size:.89rem}
.product {background:white;border:1px solid #e0ece3;border-radius:17px;padding:12px;box-shadow:0 5px 16px #1b6a3912;min-height:220px}
.product-art {height:128px;display:flex;align-items:center;justify-content:center;border-radius:12px;background:linear-gradient(130deg,#f5fce8,#e3f8ec);font-size:3.7rem;margin-bottom:10px}
.product-photo {width:100%;height:128px;object-fit:cover;border-radius:12px;margin-bottom:10px} 
.product-name {font-weight:900;font-size:.93rem;color:#173e30;min-height:21px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.product-en {font-size:.74rem;color:#6a8075;min-height:20px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.product-category {display:inline-block;border-radius:20px;background:#e8f7ee;color:#197247;font-size:.69rem;padding:3px 9px;margin-top:5px}
.product-price {font-size:1.18rem;font-weight:900;color:#087b48;margin-top:7px}
.basketbox {background:white;border:1px solid #d9e9de;border-radius:14px;padding:11px 13px;margin:6px 0}
.emptybox {background:#effaf5;border:1px dashed #9fd3b5;border-radius:16px;padding:22px 12px;text-align:center;color:#3b7656}
.recobox {background:white;border:1px solid #d4e8da;border-left:5px solid #16a368;border-radius:16px;padding:12px;margin:10px 0 5px;box-shadow:0 5px 15px #246b3e12}
.strength-track{height:9px;background:#e8f1e9;border-radius:20px;overflow:hidden;margin:8px 0 4px}.strength-fill{height:100%;background:linear-gradient(90deg,#3bc77d,#087c51);border-radius:20px}.rec-name {font-weight:900;color:#17533a;font-size:.98rem}
.small-muted {color:#688477;font-size:.76rem}
.chip {display:inline-block;background:#eaf8ed;color:#216a46;border-radius:8px;padding:4px 7px;margin:4px 4px 0 0;font-size:.73rem;font-weight:800}
.chip-gold {background:#fff2ca;color:#855c00}
.stButton>button {border-radius:10px!important;font-weight:800!important;min-height:37px}
.stButton>button[kind="primary"] {background:#078650!important;color:white!important;border-color:#078650!important}
.stButton>button[kind="primary"]:hover {background:#076c43!important}
[data-testid="stTextInput"] input,[data-testid="stSelectbox"]>div>div {border-radius:11px}
[data-testid="stVerticalBlock"] {gap:.5rem}
@media(max-width:850px){.hero-title{font-size:1.8rem}.hero-art{font-size:2rem}.block-container{padding:1rem .7rem}}

/* BOREAL MARCHE — COLOR ENHANCEMENT */
.stApp {
    background: linear-gradient(125deg,#effbf2,#fffdf2 55%,#e5f7ec);
}

.hero {
    border: 2px solid #4dbb81 !important;
    box-shadow: 0 12px 32px rgba(5,95,55,.17) !important;
}

.hero-title {
    color: #034d34 !important;
    text-shadow: 1px 2px 0 rgba(255,255,255,.8);
}

.hero-tag {
    color: #075d3e !important;
}

.kpi {
    border: 1px solid #a8dcb9 !important;
    border-top: 4px solid #07915b !important;
    box-shadow: 0 5px 16px rgba(0,90,50,.10) !important;
}

.kpi-num {
    color: #006a43 !important;
    font-size: 1.9rem !important;
}

.kpi-label {
    color: #3a6250 !important;
    font-weight: 700 !important;
}

.section-head {
    color: #034d34 !important;
    font-size: 1.35rem !important;
}

.product {
    border: 1px solid #b6dfc3 !important;
    box-shadow: 0 6px 20px rgba(0,90,50,.11) !important;
}

.product-art {
    background: linear-gradient(135deg,#e1f8e9,#fff1c7) !important;
}

.product-name {
    color: #064b34 !important;
}

.product-price {
    color: #007747 !important;
    font-size: 1.32rem !important;
}

.product-category, .chip {
    background: #d8f4e2 !important;
    color: #075d3c !important;
}

.basketbox {
    border: 1px solid #a9dabb !important;
    box-shadow: 0 3px 12px rgba(0,90,50,.08);
}

.recobox {
    border: 1px solid #a5d9b8 !important;
    border-left: 6px solid #008d58 !important;
    box-shadow: 0 6px 18px rgba(0,90,50,.12) !important;
}

.chip-gold {
    background: #ffedb3 !important;
    color: #795000 !important;
}

.stButton > button[kind="primary"] {
    background: #007e4d !important;
    color: white !important;
    border-color: #007e4d !important;
}

.stButton > button[kind="primary"]:hover {
    background: #005e3a !important;
}

.howbox {
    background: #d9f4e3 !important;
    border: 1px solid #a5dbb9;
}

.credit-panel {
    background: #ffffff !important;
    border: 2px solid #e4b447 !important;
    border-left: 7px solid #c99322 !important;
    border-radius: 16px !important;
    padding: 18px 22px !important;
    box-shadow: 0 6px 18px rgba(87,67,0,.12);
    color: #064b34 !important;
    font-size: 1.08rem !important;
    font-weight: 600 !important;
    line-height: 2 !important;
    max-width: 750px !important;
}

.credit-panel b {
    color: #006a43 !important;
    font-weight: 900 !important;
}

@media (max-width: 850px) {
    .credit-panel {
        font-size: .92rem !important;
        padding: 12px !important;
    }
}


/* BOREAL EYE COMFORT THEME */

/* Soft neutral background */
.stApp {
    background: #f1f4f0 !important;
    color: #203c30 !important;
}

/* Main text */
.stApp p,
.stApp label,
.stApp span {
    color: inherit;
}

/* Clear section headings */
.section-head {
    color: #174d39 !important;
}

/* Softer banner */
.hero {
    background: linear-gradient(
        110deg,#dcefe2,#f4efd8,#dcefe2
    ) !important;
    border: 1px solid #a5cbb3 !important;
}

/* White cards for readability */
.kpi,
.product,
.basketbox,
.recobox {
    background: #ffffff !important;
}

/* Inputs and dropdown controls */
[data-testid="stSelectbox"] [data-baseweb="select"],
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input {
    background: #ffffff !important;
    color: #183c2c !important;
    border-radius: 9px !important;
}

/* Dropdown popup menu */
div[data-baseweb="popover"],
div[data-baseweb="menu"],
ul[role="listbox"] {
    background: #ffffff !important;
    color: #183c2c !important;
    border: 1px solid #b8cec0 !important;
}

/* Dropdown option text */
li[role="option"],
div[role="option"] {
    color: #183c2c !important;
    background: #ffffff !important;
}

/* Highlight selected or hovered options */
li[role="option"]:hover,
div[role="option"]:hover,
li[aria-selected="true"],
div[aria-selected="true"] {
    background: #dcefe2 !important;
    color: #064a31 !important;
}

/* Labels and captions */
[data-testid="stWidgetLabel"],
[data-testid="stCaptionContainer"] {
    color: #355a47 !important;
}

/* Buttons */
.stButton > button {
    font-weight: 700 !important;
}

/* Academic credits */
.credit-panel {
    background: #fffdf5 !important;
    border: 1px solid #c9b77d !important;
    border-left: 5px solid #b88c32 !important;
    color: #174d39 !important;
}


/* BOREAL VIBRANT MODERN THEME */

/* Comfortable page background */
.stApp {
    background: linear-gradient(135deg,#edf5ee,#f7f4e8 60%,#e4f2e8) !important;
    color: #183d30 !important;
}

/* Vibrant grocery banner */
.hero {
    background: linear-gradient(110deg,#c6f2d8,#fff0b7 55%,#b8ecd0) !important;
    border: 2px solid #35b579 !important;
    box-shadow: 0 12px 30px rgba(4,98,58,.17) !important;
}

.hero-title {
    color: #034d32 !important;
    text-shadow: 1px 2px 0 rgba(255,255,255,.65);
}

/* Stronger headings */
.section-head {
    color: #075b3d !important;
    font-size: 1.4rem !important;
    font-weight: 900 !important;
}

/* Dashboard statistics */
.kpi {
    background: linear-gradient(145deg,#ffffff,#e8f8ee) !important;
    border: 1px solid #8ad6a8 !important;
    border-top: 5px solid #07945c !important;
    border-radius: 18px !important;
    box-shadow: 0 7px 18px rgba(0,100,55,.12) !important;
}

.kpi-num {
    color: #006d44 !important;
    font-size: 2rem !important;
}

/* Product cards */
.product {
    background: #fffefa !important;
    border: 1px solid #a9ddbc !important;
    border-radius: 18px !important;
    box-shadow: 0 6px 18px rgba(0,80,40,.12) !important;
    transition: transform .2s ease, box-shadow .2s ease;
}

.product:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 25px rgba(0,90,45,.20) !important;
}

.product-art {
    background: linear-gradient(135deg,#d5f7e2,#fff0bd) !important;
}

.product-price {
    color: #007847 !important;
    font-size: 1.4rem !important;
}

/* Basket and recommendations */
.basketbox {
    background: #ffffff !important;
    border: 1px solid #91d7ad !important;
    border-radius: 14px !important;
}

.recobox {
    background: #fffefa !important;
    border: 1px solid #a0dcb8 !important;
    border-left: 6px solid #07945c !important;
    border-radius: 16px !important;
    box-shadow: 0 6px 16px rgba(0,90,50,.12) !important;
}

/* Clear buttons */
.stButton > button[kind="primary"] {
    background: #008753 !important;
    color: #ffffff !important;
    border-color: #008753 !important;
}

.stButton > button[kind="primary"]:hover {
    background: #006c42 !important;
}

/* Readable dropdowns */
[data-testid="stSelectbox"] [data-baseweb="select"] {
    background: #ffffff !important;
    border: 1px solid #83c9a1 !important;
    border-radius: 10px !important;
}

[data-testid="stSelectbox"] [data-baseweb="select"] * {
    color: #173f2e !important;
}

div[data-baseweb="popover"],
div[data-baseweb="menu"],
ul[role="listbox"] {
    background: #ffffff !important;
    color: #173f2e !important;
}

li[role="option"],
div[role="option"] {
    background: #ffffff !important;
    color: #173f2e !important;
}

li[role="option"]:hover,
div[role="option"]:hover,
li[aria-selected="true"],
div[aria-selected="true"] {
    background: #c9efda !important;
    color: #064b32 !important;
}

/* Academic credit panel */
.credit-panel {
    background: #fffdf2 !important;
    border: 2px solid #d7aa38 !important;
    border-left: 7px solid #c28d18 !important;
    box-shadow: 0 7px 20px rgba(120,80,0,.12) !important;
}


/* BOREAL FINAL VISUAL DESIGN */

/* Background and typography */
.stApp {
    background: #f0f2ee !important;
    color: #171c19 !important;
}

html, body, .stApp,
.stApp p, .stApp label {
    font-family: 'Nunito Sans', sans-serif;
}

.stApp p, .stApp label {
    color: #202720;
}

/* Premium grocery banner */
.hero {
    background: linear-gradient(
        115deg,#bcebd1 0%,#f8edc7 55%,#c2e9d5 100%
    ) !important;
    border: 2px solid #60ba89 !important;
    border-radius: 24px !important;
    box-shadow: 0 12px 28px rgba(12,70,43,.13) !important;
}

.hero-title {
    color: #102d20 !important;
    font-size: 4.2rem !important;
    letter-spacing: -.035em;
    line-height: 1.12 !important;
    text-shadow: none !important;
}

.hero-tag {
    color: #135b3b !important;
    font-size: .93rem !important;
}

.hero-desc {
    color: #1c3025 !important;
}

/* Academic credits */
.credit-panel {
    background: #fff9e8 !important;
    border: 2px solid #d7a52d !important;
    border-left: 8px solid #b57c10 !important;
    border-radius: 16px !important;
    box-shadow: 0 7px 20px rgba(90,65,10,.12) !important;
    color: #151b17 !important;
    font-size: 1.13rem !important;
    line-height: 2 !important;
    font-weight: 700 !important;
}

.credit-panel b {
    color: #064a2d !important;
}

/* Statistics */
.kpi {
    background: #ffffff !important;
    border: 1px solid #b2d5bf !important;
    border-top: 5px solid #008456 !important;
    border-radius: 18px !important;
    box-shadow: 0 6px 18px rgba(0,60,35,.09) !important;
}

.kpi-num {
    color: #075e3d !important;
    font-size: 2rem !important;
}

.kpi-label {
    color: #303d34 !important;
    font-size: .85rem !important;
    font-weight: 700 !important;
}

/* Section titles */
.section-head {
    color: #15291d !important;
    font-size: 1.43rem !important;
    font-weight: 900 !important;
}

/* Product catalogue */
.product {
    background: #fffefa !important;
    border: 1px solid #b4d4be !important;
    border-radius: 18px !important;
    box-shadow: 0 5px 16px rgba(0,50,25,.09) !important;
    transition: transform .2s, box-shadow .2s;
}

.product:hover {
    transform: translateY(-3px);
    box-shadow: 0 11px 25px rgba(0,60,35,.16) !important;
}

.product-art {
    background: linear-gradient(135deg,#d8f1e1,#f9eec6) !important;
}

.product-name {
    color: #161d18 !important;
    font-size: 1rem !important;
}

.product-en {
    color: #46544b !important;
    font-size: .82rem !important;
}

.product-price {
    color: #006b43 !important;
    font-size: 1.42rem !important;
}

/* Basket and recommendations */
.basketbox, .recobox {
    background: #ffffff !important;
    border: 1px solid #b2d5bf !important;
    border-radius: 15px !important;
    box-shadow: 0 4px 14px rgba(0,55,30,.08) !important;
}

.recobox {
    border-left: 6px solid #008456 !important;
}

.rec-name {
    color: #14271b !important;
    font-size: 1.07rem !important;
}

.small-muted {
    color: #45564a !important;
    font-size: .84rem !important;
}

/* Chips */
.chip {
    background: #dcefe2 !important;
    color: #134e31 !important;
    font-weight: 800 !important;
}

.chip-gold {
    background: #f9e5a7 !important;
    color: #614300 !important;
}

/* Buttons */
.stButton > button {
    border-radius: 11px !important;
    font-weight: 800 !important;
    border: 1px solid #b5cabe !important;
}

.stButton > button[kind="primary"] {
    background: #007a4b !important;
    color: #ffffff !important;
    border-color: #007a4b !important;
}

.stButton > button[kind="primary"]:hover {
    background: #005d39 !important;
    color: #ffffff !important;
}

/* Input and dropdown readability */
[data-testid="stSelectbox"] [data-baseweb="select"],
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input {
    background: #ffffff !important;
    color: #171c19 !important;
    border: 1px solid #9ebbac !important;
    border-radius: 10px !important;
}

[data-testid="stSelectbox"] [data-baseweb="select"] * {
    color: #171c19 !important;
}

div[data-baseweb="popover"],
ul[role="listbox"] {
    background: #ffffff !important;
    color: #171c19 !important;
}

li[role="option"],
div[role="option"] {
    color: #171c19 !important;
    background: #ffffff !important;
}

li[role="option"]:hover,
div[role="option"]:hover,
li[aria-selected="true"],
div[aria-selected="true"] {
    background: #c7e8d4 !important;
    color: #102b1c !important;
}

/* Helpful instructions */
.howbox {
    background: #d9efe0 !important;
    border: 1px solid #a9cdb7 !important;
    color: #1c3425 !important;
}

/* Responsive title */
@media(max-width:850px) {
    .hero-title {
        font-size: 2.5rem !important;
    }
    .credit-panel {
        font-size: .95rem !important;
    }
}


/* BOREAL BUTTON CONTRAST FIX */

/* Primary buttons: white text on green */
.stButton > button[kind="primary"],
.stButton > button[data-testid="stBaseButton-primary"] {
    background-color: #007a4b !important;
    border-color: #007a4b !important;
    color: #ffffff !important;
}

/* Force nested text and icons to stay white */
.stButton > button[kind="primary"] *,
.stButton > button[data-testid="stBaseButton-primary"] * {
    color: #ffffff !important;
    fill: #ffffff !important;
    stroke: #ffffff !important;
}

/* Hover and focus */
.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid="stBaseButton-primary"]:hover {
    background-color: #005c39 !important;
    border-color: #005c39 !important;
    color: #ffffff !important;
}

/* Secondary buttons: dark text on light background */
.stButton > button[kind="secondary"],
.stButton > button[data-testid="stBaseButton-secondary"] {
    background: #ffffff !important;
    color: #172b21 !important;
    border: 1px solid #9fc8ae !important;
}

.stButton > button[kind="secondary"] *,
.stButton > button[data-testid="stBaseButton-secondary"] * {
    color: #172b21 !important;
}


/* BOREAL POLISHED STOREFRONT V1 */

/* Comfortable, modern background */
.stApp {
    background: #edf1ed !important;
    color: #18211c !important;
}

/* Section titles */
.section-head {
    font-size: 1.55rem !important;
    color: #102b1d !important;
    font-weight: 900 !important;
    letter-spacing: -.02em;
}

/* Product cards */
.product {
    background: #fffefa !important;
    border: 1px solid #9fcbb0 !important;
    border-radius: 20px !important;
    box-shadow: 0 7px 20px rgba(17,72,40,.11) !important;
}

.product:hover {
    border-color: #008754 !important;
    box-shadow: 0 12px 26px rgba(17,72,40,.18) !important;
}

.product-art {
    background: linear-gradient(140deg,#d8f3e2,#fff0c2) !important;
    border-radius: 15px !important;
}

.product-name {
    color: #111b14 !important;
    font-size: 1.08rem !important;
    font-weight: 900 !important;
}

.product-en {
    color: #46534a !important;
    font-size: .88rem !important;
}

.product-price {
    color: #006a3f !important;
    font-size: 1.5rem !important;
    font-weight: 900 !important;
}

/* Category sidebar */
[data-testid="stRadio"] label {
    color: #17271c !important;
    font-weight: 650 !important;
}

.howbox {
    background: #d5ecdd !important;
    border: 1px solid #9ac9aa !important;
    color: #163c26 !important;
    border-radius: 16px !important;
}

/* Basket */
.basketbox {
    background: #ffffff !important;
    border: 1px solid #a1cdb0 !important;
    border-radius: 16px !important;
    box-shadow: 0 5px 15px rgba(20,70,40,.08) !important;
}

/* Recommendation cards */
.recobox {
    background: #ffffff !important;
    border: 1px solid #a1cdb0 !important;
    border-left: 7px solid #008754 !important;
    border-radius: 17px !important;
    box-shadow: 0 7px 20px rgba(20,70,40,.11) !important;
}

.rec-name {
    color: #101c14 !important;
    font-size: 1.15rem !important;
}

.recobox .small-muted {
    color: #405247 !important;
    font-size: .88rem !important;
}

/* All primary buttons and their text */
.stButton button[data-testid="stBaseButton-primary"],
.stButton button[kind="primary"] {
    background: #007a4b !important;
    color: #ffffff !important;
    border: 1px solid #007a4b !important;
    border-radius: 12px !important;
    min-height: 42px !important;
}

.stButton button[data-testid="stBaseButton-primary"] *,
.stButton button[kind="primary"] * {
    color: #ffffff !important;
}

.stButton button[data-testid="stBaseButton-primary"]:hover,
.stButton button[kind="primary"]:hover {
    background: #005d39 !important;
}

/* Clear inputs */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stSelectbox"] [data-baseweb="select"] {
    background: #ffffff !important;
    color: #17251b !important;
    border: 1px solid #93b9a0 !important;
}

/* Academic credit panel */
.credit-panel {
    background: #fffaf0 !important;
    color: #15261a !important;
    border: 2px solid #d4ad54 !important;
    border-left: 8px solid #b98315 !important;
    font-size: 1.15rem !important;
}


/* BOREAL ANALYTICS VISIBILITY V2 */
.stTabs [data-baseweb="tab-list"] {gap: 10px; border-bottom: 2px solid #C3D8CB;}
.stTabs [data-baseweb="tab"] {background: #E0EEE5; border: 1px solid #B6D2C1; border-radius: 11px 11px 0 0; padding: 12px 22px; color: #18251D !important; font-weight: 800;}
.stTabs [data-baseweb="tab"] * {color: #18251D !important;}
.stTabs [aria-selected="true"] {background: #087B51 !important; border-color: #087B51 !important;}
.stTabs [aria-selected="true"] * {color: #FFFFFF !important;}
.stTabs [data-baseweb="tab-panel"] h2, .stTabs [data-baseweb="tab-panel"] h3 {color: #12271A !important; font-weight: 850 !important;}
.stTabs [data-baseweb="tab-panel"] [data-testid="stMetric"] {background: #FFFDF7; border: 1px solid #B9D8C5; border-top: 4px solid #008D69; border-radius: 14px; padding: 13px;}
.stTabs [data-baseweb="tab-panel"] [data-testid="stMetricValue"] {color: #075B3E !important; font-weight: 850;}

</style>''',unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def load_data():
    p=pd.read_csv(ROOT/'data'/'products.csv')
    required={'Item','Item_EN','Category','Price'}
    if not required.issubset(p.columns):
        raise ValueError(f"Catalogue columns missing: {required-set(p.columns)}")
    def read(name):
        with (ROOT/'models'/name).open(encoding='utf-8') as f:return json.load(f)
    return p,read('rules.json'),read('popularity.json'),read('metadata.json')

try:
    products,rules,popularity,metadata=load_data()
except (OSError,ValueError,json.JSONDecodeError) as e:
    st.error(f'Project files could not be loaded: {e}')
    st.stop()

catalogue={p['Item']:p for p in products.to_dict('records')}
# Store quantities, not duplicate item names. Apriori still uses presence/absence.
if 'basket' not in st.session_state: st.session_state.basket={}
if isinstance(st.session_state.basket,list):
    st.session_state.basket={item:1 for item in st.session_state.basket if item in catalogue}
def add(item):
    if item in catalogue: st.session_state.basket[item]=st.session_state.basket.get(item,0)+1
def remove(item): st.session_state.basket.pop(item,None)
def decrement(item):
    if item in st.session_state.basket:
        st.session_state.basket[item]-=1
        if st.session_state.basket[item]<=0: st.session_state.basket.pop(item,None)
def clear():st.session_state.basket={}
def slug(item):
    import unicodedata
    v=unicodedata.normalize('NFKD',str(item)).encode('ascii','ignore').decode('ascii')
    return re.sub(r'[^a-z0-9]+','-',v.lower()).strip('-')

def product_image(item):
    """Use exact product photo only if supplied locally; never show a wrong product photo."""
    base=ROOT/'app'/'assets'/'products'
    for ext in ('.webp','.jpg','.jpeg','.png'):
        path=base/(slug(item)+ext)
        if path.is_file(): return path
    return None

def safe(x):return escape(str(x),quote=True)
def emoji(category,item=''):
    n=str(item).lower();c=str(category).lower()
    for needle,symbol in [('steak','🥩'),('saucisse','🌭'),('poulet','🍗'),('bacon','🥓'),('saumon','🐟'),('oeuf','🥚'),('œuf','🥚'),('lait','🥛'),('fromage','🧀'),('pomme','🍎'),('banane','🍌'),('tomate','🍅'),('pain','🥖'),('bière','🍺'),('biscuit','🍪'),('sac réutilisable','🛍️'),('noix','🥜'),('beurre d\'arachide','🥜'),('charbon','🔥'),('couche','🍼')]:
        if needle in n:return symbol
    for needle,symbol in [('viande','🥩'),('poisson','🐟'),('laitier','🧀'),('fruit','🍎'),('légume','🥦'),('boisson','🥤'),('bébé','🍼'),('boulanger','🥖'),('épicer','🫙'),('maison','🧼'),('surgel','❄️'),('collation','🍪')]:
        if needle in c:return symbol
    return '🛒'

@st.cache_data(show_spinner=False)
def index_singleton_rules(raw):
    """Only single-product consequents have valid per-product confidence and lift."""
    out=[]
    for r in raw:
        a=r.get('antecedents',[]);c=r.get('consequents',[])
        if len(c)==1 and a and float(r.get('lift',0))>1:
            out.append((frozenset(a),c[0],float(r['support']),float(r['confidence']),float(r['lift'])))
    return out
single_rules=index_singleton_rules(rules)
def recommend(basket,limit=5):
    have=set(basket);best={}
    for antecedents,item,support,confidence,lift in single_rules:
        if not antecedents.issubset(have) or item in have or item not in catalogue:continue
        rec={'item':item,'antecedents':sorted(antecedents),'support':support,'confidence':confidence,'lift':lift}
        if item not in best or (lift,confidence)>(best[item]['lift'],best[item]['confidence']):best[item]=rec
    return sorted(best.values(),key=lambda r:(-r['lift'],-r['confidence'],r['item']))[:limit]
def popular(excluded,limit=5):return [r for r in popularity if r.get('item') in catalogue and r['item'] not in excluded][:limit]
def strength(lift):return 'Very strong' if lift>=5 else 'Strong' if lift>=3 else 'Moderate' if lift>=1.5 else 'Weak'

st.markdown('''<div class="hero" style="
  background:linear-gradient(115deg,#dcfce7 0%,#fef9c3 55%,#d1fae5 100%);
  border:2px solid #a7dfbd;
  padding:34px 42px;
  box-shadow:0 10px 30px rgba(5,100,55,.12);
">
<div style="flex:1">

  <div style="font-size:.95rem;font-weight:900;letter-spacing:.16em;color:#087443">
    🎓 VANIER COLLEGE &nbsp; | &nbsp; FALL 2026
  </div>

  <div style="
    font-size:4rem;
    font-weight:900;
    color:#064e3b;
    line-height:1.15;
    margin:12px 0 8px;
    text-shadow:1px 2px 0 rgba(255,255,255,.7);
  ">
    🛒 Boréal Marché
  </div>

  <div style="font-size:1.4rem;font-weight:800;color:#166534;margin-bottom:18px">
    Smart Grocery Recommendation System
  </div>

  <div class="credit-panel">
    <b>👨‍🎓 Student:</b> Abdelhafid Masmi
    &nbsp;&nbsp; <b>👨‍🏫 Professor:</b> Steve Ataky
    <div><b>📘 Course:</b> 420-975-VA — Unsupervised Machine Learning</div>
  </div>

</div>

<div class="hero-art" style="font-size:4.5rem">
  🥬🍅🥕🧀🥖
</div>

</div>''',unsafe_allow_html=True)
total=sum(float(catalogue[i]['Price'])*qty for i,qty in st.session_state.basket.items())
unit_count=sum(st.session_state.basket.values())
for col,(num,label) in zip(st.columns(4),[(len(products),'Catalogue products'),(f'{len(rules):,}','Association rules'),(f"{float(metadata.get('coverage',0)):.1%}",'Recommendation coverage'),(f'${total:.2f}','Basket total · CAD')]):
    with col:st.markdown(f'<div class="kpi"><div class="kpi-num">{safe(num)}</div><div class="kpi-label">{safe(label)}</div></div>',unsafe_allow_html=True)

store_tab, analytics_tab = st.tabs(['🛍️ Grocery Store', '📊 Analytics & Insights'])

with store_tab:
    side,center,right=st.columns([.9,2.7,1.35],gap='medium')
    with side:
        st.markdown('<div class="section-head">🗂️ Categories</div>',unsafe_allow_html=True)
        categories=['All categories']+sorted(products['Category'].dropna().unique().tolist())
        category=st.radio('Select category',categories,format_func=lambda c:f'{emoji(c)} {c} ({len(products) if c=="All categories" else int((products.Category==c).sum())})',label_visibility='collapsed')
        st.markdown('<div class="howbox"><b>💡 How it works</b><div>① Browse the catalogue</div><div>② Add products to your basket</div><div>③ Discover matching recommendations</div><div>④ Explore the Apriori evidence</div></div>',unsafe_allow_html=True)

    with center:
        st.markdown('<div class="section-head">🛍️ Explore our products</div>',unsafe_allow_html=True)
        query=st.text_input('Find a product',placeholder='🔎 Search French or English product names…',label_visibility='collapsed')
        c1,c2=st.columns([1.2,1])
        with c1:order=st.selectbox('Sort by',['Catalogue order','Name A → Z','Name Z → A','Price: low to high','Price: high to low'])
        with c2:page_size=st.selectbox('Products per page',[8,12,16],index=0)
        view=products if category=='All categories' else products[products['Category']==category]
        if query.strip():
            q=query.strip();view=view[view['Item'].str.contains(q,case=False,regex=False,na=False)|view['Item_EN'].str.contains(q,case=False,regex=False,na=False)]
        if order=='Name A → Z':view=view.sort_values('Item')
        elif order=='Name Z → A':view=view.sort_values('Item',ascending=False)
        elif order=='Price: low to high':view=view.sort_values('Price')
        elif order=='Price: high to low':view=view.sort_values('Price',ascending=False)
        pages=max(1,(len(view)+page_size-1)//page_size)
        page=st.number_input('Page',min_value=1,max_value=pages,value=1,step=1)
        st.caption(f'{len(view)} products found · Page {page} of {pages}')
        shown=view.iloc[(page-1)*page_size:page*page_size].to_dict('records')
        if not shown:st.info('No products match your search. Try another name or category.')
        for start in range(0,len(shown),4):
            cols=st.columns(4,gap='small')
            for col,p in zip(cols,shown[start:start+4]):
                with col:
                    item=p['Item'];added=item in st.session_state.basket
                    photo=product_image(item)
                    art=(f'<img class="product-photo" src="data:image/{photo.suffix.lstrip(".")};base64,{__import__("base64").b64encode(photo.read_bytes()).decode()}" alt="{safe(item)}">' if photo else f'<div class="product-art">{emoji(p["Category"],item)}</div>')
                    st.markdown(f'<div class="product">{art}<div class="product-name" title="{safe(item)}">{safe(item)}</div><div class="product-en" title="{safe(p["Item_EN"])}">{safe(p["Item_EN"])}</div><span class="product-category">{safe(p["Category"])}</span><div class="product-price">${float(p["Price"]):.2f}</div></div>',unsafe_allow_html=True)
                    st.button(f'＋ Add another ({st.session_state.basket[item]})' if added else '＋ Add to basket',key=f'catalog_{item}',on_click=add,args=(item,),type='primary',use_container_width=True)

    with right:
        st.markdown(f'<div class="section-head">🧺 Your basket ({unit_count} items)</div>',unsafe_allow_html=True)
        if not st.session_state.basket:
            st.markdown('<div class="emptybox"><div style="font-size:2.5rem">🛒</div><b>Your basket is empty!</b><div>Choose products to unlock personalized suggestions.</div></div>',unsafe_allow_html=True)
        else:
            for item,qty in list(st.session_state.basket.items()):
                p=catalogue[item]
                st.markdown(f'<div class="basketbox"><b>{emoji(p["Category"],item)} {safe(item)}</b><div class="small-muted">${float(p["Price"]):.2f} each · {safe(p["Category"])}</div><b style="color:#087b48">Line total: ${float(p["Price"])*qty:.2f}</b></div>',unsafe_allow_html=True)
                a,b,c,d=st.columns([1,1,1,1.5],gap='small')
                with a: st.button('−',key=f'minus_{item}',on_click=decrement,args=(item,),use_container_width=True)
                with b: st.markdown(f'<div style="text-align:center;padding-top:8px;font-weight:900">{qty}</div>',unsafe_allow_html=True)
                with c: st.button('＋',key=f'plus_{item}',on_click=add,args=(item,),use_container_width=True)
                with d: st.button('Remove',key=f'remove_{item}',on_click=remove,args=(item,),use_container_width=True)
            st.success(f'🧾 **Basket total: ${total:.2f} CAD** · {unit_count} units')
            st.button('🗑️ Clear basket',on_click=clear,use_container_width=True)
        st.markdown('<div class="section-head">✨ Recommended for you</div>',unsafe_allow_html=True)
        chosen=recommend(st.session_state.basket.keys())
        if not st.session_state.basket:st.info('Popular products shown until you add something to your basket.')
        elif not chosen:
            st.warning('No matching rule for this basket. Showing popular products instead.')
            if len(st.session_state.basket)==1:
                item=next(iter(st.session_state.basket));pop=next((p for p in popularity if p.get('item')==item),None)
                if pop and float(pop.get('support',1))<float(metadata.get('min_support',0)):
                    st.caption(f'Rare product: {item} appears in {float(pop["support"]):.3%} of baskets, below the {float(metadata["min_support"]):.2%} minimum support threshold.')
        if chosen:
            for r in chosen:
                item=r['item'];p=catalogue[item];why=', '.join(r['antecedents'])
                st.markdown(f'<div class="recobox"><div class="rec-name">{emoji(p["Category"],item)} {safe(item)} · ${float(p["Price"]):.2f}</div><div class="small-muted">{safe(p["Item_EN"])} · {safe(p["Category"])}</div><div style="font-size:.83rem;margin-top:8px">Because your basket contains <b>{safe(why)}</b>, customers with those items also buy <b>{safe(item)}</b> <b>{r["confidence"]:.1%}</b> of the time — <b>{r["lift"]:.2f}×</b> the average rate.</div><span class="chip chip-gold">⭐ {strength(r["lift"])}</span><div class="strength-track"><div class="strength-fill" style="width:{min(100,max(0,r['confidence']*100)):.1f}%"></div></div><div class="small-muted">Confidence: {r['confidence']:.1%} · Lift: {r['lift']:.2f}×</div><span class="chip">Support {r["support"]:.2%}</span><span class="chip">Confidence {r["confidence"]:.1%}</span><span class="chip">Lift {r["lift"]:.2f}×</span></div>',unsafe_allow_html=True)
                st.button(f'＋ Add {item}',key=f'reco_{item}',on_click=add,args=(item,),type='primary',use_container_width=True)
        else:
            for p in popular(set(st.session_state.basket)):
                item=p['item'];c=catalogue[item]
                st.markdown(f'<div class="recobox"><div class="rec-name">{emoji(c["Category"],item)} {safe(item)} · ${float(c["Price"]):.2f}</div><div class="small-muted">{safe(c["Item_EN"])} · {safe(c["Category"])}</div><span class="chip chip-gold">🔥 Popular choice</span><span class="chip">In {float(p["support"]):.1%} of baskets</span></div>',unsafe_allow_html=True)
                st.button(f'＋ Add {item}',key=f'popular_{item}',on_click=add,args=(item,),use_container_width=True)
            st.caption('Popularity fallback — not association-rule recommendations.')
        with st.expander('🔍 Rules that fired · Audit trail'):
            if chosen:
                df=pd.DataFrame([{'If basket contains':', '.join(r['antecedents']),'Then suggest':r['item'],'Support':r['support'],'Confidence':r['confidence'],'Lift':r['lift']} for r in chosen])
                st.dataframe(df,hide_index=True,use_container_width=True)
                st.caption('Highest-lift qualifying singleton-consequent rule per suggested product.')
            else:st.write('No qualifying recommendation rules currently fire.')

    st.divider()
    st.caption('📷 Product photos: place correctly named .jpg/.png/.webp files in app/assets/products/ (e.g., steak-de-boeuf.jpg). Products without photos display illustrated category icons. This prevents misleading product images.')
    with st.expander('📘 Methodology, limitations and reproducibility'):
        st.markdown(f'''**Offline mining:** Apriori runs in the notebook; this application only loads exported JSON rules.

    **Thresholds:** minimum support {metadata.get('min_support','N/A')}, minimum confidence {metadata.get('min_confidence','N/A')}, lift strictly greater than 1.

    **Matching:** All antecedent items must be in the basket. Already selected products are never recommended. When two rules suggest the same product, the highest-lift rule wins.

    **Metric integrity:** Rules with multiple consequents are excluded from individual-product suggestions; their joint confidence and lift cannot be attributed to just one consequent.

    **Fallbacks:** Empty baskets and baskets with no matching rules show popular products. Very rare products may be absent from all frequent itemsets.

    **Limitations:** Association does not prove causation; popularity bias and support thresholds reduce coverage. Quantities affect basket totals, but rule matching uses product presence only. Strength labels are descriptive, not statistical significance tests.''')


# BOREAL_ANALYTICS_TAB_V1 — charts from existing offline project artifacts.
with analytics_tab:
    import altair as alt
    # BOREAL_ANALYTICS_REFINED_V2
    st.markdown('## 📊 Analytics & Insights')
    st.caption('Actual catalogue, saved rules, popularity data and benchmark results. No mining runs in this app.')

    covered = len({str(r.get('consequents', [None])[0]) for r in rules
                   if isinstance(r, dict) and len(r.get('consequents', [])) == 1
                   and r.get('consequents', [None])[0] in catalogue
                   and float(r.get('lift', 0)) > 1})
    coverage_count = len(products)
    a, b, c, d = st.columns(4)
    a.metric('Shopping baskets', f"{int(metadata['number_of_baskets']):,}" if metadata.get('number_of_baskets') is not None else 'Not available')
    b.metric('Catalogue products', f'{coverage_count:,}')
    c.metric('Saved association rules', f'{len(rules):,}')
    d.metric('Rule-based coverage', f'{covered / coverage_count:.1%}' if coverage_count else 'N/A')

    st.markdown('### 🛒 Most frequent products')
    pop_rows = []
    for rec in popularity:
        if isinstance(rec, dict) and rec.get('item') in catalogue:
            try:
                pop_rows.append({'Product': str(rec['item']), 'Basket frequency (%)': 100 * float(rec['support'])})
            except (KeyError, ValueError, TypeError):
                pass
    if pop_rows:
        pop_df = pd.DataFrame(pop_rows).sort_values('Basket frequency (%)', ascending=False).head(10)
        st.altair_chart(alt.Chart(pop_df).mark_bar(cornerRadiusEnd=5).encode(
            x=alt.X('Basket frequency (%):Q', title='Share of shopping baskets (%)', scale=alt.Scale(domain=[0, 100])),
            y=alt.Y('Product:N', sort='-x', title=None),
            color=alt.condition(alt.datum.Product == 'Sac réutilisable', alt.value('#D29B28'), alt.value('#008D69')),
            tooltip=[alt.Tooltip('Product:N'), alt.Tooltip('Basket frequency (%):Q', format='.2f')]
        ).properties(height=340, background='#FFFFFF').configure_axis(labelColor='#17231D', titleColor='#17231D', labelFontSize=12, titleFontSize=12).configure_view(stroke=None), use_container_width=True)
        st.caption('Percentage of shopping baskets containing each product; sourced from models/popularity.json.')
    else:
        st.info('Product-frequency values were not available in popularity.json.')

    left_chart, right_chart = st.columns(2)
    with left_chart:
        st.markdown('### 🎯 Recommendation coverage')
        coverage_df = pd.DataFrame({'Products': [covered, coverage_count - covered]},
                                   index=['Covered by qualifying rules', 'Not covered'])
        st.altair_chart(alt.Chart(pd.DataFrame({'Status': ['Covered', 'Not covered'], 'Products': [covered, coverage_count - covered]})).mark_bar(cornerRadiusEnd=6).encode(
            x=alt.X('Status:N', title=None, sort=['Covered', 'Not covered']),
            y=alt.Y('Products:Q', title='Catalogue products'),
            color=alt.Color('Status:N', scale=alt.Scale(domain=['Covered', 'Not covered'], range=['#008D69', '#E2B451']), legend=None),
            tooltip=['Status:N', 'Products:Q']
        ).properties(height=290, background='#FFFFFF').configure_axis(labelColor='#17231D', titleColor='#17231D', labelFontSize=12).configure_view(stroke=None), use_container_width=True)
        st.caption('Coverage counts distinct products that can appear as a single-product rule consequent; it is not accuracy.')
    with right_chart:
        st.markdown('### 📈 Confidence vs. lift')
        chart_rows = []
        for rule in rules:
            if not isinstance(rule, dict) or len(rule.get('consequents', [])) != 1:
                continue
            try:
                chart_rows.append({'Confidence (%)': 100 * float(rule['confidence']),
                                   'Lift': float(rule['lift'])})
            except (KeyError, ValueError, TypeError):
                continue
        if chart_rows:
            scatter_df = pd.DataFrame(chart_rows)
            # Sampling affects only display performance, never the underlying recommendations.
            if len(scatter_df) > 2500:
                scatter_df = scatter_df.sample(n=2500, random_state=42)
                st.caption('Plot displays a reproducible sample of 2,500 qualifying singleton-consequent rules.')
            st.altair_chart(alt.Chart(scatter_df).mark_circle(size=42, opacity=.55, color='#1976A3').encode(
                x=alt.X('Confidence (%):Q', title='Confidence (%)'),
                y=alt.Y('Lift:Q', title='Lift'),
                tooltip=[alt.Tooltip('Confidence (%):Q', format='.1f'), alt.Tooltip('Lift:Q', format='.2f')]
            ).properties(height=290, background='#FFFFFF').interactive().configure_axis(labelColor='#17231D', titleColor='#17231D', labelFontSize=12).configure_view(stroke=None), use_container_width=True)
        else:
            st.info('No singleton-consequent rule metrics were found.')

    st.markdown('### ⚙️ Apriori benchmark')
    benchmark_file = ROOT / 'reports' / 'benchmark.md'
    if benchmark_file.is_file():
        lines = benchmark_file.read_text(encoding='utf-8').splitlines()
        table_lines = [line.strip() for line in lines if line.strip().startswith('|')]
        benchmark_rows = []
        if table_lines:
            headers = [h.strip().strip('`').lower().replace(' ', '_') for h in table_lines[0].strip('|').split('|')]
            for line in table_lines[1:]:
                values = [v.strip() for v in line.strip('|').split('|')]
                if len(values) != len(headers) or all(set(v) <= set(':- ') for v in values):
                    continue
                row = dict(zip(headers, values))
                try:
                    support = row.get('min_support', row.get('support', ''))
                    rule_count = int(row.get('rules', '').replace(',', ''))
                    runtime = float(row.get('time_seconds', row.get('runtime_seconds', 'nan')))
                    benchmark_rows.append({'Min support': support, 'Rules': rule_count, 'Time (seconds)': runtime})
                except (ValueError, TypeError):
                    continue
        if benchmark_rows:
            bench = pd.DataFrame(benchmark_rows)
            st.altair_chart(alt.Chart(bench).mark_bar(cornerRadiusEnd=5, color='#B37C20').encode(
                x=alt.X('Min support:N', title='Minimum support', sort=None),
                y=alt.Y('Rules:Q', title='Number of association rules'),
                tooltip=['Min support:N', alt.Tooltip('Rules:Q', format=',')]
            ).properties(height=300, background='#FFFFFF').configure_axis(labelColor='#17231D', titleColor='#17231D', labelFontSize=12).configure_view(stroke=None), use_container_width=True)
            st.dataframe(bench, hide_index=True, use_container_width=True)
            st.caption('Measured results loaded from reports/benchmark.md, not rerun in Streamlit.')
        else:
            st.info('Benchmark table format could not be parsed. See reports/benchmark.md for the original measurements.')
    else:
        st.info('Benchmark report not found. Expected reports/benchmark.md.')

    st.markdown('### 📚 Interpretation')
    st.markdown("""- **Support** measures how often an item combination appears in baskets.
- **Confidence** measures how frequently the consequent appears when the antecedent appears.
- **Lift** compares the association to the consequent’s baseline frequency; values above 1 indicate positive association.
- **Coverage** measures how many catalogue products can be recommended by qualifying rules, not prediction accuracy.
- **Limitations:** Associations do not prove causation; rare items and popularity bias can reduce coverage.""")
