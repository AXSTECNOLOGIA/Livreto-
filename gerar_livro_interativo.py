#!/usr/bin/env python3
"""Gerador: Livro Interativo — Estudo do Evangelho de João
Uso: python3 gerar_livro_interativo.py
Saída: estudo_joao_cap1_livro.html
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from cap1_dados import CAP1, NAVY, GOLD, CREAM, GREEN, PURPLE, ORANGE, GRAY

OUTPUT = "estudo_joao_cap1_livro.html"

def esc(s):
    return str(s).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"','&quot;')

# ─────────────────────────────── SVG ILUSTRAÇÕES ────────────────────────────

def svg_cosmos():
    return '''<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:100%;position:absolute;top:0;left:0">
  <defs>
    <radialGradient id="cg1" cx="50%" cy="45%" r="60%">
      <stop offset="0%" stop-color="#f5d06a" stop-opacity="0.9"/>
      <stop offset="30%" stop-color="#c9a84c" stop-opacity="0.5"/>
      <stop offset="70%" stop-color="#1a2744" stop-opacity="0.8"/>
      <stop offset="100%" stop-color="#0d1a33" stop-opacity="1"/>
    </radialGradient>
  </defs>
  <rect width="400" height="300" fill="url(#cg1)"/>
  <circle cx="200" cy="130" r="8" fill="#fff" opacity="0.95"/>
  <circle cx="200" cy="130" r="20" fill="none" stroke="#f5d06a" stroke-width="1" opacity="0.6"/>
  <circle cx="200" cy="130" r="40" fill="none" stroke="#c9a84c" stroke-width="0.8" opacity="0.4"/>
  <circle cx="200" cy="130" r="70" fill="none" stroke="#c9a84c" stroke-width="0.5" opacity="0.25"/>
  <circle cx="200" cy="130" r="110" fill="none" stroke="#c9a84c" stroke-width="0.3" opacity="0.15"/>
  <circle cx="60" cy="40" r="2" fill="#fff" opacity="0.8"/>
  <circle cx="340" cy="60" r="1.5" fill="#fff" opacity="0.7"/>
  <circle cx="90" cy="200" r="1" fill="#fff" opacity="0.6"/>
  <circle cx="310" cy="220" r="2" fill="#fff" opacity="0.5"/>
  <circle cx="150" cy="260" r="1" fill="#fff" opacity="0.6"/>
  <circle cx="270" cy="270" r="1.5" fill="#fff" opacity="0.4"/>
  <circle cx="30" cy="140" r="1" fill="#fff" opacity="0.5"/>
  <circle cx="370" cy="180" r="1" fill="#fff" opacity="0.6"/>
</svg>'''

def svg_luz():
    return '''<svg viewBox="0 0 400 260" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:auto;display:block">
  <defs>
    <radialGradient id="lg1" cx="20%" cy="50%" r="80%">
      <stop offset="0%" stop-color="#fde68a"/>
      <stop offset="40%" stop-color="#c9a84c" stop-opacity="0.6"/>
      <stop offset="100%" stop-color="#1a2744" stop-opacity="0.9"/>
    </radialGradient>
  </defs>
  <rect width="400" height="260" fill="#1a2744"/>
  <ellipse cx="80" cy="130" rx="60" ry="60" fill="url(#lg1)" opacity="0.9"/>
  <line x1="80" y1="130" x2="400" y2="50" stroke="#fde68a" stroke-width="1.5" opacity="0.3"/>
  <line x1="80" y1="130" x2="400" y2="100" stroke="#fde68a" stroke-width="2" opacity="0.4"/>
  <line x1="80" y1="130" x2="400" y2="130" stroke="#fde68a" stroke-width="2.5" opacity="0.5"/>
  <line x1="80" y1="130" x2="400" y2="160" stroke="#fde68a" stroke-width="2" opacity="0.4"/>
  <line x1="80" y1="130" x2="400" y2="210" stroke="#fde68a" stroke-width="1.5" opacity="0.3"/>
  <rect x="200" y="0" width="200" height="260" fill="#0d1a33" opacity="0.4"/>
</svg>'''

def svg_cordeiro():
    return '''<svg viewBox="0 0 360 220" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:auto;display:block">
  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#bfdbfe"/>
      <stop offset="100%" stop-color="#dbeafe"/>
    </linearGradient>
  </defs>
  <rect width="360" height="220" fill="url(#sky)"/>
  <ellipse cx="180" cy="200" rx="180" ry="30" fill="#86efac" opacity="0.6"/>
  <ellipse cx="180" cy="145" rx="55" ry="40" fill="white" opacity="0.95"/>
  <ellipse cx="155" cy="135" rx="28" ry="22" fill="white" opacity="0.9"/>
  <ellipse cx="205" cy="133" rx="25" ry="20" fill="white" opacity="0.9"/>
  <ellipse cx="180" cy="128" rx="35" ry="25" fill="white" opacity="0.95"/>
  <ellipse cx="180" cy="140" rx="45" ry="30" fill="white" opacity="0.9"/>
  <circle cx="168" cy="133" r="15" fill="white"/>
  <circle cx="162" cy="130" r="4" fill="#1a2744" opacity="0.8"/>
  <circle cx="163" cy="129" r="1.5" fill="white"/>
  <ellipse cx="162" cy="150" rx="6" ry="10" fill="white"/>
  <line x1="154" y1="165" x2="150" y2="185" stroke="#d4d4d4" stroke-width="3" stroke-linecap="round"/>
  <line x1="170" y1="168" x2="168" y2="190" stroke="#d4d4d4" stroke-width="3" stroke-linecap="round"/>
  <circle cx="240" cy="60" r="25" fill="#fde68a" opacity="0.6"/>
  <circle cx="240" cy="60" r="35" fill="none" stroke="#fde68a" stroke-width="8" opacity="0.2"/>
</svg>'''

def svg_discipulos():
    return '''<svg viewBox="0 0 360 220" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:auto;display:block">
  <defs>
    <linearGradient id="sunset" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#fed7aa"/>
      <stop offset="60%" stop-color="#f97316" stop-opacity="0.5"/>
      <stop offset="100%" stop-color="#1a2744"/>
    </linearGradient>
  </defs>
  <rect width="360" height="220" fill="url(#sunset)"/>
  <ellipse cx="180" cy="185" rx="180" ry="15" fill="#1a2744" opacity="0.9"/>
  <circle cx="200" cy="90" r="30" fill="#fde68a" opacity="0.7"/>
  <line x1="0" y1="185" x2="360" y2="185" stroke="#1a2744" stroke-width="2"/>
  <g transform="translate(50,120)">
    <circle cx="0" cy="-30" r="12" fill="#c9a84c" opacity="0.8"/>
    <rect x="-8" y="-18" width="16" height="40" rx="4" fill="#e07b39" opacity="0.8"/>
  </g>
  <g transform="translate(90,115)">
    <circle cx="0" cy="-30" r="12" fill="#c9a84c" opacity="0.8"/>
    <rect x="-8" y="-18" width="16" height="45" rx="4" fill="#1a2744" opacity="0.8"/>
  </g>
  <g transform="translate(130,118)">
    <circle cx="0" cy="-30" r="12" fill="#c9a84c" opacity="0.8"/>
    <rect x="-8" y="-18" width="16" height="42" rx="4" fill="#2d6a4f" opacity="0.8"/>
  </g>
  <path d="M20,185 Q80,140 140,160 Q200,180 280,130 Q320,110 360,120" stroke="#60a5fa" stroke-width="3" fill="none" opacity="0.5"/>
</svg>'''

def svg_capa_bg():
    return '''<svg viewBox="0 0 500 680" xmlns="http://www.w3.org/2000/svg" style="position:absolute;top:0;left:0;width:100%;height:100%">
  <defs>
    <radialGradient id="cbg" cx="50%" cy="35%" r="70%">
      <stop offset="0%" stop-color="#2a3f6e"/>
      <stop offset="100%" stop-color="#0d1728"/>
    </radialGradient>
  </defs>
  <rect width="500" height="680" fill="url(#cbg)"/>
  <circle cx="250" cy="210" r="6" fill="#f5d06a" opacity="0.95"/>
  <circle cx="250" cy="210" r="25" fill="none" stroke="#c9a84c" stroke-width="1.5" opacity="0.5"/>
  <circle cx="250" cy="210" r="55" fill="none" stroke="#c9a84c" stroke-width="1" opacity="0.3"/>
  <circle cx="250" cy="210" r="95" fill="none" stroke="#c9a84c" stroke-width="0.6" opacity="0.15"/>
  <line x1="250" y1="210" x2="80" y2="50" stroke="#c9a84c" stroke-width="0.8" opacity="0.2"/>
  <line x1="250" y1="210" x2="420" y2="70" stroke="#c9a84c" stroke-width="0.8" opacity="0.2"/>
  <line x1="250" y1="210" x2="50" y2="280" stroke="#c9a84c" stroke-width="0.8" opacity="0.15"/>
  <line x1="250" y1="210" x2="450" y2="300" stroke="#c9a84c" stroke-width="0.8" opacity="0.15"/>
  <circle cx="80" cy="50" r="1.5" fill="#fff" opacity="0.7"/>
  <circle cx="420" cy="70" r="1" fill="#fff" opacity="0.6"/>
  <circle cx="50" cy="160" r="1.5" fill="#fff" opacity="0.5"/>
  <circle cx="460" cy="200" r="1" fill="#fff" opacity="0.6"/>
  <circle cx="100" cy="350" r="1" fill="#fff" opacity="0.4"/>
  <circle cx="390" cy="400" r="1.5" fill="#fff" opacity="0.5"/>
  <circle cx="30" cy="500" r="1" fill="#fff" opacity="0.4"/>
  <circle cx="470" cy="550" r="1" fill="#fff" opacity="0.5"/>
  <rect x="0" y="560" width="500" height="120" fill="#0d1728" opacity="0.7"/>
  <line x1="30" y1="565" x2="470" y2="565" stroke="#c9a84c" stroke-width="1" opacity="0.4"/>
</svg>'''

def svg_map():
    return '''<svg viewBox="0 0 240 300" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:auto;border-radius:8px;overflow:hidden">
  <rect width="240" height="300" fill="#e0f2fe" rx="4"/>
  <path d="M0,0 L55,0 L60,40 L65,90 L58,160 L52,220 L46,300 L0,300 Z" fill="#93c5fd" opacity="0.7"/>
  <path d="M55,0 L220,0 L220,105 L55,105 Z" fill="#86efac" opacity="0.55"/>
  <path d="M55,105 L220,105 L220,195 L55,195 Z" fill="#fde68a" opacity="0.6"/>
  <path d="M55,195 L220,195 L220,300 L46,300 L52,220 Z" fill="#fed7aa" opacity="0.65"/>
  <path d="M200,5 Q196,55 200,105 Q204,160 196,220 Q190,270 184,300" stroke="#60a5fa" fill="none" stroke-width="2.5" opacity="0.75"/>
  <text x="28" y="148" font-size="7" fill="#1e40af" transform="rotate(-90,28,148)" font-family="Arial" font-weight="bold">Mar Mediterrâneo</text>
  <text x="128" y="55" text-anchor="middle" font-size="11" font-weight="bold" fill="#14532d" font-family="Arial">GALILEIA</text>
  <text x="128" y="155" text-anchor="middle" font-size="10" font-weight="bold" fill="#92400e" font-family="Arial">SAMARIA</text>
  <text x="130" y="250" text-anchor="middle" font-size="11" font-weight="bold" fill="#7c2d12" font-family="Arial">JUDEIA</text>
  <text x="205" y="165" font-size="7" fill="#1e40af" transform="rotate(80,205,165)" font-family="Arial">Rio Jordão</text>
  <circle cx="125" cy="65" r="4" fill="#1a2744"/>
  <text x="131" y="69" font-size="8" fill="#1a2744" font-family="Arial">Caná</text>
  <circle cx="100" cy="82" r="3.5" fill="#1a2744"/>
  <text x="106" y="86" font-size="7.5" fill="#1a2744" font-family="Arial">Nazaré</text>
  <circle cx="190" cy="145" r="3.5" fill="#1a2744"/>
  <text x="115" y="142" font-size="6.5" fill="#1a2744" font-family="Arial">Betânia (Jordão)</text>
  <circle cx="112" cy="240" r="5" fill="#1a2744"/>
  <text x="119" y="244" font-size="8.5" fill="#1a2744" font-weight="bold" font-family="Arial">Jerusalém</text>
  <circle cx="115" cy="270" r="3.5" fill="#1a2744"/>
  <text x="121" y="274" font-size="7.5" fill="#1a2744" font-family="Arial">Belém</text>
  <text x="218" y="18" font-size="12" font-weight="bold" fill="#1a2744" font-family="Arial">N</text>
  <line x1="223" y1="20" x2="223" y2="32" stroke="#1a2744" stroke-width="1.5"/>
  <polygon points="223,8 220,20 226,20" fill="#1a2744"/>
</svg>'''

# ─────────────────────────────── CSS ────────────────────────────────────────

def make_css():
    return """
:root {
  --navy: #1a2744; --gold: #c9a84c; --cream: #f5f0e8;
  --green: #2d6a4f; --purple: #6b3d8f; --orange: #e07b39; --gray: #8b8680;
  --page-w: 460px; --page-h: 640px; --spine: 40px;
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
body{
  background:#2c3e50;
  min-height:100vh;
  display:flex;
  flex-direction:column;
  align-items:center;
  justify-content:center;
  font-family:'Georgia',serif;
  overflow-x:hidden;
  padding:20px 0 80px;
}
/* ── Book shell ── */
.scene{
  perspective:2200px;
  width:calc(var(--page-w)*2 + var(--spine));
  max-width:98vw;
}
.book-wrap{
  position:relative;
  width:100%;
  height:var(--page-h);
  transform-style:preserve-3d;
  transform:rotateY(-4deg);
  transition:transform .4s ease;
  box-shadow:0 30px 80px rgba(0,0,0,0.7), 0 10px 30px rgba(0,0,0,0.4);
}
.book-wrap:hover{transform:rotateY(-1deg)}
/* Spine */
.spine{
  position:absolute;
  left:calc(50% - var(--spine)/2);
  top:0;
  width:var(--spine);
  height:100%;
  background:linear-gradient(to right,
    rgba(0,0,0,0.45) 0%,
    rgba(0,0,0,0.08) 40%,
    rgba(0,0,0,0.08) 60%,
    rgba(0,0,0,0.45) 100%);
  z-index:20;
  pointer-events:none;
}
/* ── Spreads ── */
.spread{
  position:absolute;
  top:0;left:0;
  width:100%;height:100%;
  display:flex;
  opacity:0;
  transform:translateX(40px) scale(0.97);
  transition:opacity .5s ease, transform .5s ease;
  pointer-events:none;
}
.spread.active{
  opacity:1;
  transform:translateX(0) scale(1);
  pointer-events:all;
  z-index:10;
}
.spread.exit-left{
  opacity:0;
  transform:translateX(-40px) scale(0.97);
}
/* ── Pages ── */
.page{
  flex:0 0 calc(50% - var(--spine)/2);
  height:100%;
  background:var(--cream);
  overflow:hidden;
  position:relative;
}
.page.left{
  border-radius:4px 0 0 4px;
  box-shadow:-4px 0 12px rgba(0,0,0,0.2);
  background:linear-gradient(to right,
    #ede8df 0%,
    #f5f0e8 6%,
    #f5f0e8 100%);
}
.page.right{
  border-radius:0 4px 4px 0;
  box-shadow:4px 0 12px rgba(0,0,0,0.2);
  background:linear-gradient(to left,
    #ede8df 0%,
    #f5f0e8 6%,
    #f5f0e8 100%);
}
/* Full-bleed pages (cover, back) */
.page.full-bleed{
  flex:0 0 100%;
  border-radius:4px;
  background:var(--navy);
}
/* ── Section header chip ── */
.sec-head{
  background:var(--navy);
  color:var(--gold);
  padding:7px 14px;
  font-size:10px;
  font-weight:bold;
  letter-spacing:1.5px;
  text-transform:uppercase;
  display:flex;
  align-items:center;
  gap:8px;
  font-family:Arial,sans-serif;
}
.sec-head.green{background:var(--green)}
.sec-head.purple{background:var(--purple)}
.sec-head.orange{background:var(--orange)}
.sec-head.gold{background:var(--gold);color:var(--navy)}
/* ── Scroll area inside page ── */
.pg-scroll{
  height:calc(100% - 0px);
  overflow-y:auto;
  scrollbar-width:thin;
  scrollbar-color:var(--gold) transparent;
}
.pg-scroll::-webkit-scrollbar{width:4px}
.pg-scroll::-webkit-scrollbar-thumb{background:var(--gold);border-radius:2px}
.pg-pad{padding:18px}
.pg-pad-sm{padding:12px}
/* ── Cover styles ── */
.cover-inner{
  position:relative;
  width:100%;height:100%;
  background:var(--navy);
  display:flex;
  flex-direction:column;
  align-items:center;
  justify-content:center;
  overflow:hidden;
}
.cover-serie{
  color:var(--gold);
  font-size:9px;
  letter-spacing:3px;
  text-transform:uppercase;
  font-family:Arial,sans-serif;
  border:1px solid var(--gold);
  padding:4px 12px;
  margin-bottom:16px;
  opacity:0.85;
}
.cover-book{
  color:var(--gold);
  font-size:72px;
  font-weight:bold;
  letter-spacing:8px;
  line-height:1;
  text-shadow:0 0 40px rgba(201,168,76,0.5);
}
.cover-subtitle{
  color:#c8d6e5;
  font-size:11px;
  letter-spacing:4px;
  text-transform:uppercase;
  font-family:Arial,sans-serif;
  margin-top:8px;
  opacity:0.8;
}
.cover-divider{
  width:120px;height:1px;
  background:var(--gold);
  margin:20px auto;
  opacity:0.5;
}
.cover-cap-box{
  border:2px solid var(--gold);
  padding:8px 24px;
  margin:8px 0;
}
.cover-cap-label{
  color:var(--gold);
  font-size:10px;
  letter-spacing:3px;
  text-transform:uppercase;
  font-family:Arial,sans-serif;
}
.cover-cap-num{
  color:var(--gold);
  font-size:28px;
  font-weight:bold;
  text-align:center;
  line-height:1.2;
}
.cover-title{
  color:white;
  font-size:18px;
  text-align:center;
  margin-top:12px;
  font-style:italic;
  letter-spacing:1px;
}
.cover-verse{
  color:#c8d6e5;
  font-size:12px;
  text-align:center;
  font-style:italic;
  margin-top:20px;
  padding:0 40px;
  line-height:1.6;
  opacity:0.9;
}
.cover-verse-ref{
  color:var(--gold);
  font-size:10px;
  font-family:Arial,sans-serif;
  letter-spacing:1px;
  margin-top:6px;
}
/* ── TOC ── */
.toc-item{
  display:flex;
  align-items:center;
  gap:10px;
  padding:10px 0;
  border-bottom:1px solid rgba(201,168,76,0.2);
  cursor:pointer;
  transition:background .2s;
  border-radius:4px;
  padding-left:8px;
}
.toc-item:hover{background:rgba(201,168,76,0.1)}
.toc-num{
  width:28px;height:28px;
  background:var(--navy);
  color:var(--gold);
  border-radius:50%;
  display:flex;align-items:center;justify-content:center;
  font-size:12px;font-weight:bold;
  flex-shrink:0;
  font-family:Arial,sans-serif;
}
.toc-text{flex:1}
.toc-spread{font-size:13px;color:var(--navy);font-weight:bold}
.toc-ref{font-size:10px;color:var(--gray);font-family:Arial,sans-serif;margin-top:2px}
.toc-arrow{color:var(--gold);font-size:14px}
/* ── Character cards ── */
.char-card{
  border-radius:8px;
  overflow:hidden;
  margin-bottom:14px;
  box-shadow:0 2px 8px rgba(0,0,0,0.12);
}
.char-head{
  display:flex;
  align-items:center;
  gap:12px;
  padding:12px 14px;
  color:white;
}
.char-avatar{
  width:46px;height:46px;
  border-radius:50%;
  background:rgba(255,255,255,0.2);
  display:flex;align-items:center;justify-content:center;
  font-size:22px;font-weight:bold;
  flex-shrink:0;
  border:2px solid rgba(255,255,255,0.4);
}
.char-nome{font-size:14px;font-weight:bold;font-family:Arial,sans-serif}
.char-titulo{font-size:10px;opacity:0.8;font-family:Arial,sans-serif;letter-spacing:.5px}
.char-body{padding:10px 14px;background:white;font-size:11px;color:#444;line-height:1.55}
.char-verse{
  margin-top:8px;padding:6px 10px;
  background:#f8f5ee;
  border-left:3px solid var(--gold);
  font-style:italic;
  font-size:10.5px;color:var(--navy);
}
/* ── Timeline ── */
.timeline{position:relative;padding-left:24px}
.timeline::before{
  content:'';position:absolute;left:8px;top:0;bottom:0;
  width:2px;background:var(--gold);opacity:0.4;
}
.tl-item{position:relative;margin-bottom:12px}
.tl-dot{
  position:absolute;left:-20px;top:4px;
  width:10px;height:10px;
  border-radius:50%;
  background:var(--gold);
  border:2px solid white;
  box-shadow:0 0 0 1px var(--gold);
}
.tl-year{font-size:10px;font-weight:bold;color:var(--navy);font-family:Arial,sans-serif}
.tl-event{font-size:10.5px;color:#555;line-height:1.4;margin-top:2px}
/* ── Flip cards ── */
.flip-card{
  perspective:900px;
  cursor:pointer;
  height:100%;
  min-height:200px;
}
.flip-inner{
  position:relative;
  width:100%;height:100%;
  transform-style:preserve-3d;
  transition:transform .55s cubic-bezier(.4,0,.2,1);
}
.flip-card.flipped .flip-inner{transform:rotateY(180deg)}
.flip-front,.flip-back{
  position:absolute;
  top:0;left:0;
  width:100%;height:100%;
  backface-visibility:hidden;
  border-radius:8px;
  overflow:hidden;
}
.flip-back{transform:rotateY(180deg)}
.flip-front-inner{
  height:100%;
  display:flex;flex-direction:column;
  padding:14px;
}
.flip-num{
  font-size:28px;font-weight:bold;
  line-height:1;
  color:rgba(255,255,255,0.3);
  font-family:Arial,sans-serif;
}
.flip-ref{font-size:10px;color:rgba(255,255,255,0.7);font-family:Arial,sans-serif;letter-spacing:.5px;margin-top:2px}
.flip-title{font-size:13px;font-weight:bold;color:white;margin-top:8px;font-family:Arial,sans-serif;line-height:1.3}
.flip-text{
  font-size:10.5px;color:rgba(255,255,255,0.88);
  line-height:1.55;
  margin-top:10px;flex:1;
  font-style:italic;
}
.flip-hint{
  margin-top:10px;
  font-size:9.5px;
  color:rgba(255,255,255,0.55);
  text-align:center;
  font-family:Arial,sans-serif;
  border-top:1px solid rgba(255,255,255,0.15);
  padding-top:8px;
}
.flip-back-inner{
  height:100%;
  display:flex;flex-direction:column;
  padding:14px;
  background:white;
}
.flip-back-label{
  font-size:9px;
  letter-spacing:1.5px;
  text-transform:uppercase;
  color:var(--gold);
  font-family:Arial,sans-serif;
  font-weight:bold;
}
.flip-back-title{font-size:14px;font-weight:bold;color:var(--navy);margin-top:6px;font-family:Arial,sans-serif}
.flip-back-text{font-size:11px;color:#444;line-height:1.6;margin-top:10px;flex:1}
.flip-back-hint{
  font-size:9.5px;color:var(--gray);
  text-align:center;
  border-top:1px solid #e5e5e5;
  padding-top:8px;
  margin-top:8px;
  font-family:Arial,sans-serif;
}
/* ── Synthesis cards ── */
.syn-card{
  border-radius:8px;
  overflow:hidden;
  margin-bottom:12px;
}
.syn-head{
  display:flex;align-items:center;gap:10px;
  padding:10px 14px;color:white;
  font-family:Arial,sans-serif;
}
.syn-icon{font-size:18px;width:32px;text-align:center}
.syn-title{font-size:13px;font-weight:bold}
.syn-body{
  padding:10px 14px;
  font-size:11px;color:#444;
  line-height:1.55;
  background:white;
}
/* ── Curiosity cards ── */
.cur-card{
  border-radius:8px;
  overflow:hidden;
  margin-bottom:14px;
  border:1px solid #e5dcc8;
}
.cur-head{
  display:flex;align-items:center;gap:8px;
  padding:8px 12px;
  background:var(--navy);color:var(--gold);
  font-family:Arial,sans-serif;
}
.cur-icon{font-size:16px}
.cur-title{font-size:11px;font-weight:bold;letter-spacing:.5px}
.cur-body{padding:10px 12px;font-size:11px;color:#444;line-height:1.55}
/* ── Application & Challenge ── */
.app-item{
  display:flex;align-items:flex-start;gap:12px;
  padding:10px 0;border-bottom:1px solid #e8e2d8;
}
.app-num{
  width:30px;height:30px;
  border-radius:50%;
  display:flex;align-items:center;justify-content:center;
  font-size:13px;font-weight:bold;color:white;
  flex-shrink:0;
  font-family:Arial,sans-serif;
}
.app-content{}
.app-title{font-size:12px;font-weight:bold;color:var(--navy);font-family:Arial,sans-serif}
.app-text{font-size:10.5px;color:#555;line-height:1.5;margin-top:3px}
.challenge-item{
  display:flex;align-items:flex-start;gap:8px;
  margin-bottom:10px;
  padding:8px 10px;
  background:#fff8e7;
  border-radius:6px;
  border-left:3px solid var(--orange);
}
.challenge-check{
  width:20px;height:20px;
  border:2px solid var(--orange);
  border-radius:4px;
  flex-shrink:0;
  cursor:pointer;
  display:flex;align-items:center;justify-content:center;
  font-size:12px;
  color:var(--orange);
  transition:background .2s;
}
.challenge-check.done{background:var(--orange);color:white}
.challenge-text{font-size:11px;color:#555;line-height:1.45}
/* ── Diary / Reflection ── */
.reflection-q{margin-bottom:14px}
.q-label{
  font-size:11px;font-weight:bold;color:var(--navy);
  font-family:Arial,sans-serif;
  margin-bottom:5px;
  display:flex;align-items:center;gap:6px;
}
.q-num{
  width:20px;height:20px;
  background:var(--navy);color:var(--gold);
  border-radius:50%;
  display:flex;align-items:center;justify-content:center;
  font-size:10px;font-weight:bold;
  flex-shrink:0;font-family:Arial,sans-serif;
}
.q-textarea{
  width:100%;
  min-height:60px;
  border:1px solid #ddd;
  border-radius:6px;
  padding:8px;
  font-size:11px;
  color:#333;
  background:#fffdf7;
  resize:vertical;
  font-family:'Georgia',serif;
  transition:border-color .2s;
  box-sizing:border-box;
}
.q-textarea:focus{outline:none;border-color:var(--gold);box-shadow:0 0 0 2px rgba(201,168,76,0.15)}
/* ── Memory exercise ── */
.memory-verse{
  font-size:14px;color:var(--navy);
  line-height:2.2;
  text-align:center;
  padding:10px 0;
}
.mem-blank{
  display:inline-block;
  border:none;
  border-bottom:2px solid var(--navy);
  width:70px;
  text-align:center;
  font-size:13px;
  font-family:'Georgia',serif;
  color:var(--navy);
  background:transparent;
  padding:0 4px;
  transition:border-color .2s;
}
.mem-blank:focus{outline:none;border-color:var(--gold)}
.mem-blank.correct{border-color:#22c55e;color:#22c55e}
.mem-blank.wrong{border-color:#ef4444;color:#ef4444}
.mem-ref{
  font-size:10px;color:var(--gold);
  font-family:Arial,sans-serif;
  letter-spacing:1px;
  text-align:center;
  margin-top:8px;
}
.mem-btns{display:flex;gap:8px;justify-content:center;margin-top:14px}
.mem-btn{
  padding:7px 18px;border:none;border-radius:20px;
  font-size:12px;font-family:Arial,sans-serif;
  cursor:pointer;transition:all .2s;
}
.mem-btn.check{background:var(--navy);color:var(--gold)}
.mem-btn.reveal{background:transparent;border:1px solid var(--navy);color:var(--navy)}
.mem-btn:hover{opacity:.85}
.mem-result{
  text-align:center;font-size:12px;
  margin-top:8px;padding:6px;
  border-radius:4px;
  font-family:Arial,sans-serif;
}
/* ── Prayer ── */
.prayer-box{
  background:linear-gradient(135deg,var(--navy) 0%,#2a3f6e 100%);
  border-radius:8px;padding:18px;
  color:rgba(255,255,255,0.9);
  font-size:11.5px;line-height:1.7;
  font-style:italic;
  position:relative;
}
.prayer-quote{
  font-size:40px;color:var(--gold);opacity:0.3;
  line-height:1;
  position:absolute;top:10px;left:14px;
  font-family:Georgia,serif;
}
.prayer-text{margin-top:24px;position:relative;z-index:1}
.prayer-amen{
  text-align:right;
  color:var(--gold);
  font-size:12px;
  font-style:normal;
  font-weight:bold;
  margin-top:10px;
  font-family:Arial,sans-serif;
}
/* ── Back cover ── */
.back-cover{
  position:relative;
  width:100%;height:100%;
  background:var(--navy);
  display:flex;flex-direction:column;
  align-items:center;justify-content:center;
  overflow:hidden;
}
.bc-next{
  border:2px solid var(--gold);
  padding:16px 32px;
  text-align:center;
  margin:20px;
}
.bc-next-label{color:var(--gold);font-size:9px;letter-spacing:2px;text-transform:uppercase;font-family:Arial,sans-serif}
.bc-next-title{color:white;font-size:18px;font-weight:bold;margin-top:4px}
.bc-next-ref{color:rgba(255,255,255,0.6);font-size:11px;font-family:Arial,sans-serif;margin-top:4px}
/* ── Navigation ── */
.nav-bar{
  display:flex;align-items:center;gap:16px;
  margin-top:18px;
}
.nav-btn{
  width:46px;height:46px;
  border-radius:50%;
  border:2px solid rgba(255,255,255,0.4);
  background:rgba(255,255,255,0.1);
  color:white;font-size:20px;
  cursor:pointer;
  display:flex;align-items:center;justify-content:center;
  transition:all .2s;
  backdrop-filter:blur(4px);
}
.nav-btn:hover:not(:disabled){background:rgba(255,255,255,0.25);border-color:white}
.nav-btn:disabled{opacity:.3;cursor:default}
.nav-info{
  color:rgba(255,255,255,0.8);
  font-size:12px;font-family:Arial,sans-serif;
  text-align:center;min-width:80px;
}
.nav-dots{
  display:flex;gap:6px;justify-content:center;margin-top:8px;
}
.nav-dot{
  width:7px;height:7px;
  border-radius:50%;
  background:rgba(255,255,255,0.3);
  cursor:pointer;transition:background .2s;
}
.nav-dot.active{background:var(--gold)}
/* ── Progress bar ── */
.progress-bar{
  position:fixed;top:0;left:0;
  width:0%;height:3px;
  background:linear-gradient(to right,var(--gold),#f5d06a);
  z-index:1000;
  transition:width .4s ease;
}
/* ── Input Panel (New Doc) ── */
.fab{
  position:fixed;bottom:24px;right:24px;
  width:56px;height:56px;
  border-radius:50%;
  background:var(--gold);
  color:var(--navy);
  font-size:28px;font-weight:bold;
  border:none;cursor:pointer;
  display:flex;align-items:center;justify-content:center;
  box-shadow:0 4px 20px rgba(0,0,0,0.35);
  transition:all .25s;
  z-index:500;
  font-family:Arial,sans-serif;
}
.fab:hover{transform:scale(1.1);box-shadow:0 6px 28px rgba(0,0,0,0.45)}
.fab-tooltip{
  position:fixed;bottom:90px;right:28px;
  background:rgba(0,0,0,0.75);color:white;
  font-size:11px;padding:5px 10px;border-radius:4px;
  font-family:Arial,sans-serif;
  opacity:0;pointer-events:none;
  transition:opacity .2s;
  white-space:nowrap;
  z-index:500;
}
.fab:hover + .fab-tooltip{opacity:1}
.input-panel{
  position:fixed;
  top:0;right:0;bottom:0;
  width:440px;max-width:100vw;
  background:white;
  z-index:600;
  transform:translateX(100%);
  transition:transform .35s cubic-bezier(.4,0,.2,1);
  display:flex;flex-direction:column;
  box-shadow:-8px 0 40px rgba(0,0,0,0.3);
}
.input-panel.open{transform:translateX(0)}
.panel-overlay{
  position:fixed;inset:0;
  background:rgba(0,0,0,0.5);
  z-index:590;
  opacity:0;pointer-events:none;
  transition:opacity .35s;
}
.panel-overlay.open{opacity:1;pointer-events:all}
.panel-header{
  background:var(--navy);
  padding:16px 20px;
  display:flex;align-items:center;justify-content:space-between;
}
.panel-header h3{color:var(--gold);font-size:16px;font-family:Arial,sans-serif}
.panel-close{
  background:none;border:none;color:rgba(255,255,255,0.7);
  font-size:20px;cursor:pointer;padding:4px 8px;
  transition:color .2s;
}
.panel-close:hover{color:white}
.panel-tabs{
  display:flex;
  border-bottom:2px solid #e5e5e5;
}
.panel-tab{
  flex:1;padding:12px;
  background:none;border:none;
  font-size:13px;font-family:Arial,sans-serif;
  cursor:pointer;color:#888;
  border-bottom:3px solid transparent;
  margin-bottom:-2px;
  transition:all .2s;
}
.panel-tab.active{color:var(--navy);border-bottom-color:var(--gold);font-weight:bold}
.panel-body{flex:1;overflow-y:auto;padding:16px}
.panel-section{display:none}
.panel-section.active{display:block}
.panel-label{font-size:12px;font-weight:bold;color:var(--navy);font-family:Arial,sans-serif;margin-bottom:6px;margin-top:14px}
.panel-label:first-child{margin-top:0}
.panel-textarea{
  width:100%;min-height:200px;
  border:1px solid #ddd;border-radius:6px;
  padding:10px;font-size:12px;
  font-family:'Georgia',serif;color:#333;
  resize:vertical;line-height:1.6;
  transition:border-color .2s;
}
.panel-textarea:focus{outline:none;border-color:var(--gold)}
.panel-hint{font-size:11px;color:#888;font-family:Arial,sans-serif;margin-top:4px;line-height:1.5}
.pdf-drop{
  border:2px dashed #ccc;border-radius:8px;
  padding:30px 20px;text-align:center;
  cursor:pointer;transition:all .2s;
  margin-bottom:12px;
  position:relative;
}
.pdf-drop:hover,.pdf-drop.drag{border-color:var(--gold);background:#fffbf0}
.pdf-drop input[type=file]{
  position:absolute;inset:0;opacity:0;cursor:pointer;
}
.pdf-drop-icon{font-size:36px;margin-bottom:8px}
.pdf-drop-text{font-size:12px;color:#666;font-family:Arial,sans-serif}
.pdf-drop-sub{font-size:10px;color:#999;margin-top:4px}
.pdf-status{
  padding:8px 12px;border-radius:6px;
  font-size:11.5px;font-family:Arial,sans-serif;
  margin-bottom:8px;
}
.pdf-status.loading{background:#f0f9ff;color:#0369a1}
.pdf-status.success{background:#f0fdf4;color:#15803d}
.pdf-status.error{background:#fef2f2;color:#dc2626}
.panel-btn{
  width:100%;padding:11px;border:none;border-radius:6px;
  background:var(--navy);color:var(--gold);
  font-size:13px;font-family:Arial,sans-serif;font-weight:bold;
  cursor:pointer;margin-top:10px;
  transition:opacity .2s;
  letter-spacing:.5px;
}
.panel-btn:hover{opacity:.85}
.panel-btn.secondary{
  background:transparent;
  border:1px solid var(--navy);
  color:var(--navy);
  margin-top:6px;
}
.panel-divider{
  height:1px;background:#eee;margin:14px 0;
}
/* ── "O que aprendemos" checkmarks ── */
.learn-item{
  display:flex;align-items:flex-start;gap:8px;
  padding:7px 0;border-bottom:1px solid #ece8df;
  font-size:11.5px;color:#333;line-height:1.4;
}
.learn-check{color:var(--green);font-size:14px;flex-shrink:0;margin-top:1px}
/* ── Panorama tags ── */
.panorama-tag{
  display:inline-block;
  background:var(--navy);color:var(--gold);
  border-radius:12px;padding:3px 10px;
  font-size:10px;font-family:Arial,sans-serif;
  margin:3px 2px;letter-spacing:.3px;
}
/* ── Responsive ── */
@media(max-width:1000px){
  :root{--page-w:44vw;--page-h:70vh;--spine:28px}
}
@media(max-width:700px){
  :root{--page-w:92vw;--page-h:auto;--spine:0px}
  .book-wrap{transform:none;height:auto}
  .spread{position:relative;flex-direction:column;transform:none !important;opacity:1 !important;pointer-events:all !important;display:none}
  .spread.active{display:flex}
  .page{flex:0 0 auto;width:100%;border-radius:8px;margin-bottom:12px;
    min-height:50vh}
  .page.full-bleed{flex:0 0 auto;width:100%;min-height:70vh}
  .spine{display:none}
  .scene,.book-wrap{width:100%}
  .input-panel{width:100vw}
}
"""

# ─────────────────────────────── SPREADS ────────────────────────────────────

def spread_cover(cap):
    t = cap["titulo"]; sub = cap["subtitulo"]; serie = cap["serie"]
    tema = cap["tema_geral"]; vk = cap["versiculo_chave"]
    return f'''<div class="spread active" id="spread-0">
  <div class="page full-bleed">
    <div class="cover-inner">
      {svg_capa_bg()}
      <div style="position:relative;z-index:2;text-align:center;padding:30px">
        <div class="cover-serie">{esc(serie)}</div>
        <div class="cover-book">JOÃO</div>
        <div class="cover-subtitle">{esc(tema)}</div>
        <div class="cover-divider"></div>
        <div class="cover-cap-box">
          <div class="cover-cap-label">Capítulo</div>
          <div class="cover-cap-num">{cap["numero"]}</div>
        </div>
        <div class="cover-title">{esc(t)}</div>
        <div style="color:var(--gold);font-size:11px;font-family:Arial;letter-spacing:2px;margin-top:6px;opacity:.7">{esc(sub)}</div>
        <div class="cover-divider"></div>
        <div class="cover-verse">&ldquo;{esc(vk["texto"])}&rdquo;</div>
        <div class="cover-verse-ref">{esc(vk["ref"])}</div>
      </div>
    </div>
  </div>
</div>'''

def spread_toc(cap):
    toc_items = [
        ("Panorama do Capítulo","Visão geral e estrutura","2"),
        ("Personagens Principais","Quem são e o que fazem","3"),
        ("Contexto Histórico","Período, local e cronologia","4"),
        ("Estudo por Blocos","João 1:1-51 em 5 blocos","5–7"),
        ("Síntese Teológica","Grandes temas do capítulo","8"),
        ("Curiosidades Bíblicas","Detalhes históricos e culturais","9"),
        ("Aplicação Prática","Como viver o texto hoje","10"),
        ("Diário de Reflexão","Perguntas para meditação","11"),
        ("Para Memorizar","Exercício com João 1:1","12"),
        ("Oração Final","Oração baseada no capítulo","12"),
    ]
    items_html = ""
    for i,(title,ref,pg) in enumerate(toc_items):
        items_html += f'''<div class="toc-item" onclick="goSpread({i+2})">
    <div class="toc-num">{i+1}</div>
    <div class="toc-text">
      <div class="toc-spread">{esc(title)}</div>
      <div class="toc-ref">{esc(ref)}</div>
    </div>
    <div class="toc-arrow">›</div>
  </div>'''

    learns = cap["aprendemos_sobre_jesus"]
    learns_html = "".join(f'<div class="learn-item"><span class="learn-check">✓</span><span>{esc(l)}</span></div>' for l in learns)

    return f'''<div class="spread" id="spread-1">
  <div class="page left">
    <div class="sec-head">📖 Sumário Interativo</div>
    <div class="pg-scroll"><div class="pg-pad-sm">{items_html}</div></div>
  </div>
  <div class="page right">
    <div class="sec-head green">✝ O Que Aprendemos Sobre Jesus?</div>
    <div class="pg-scroll"><div class="pg-pad">
      {learns_html}
      <div style="margin-top:18px;padding:14px;background:linear-gradient(135deg,var(--navy),#2a3f6e);border-radius:8px;color:white">
        <div style="font-size:9px;letter-spacing:2px;text-transform:uppercase;color:var(--gold);font-family:Arial;font-weight:bold">Versículo-chave</div>
        <div style="font-size:12px;line-height:1.65;margin-top:8px;font-style:italic">&ldquo;{esc(cap["versiculo_chave"]["texto"])}&rdquo;</div>
        <div style="text-align:right;color:var(--gold);font-size:10px;font-family:Arial;margin-top:8px">{esc(cap["versiculo_chave"]["ref"])}</div>
      </div>
    </div></div>
  </div>
</div>'''

def spread_panorama(cap):
    pan = cap["panorama"]
    temas_html = "".join(f'<span class="panorama-tag">{esc(t)}</span>' for t in pan["temas"])
    estrutura_html = ""
    for e in pan["estrutura"]:
        estrutura_html += f'''<div style="display:flex;gap:10px;padding:9px 0;border-bottom:1px solid #e8e2d8;align-items:flex-start">
  <div style="background:var(--navy);color:var(--gold);padding:3px 8px;border-radius:4px;font-size:9.5px;font-family:Arial;font-weight:bold;flex-shrink:0;margin-top:1px">{esc(e["ref"])}</div>
  <div style="font-size:12px;color:var(--navy);line-height:1.4">{esc(e["titulo"])}</div>
</div>'''
    return f'''<div class="spread" id="spread-2">
  <div class="page left">
    <div class="sec-head">📖 Panorama do Capítulo</div>
    <div class="pg-scroll"><div class="pg-pad">
      <p style="font-size:11.5px;color:#444;line-height:1.7;margin-bottom:14px">{esc(pan["texto"])}</p>
      <div style="margin-bottom:14px">
        <div style="font-size:10px;font-weight:bold;color:var(--navy);font-family:Arial;letter-spacing:.5px;margin-bottom:8px;text-transform:uppercase">Temas do Capítulo</div>
        {temas_html}
      </div>
    </div></div>
  </div>
  <div class="page right">
    <div class="sec-head">📋 Estrutura</div>
    <div class="pg-scroll"><div class="pg-pad">
      {estrutura_html}
      <div style="margin-top:16px;padding:14px;background:#fff8e7;border-radius:8px;border-left:3px solid var(--gold)">
        <div style="font-size:10px;font-weight:bold;color:var(--navy);font-family:Arial;text-transform:uppercase;letter-spacing:.5px">Propósito de João</div>
        <p style="font-size:11.5px;color:#444;line-height:1.6;margin-top:8px;font-style:italic">&ldquo;Estas coisas foram escritas para que vocês creiam que Jesus é o Cristo, o Filho de Deus, e que, crendo, tenham vida em seu nome.&rdquo;</p>
        <div style="text-align:right;color:var(--gold);font-size:10px;font-family:Arial;margin-top:6px">João 20:31</div>
      </div>
    </div></div>
  </div>
</div>'''

def spread_personagens(cap):
    chars = cap["personagens"]
    def char_card(c):
        return f'''<div class="char-card">
  <div class="char-head" style="background:{c["cor"]}">
    <div class="char-avatar">{esc(c["inicial"])}</div>
    <div>
      <div class="char-nome">{esc(c["nome"])}</div>
      <div class="char-titulo">{esc(c["titulo"])}</div>
    </div>
  </div>
  <div class="char-body">
    {esc(c["descricao"])}
    <div class="char-verse">{esc(c["versiculo"])}</div>
  </div>
</div>'''
    return f'''<div class="spread" id="spread-3">
  <div class="page left">
    <div class="sec-head">👥 Personagens Principais</div>
    <div class="pg-scroll"><div class="pg-pad-sm">
      {char_card(chars[0])}
      {char_card(chars[1])}
    </div></div>
  </div>
  <div class="page right">
    <div class="sec-head">👥 Personagens Principais</div>
    <div class="pg-scroll"><div class="pg-pad-sm">
      {char_card(chars[2])}
      {char_card(chars[3])}
    </div></div>
  </div>
</div>'''

def spread_contexto(cap):
    ctx = cap["contexto"]
    marcos_html = ""
    for m in ctx["marcos"]:
        marcos_html += f'''<div class="tl-item">
  <div class="tl-dot"></div>
  <div class="tl-year">{esc(m["ano"])}</div>
  <div class="tl-event">{esc(m["evento"])}</div>
</div>'''
    return f'''<div class="spread" id="spread-4">
  <div class="page left">
    <div class="sec-head">📜 Contexto Histórico</div>
    <div class="pg-scroll"><div class="pg-pad">
      <div style="background:#fff8e7;border-radius:6px;padding:8px 12px;font-size:10px;font-family:Arial;color:var(--gray);margin-bottom:12px">
        ⏱ {esc(ctx["periodo"])}
      </div>
      <p style="font-size:11.5px;color:#444;line-height:1.7;margin-bottom:16px">{esc(ctx["texto"])}</p>
      <div style="font-size:10px;font-weight:bold;color:var(--navy);font-family:Arial;text-transform:uppercase;letter-spacing:.5px;margin-bottom:6px">📍 {esc(ctx["local"])}</div>
    </div></div>
  </div>
  <div class="page right">
    <div class="sec-head">⏳ Linha do Tempo</div>
    <div class="pg-scroll"><div class="pg-pad">
      <div class="timeline">{marcos_html}</div>
      <div style="margin-top:16px">
        <div class="sec-head" style="border-radius:4px;margin-bottom:8px">🗺 Local em Destaque</div>
        {svg_map()}
      </div>
    </div></div>
  </div>
</div>'''

def spread_blocos_12(cap):
    b = cap["blocos"]
    def flip(bloco, i):
        clr = bloco["cor"]
        txt_short = bloco["texto"][:280] + ("…" if len(bloco["texto"])>280 else "")
        return f'''<div class="flip-card" id="flip-{i}" onclick="this.classList.toggle('flipped')" style="flex:1;min-height:260px">
  <div class="flip-inner">
    <div class="flip-front" style="background:{clr}">
      <div class="flip-front-inner">
        <div class="flip-num">{bloco["num"]}</div>
        <div class="flip-ref">{esc(bloco["ref"])}</div>
        <div class="flip-title">{esc(bloco["titulo"])}</div>
        <div class="flip-text">&ldquo;{esc(txt_short)}&rdquo;</div>
        <div class="flip-hint">▣ Toque para revelar o aprendizado</div>
      </div>
    </div>
    <div class="flip-back">
      <div class="flip-back-inner">
        <div class="flip-back-label">Aprendizado</div>
        <div class="flip-back-title">{esc(bloco["aprendizado_titulo"])}</div>
        <div class="flip-back-text">{esc(bloco["aprendizado"])}</div>
        <div class="flip-back-hint">▣ Toque para voltar ao texto</div>
      </div>
    </div>
  </div>
</div>'''
    return f'''<div class="spread" id="spread-5">
  <div class="page left">
    <div class="sec-head">📖 Bloco 1 — {esc(b[0]["ref"])}</div>
    <div class="pg-scroll"><div class="pg-pad" style="height:calc(100% - 34px);display:flex;flex-direction:column">
      {flip(b[0],0)}
    </div></div>
  </div>
  <div class="page right">
    <div class="sec-head">📖 Bloco 2 — {esc(b[1]["ref"])}</div>
    <div class="pg-scroll"><div class="pg-pad" style="height:calc(100% - 34px);display:flex;flex-direction:column">
      {flip(b[1],1)}
    </div></div>
  </div>
</div>'''

def spread_bloco3(cap):
    b = cap["blocos"][2]
    clr = b["cor"]
    return f'''<div class="spread" id="spread-6">
  <div class="page left">
    <div class="sec-head gold">✦ Versículo Chave</div>
    <div class="pg-scroll"><div class="pg-pad">
      <div style="position:relative;height:220px;border-radius:8px;overflow:hidden;margin-bottom:14px">
        {svg_cosmos()}
        <div style="position:relative;z-index:2;padding:20px;height:100%;display:flex;flex-direction:column;justify-content:flex-end">
          <div style="color:var(--gold);font-size:10px;font-family:Arial;letter-spacing:1.5px;text-transform:uppercase">Encarnação</div>
          <div style="color:white;font-size:15px;line-height:1.5;margin-top:6px;font-style:italic">&ldquo;E o Verbo se fez carne e habitou entre nós&rdquo;</div>
          <div style="color:var(--gold);font-size:10px;font-family:Arial;margin-top:6px">João 1:14</div>
        </div>
      </div>
      <p style="font-size:11.5px;color:#444;line-height:1.7">
        A encarnação é o maior milagre da história: o Criador infinito tornou-se criatura finita.
        Deus não apenas falou <em>sobre</em> o amor — Ele <em>veio</em> em amor.
        O Verbo não se disfarçou de humano; Ele <em>se tornou</em> plenamente humano.
      </p>
    </div></div>
  </div>
  <div class="page right">
    <div class="sec-head" style="background:{clr}">📖 Bloco 3 — {esc(b["ref"])}</div>
    <div class="pg-scroll"><div class="pg-pad" style="height:calc(100% - 34px);display:flex;flex-direction:column">
      <div class="flip-card" id="flip-2" onclick="this.classList.toggle('flipped')" style="flex:1">
        <div class="flip-inner">
          <div class="flip-front" style="background:{clr}">
            <div class="flip-front-inner">
              <div class="flip-num">{b["num"]}</div>
              <div class="flip-ref">{esc(b["ref"])}</div>
              <div class="flip-title">{esc(b["titulo"])}</div>
              <div class="flip-text">&ldquo;{esc(b["texto"][:280])}…&rdquo;</div>
              <div class="flip-hint">▣ Toque para revelar o aprendizado</div>
            </div>
          </div>
          <div class="flip-back">
            <div class="flip-back-inner">
              <div class="flip-back-label">Aprendizado</div>
              <div class="flip-back-title">{esc(b["aprendizado_titulo"])}</div>
              <div class="flip-back-text">{esc(b["aprendizado"])}</div>
              <div class="flip-back-hint">▣ Toque para voltar ao texto</div>
            </div>
          </div>
        </div>
      </div>
    </div></div>
  </div>
</div>'''

def spread_blocos_45(cap):
    b = cap["blocos"]
    def flip(bloco, idx):
        clr = bloco["cor"]
        return f'''<div class="flip-card" id="flip-{idx}" onclick="this.classList.toggle('flipped')" style="flex:1;min-height:260px">
  <div class="flip-inner">
    <div class="flip-front" style="background:{clr}">
      <div class="flip-front-inner">
        <div class="flip-num">{bloco["num"]}</div>
        <div class="flip-ref">{esc(bloco["ref"])}</div>
        <div class="flip-title">{esc(bloco["titulo"])}</div>
        <div class="flip-text">&ldquo;{esc(bloco["texto"][:260])}…&rdquo;</div>
        <div class="flip-hint">▣ Toque para revelar o aprendizado</div>
      </div>
    </div>
    <div class="flip-back">
      <div class="flip-back-inner">
        <div class="flip-back-label">Aprendizado</div>
        <div class="flip-back-title">{esc(bloco["aprendizado_titulo"])}</div>
        <div class="flip-back-text">{esc(bloco["aprendizado"])}</div>
        <div class="flip-back-hint">▣ Toque para voltar ao texto</div>
      </div>
    </div>
  </div>
</div>'''
    return f'''<div class="spread" id="spread-7">
  <div class="page left">
    <div class="sec-head">📖 Bloco 4 — {esc(b[3]["ref"])}</div>
    <div class="pg-scroll"><div class="pg-pad" style="height:calc(100% - 34px);display:flex;flex-direction:column">
      {flip(b[3],3)}
    </div></div>
  </div>
  <div class="page right">
    <div class="sec-head">📖 Bloco 5 — {esc(b[4]["ref"])}</div>
    <div class="pg-scroll"><div class="pg-pad" style="height:calc(100% - 34px);display:flex;flex-direction:column">
      {flip(b[4],4)}
    </div></div>
  </div>
</div>'''

def spread_sintese(cap):
    syn = cap["sintese"]["temas"]
    def sc(t):
        return f'''<div class="syn-card">
  <div class="syn-head" style="background:{t["cor"]}">
    <div class="syn-icon">{t["icone"]}</div>
    <div class="syn-title">{esc(t["titulo"])}</div>
  </div>
  <div class="syn-body">{esc(t["texto"])}</div>
</div>'''
    return f'''<div class="spread" id="spread-8">
  <div class="page left">
    <div class="sec-head">✦ Síntese Teológica</div>
    <div class="pg-scroll"><div class="pg-pad-sm">{sc(syn[0])}{sc(syn[1])}</div></div>
  </div>
  <div class="page right">
    <div class="sec-head">✦ Síntese Teológica</div>
    <div class="pg-scroll"><div class="pg-pad-sm">{sc(syn[2])}{sc(syn[3])}</div></div>
  </div>
</div>'''

def spread_curiosidades(cap):
    curs = cap["curiosidades"]
    def cc(c):
        return f'''<div class="cur-card">
  <div class="cur-head">
    <div class="cur-icon">{c["icone"]}</div>
    <div class="cur-title">{esc(c["titulo"])}</div>
  </div>
  <div class="cur-body">{esc(c["texto"])}</div>
</div>'''
    return f'''<div class="spread" id="spread-9">
  <div class="page left">
    <div class="sec-head purple">💡 Curiosidades Bíblicas</div>
    <div class="pg-scroll"><div class="pg-pad-sm">{cc(curs[0])}{cc(curs[1])}</div></div>
  </div>
  <div class="page right">
    <div class="sec-head purple">💡 Curiosidades Bíblicas</div>
    <div class="pg-scroll"><div class="pg-pad-sm">{cc(curs[2])}{cc(curs[3])}</div></div>
  </div>
</div>'''

def spread_aplicacao(cap):
    app = cap["aplicacao"]["pontos"]
    des = cap["desafio"]
    app_html = ""
    for p in app:
        app_html += f'''<div class="app-item">
  <div class="app-num" style="background:{NAVY}">{p["num"]}</div>
  <div class="app-content">
    <div class="app-title">{esc(p["titulo"])}</div>
    <div class="app-text">{esc(p["texto"])}</div>
  </div>
</div>'''
    tasks_html = ""
    for i,t in enumerate(des["tarefas"]):
        tasks_html += f'''<div class="challenge-item">
  <div class="challenge-check" onclick="this.classList.toggle('done')" title="Marcar como concluído">✓</div>
  <div class="challenge-text">{esc(t)}</div>
</div>'''
    return f'''<div class="spread" id="spread-10">
  <div class="page left">
    <div class="sec-head">🎯 Aplicação Prática</div>
    <div class="pg-scroll"><div class="pg-pad">{app_html}</div></div>
  </div>
  <div class="page right">
    <div class="sec-head orange">🚩 Desafio da Semana</div>
    <div class="pg-scroll"><div class="pg-pad">
      <p style="font-size:11.5px;color:#444;line-height:1.65;margin-bottom:14px">{esc(des["descricao"])}</p>
      {tasks_html}
    </div></div>
  </div>
</div>'''

def spread_diario(cap):
    qs = cap["reflexao"]["perguntas"]
    def qa(q, idx):
        key = f"joao_cap1_q{idx}"
        return f'''<div class="reflection-q">
  <div class="q-label">
    <div class="q-num">{idx+1}</div>
    {esc(q)}
  </div>
  <textarea class="q-textarea" data-key="{key}" placeholder="Escreva sua reflexão..." rows="3" oninput="saveDiary(this)">{"{}"}</textarea>
</div>'''
    left = "".join(qa(qs[i],i) for i in range(3))
    right = "".join(qa(qs[i],i) for i in range(3,6))
    return f'''<div class="spread" id="spread-11">
  <div class="page left">
    <div class="sec-head">✏ Diário de Reflexão</div>
    <div class="pg-scroll"><div class="pg-pad" id="diary-left">{left}</div></div>
  </div>
  <div class="page right">
    <div class="sec-head">✏ Diário de Reflexão</div>
    <div class="pg-scroll"><div class="pg-pad" id="diary-right">{right}</div></div>
  </div>
</div>'''

def spread_memoria(cap):
    mem = cap["memoria"]
    words = mem["texto"].split()
    blanks = set(mem["blanks_idx"])
    verse_html = ""
    for i, w in enumerate(words):
        if i in blanks:
            clean = w.rstrip(",.")
            verse_html += f'<input class="mem-blank" id="mb-{i}" data-answer="{esc(clean.lower())}" placeholder="___" autocomplete="off"> '
        else:
            verse_html += esc(w) + " "
    oracao = cap["oracao"]
    return f'''<div class="spread" id="spread-12">
  <div class="page left">
    <div class="sec-head gold">📝 Para Memorizar</div>
    <div class="pg-scroll"><div class="pg-pad">
      <div style="background:var(--navy);border-radius:8px;padding:16px;margin-bottom:14px;text-align:center">
        <div style="font-size:9px;color:var(--gold);letter-spacing:2px;font-family:Arial;text-transform:uppercase">Versículo da Semana</div>
        <div style="color:var(--gold);font-size:22px;margin:6px 0">❝</div>
        <div style="color:rgba(255,255,255,0.9);font-size:12px;font-style:italic;line-height:1.7">{esc(mem["texto"])}</div>
        <div style="color:var(--gold);font-size:11px;font-family:Arial;margin-top:8px">{esc(mem["ref"])}</div>
      </div>
      <div style="font-size:11px;color:var(--navy);font-family:Arial;font-weight:bold;margin-bottom:10px">
        Complete as lacunas:
      </div>
      <div class="memory-verse">{verse_html}</div>
      <div class="mem-ref">{esc(mem["ref"])}</div>
      <div class="mem-btns">
        <button class="mem-btn check" onclick="checkMemory()">Verificar</button>
        <button class="mem-btn reveal" onclick="revealMemory()">Revelar</button>
        <button class="mem-btn reveal" onclick="resetMemory()">Reiniciar</button>
      </div>
      <div id="mem-result" class="mem-result"></div>
    </div></div>
  </div>
  <div class="page right">
    <div class="sec-head">🙏 Oração Final</div>
    <div class="pg-scroll"><div class="pg-pad">
      <div class="prayer-box">
        <div class="prayer-quote">&ldquo;</div>
        <div class="prayer-text">{esc(oracao["texto"])}</div>
        <div class="prayer-amen">— Amém</div>
      </div>
      <div style="margin-top:16px;padding:14px;background:#f0fdf4;border-radius:8px;border:1px solid #86efac">
        <div style="font-size:10px;font-weight:bold;color:var(--green);font-family:Arial;text-transform:uppercase;letter-spacing:.5px">Próximos Passos</div>
        <ul style="margin-top:8px;padding-left:16px;font-size:11.5px;color:#444;line-height:1.7">
          <li>Leia João capítulo 2 na próxima semana</li>
          <li>Compartilhe sua maior descoberta com alguém</li>
          <li>Ore usando o versículo que você memorizou</li>
          <li>Traga suas reflexões para o grupo</li>
        </ul>
      </div>
    </div></div>
  </div>
</div>'''

def spread_contracapa(cap):
    return f'''<div class="spread" id="spread-13">
  <div class="page full-bleed">
    <div class="back-cover">
      {svg_capa_bg()}
      <div style="position:relative;z-index:2;text-align:center;padding:40px">
        <div style="color:var(--gold);font-size:10px;letter-spacing:3px;text-transform:uppercase;font-family:Arial;margin-bottom:20px">{esc(cap["serie"])}</div>
        <div style="color:rgba(255,255,255,0.5);font-size:13px;font-family:Arial;margin-bottom:30px">Capítulo {cap["numero"]} concluído!</div>
        <div style="color:white;font-size:18px;margin-bottom:30px;font-style:italic">&ldquo;Coisas maiores do que estas verás.&rdquo;<br><span style="font-size:12px;color:var(--gold);font-style:normal">João 1:50</span></div>
        <div class="bc-next">
          <div class="bc-next-label">Próximo Capítulo</div>
          <div class="bc-next-title">O Primeiro Milagre</div>
          <div class="bc-next-ref">João 2:1-25 — As Bodas de Caná</div>
        </div>
        <div style="color:rgba(255,255,255,0.4);font-size:10px;font-family:Arial;margin-top:30px;letter-spacing:1px">ESTUDO BÍBLICO INTERATIVO</div>
      </div>
    </div>
  </div>
</div>'''

# ─────────────────────── INPUT PANEL (Novo Capítulo) ────────────────────────

def make_input_panel():
    return '''<div class="panel-overlay" id="panel-overlay" onclick="closePanel()"></div>
<div class="input-panel" id="input-panel">
  <div class="panel-header">
    <h3>➕ Novo Documento</h3>
    <button class="panel-close" onclick="closePanel()">✕</button>
  </div>
  <div class="panel-tabs">
    <button class="panel-tab active" onclick="switchTab(this,'tab-text')">✏ Inserir Texto</button>
    <button class="panel-tab" onclick="switchTab(this,'tab-pdf')">📄 Ler PDF</button>
  </div>
  <div class="panel-body">

    <!-- TAB: Texto -->
    <div class="panel-section active" id="tab-text">
      <div class="panel-label">Título do capítulo</div>
      <input type="text" id="new-title" placeholder="Ex: Capítulo 2 — O Primeiro Milagre"
        style="width:100%;padding:8px 10px;border:1px solid #ddd;border-radius:6px;font-size:13px;font-family:Arial">
      <div class="panel-label">Referência bíblica</div>
      <input type="text" id="new-ref" placeholder="Ex: João 2:1-25"
        style="width:100%;padding:8px 10px;border:1px solid #ddd;border-radius:6px;font-size:13px;font-family:Arial;margin-bottom:4px">
      <div class="panel-divider"></div>
      <div class="panel-label">Conteúdo do capítulo</div>
      <div class="panel-hint">Cole o texto do capítulo abaixo. Você pode incluir versículos, comentários, aplicações, etc.</div>
      <textarea class="panel-textarea" id="new-content" placeholder="Cole o conteúdo aqui...&#10;&#10;Dica: Separe seções com linhas em branco."></textarea>
      <button class="panel-btn" onclick="processText()">Processar e Visualizar</button>
      <button class="panel-btn secondary" onclick="downloadTemplate()">Baixar Template JSON</button>
      <div id="text-preview" style="display:none;margin-top:12px;padding:12px;background:#f8f8f8;border-radius:6px;font-size:11.5px;color:#333;line-height:1.6;max-height:200px;overflow-y:auto"></div>
    </div>

    <!-- TAB: PDF -->
    <div class="panel-section" id="tab-pdf">
      <div class="panel-hint" style="margin-bottom:12px">Selecione um arquivo PDF para extrair o texto automaticamente. Para PDFs complexos (escaneados, com proteção), use a aba "Inserir Texto".</div>
      <div class="pdf-drop" id="pdf-drop" ondragover="event.preventDefault();this.classList.add('drag')" ondragleave="this.classList.remove('drag')" ondrop="handleDrop(event)">
        <input type="file" id="pdf-file" accept=".pdf" onchange="handlePDFFile(this.files[0])">
        <div class="pdf-drop-icon">📄</div>
        <div class="pdf-drop-text">Clique para selecionar ou arraste o PDF</div>
        <div class="pdf-drop-sub">Apenas arquivos .pdf</div>
      </div>
      <div id="pdf-status" style="display:none" class="pdf-status"></div>
      <div id="pdf-extracted-section" style="display:none">
        <div class="panel-label">Texto extraído</div>
        <textarea class="panel-textarea" id="pdf-text" style="min-height:160px" placeholder="Texto extraído do PDF..."></textarea>
        <button class="panel-btn" onclick="processPDFText()">Usar este texto</button>
        <button class="panel-btn secondary" onclick="copyPDFText()">Copiar texto</button>
      </div>
    </div>
  </div>
</div>

<button class="fab" id="fab" onclick="openPanel()" title="Novo Documento">+</button>
<div class="fab-tooltip">Novo documento</div>'''

# ─────────────────────────────── JAVASCRIPT ─────────────────────────────────

def make_js():
    return '''<script>
// ── Book navigation ──────────────────────────────────────────────────────────
const TOTAL = 14;
let current = 0;
const spreads = Array.from(document.querySelectorAll('.spread'));
const progressBar = document.getElementById('progress-bar');

function goSpread(n) {
  if (n < 0 || n >= TOTAL) return;
  const prev = document.getElementById('spread-' + current);
  if (prev) {
    prev.classList.remove('active');
    prev.classList.add(n > current ? 'exit-left' : 'exit-right');
    setTimeout(() => prev.classList.remove('exit-left', 'exit-right'), 500);
  }
  current = n;
  const next = document.getElementById('spread-' + current);
  if (next) next.classList.add('active');
  updateNav();
  loadDiary();
}

function updateNav() {
  document.getElementById('nav-current').textContent = current + 1;
  document.getElementById('btn-prev').disabled = current === 0;
  document.getElementById('btn-next').disabled = current === TOTAL - 1;
  const pct = (current / (TOTAL - 1)) * 100;
  progressBar.style.width = pct + '%';
  document.querySelectorAll('.nav-dot').forEach((d,i) => {
    d.classList.toggle('active', i === current);
  });
}

document.getElementById('btn-prev').addEventListener('click', () => goSpread(current - 1));
document.getElementById('btn-next').addEventListener('click', () => goSpread(current + 1));

// Keyboard
document.addEventListener('keydown', e => {
  if (['INPUT','TEXTAREA'].includes(document.activeElement.tagName)) return;
  if (e.key === 'ArrowRight' || e.key === 'PageDown') goSpread(current + 1);
  if (e.key === 'ArrowLeft' || e.key === 'PageUp') goSpread(current - 1);
  if (e.key === 'Home') goSpread(0);
  if (e.key === 'End') goSpread(TOTAL - 1);
});

// Touch swipe
let tx = 0;
document.querySelector('.book-wrap').addEventListener('touchstart', e => { tx = e.touches[0].clientX; }, {passive:true});
document.querySelector('.book-wrap').addEventListener('touchend', e => {
  const dx = e.changedTouches[0].clientX - tx;
  if (Math.abs(dx) > 50) goSpread(current + (dx < 0 ? 1 : -1));
}, {passive:true});

// ── Diary (localStorage) ──────────────────────────────────────────────────────
let diaryTimer = null;
function saveDiary(el) {
  clearTimeout(diaryTimer);
  diaryTimer = setTimeout(() => {
    localStorage.setItem(el.dataset.key, el.value);
  }, 400);
}
function loadDiary() {
  document.querySelectorAll('[data-key]').forEach(el => {
    const saved = localStorage.getItem(el.dataset.key);
    if (saved) el.value = saved;
  });
}
loadDiary();

// ── Memory exercise ───────────────────────────────────────────────────────────
function checkMemory() {
  const inputs = document.querySelectorAll('.mem-blank');
  let correct = 0;
  inputs.forEach(inp => {
    const ans = inp.dataset.answer.toLowerCase().replace(/[,\.]/g,'');
    const val = inp.value.trim().toLowerCase().replace(/[,\.]/g,'');
    inp.classList.remove('correct','wrong');
    if (val === '' ) return;
    if (val === ans) { inp.classList.add('correct'); correct++; }
    else inp.classList.add('wrong');
  });
  const result = document.getElementById('mem-result');
  if (correct === inputs.length) {
    result.style.background = '#f0fdf4'; result.style.color = '#15803d';
    result.textContent = '🎉 Parabéns! Você completou o versículo corretamente!';
  } else {
    result.style.background = '#fff7ed'; result.style.color = '#c2410c';
    result.textContent = `${correct}/${inputs.length} palavras corretas. Continue tentando!`;
  }
}
function revealMemory() {
  document.querySelectorAll('.mem-blank').forEach(inp => {
    inp.value = inp.dataset.answer;
    inp.classList.remove('correct','wrong');
    inp.classList.add('correct');
  });
  const result = document.getElementById('mem-result');
  result.style.background = '#f0f9ff'; result.style.color = '#0369a1';
  result.textContent = 'Respostas reveladas. Tente memorizar e reinicie para praticar!';
}
function resetMemory() {
  document.querySelectorAll('.mem-blank').forEach(inp => {
    inp.value = ''; inp.classList.remove('correct','wrong');
  });
  const result = document.getElementById('mem-result');
  result.textContent = ''; result.style.background = 'transparent';
}

// ── Input Panel ───────────────────────────────────────────────────────────────
function openPanel() {
  document.getElementById('input-panel').classList.add('open');
  document.getElementById('panel-overlay').classList.add('open');
}
function closePanel() {
  document.getElementById('input-panel').classList.remove('open');
  document.getElementById('panel-overlay').classList.remove('open');
}
function switchTab(btn, tabId) {
  document.querySelectorAll('.panel-tab').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.panel-section').forEach(s => s.classList.remove('active'));
  btn.classList.add('active');
  document.getElementById(tabId).classList.add('active');
}

// ── Text input processing ─────────────────────────────────────────────────────
function processText() {
  const title = document.getElementById('new-title').value.trim();
  const ref = document.getElementById('new-ref').value.trim();
  const content = document.getElementById('new-content').value.trim();
  if (!content) { alert('Cole o conteúdo do capítulo antes de continuar.'); return; }
  const preview = document.getElementById('text-preview');
  const paragraphs = content.split(/\n\n+/).filter(p => p.trim());
  let html = '';
  if (title) html += `<strong>${title}</strong><br>`;
  if (ref) html += `<em>${ref}</em><hr style="margin:8px 0">`;
  paragraphs.slice(0, 5).forEach(p => { html += `<p style="margin-bottom:8px">${p.replace(/\n/g,'<br>')}</p>`; });
  if (paragraphs.length > 5) html += `<p style="color:#888">[... ${paragraphs.length - 5} parágrafos adicionais]</p>`;
  preview.innerHTML = html;
  preview.style.display = 'block';
}

function downloadTemplate() {
  const template = {
    numero: 2,
    titulo: "Título do Capítulo",
    subtitulo: "João X:Y-Z",
    serie: "Estudo do Evangelho de João",
    tema_geral: "Tema geral",
    versiculo_chave: { texto: "...", ref: "João X:Y" },
    panorama: { texto: "...", temas: ["Tema 1","Tema 2"], estrutura: [{ ref:"X:1-10", titulo:"Seção 1" }] },
    personagens: [{ nome:"Nome", titulo:"Título", descricao:"...", versiculo:"...", cor:"#1a2744", inicial:"N" }],
    contexto: { titulo:"Contexto", periodo:"...", texto:"...", marcos:[{ ano:"...", evento:"..." }], local:"..." },
    blocos: [{ num:1, ref:"João X:1-5", titulo:"...", cor:"#1a2744", icone:"✦", texto:"...", aprendizado_titulo:"...", aprendizado:"..." }],
    aprendemos_sobre_jesus: ["Ponto 1","Ponto 2"],
    sintese: { titulo:"Síntese", temas:[{ titulo:"...", texto:"...", icone:"✦", cor:"#1a2744" }] },
    curiosidades: [{ titulo:"...", texto:"...", icone:"💡" }],
    aplicacao: { titulo:"...", pontos:[{ num:"1", titulo:"...", texto:"...", icone:"✝" }] },
    desafio: { titulo:"...", descricao:"...", tarefas:["Tarefa 1"] },
    reflexao: { titulo:"...", perguntas:["Pergunta 1?"] },
    memoria: { texto:"...", ref:"João X:Y", blanks_idx:[2,5] },
    oracao: { titulo:"...", texto:"..." }
  };
  const blob = new Blob([JSON.stringify(template, null, 2)], {type:'application/json'});
  const a = document.createElement('a'); a.href = URL.createObjectURL(blob);
  a.download = 'template_capitulo.json'; a.click();
}

// ── PDF extraction ────────────────────────────────────────────────────────────
function handlePDFFile(file) {
  if (!file) return;
  document.getElementById('pdf-drop').classList.remove('drag');
  const status = document.getElementById('pdf-status');
  status.style.display = 'block';
  status.className = 'pdf-status loading';
  status.textContent = '⏳ Lendo o arquivo PDF...';

  const reader = new FileReader();
  reader.onload = function(e) {
    try {
      const text = extractPDFText(e.target.result);
      document.getElementById('pdf-text').value = text;
      document.getElementById('pdf-extracted-section').style.display = 'block';
      status.className = 'pdf-status success';
      status.textContent = '✓ Texto extraído com sucesso! Revise e use conforme necessário.';
    } catch(err) {
      status.className = 'pdf-status error';
      status.textContent = '✗ Não foi possível extrair texto automaticamente. Por favor, copie e cole o conteúdo manualmente na aba "Inserir Texto".';
    }
  };
  reader.onerror = function() {
    status.className = 'pdf-status error';
    status.textContent = '✗ Erro ao ler o arquivo. Verifique se é um PDF válido.';
  };
  reader.readAsArrayBuffer(file);
}

function extractPDFText(buffer) {
  const bytes = new Uint8Array(buffer);
  // Decode as Latin-1 to preserve byte values
  let raw = '';
  for (let i = 0; i < Math.min(bytes.length, 2000000); i++) {
    raw += String.fromCharCode(bytes[i]);
  }

  const texts = [];
  // Method 1: BT...ET blocks with Tj/TJ operators
  const btEt = raw.matchAll(/BT([\s\S]{0,2000}?)ET/g);
  for (const m of btEt) {
    const block = m[1];
    // Tj: (text)Tj
    for (const tj of block.matchAll(/\(([^)]{0,200})\)\s*Tj/g)) {
      const t = cleanPDFString(tj[1]);
      if (t.trim()) texts.push(t);
    }
    // TJ: [(text)-num(text)]TJ
    for (const tj of block.matchAll(/\[([\s\S]{0,500}?)\]\s*TJ/g)) {
      for (const p of tj[1].matchAll(/\(([^)]{0,200})\)/g)) {
        const t = cleanPDFString(p[1]);
        if (t.trim()) texts.push(t);
      }
    }
  }

  if (texts.length > 0) {
    return texts.join(' ')
      .replace(/\\n/g,'\\n')
      .replace(/  +/g,' ')
      .trim();
  }

  // Method 2: Look for readable ASCII strings (fallback)
  let ascii = '';
  for (let i = 0; i < bytes.length; i++) {
    const b = bytes[i];
    if (b >= 32 && b < 127) ascii += String.fromCharCode(b);
    else if (b === 10 || b === 13) ascii += ' ';
  }
  // Filter out PDF syntax noise, keep words
  const words = ascii.match(/[a-zA-ZÀ-ÿ]{3,}/g) || [];
  if (words.length > 20) return words.join(' ');

  throw new Error('No text found');
}

function cleanPDFString(s) {
  return s
    .replace(/\\(n|r)/g,' ')
    .replace(/\\t/g,' ')
    .replace(/\\\\/g,'\\')
    .replace(/\\([0-7]{3})/g, (m,o) => String.fromCharCode(parseInt(o,8)))
    .replace(/[\\(\\)]/g,'');
}

function handleDrop(e) {
  e.preventDefault();
  document.getElementById('pdf-drop').classList.remove('drag');
  const file = e.dataTransfer.files[0];
  if (file && file.type === 'application/pdf') handlePDFFile(file);
  else alert('Por favor, selecione um arquivo PDF válido.');
}

function processPDFText() {
  const text = document.getElementById('pdf-text').value;
  if (!text) return;
  document.getElementById('new-content').value = text;
  switchTab(document.querySelectorAll('.panel-tab')[0], 'tab-text');
}

function copyPDFText() {
  const text = document.getElementById('pdf-text').value;
  navigator.clipboard.writeText(text).then(() => {
    alert('Texto copiado para a área de transferência!');
  }).catch(() => {
    document.getElementById('pdf-text').select();
    document.execCommand('copy');
    alert('Texto copiado!');
  });
}

// ── Init ──────────────────────────────────────────────────────────────────────
updateNav();
</script>'''

# ─────────────────────────────── ASSEMBLER ──────────────────────────────────

def gerar(cap):
    # Build nav dots
    dots = "".join(f'<div class="nav-dot{" active" if i==0 else ""}" onclick="goSpread({i})" title="Página {i+1}"></div>' for i in range(14))

    spreads_html = "\n".join([
        spread_cover(cap),
        spread_toc(cap),
        spread_panorama(cap),
        spread_personagens(cap),
        spread_contexto(cap),
        spread_blocos_12(cap),
        spread_bloco3(cap),
        spread_blocos_45(cap),
        spread_sintese(cap),
        spread_curiosidades(cap),
        spread_aplicacao(cap),
        spread_diario(cap),
        spread_memoria(cap),
        spread_contracapa(cap),
    ])

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(cap['titulo'])} — {esc(cap['serie'])}</title>
<style>{make_css()}</style>
</head>
<body>
<div class="progress-bar" id="progress-bar"></div>

<div class="scene">
  <div class="book-wrap">
    <div class="spine"></div>
    {spreads_html}
  </div>

  <!-- Navigation -->
  <div class="nav-bar">
    <button class="nav-btn" id="btn-prev" disabled>&#8249;</button>
    <div class="nav-info">
      <div><span id="nav-current">1</span> / 14</div>
      <div class="nav-dots">{dots}</div>
    </div>
    <button class="nav-btn" id="btn-next">&#8250;</button>
  </div>
</div>

{make_input_panel()}
{make_js()}
</body>
</html>"""

    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(html)
    size = os.path.getsize(OUTPUT)
    print(f"✓ {OUTPUT} gerado — {size//1024} KB")
    return OUTPUT

if __name__ == "__main__":
    gerar(CAP1)
