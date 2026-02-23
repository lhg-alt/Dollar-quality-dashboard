"""
달러 강세 품질 분석 대시보드
Dollar Strength Quality Analysis Dashboard
Run: streamlit run dollar_quality_dashboard.py
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import numpy as np

# ── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="달러 강세 품질 분석 대시보드",
    page_icon="💵",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Dark finance theme */
    .stApp { background-color: #0d1117; color: #e6edf3; }
    .block-container { padding-top: 1.5rem; }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #161b22, #1c2128);
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 16px 20px;
        margin: 6px 0;
    }
    .metric-label { font-size: 0.78rem; color: #8b949e; letter-spacing: 0.05em; text-transform: uppercase; }
    .metric-value { font-size: 1.6rem; font-weight: 700; margin: 4px 0; }
    .metric-delta { font-size: 0.82rem; }
    .green { color: #3fb950; }
    .red { color: #f85149; }
    .yellow { color: #d29922; }
    .blue { color: #58a6ff; }

    /* Signal box */
    .signal-growth {
        background: linear-gradient(135deg, #0d4a1f, #1a6b2e);
        border: 2px solid #3fb950;
        border-radius: 12px;
        padding: 20px 24px;
        text-align: center;
    }
    .signal-fear {
        background: linear-gradient(135deg, #4a0d0d, #6b1a1a);
        border: 2px solid #f85149;
        border-radius: 12px;
        padding: 20px 24px;
        text-align: center;
    }
    .signal-tight {
        background: linear-gradient(135deg, #4a3a0d, #6b541a);
        border: 2px solid #d29922;
        border-radius: 12px;
        padding: 20px 24px;
        text-align: center;
    }
    .signal-neutral {
        background: linear-gradient(135deg, #1c2128, #21262d);
        border: 2px solid #58a6ff;
        border-radius: 12px;
        padding: 20px 24px;
        text-align: center;
    }
    .signal-title { font-size: 1.0rem; color: #8b949e; margin-bottom: 8px; letter-spacing: 0.05em; }
    .signal-body { font-size: 2.0rem; font-weight: 800; }
    .signal-desc { font-size: 0.9rem; margin-top: 8px; opacity: 0.85; }

    /* Alert box */
    .alert-danger {
        background: #4a0d0d;
        border-left: 4px solid #f85149;
        border-radius: 6px;
        padding: 12px 16px;
        margin: 8px 0;
        font-size: 0.9rem;
    }
    .alert-warning {
        background: #3d2c00;
        border-left: 4px solid #d29922;
        border-radius: 6px;
        padding: 12px 16px;
        margin: 8px 0;
        font-size: 0.9rem;
    }
    .alert-success {
        background: #0d2b14;
        border-left: 4px solid #3fb950;
        border-radius: 6px;
        padding: 12px 16px;
        margin: 8px 0;
        font-size: 0.9rem;
    }
    .alert-info {
        background: #0d1d3b;
        border-left: 4px solid #58a6ff;
        border-radius: 6px;
        padding: 12px 16px;
        margin: 8px 0;
        font-size: 0.9rem;
    }

    /* Sidebar */
    [data-testid="stSidebar"] { background: #161b22; border-right: 1px solid #30363d; }
    .sidebar-link {
        display: block;
        background: #21262d;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 10px 14px;
        margin: 5px 0;
        color: #58a6ff !important;
        text-decoration: none;
        font-size: 0.85rem;
        transition: all 0.2s;
    }
    .sidebar-link:hover { background: #30363d; border-color: #58a6ff; }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab"] { color: #8b949e; }
    .stTabs [aria-selected="true"] { color: #e6edf3 !important; border-bottom-color: #58a6ff !important; }
    
    /* Divider */
    hr { border-color: #30363d; }
    
    /* Plotly charts background */
    .js-plotly-plot { border-radius: 10px; }

    h1, h2, h3 { color: #e6edf3; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 💵 달러 품질 대시보드")
    st.markdown("---")

    st.markdown("### 📡 실시간 데이터")
    st.markdown("""
    <a class="sidebar-link" href="https://investing.com/rates-bonds/u.s.-10-year-bond-yield" target="_blank">
        📈 [1단계] 미국 10년물 금리
    </a>
    <a class="sidebar-link" href="https://investing.com/etfs/ishares-jp-morgan-usd-em-bond-etf" target="_blank">
        🌏 [1단계] 신흥국 채권 ETF (EMB)
    </a>
    <a class="sidebar-link" href="https://investing.com/rates-bonds/south-korea-3-month-bond-yield" target="_blank">
        🇰🇷 [2단계] 한국 3개월물 금리
    </a>
    <a class="sidebar-link" href="https://investing.com/currencies/usd-krw" target="_blank">
        💱 [3단계] USD/KRW 현물환율
    </a>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### ⚙️ 데이터 설정")
    period_option = st.selectbox("조회 기간", ["1mo", "3mo", "6mo", "1y", "2y"], index=1)

    st.markdown("---")
    st.markdown("### 📊 분석 기준")
    st.markdown("""
    <div style="font-size:0.8rem; color:#8b949e; line-height:1.7">
    🟢 <b>성장 달러</b>: 금리↑ + 주식↑<br>
    🔴 <b>공포 달러</b>: 금리↑ + 주식↓ + EM↓<br>
    🟡 <b>경색 달러</b>: 베이시스 괴리 심화<br>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    refresh_btn = st.button("🔄 데이터 새로고침", use_container_width=True)

# ── Data Fetching ──────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def fetch_data(period: str):
    tickers = {
        "TNX": "^TNX",      # 10Y Treasury Yield
        "SPX": "^GSPC",     # S&P 500
        "EEM": "EEM",       # EM Equity ETF
        "EMB": "EMB",       # EM Bond ETF
        "DXY": "DX-Y.NYB",  # Dollar Index
        "IRX": "^IRX",      # US 3M T-Bill
    }
    data = {}
    for name, ticker in tickers.items():
        try:
            df = yf.download(ticker, period=period, progress=False, auto_adjust=True)
            if not df.empty:
                data[name] = df["Close"].squeeze()
        except Exception:
            pass
    return data

if refresh_btn:
    st.cache_data.clear()

with st.spinner("📡 시장 데이터 수신 중..."):
    market_data = fetch_data(period_option)

# Current values helper
def last_val(key):
    if key in market_data and not market_data[key].empty:
        return float(market_data[key].dropna().iloc[-1])
    return None

def prev_val(key):
    s = market_data[key].dropna() if key in market_data else pd.Series(dtype=float)
    return float(s.iloc[-2]) if len(s) >= 2 else None

def delta_pct(key):
    c, p = last_val(key), prev_val(key)
    if c and p and p != 0:
        return (c - p) / p * 100
    return None

# Header
st.markdown("""
<div style="display:flex; align-items:center; gap:12px; margin-bottom:8px">
    <span style="font-size:2rem">💵</span>
    <div>
        <h1 style="margin:0; font-size:1.8rem">달러 강세 품질 분석 대시보드</h1>
        <p style="margin:0; color:#8b949e; font-size:0.85rem">Dollar Strength Quality Analysis · 실시간 3단계 분석 시스템</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Quick metrics row
cols = st.columns(6)
metrics = [
    ("DXY", "달러 지수 (DXY)", "{:.2f}", ""),
    ("TNX", "미국 10Y 금리", "{:.2f}%", ""),
    ("SPX", "S&P 500", "{:,.0f}", ""),
    ("EEM", "EEM (신흥국주식)", "{:.2f}", ""),
    ("EMB", "EMB (신흥국채권)", "{:.2f}", ""),
    ("IRX", "미국 3M 금리", "{:.2f}%", ""),
]
for i, (key, label, fmt, _) in enumerate(metrics):
    with cols[i]:
        v = last_val(key)
        d = delta_pct(key)
        if v:
            color = "green" if (d or 0) >= 0 else "red"
            delta_str = f"{'▲' if (d or 0) >= 0 else '▼'} {abs(d):.2f}%" if d else "–"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value {color}">{fmt.format(v)}</div>
                <div class="metric-delta {color}">{delta_str}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value" style="color:#8b949e">–</div>
                <div class="metric-delta" style="color:#8b949e">데이터 없음</div>
            </div>
            """, unsafe_allow_html=True)

st.markdown("---")

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "📊 1단계: 동행성 분석",
    "🔬 2~3단계: 유동성 골절 분석",
    "🏁 종합 판독 & 결론",
])

# ════════════════════════════════════════════════════════
# TAB 1: 동행성 분석
# ════════════════════════════════════════════════════════
with tab1:
    st.markdown("### 📈 1단계: 핵심 지표 동행성 분석")

    # Normalize helper
    def normalize(series):
        s = series.dropna()
        if s.empty:
            return s
        return (s - s.min()) / (s.max() - s.min()) * 100

    # Build chart
    fig = go.Figure()
    colors_map = {
        "TNX": ("#f85149", "미국 10Y 금리"),
        "SPX": ("#3fb950", "S&P 500"),
        "EEM": ("#58a6ff", "EEM 신흥국주식"),
        "EMB": ("#d29922", "EMB 신흥국채권"),
        "DXY": ("#bc8cff", "달러 지수(DXY)"),
    }
    has_data = False
    for key, (color, label) in colors_map.items():
        if key in market_data:
            norm = normalize(market_data[key])
            if not norm.empty:
                has_data = True
                fig.add_trace(go.Scatter(
                    x=norm.index, y=norm.values,
                    name=label, line=dict(color=color, width=2),
                    hovertemplate=f"<b>{label}</b><br>날짜: %{{x|%Y-%m-%d}}<br>정규화값: %{{y:.1f}}<extra></extra>"
                ))

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#161b22",
        plot_bgcolor="#0d1117",
        title=dict(text="핵심 지표 정규화 비교 (0~100 스케일)", font=dict(size=15, color="#e6edf3")),
        xaxis=dict(gridcolor="#21262d", showgrid=True),
        yaxis=dict(gridcolor="#21262d", showgrid=True, title="정규화 값 (0~100)"),
        legend=dict(bgcolor="#161b22", bordercolor="#30363d", borderwidth=1),
        height=420,
        hovermode="x unified",
    )

    if has_data:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️ 시장 데이터를 가져오지 못했습니다. 네트워크를 확인하세요.")

    # Analysis logic
    st.markdown("### 🔍 자동 판독 결과")

    tnx = last_val("TNX"); tnx_d = delta_pct("TNX")
    spx = last_val("SPX"); spx_d = delta_pct("SPX")
    eem = last_val("EEM"); eem_d = delta_pct("EEM")
    emb = last_val("EMB"); emb_d = delta_pct("EMB")
    dxy = last_val("DXY"); dxy_d = delta_pct("DXY")

    col_l, col_r = st.columns([3, 2])
    with col_l:
        alerts = []

        # 1. Growth Dollar
        if tnx_d and spx_d:
            if tnx_d > 0 and spx_d > 0:
                alerts.append(("success", "✅ 성장 달러 신호: 금리↑ + 주식↑ → 경제 성장 기대 반영. EM 자금 유입 가능성 주목."))
            elif tnx_d > 0 and spx_d < 0:
                alerts.append(("danger", "🚨 공포 달러 경고: 금리↑ + 주식↓ → 위험회피 국면. EM 자금 이탈 주의!"))
            elif tnx_d < 0 and spx_d < 0:
                alerts.append(("warning", "⚠️ 복합 약세 신호: 금리↓ + 주식↓ → 경기침체 우려. 안전자산 수요 점검 필요."))
            elif tnx_d < 0 and spx_d > 0:
                alerts.append(("info", "💡 유동성 랠리 신호: 금리↓ + 주식↑ → 완화적 환경. 달러 강세 지속성 의문."))

        # 2. EM signals
        if eem_d and emb_d:
            if eem_d < -1.0 and emb_d < -1.0:
                alerts.append(("danger", "🚨 EM 전면 이탈: EEM↓ + EMB↓ 동반 하락 → 신흥국 유동성 위기 경고!"))
            elif eem_d < -0.5 or emb_d < -0.5:
                alerts.append(("warning", "⚠️ EM 부분 이탈: 신흥국 자산 선별적 약세 → 달러 강세 압력 존재."))

        # 3. DXY momentum
        if dxy_d:
            if dxy_d > 0.5:
                alerts.append(("warning", f"📊 DXY 강세 가속: 달러 지수 {dxy_d:+.2f}% → 원화·신흥국 통화 압박 예상."))
            elif dxy_d < -0.5:
                alerts.append(("info", f"📊 DXY 약세 전환: 달러 지수 {dxy_d:+.2f}% → 위험자산 숨통 트임."))

        if not alerts:
            alerts.append(("info", "📡 현재 뚜렷한 방향성 신호 없음. 추가 지표 모니터링 권장."))

        for atype, msg in alerts:
            st.markdown(f'<div class="alert-{atype}">{msg}</div>', unsafe_allow_html=True)

    with col_r:
        st.markdown("#### 📋 현재 지표 방향")
        def arrow(d):
            if d is None: return "–"
            return f"🔴 ▼ {abs(d):.2f}%" if d < 0 else f"🟢 ▲ {d:.2f}%"

        indicator_data = {
            "미국 10Y 금리": arrow(tnx_d),
            "S&P 500": arrow(spx_d),
            "EEM (신흥국주식)": arrow(eem_d),
            "EMB (신흥국채권)": arrow(emb_d),
            "달러 지수 DXY": arrow(dxy_d),
        }
        for k, v in indicator_data.items():
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; padding:8px 12px;
                        background:#161b22; border-radius:6px; margin:4px 0;
                        border:1px solid #30363d; font-size:0.85rem">
                <span style="color:#8b949e">{k}</span>
                <span>{v}</span>
            </div>
            """, unsafe_allow_html=True)

    # Correlation heatmap
    st.markdown("---")
    st.markdown("### 🔥 지표 간 상관관계 히트맵")

    dfs = []
    labels = {"TNX": "10Y금리", "SPX": "S&P500", "EEM": "EEM", "EMB": "EMB", "DXY": "DXY"}
    for key, label in labels.items():
        if key in market_data:
            s = market_data[key].dropna().pct_change().rename(label)
            dfs.append(s)

    if len(dfs) >= 2:
        corr = pd.concat(dfs, axis=1).corr()
        fig_corr = go.Figure(go.Heatmap(
            z=corr.values,
            x=corr.columns.tolist(),
            y=corr.index.tolist(),
            colorscale=[[0, "#f85149"], [0.5, "#161b22"], [1, "#3fb950"]],
            zmin=-1, zmax=1,
            text=np.round(corr.values, 2),
            texttemplate="%{text}",
            hovertemplate="<b>%{y} vs %{x}</b><br>상관계수: %{z:.2f}<extra></extra>",
        ))
        fig_corr.update_layout(
            template="plotly_dark",
            paper_bgcolor="#161b22",
            plot_bgcolor="#161b22",
            height=300,
            margin=dict(l=10, r=10, t=30, b=10),
            title=dict(text="일간 수익률 상관계수", font=dict(size=13)),
        )
        st.plotly_chart(fig_corr, use_container_width=True)

# ════════════════════════════════════════════════════════
# TAB 2: 유동성 골절 분석
# ════════════════════════════════════════════════════════
with tab2:
    st.markdown("### 🔬 2~3단계: 스왑 포인트 & CIP 이탈 분석")
    st.markdown("""
    <div class="alert-info">
    💡 <b>CIP (Covered Interest Parity)</b>: 이자율 평가 조건. 이론가와 실제 스왑 포인트의 괴리는 <b>달러 조달 경색</b>의 핵심 신호입니다.
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1.2, 1.8])

    with col1:
        st.markdown("#### 📝 시장 데이터 입력")

        spot = st.number_input("현물 환율 (USD/KRW Spot)", value=1440.0, step=1.0, format="%.2f",
                               help="예: 1440.00")
        us_3m = st.number_input("미국 3M 금리 (%)", value=3.69, step=0.01, format="%.2f",
                                help="예: 3.69 → 연율 기준")

        # Auto-fill from yfinance
        irx = last_val("IRX")
        if irx:
            st.caption(f"💡 yfinance 자동 수집: US 3M = {irx:.2f}%")

        kr_3m = st.number_input("한국 3M 금리 (%)", value=2.70, step=0.01, format="%.2f",
                                help="한국은행 또는 인베스팅닷컴 참고")
        swap_bid = st.number_input("실제 스왑 포인트 Bid (원 단위)", value=-720.0, step=1.0, format="%.2f",
                                   help="음수 = 선물 할인. 예: -720")
        swap_ask = st.number_input("실제 스왑 포인트 Ask (원 단위)", value=-220.0, step=1.0, format="%.2f",
                                   help="음수 = 선물 할인. 예: -220")

        days = st.slider("계약 만기 (일)", min_value=30, max_value=365, value=90, step=30)

        st.markdown("---")
        calc_btn = st.button("⚡ CIP 분석 실행", use_container_width=True, type="primary")

    with col2:
        st.markdown("#### 📊 CIP 분석 결과")

        # Always show results (auto-calculate)
        # CIP Formula
        t = days / 360
        domestic = kr_3m / 100
        foreign = us_3m / 100
        theoretical_rate = spot * (domestic - foreign) / (1 + foreign) * t
        theoretical_annual = spot * (domestic - foreign) / (1 + foreign)  # annualized

        swap_mid = (swap_bid + swap_ask) / 2
        basis = swap_bid - theoretical_rate          # 실전 베이시스
        friction = swap_ask - swap_bid               # 마찰계수 (bid-ask spread)
        deviation_pct = (basis / abs(theoretical_rate) * 100) if theoretical_rate != 0 else 0

        # Results display
        res_cols = st.columns(2)
        with res_cols[0]:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">이론적 스왑 포인트 (CIP)</div>
                <div class="metric-value blue">{theoretical_rate:+.2f}</div>
                <div class="metric-delta" style="color:#8b949e">{days}일 기준</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">실제 스왑 Mid</div>
                <div class="metric-value yellow">{swap_mid:+.2f}</div>
                <div class="metric-delta" style="color:#8b949e">Bid {swap_bid:+.0f} / Ask {swap_ask:+.0f}</div>
            </div>
            """, unsafe_allow_html=True)
        with res_cols[1]:
            basis_color = "red" if basis < -50 else "yellow" if basis < 0 else "green"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">베이시스 괴리 (Bid-이론가)</div>
                <div class="metric-value {basis_color}">{basis:+.2f}</div>
                <div class="metric-delta {basis_color}">괴리율 {deviation_pct:+.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
            friction_color = "red" if friction > 200 else "yellow" if friction > 100 else "green"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">마찰계수 (Ask-Bid)</div>
                <div class="metric-value {friction_color}">{friction:+.2f}</div>
                <div class="metric-delta" style="color:#8b949e">시장 거래비용</div>
            </div>
            """, unsafe_allow_html=True)

        # Bar Chart
        fig_bar = go.Figure()
        categories = ["이론가 (CIP)", "실제 Bid", "실제 Ask", "베이시스 괴리"]
        values = [theoretical_rate, swap_bid, swap_ask, basis]
        bar_colors = ["#58a6ff", "#d29922", "#d29922",
                      "#f85149" if basis < -50 else "#d29922" if basis < 0 else "#3fb950"]

        fig_bar.add_trace(go.Bar(
            x=categories, y=values,
            marker_color=bar_colors,
            text=[f"{v:+.1f}" for v in values],
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>값: %{y:+.2f}<extra></extra>"
        ))
        fig_bar.update_layout(
            template="plotly_dark",
            paper_bgcolor="#161b22",
            plot_bgcolor="#0d1117",
            height=280,
            title=dict(text="이론가 vs 실제 스왑 포인트 비교", font=dict(size=13, color="#e6edf3")),
            xaxis=dict(gridcolor="#21262d"),
            yaxis=dict(gridcolor="#21262d", title="스왑 포인트 (원)"),
            margin=dict(t=50, b=20, l=10, r=10),
            showlegend=False,
        )
        fig_bar.add_hline(y=0, line_dash="dot", line_color="#8b949e", line_width=1)
        st.plotly_chart(fig_bar, use_container_width=True)

        # Signal
        if basis < -200 or friction > 300:
            signal_class, signal_emoji, signal_text = "signal-tight", "🚨", "경고: 달러 접근 경색 발생"
            desc = f"베이시스 괴리 {basis:+.1f}pt / 마찰계수 {friction:.1f}pt → 달러 조달 비용 급등. 즉각 모니터링 필요!"
        elif basis < -50 or friction > 150:
            signal_class, signal_emoji, signal_text = "signal-fear", "⚠️", "주의: 유동성 골절 감지"
            desc = f"베이시스 이탈 {deviation_pct:.1f}% → CIP 조건 위반. 시장 마찰 상승 중."
        elif basis > 0:
            signal_class, signal_emoji, signal_text = "signal-growth", "✅", "정상: CIP 균형 유지"
            desc = "이론가 대비 실제 스왑 포인트 정상 범위. 달러 조달 원활."
        else:
            signal_class, signal_emoji, signal_text = "signal-neutral", "📊", "관찰: 소폭 괴리 발생"
            desc = f"경미한 베이시스 이탈 ({deviation_pct:.1f}%). 지속 모니터링 권장."

        st.markdown(f"""
        <div class="{signal_class}" style="margin-top:8px">
            <div class="signal-title">유동성 골절 판정</div>
            <div class="signal-body">{signal_emoji} {signal_text}</div>
            <div class="signal-desc">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

        # CIP formula display
        st.markdown("---")
        st.markdown("""
        **계산 공식:**
        - **이론 스왑** = Spot × (국내금리 - 해외금리) / (1 + 해외금리) × (Days/360)  
        - **베이시스** = 실제 Bid − 이론 스왑  
        - **마찰계수** = 실제 Ask − 실제 Bid
        """)

# ════════════════════════════════════════════════════════
# TAB 3: 종합 판독
# ════════════════════════════════════════════════════════
with tab3:
    st.markdown("### 🏁 종합 판독: 오늘의 달러 품질")

    # Collect all signals
    tnx_d_v = delta_pct("TNX") or 0
    spx_d_v = delta_pct("SPX") or 0
    eem_d_v = delta_pct("EEM") or 0
    emb_d_v = delta_pct("EMB") or 0
    dxy_d_v = delta_pct("DXY") or 0

    # Score system
    growth_score = 0
    fear_score = 0
    tight_score = 0

    # 1단계 scoring
    if tnx_d_v > 0 and spx_d_v > 0: growth_score += 2
    elif tnx_d_v > 0 and spx_d_v < 0: fear_score += 2
    elif tnx_d_v < 0 and spx_d_v < 0: fear_score += 1

    if eem_d_v < -1.0: fear_score += 2
    elif eem_d_v < 0: fear_score += 1
    elif eem_d_v > 0.5: growth_score += 1

    if emb_d_v < -1.0: fear_score += 2
    elif emb_d_v < 0: fear_score += 1

    if dxy_d_v > 0.5: fear_score += 1  # 급격한 달러 강세는 공포 신호
    elif dxy_d_v < -0.5: growth_score += 1

    # 2~3단계 scoring (use computed values from tab2)
    try:
        if basis < -200: tight_score += 3
        elif basis < -50: tight_score += 2
        elif basis < 0: tight_score += 1

        if friction > 300: tight_score += 2
        elif friction > 150: tight_score += 1
    except Exception:
        pass

    # Final verdict
    total = growth_score + fear_score + tight_score
    if total == 0:
        verdict = "neutral"
    elif tight_score >= 3:
        verdict = "tight"
    elif fear_score > growth_score and fear_score >= 2:
        verdict = "fear"
    elif growth_score > fear_score:
        verdict = "growth"
    else:
        verdict = "neutral"

    verdict_map = {
        "growth": ("signal-growth", "🦖 성장 달러", "달러 강세의 질이 '성장'에 기반합니다. 미국 경제 호조로 자금이 유입되는 구조적 강세국면. 위험자산과 달러가 함께 상승하는 이상적 환경."),
        "fear":   ("signal-fear",   "💀 공포 달러", "달러 강세의 질이 '공포'에 기반합니다. 위험회피 수요로 달러가 강세를 보이는 국면. 주식·EM 자산 동반 약세, 안전자산 선호 확대."),
        "tight":  ("signal-tight",  "🔥 경색 달러", "달러 강세의 질이 '경색'에 기반합니다. CIP 이탈 및 스왑 마찰 심화. 달러 조달 비용 급등으로 금융시장 기능 저하 우려."),
        "neutral":("signal-neutral","📊 관찰 구간", "현재 뚜렷한 달러 품질 판정이 어렵습니다. 추가 지표 모니터링과 데이터 입력을 권장합니다."),
    }

    v_class, v_title, v_desc = verdict_map[verdict]

    col_verdict, col_score = st.columns([2, 1])
    with col_verdict:
        st.markdown(f"""
        <div class="{v_class}" style="padding:30px; margin-bottom:20px">
            <div class="signal-title" style="font-size:1.1rem">오늘의 달러 품질 판정</div>
            <div class="signal-body" style="font-size:2.8rem; margin:12px 0">{v_title}</div>
            <div class="signal-desc" style="font-size:1.0rem; line-height:1.8">{v_desc}</div>
        </div>
        """, unsafe_allow_html=True)

    with col_score:
        st.markdown("#### 📊 점수 분포")
        fig_score = go.Figure(go.Bar(
            y=["🟢 성장", "🔴 공포", "🟡 경색"],
            x=[growth_score, fear_score, tight_score],
            orientation="h",
            marker_color=["#3fb950", "#f85149", "#d29922"],
            text=[f"{growth_score}pt", f"{fear_score}pt", f"{tight_score}pt"],
            textposition="outside",
        ))
        fig_score.update_layout(
            template="plotly_dark",
            paper_bgcolor="#161b22",
            plot_bgcolor="#0d1117",
            height=200,
            margin=dict(l=10, r=60, t=20, b=10),
            xaxis=dict(gridcolor="#21262d", range=[0, max(growth_score, fear_score, tight_score, 1)+1.5]),
            yaxis=dict(gridcolor="rgba(0,0,0,0)"),
            showlegend=False,
        )
        st.plotly_chart(fig_score, use_container_width=True)

    # Summary table
    st.markdown("### 📋 전체 지표 요약")

    try:
        basis_v = f"{basis:+.1f}pt (괴리율 {deviation_pct:+.1f}%)"
        friction_v = f"{friction:.1f}pt"
        theoretical_v = f"{theoretical_rate:+.1f}"
    except Exception:
        basis_v = friction_v = theoretical_v = "입력 필요"

    summary_data = {
        "분석 단계": ["1단계", "1단계", "1단계", "1단계", "1단계", "2~3단계", "2~3단계", "2~3단계"],
        "지표": ["미국 10Y 금리", "S&P 500", "EEM 신흥국주식", "EMB 신흥국채권", "달러 지수(DXY)",
                "CIP 이론 스왑포인트", "베이시스 괴리", "마찰계수(Bid-Ask)"],
        "현재값": [
            f"{last_val('TNX'):.2f}%" if last_val('TNX') else "–",
            f"{last_val('SPX'):,.0f}" if last_val('SPX') else "–",
            f"{last_val('EEM'):.2f}" if last_val('EEM') else "–",
            f"{last_val('EMB'):.2f}" if last_val('EMB') else "–",
            f"{last_val('DXY'):.2f}" if last_val('DXY') else "–",
            theoretical_v, basis_v, friction_v,
        ],
        "일간변화": [
            f"{tnx_d_v:+.2f}%", f"{spx_d_v:+.2f}%", f"{eem_d_v:+.2f}%",
            f"{emb_d_v:+.2f}%", f"{dxy_d_v:+.2f}%", "–", "–", "–",
        ],
        "신호": [
            "🔴" if tnx_d_v > 0.05 else "🟢" if tnx_d_v < -0.05 else "⚪",
            "🟢" if spx_d_v > 0 else "🔴" if spx_d_v < 0 else "⚪",
            "🟢" if eem_d_v > 0 else "🔴" if eem_d_v < 0 else "⚪",
            "🟢" if emb_d_v > 0 else "🔴" if emb_d_v < 0 else "⚪",
            "🔴" if dxy_d_v > 0.3 else "🟢" if dxy_d_v < -0.3 else "⚪",
            "–",
            "🚨" if "급등" in basis_v or (isinstance(basis, float) and basis < -200) else "⚠️" if isinstance(basis, float) and basis < -50 else "🟢",
            "🚨" if isinstance(friction, float) and friction > 300 else "⚠️" if isinstance(friction, float) and friction > 150 else "🟢",
        ]
    }
    df_summary = pd.DataFrame(summary_data)
    st.dataframe(df_summary, use_container_width=True, hide_index=True)

    # Quick links
    st.markdown("---")
    st.markdown("### 🔗 데이터 수집 바로가기")
    link_cols = st.columns(4)
    links = [
        ("📈 미국 10Y 금리", "https://investing.com/rates-bonds/u.s.-10-year-bond-yield"),
        ("🌏 EMB 신흥국채권", "https://investing.com/etfs/ishares-jp-morgan-usd-em-bond-etf"),
        ("🇰🇷 한국 3M 금리", "https://investing.com/rates-bonds/south-korea-3-month-bond-yield"),
        ("💱 USD/KRW 현물", "https://investing.com/currencies/usd-krw"),
    ]
    for i, (label, url) in enumerate(links):
        with link_cols[i]:
            st.link_button(label, url, use_container_width=True)

    st.markdown("---")
    st.markdown("""
    <div style="text-align:center; color:#8b949e; font-size:0.78rem; margin-top:10px">
    💵 달러 강세 품질 분석 대시보드 · 데이터 출처: yfinance (Yahoo Finance) · 
    스왑 데이터: 사용자 입력 · 
    <b>본 대시보드는 투자 조언이 아니며, 참고용 분석 도구입니다.</b>
    </div>
    """, unsafe_allow_html=True)

