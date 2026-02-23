"""
달러 강세 품질 분석 대시보드
Dollar Strength Quality Analysis Dashboard

실행 방법:
    pip install streamlit yfinance pandas plotly
    streamlit run dollar_quality_dashboard.py
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# ── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="달러 강세 품질 분석 대시보드",
    page_icon="💵",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 비밀번호 설정 ───────────────────────────────────────────────────────────────
CORRECT_PASSWORD = "1116"

# ── Light Theme CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* ── 전체 배경: 밝은 흰색 ── */
    .stApp { background-color: #f7f9fc; color: #1a202c; }
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }

    /* ── 비밀번호 화면 ── */
    .pw-container {
        max-width: 420px;
        margin: 80px auto;
        background: white;
        border-radius: 20px;
        padding: 48px 52px;
        box-shadow: 0 8px 40px rgba(0,0,0,0.10);
        text-align: center;
        border: 1px solid #e2e8f0;
    }
    .pw-logo { font-size: 3.5rem; margin-bottom: 10px; }
    .pw-title { font-size: 1.5rem; font-weight: 800; color: #1a202c; margin-bottom: 6px; }
    .pw-sub   { font-size: 0.85rem; color: #718096; margin-bottom: 28px; }
    .pw-error { color: #e53e3e; font-size: 0.85rem; font-weight: 600; margin-top: 8px; }

    /* ── 메트릭 카드 ── */
    .metric-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px 18px;
        margin: 4px 0;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05);
        transition: box-shadow 0.2s;
    }
    .metric-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.10); }
    .metric-label { font-size: 0.72rem; color: #718096; letter-spacing: 0.06em; text-transform: uppercase; font-weight: 600; margin-bottom: 4px; }
    .metric-value { font-size: 1.55rem; font-weight: 700; margin: 4px 0; }
    .metric-delta { font-size: 0.8rem; font-weight: 600; }

    /* ── 색상 ── */
    .green  { color: #16a34a; }
    .red    { color: #dc2626; }
    .yellow { color: #d97706; }
    .blue   { color: #2563eb; }
    .gray   { color: #718096; }

    /* ── 신호 박스 ── */
    .signal-growth {
        background: linear-gradient(135deg, #f0fdf4, #dcfce7);
        border: 2px solid #86efac;
        border-radius: 16px;
        padding: 24px 28px;
        text-align: center;
    }
    .signal-fear {
        background: linear-gradient(135deg, #fff1f2, #fee2e2);
        border: 2px solid #fca5a5;
        border-radius: 16px;
        padding: 24px 28px;
        text-align: center;
    }
    .signal-tight {
        background: linear-gradient(135deg, #fffbeb, #fef3c7);
        border: 2px solid #fcd34d;
        border-radius: 16px;
        padding: 24px 28px;
        text-align: center;
    }
    .signal-neutral {
        background: linear-gradient(135deg, #eff6ff, #dbeafe);
        border: 2px solid #93c5fd;
        border-radius: 16px;
        padding: 24px 28px;
        text-align: center;
    }
    .signal-title { font-size: 0.8rem; color: #718096; margin-bottom: 8px; letter-spacing: 0.06em; text-transform: uppercase; font-weight: 600; }
    .signal-body  { font-size: 2.1rem; font-weight: 900; }
    .signal-desc  { font-size: 0.88rem; margin-top: 10px; color: #4a5568; line-height: 1.7; }
    .signal-growth .signal-body { color: #15803d; }
    .signal-fear   .signal-body { color: #b91c1c; }
    .signal-tight  .signal-body { color: #92400e; }
    .signal-neutral .signal-body { color: #1d4ed8; }

    /* ── 알림 박스 ── */
    .alert-danger {
        background: #fff1f2;
        border-left: 4px solid #dc2626;
        border-radius: 8px;
        padding: 12px 16px;
        margin: 8px 0;
        font-size: 0.875rem;
        color: #7f1d1d;
    }
    .alert-warning {
        background: #fffbeb;
        border-left: 4px solid #d97706;
        border-radius: 8px;
        padding: 12px 16px;
        margin: 8px 0;
        font-size: 0.875rem;
        color: #78350f;
    }
    .alert-success {
        background: #f0fdf4;
        border-left: 4px solid #16a34a;
        border-radius: 8px;
        padding: 12px 16px;
        margin: 8px 0;
        font-size: 0.875rem;
        color: #14532d;
    }
    .alert-info {
        background: #eff6ff;
        border-left: 4px solid #2563eb;
        border-radius: 8px;
        padding: 12px 16px;
        margin: 8px 0;
        font-size: 0.875rem;
        color: #1e3a8a;
    }

    /* ── 사이드바 ── */
    [data-testid="stSidebar"] {
        background: white;
        border-right: 1px solid #e2e8f0;
    }
    .sidebar-link {
        display: block;
        background: #f7f9fc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 10px 14px;
        margin: 5px 0;
        color: #2563eb !important;
        text-decoration: none;
        font-size: 0.82rem;
        font-weight: 500;
        transition: all 0.2s;
    }
    .sidebar-link:hover {
        background: #eff6ff;
        border-color: #93c5fd;
    }

    /* ── 탭 스타일 ── */
    .stTabs [data-baseweb="tab-list"] { gap: 4px; }
    .stTabs [data-baseweb="tab"] {
        color: #718096;
        font-weight: 500;
        border-radius: 8px 8px 0 0;
    }
    .stTabs [aria-selected="true"] {
        color: #2563eb !important;
        border-bottom-color: #2563eb !important;
        font-weight: 700;
    }

    /* ── 섹션 제목 ── */
    h1, h2, h3 { color: #1a202c !important; }

    /* ── 데이터프레임 ── */
    .stDataFrame { border-radius: 10px; overflow: hidden; }

    /* ── 구분선 ── */
    hr { border-color: #e2e8f0; }

    /* ── Plotly 차트 ── */
    .js-plotly-plot .plotly { border-radius: 10px; }

    /* ── 버튼 ── */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# 비밀번호 인증 로직
# ══════════════════════════════════════════════════════════════════════════════
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    # 사이드바 숨기기 (비밀번호 화면에서)
    st.markdown("""
    <style>
        [data-testid="stSidebar"] { display: none; }
        header { display: none; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="pw-container">
        <div class="pw-logo">💵</div>
        <div class="pw-title">달러 품질 분석 시스템</div>
        <div class="pw-sub">접근 비밀번호를 입력하세요</div>
    </div>
    """, unsafe_allow_html=True)

    # 비밀번호 입력 영역 (중앙 정렬)
    col_l, col_c, col_r = st.columns([1, 1.2, 1])
    with col_c:
        pw_input = st.text_input(
            label="비밀번호",
            type="password",
            placeholder="비밀번호 4자리 입력",
            label_visibility="collapsed",
            key="pw_field"
        )
        enter_btn = st.button("🔓 입장하기", use_container_width=True, type="primary")

        if enter_btn or (pw_input and len(pw_input) >= 1):
            if enter_btn:
                if pw_input == CORRECT_PASSWORD:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.markdown('<div style="color:#dc2626; font-size:0.85rem; font-weight:600; text-align:center; margin-top:8px;">❌ 비밀번호가 올바르지 않습니다</div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center; margin-top:24px; font-size:0.75rem; color:#a0aec0;">
        💵 달러 강세 품질 분석 대시보드 · 접근 제한 구역
    </div>
    """, unsafe_allow_html=True)

    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
# 인증 통과 후 메인 대시보드
# ══════════════════════════════════════════════════════════════════════════════

# ── 사이드바 ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 💵 달러 품질 대시보드")
    st.markdown("---")

    st.markdown("### 📡 실시간 데이터")
    st.markdown("""
    <a class="sidebar-link" href="https://kr.investing.com/rates-bonds/u.s.-10-year-bond-yield" target="_blank">
        📈 [1단계] 미국 10년물 금리
    </a>
    <a class="sidebar-link" href="https://kr.investing.com/etfs/ishares-jp-morgan-usd-em-bond-etf" target="_blank">
        🌏 [1단계] 신흥국 채권 ETF (EMB)
    </a>
    <a class="sidebar-link" href="https://kr.investing.com/rates-bonds/south-korea-3-month-bond-yield" target="_blank">
        🇰🇷 [2단계] 한국 3개월물 금리
    </a>
    <a class="sidebar-link" href="https://kr.investing.com/currencies/usd-krw" target="_blank">
        💱 [3단계] USD/KRW 현물환율
    </a>
    <a class="sidebar-link" href="https://fred.stlouisfed.org/series/DGS10" target="_blank">
        🏦 FRED 미국 10Y 금리
    </a>
    <a class="sidebar-link" href="https://www.bok.or.kr" target="_blank">
        🏛 한국은행 기준금리
    </a>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### ⚙️ 데이터 설정")
    period_option = st.selectbox("조회 기간", ["1mo", "3mo", "6mo", "1y", "2y"], index=1)

    st.markdown("---")
    st.markdown("### 📊 판정 기준")
    st.markdown("""
    <div style="font-size:0.82rem; color:#4a5568; line-height:1.9; background:#f7f9fc; padding:12px; border-radius:8px; border:1px solid #e2e8f0;">
    🟢 <b>성장 달러</b>: 금리↑ + 주식↑<br>
    🔴 <b>공포 달러</b>: 금리↑ + 주식↓ + EM↓<br>
    🟡 <b>경색 달러</b>: 베이시스 괴리 심화
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    refresh_btn = st.button("🔄 데이터 새로고침", use_container_width=True)

    st.markdown("---")
    # 로그아웃 버튼
    if st.button("🔒 로그아웃", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()


# ── 데이터 수집 ───────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def fetch_data(period: str):
    tickers = {
        "TNX": "^TNX",
        "SPX": "^GSPC",
        "EEM": "EEM",
        "EMB": "EMB",
        "DXY": "DX-Y.NYB",
        "IRX": "^IRX",
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

with st.spinner("📡 yfinance로 시장 데이터 수신 중..."):
    market_data = fetch_data(period_option)

# ── 헬퍼 함수 ─────────────────────────────────────────────────────────────────
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


# ── 헤더 ──────────────────────────────────────────────────────────────────────
col_hd1, col_hd2 = st.columns([3, 1])
with col_hd1:
    st.markdown("# 💵 달러 강세 품질 분석 대시보드")
    st.markdown(
        f"<span style='color:#718096; font-size:0.85rem;'>yfinance 자동수집 · 3단계 분석 시스템 · "
        f"업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>",
        unsafe_allow_html=True
    )
with col_hd2:
    st.markdown("<br>", unsafe_allow_html=True)
    data_count = len(market_data)
    if data_count >= 5:
        st.success(f"✅ {data_count}/6 종목 수집 완료")
    elif data_count > 0:
        st.warning(f"⚠️ {data_count}/6 종목만 수집됨")
    else:
        st.error("❌ 데이터 수집 실패")

st.markdown("---")

# ── 상단 메트릭 5개 ───────────────────────────────────────────────────────────
metrics_config = [
    ("DXY", "달러 지수 (DXY)", "{:.2f}", ""),
    ("TNX", "미국 10Y 금리",   "{:.2f}%", ""),
    ("SPX", "S&P 500",        "{:,.0f}", ""),
    ("EEM", "EEM 신흥국주식",  "${:.2f}", ""),
    ("EMB", "EMB 신흥국채권",  "${:.2f}", ""),
]
cols = st.columns(5)
for i, (key, label, fmt, _) in enumerate(metrics_config):
    with cols[i]:
        v = last_val(key)
        d = delta_pct(key)
        if v:
            color = "green" if (d or 0) >= 0 else "red"
            arr   = "▲" if (d or 0) >= 0 else "▼"
            delta_str = f"{arr} {abs(d):.2f}%" if d is not None else "–"
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
                <div class="metric-value gray">–</div>
                <div class="metric-delta gray">데이터 없음</div>
            </div>
            """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── 탭 ────────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "📊 1단계: 동행성 분석",
    "🔬 2~3단계: 유동성 골절 분석",
    "🏁 종합 판독 & 결론",
])

PLOTLY_LIGHT = dict(
    template="plotly_white",
    paper_bgcolor="white",
    plot_bgcolor="#fafbfc",
    font=dict(color="#1a202c"),
)


# ════════════════════════════════════════════════════════════════════════════
# TAB 1: 동행성 분석
# ════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("### 📈 핵심 지표 정규화 추세 비교")

    def normalize(series):
        s = series.dropna()
        if s.empty: return s
        return (s - s.min()) / (s.max() - s.min()) * 100

    colors_map = {
        "TNX": ("#dc2626", "미국 10Y 금리"),
        "SPX": ("#16a34a", "S&P 500"),
        "EEM": ("#2563eb", "EEM 신흥국주식"),
        "EMB": ("#d97706", "EMB 신흥국채권"),
        "DXY": ("#7c3aed", "달러 지수 (DXY)"),
    }

    fig = go.Figure()
    has_data = False
    for key, (color, label) in colors_map.items():
        if key in market_data:
            norm = normalize(market_data[key])
            if not norm.empty:
                has_data = True
                fig.add_trace(go.Scatter(
                    x=norm.index, y=norm.values,
                    name=label,
                    line=dict(color=color, width=2.2),
                    hovertemplate=f"<b>{label}</b><br>날짜: %{{x|%Y-%m-%d}}<br>정규화: %{{y:.1f}}<extra></extra>"
                ))

    fig.update_layout(
        **PLOTLY_LIGHT,
        height=380,
        title=dict(text="핵심 지표 정규화 비교 (0~100 스케일)", font=dict(size=14, color="#1a202c")),
        xaxis=dict(gridcolor="#f0f0f0", showgrid=True),
        yaxis=dict(gridcolor="#f0f0f0", showgrid=True, title="정규화 값 (0~100)"),
        legend=dict(bgcolor="rgba(255,255,255,0.9)", bordercolor="#e2e8f0", borderwidth=1),
        hovermode="x unified",
        margin=dict(t=50, b=20, l=10, r=10),
    )

    if has_data:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️ 시장 데이터를 가져오지 못했습니다. 🔄 새로고침을 눌러보세요.")

    # 판독 + 방향 요약
    col_alert, col_dir = st.columns([3, 2])

    tnx_d = delta_pct("TNX"); spx_d = delta_pct("SPX")
    eem_d = delta_pct("EEM"); emb_d = delta_pct("EMB")
    dxy_d = delta_pct("DXY")

    with col_alert:
        st.markdown("#### 🚨 자동 판독 알림")
        alerts = []

        if tnx_d is not None and spx_d is not None:
            if tnx_d > 0 and spx_d > 0:
                alerts.append(("success", "✅ 성장 달러 신호: 금리↑ + 주식↑ 동반 상승 → 미국 경제 성장 기대 반영. 달러 강세는 구조적 성격."))
            elif tnx_d > 0 and spx_d < 0:
                alerts.append(("danger", "🚨 공포 달러 경고: 금리↑ + 주식↓ 역방향 발생 → 위험회피 국면. EM 자금 이탈 주의!"))
            elif tnx_d < 0 and spx_d < 0:
                alerts.append(("warning", "⚠️ 복합 약세 신호: 금리↓ + 주식↓ 동반 하락 → 경기침체 우려. 안전자산 수요 점검 필요."))
            else:
                alerts.append(("info", "💡 유동성 랠리 신호: 금리↓ + 주식↑ → 완화적 금융 환경. 달러 강세 지속성 불투명."))

        if eem_d is not None and emb_d is not None:
            if eem_d < -1.0 and emb_d < -1.0:
                alerts.append(("danger", "🚨 EM 전면 이탈: EEM + EMB 동반 급락 → 신흥국 유동성 위기 경고!"))
            elif eem_d < -0.5 or emb_d < -0.5:
                alerts.append(("warning", "⚠️ EM 부분 이탈 감지: 신흥국 자산 선별적 약세. 달러 강세 압력 지속 중."))

        if dxy_d is not None:
            if dxy_d > 0.5:
                alerts.append(("warning", f"📊 DXY 강세 가속 (+{dxy_d:.2f}%): 달러 지수 급등 → 원화·신흥국 통화 압박 예상."))
            elif dxy_d < -0.5:
                alerts.append(("info", f"📊 DXY 약세 전환 ({dxy_d:.2f}%): 달러 지수 하락 → 위험자산 숨통."))

        if not alerts:
            alerts.append(("info", "📡 현재 뚜렷한 방향성 신호 없음. 지속 모니터링 권장."))

        for atype, msg in alerts:
            st.markdown(f'<div class="alert-{atype}">{msg}</div>', unsafe_allow_html=True)

    with col_dir:
        st.markdown("#### 📋 지표 방향 요약")
        def arrow_badge(d):
            if d is None: return "–", "gray"
            if d >= 0: return f"▲ +{d:.2f}%", "green"
            return f"▼ {d:.2f}%", "red"

        dir_items = [
            ("미국 10Y 금리", delta_pct("TNX")),
            ("S&P 500",       delta_pct("SPX")),
            ("EEM 신흥국주식", delta_pct("EEM")),
            ("EMB 신흥국채권", delta_pct("EMB")),
            ("달러 지수 DXY",  delta_pct("DXY")),
            ("미국 3M 금리",   delta_pct("IRX")),
        ]
        for lbl, d in dir_items:
            txt, color = arrow_badge(d)
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; align-items:center;
                        padding:9px 12px; background:white; border-radius:8px;
                        border:1px solid #e2e8f0; margin:4px 0; font-size:0.83rem;">
                <span style="color:#4a5568; font-weight:500;">{lbl}</span>
                <span style="font-weight:700;" class="{color}">{txt}</span>
            </div>
            """, unsafe_allow_html=True)

    # 상관관계 히트맵
    st.markdown("---")
    st.markdown("#### 🔥 지표 간 상관관계")
    ret_series = []
    ret_labels = {"TNX":"10Y금리","SPX":"S&P500","EEM":"EEM","EMB":"EMB","DXY":"DXY"}
    for key, label in ret_labels.items():
        if key in market_data:
            s = market_data[key].dropna().pct_change().rename(label)
            ret_series.append(s)

    if len(ret_series) >= 2:
        corr = pd.concat(ret_series, axis=1).corr()
        fig_corr = go.Figure(go.Heatmap(
            z=corr.values,
            x=corr.columns.tolist(),
            y=corr.index.tolist(),
            colorscale=[[0,"#dc2626"],[0.5,"#f9fafb"],[1,"#16a34a"]],
            zmin=-1, zmax=1,
            text=np.round(corr.values, 2),
            texttemplate="%{text}",
            hovertemplate="<b>%{y} vs %{x}</b><br>상관계수: %{z:.2f}<extra></extra>",
        ))
        fig_corr.update_layout(
            **PLOTLY_LIGHT,
            height=280,
            margin=dict(l=10, r=10, t=20, b=10),
            title=dict(text="일간 수익률 상관계수", font=dict(size=13)),
        )
        st.plotly_chart(fig_corr, use_container_width=True)


# ════════════════════════════════════════════════════════════════════════════
# TAB 2: 유동성 골절 분석
# ════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### 🔬 스왑 포인트 & CIP 이탈 분석")
    st.markdown("""
    <div class="alert-info">
    💡 <b>CIP (Covered Interest Parity)</b>: 이자율 평가 조건.
    이론가와 실제 스왑 포인트의 <b>괴리</b>는 달러 조달 경색의 핵심 신호입니다.
    </div>
    """, unsafe_allow_html=True)

    col_inp, col_result = st.columns([1.1, 1.9])

    with col_inp:
        st.markdown("#### 📝 데이터 입력")

        irx_val = last_val("IRX")
        default_us3m = round(irx_val, 2) if irx_val else 3.69
        if irx_val:
            st.info(f"💡 yfinance 자동수집: 미국 3M = **{irx_val:.2f}%**")

        spot    = st.number_input("현물 환율 (USD/KRW)",   value=1440.0, step=1.0,  format="%.2f")
        us_3m   = st.number_input("미국 3M 금리 (%)",      value=float(default_us3m), step=0.01, format="%.2f")
        kr_3m   = st.number_input("한국 3M 금리 (%)",      value=2.70,  step=0.01, format="%.2f")
        days    = st.slider("계약 만기 (일)",               min_value=30, max_value=365, value=90, step=30)
        swap_bid= st.number_input("실제 스왑포인트 Bid",    value=-720.0, step=1.0,  format="%.2f")
        swap_ask= st.number_input("실제 스왑포인트 Ask",    value=-220.0, step=1.0,  format="%.2f")

    with col_result:
        st.markdown("#### 📊 CIP 계산 결과")

        t = days / 360
        domestic, foreign = kr_3m / 100, us_3m / 100
        theoretical_rate = spot * (domestic - foreign) / (1 + foreign) * t
        swap_mid   = (swap_bid + swap_ask) / 2
        basis      = swap_bid - theoretical_rate
        friction   = swap_ask - swap_bid
        deviation_pct = (basis / abs(theoretical_rate) * 100) if theoretical_rate != 0 else 0

        # 결과 카드 4개
        r1, r2, r3, r4 = st.columns(2), st.columns(2)
        res_cols = st.columns(2)

        def result_card(label, value_str, color, sublabel=""):
            return f"""
            <div class="metric-card" style="margin-bottom:10px;">
                <div class="metric-label">{label}</div>
                <div class="metric-value {color}">{value_str}</div>
                <div class="metric-delta gray">{sublabel}</div>
            </div>"""

        b_color = "red" if basis < -50 else "yellow" if basis < 0 else "green"
        f_color = "red" if friction > 300 else "yellow" if friction > 150 else "green"

        with res_cols[0]:
            st.markdown(result_card("이론 스왑포인트 (CIP)", f"{theoretical_rate:+.2f}", "blue", f"{days}일 기준"), unsafe_allow_html=True)
            st.markdown(result_card("베이시스 괴리 (Bid−이론가)", f"{basis:+.2f}", b_color, f"괴리율 {deviation_pct:+.1f}%"), unsafe_allow_html=True)
        with res_cols[1]:
            st.markdown(result_card("실제 스왑 Mid", f"{swap_mid:+.2f}", "gray", f"Bid {swap_bid:+.0f} / Ask {swap_ask:+.0f}"), unsafe_allow_html=True)
            st.markdown(result_card("마찰계수 (Ask−Bid)", f"{friction:+.2f}", f_color, "시장 거래비용"), unsafe_allow_html=True)

        # 막대 차트
        fig_bar = go.Figure()
        bar_colors = [
            "#2563eb", "#d97706", "#d97706",
            "#dc2626" if basis < -50 else "#d97706" if basis < 0 else "#16a34a"
        ]
        fig_bar.add_trace(go.Bar(
            x=["이론가 (CIP)", "실제 Bid", "실제 Ask", "베이시스 괴리"],
            y=[theoretical_rate, swap_bid, swap_ask, basis],
            marker_color=bar_colors,
            text=[f"{v:+.1f}" for v in [theoretical_rate, swap_bid, swap_ask, basis]],
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>값: %{y:+.2f}<extra></extra>"
        ))
        fig_bar.add_hline(y=0, line_dash="dot", line_color="#9ca3af", line_width=1.5)
        fig_bar.update_layout(
            **PLOTLY_LIGHT,
            height=260,
            title=dict(text="이론가 vs 실제 스왑 포인트 비교", font=dict(size=13, color="#1a202c")),
            xaxis=dict(gridcolor="#f0f0f0"),
            yaxis=dict(gridcolor="#f0f0f0", title="스왑 포인트 (원)"),
            margin=dict(t=50, b=20, l=10, r=10),
            showlegend=False,
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        # 유동성 판정 신호
        if basis < -200 or friction > 300:
            sig_class, sig_emoji, sig_text = "signal-tight", "🚨", "경고: 달러 접근 경색 발생!"
            sig_desc = f"베이시스 괴리 {basis:+.1f}pt / 마찰계수 {friction:.1f}pt → 달러 조달 비용 급등. 스왑시장 기능 저하 경보."
        elif basis < -50 or friction > 150:
            sig_class, sig_emoji, sig_text = "signal-fear", "⚠️", "주의: 유동성 골절 감지"
            sig_desc = f"베이시스 이탈 {deviation_pct:.1f}% → CIP 조건 위반. 시장 마찰 상승 중."
        elif basis > 0:
            sig_class, sig_emoji, sig_text = "signal-growth", "✅", "정상: CIP 균형 유지"
            sig_desc = "이론가 대비 실제 스왑 포인트 정상 범위. 달러 조달 원활."
        else:
            sig_class, sig_emoji, sig_text = "signal-neutral", "📊", "관찰: 소폭 괴리 발생"
            sig_desc = f"경미한 베이시스 이탈 ({deviation_pct:.1f}%). 지속 모니터링 권장."

        st.markdown(f"""
        <div class="{sig_class}" style="margin-top:12px;">
            <div class="signal-title">유동성 골절 판정</div>
            <div class="signal-body">{sig_emoji} {sig_text}</div>
            <div class="signal-desc">{sig_desc}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    **📐 계산 공식:**
    - **이론 스왑** = Spot × (국내금리 − 해외금리) / (1 + 해외금리) × (Days/360)  
    - **베이시스** = 실제 Bid − 이론 스왑  
    - **마찰계수** = 실제 Ask − 실제 Bid
    """)


# ════════════════════════════════════════════════════════════════════════════
# TAB 3: 종합 판독
# ════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("### 🏁 종합 판독: 오늘의 달러 품질")

    tnx_d_v = delta_pct("TNX") or 0
    spx_d_v = delta_pct("SPX") or 0
    eem_d_v = delta_pct("EEM") or 0
    emb_d_v = delta_pct("EMB") or 0
    dxy_d_v = delta_pct("DXY") or 0

    growth_score = fear_score = tight_score = 0

    if tnx_d_v > 0 and spx_d_v > 0:   growth_score += 2
    elif tnx_d_v > 0 and spx_d_v < 0: fear_score  += 2
    elif tnx_d_v < 0 and spx_d_v < 0: fear_score  += 1

    if eem_d_v < -1.0:   fear_score   += 2
    elif eem_d_v < 0:    fear_score   += 1
    elif eem_d_v > 0.5:  growth_score += 1

    if emb_d_v < -1.0:   fear_score   += 2
    elif emb_d_v < 0:    fear_score   += 1

    if dxy_d_v > 0.5:    fear_score   += 1
    elif dxy_d_v < -0.5: growth_score += 1

    try:
        if basis < -200:   tight_score += 3
        elif basis < -50:  tight_score += 2
        elif basis < 0:    tight_score += 1
        if friction > 300: tight_score += 2
        elif friction > 150: tight_score += 1
    except Exception:
        pass

    total = growth_score + fear_score + tight_score
    if total == 0:                                  verdict = "neutral"
    elif tight_score >= 3:                          verdict = "tight"
    elif fear_score > growth_score and fear_score >= 2: verdict = "fear"
    elif growth_score > fear_score:                 verdict = "growth"
    else:                                           verdict = "neutral"

    verdict_map = {
        "growth":  ("signal-growth",  "🦖 성장 달러", "달러 강세의 질이 '성장'에 기반합니다. 미국 경제 호조로 자금이 유입되는 구조적 강세국면. 위험자산과 달러가 함께 상승하는 이상적 환경입니다."),
        "fear":    ("signal-fear",    "💀 공포 달러", "달러 강세의 질이 '공포'에 기반합니다. 위험회피 수요로 달러가 강세를 보이는 국면. 주식·EM 자산 동반 약세, 안전자산 선호 확대."),
        "tight":   ("signal-tight",   "🔥 경색 달러", "달러 강세의 질이 '경색'에 기반합니다. CIP 이탈 및 스왑 마찰 심화. 달러 조달 비용 급등으로 금융시장 기능 저하 우려."),
        "neutral": ("signal-neutral", "📊 관찰 구간", "현재 뚜렷한 달러 품질 판정이 어렵습니다. 추가 지표 모니터링과 데이터 입력을 권장합니다."),
    }

    v_class, v_title, v_desc = verdict_map[verdict]

    col_v, col_s = st.columns([2, 1])
    with col_v:
        st.markdown(f"""
        <div class="{v_class}" style="padding:32px;">
            <div class="signal-title" style="font-size:0.85rem;">오늘의 달러 품질 판정</div>
            <div class="signal-body" style="font-size:3rem; margin:14px 0;">{v_title}</div>
            <div class="signal-desc" style="font-size:0.92rem;">{v_desc}</div>
        </div>
        """, unsafe_allow_html=True)

    with col_s:
        st.markdown("#### 📊 점수 분포")
        fig_score = go.Figure(go.Bar(
            y=["🟢 성장", "🔴 공포", "🟡 경색"],
            x=[growth_score, fear_score, tight_score],
            orientation="h",
            marker_color=["#16a34a", "#dc2626", "#d97706"],
            text=[f"{growth_score}pt", f"{fear_score}pt", f"{tight_score}pt"],
            textposition="outside",
        ))
        fig_score.update_layout(
            **PLOTLY_LIGHT,
            height=200,
            margin=dict(l=10, r=60, t=10, b=10),
            xaxis=dict(gridcolor="#f0f0f0", range=[0, max(growth_score, fear_score, tight_score, 1)+1.5]),
            yaxis=dict(gridcolor="rgba(0,0,0,0)"),
            showlegend=False,
        )
        st.plotly_chart(fig_score, use_container_width=True)

    # 요약 테이블
    st.markdown("### 📋 전체 지표 요약")
    try:
        basis_v      = f"{basis:+.1f}pt (괴리율 {deviation_pct:+.1f}%)"
        friction_v   = f"{friction:.1f}pt"
        theoretical_v= f"{theoretical_rate:+.1f}"
    except Exception:
        basis_v = friction_v = theoretical_v = "탭2 입력 필요"

    summary_data = {
        "단계":   ["1단계","1단계","1단계","1단계","1단계","2~3단계","2~3단계","2~3단계"],
        "지표":   ["미국 10Y 금리","S&P 500","EEM 신흥국주식","EMB 신흥국채권","달러 지수(DXY)","CIP 이론 스왑포인트","베이시스 괴리","마찰계수(Bid-Ask)"],
        "현재값": [
            f"{last_val('TNX'):.2f}%" if last_val('TNX') else "–",
            f"{last_val('SPX'):,.0f}" if last_val('SPX') else "–",
            f"${last_val('EEM'):.2f}" if last_val('EEM') else "–",
            f"${last_val('EMB'):.2f}" if last_val('EMB') else "–",
            f"{last_val('DXY'):.2f}"  if last_val('DXY') else "–",
            theoretical_v, basis_v, friction_v,
        ],
        "일간변화": [
            f"{tnx_d_v:+.2f}%", f"{spx_d_v:+.2f}%", f"{eem_d_v:+.2f}%",
            f"{emb_d_v:+.2f}%", f"{dxy_d_v:+.2f}%", "–","–","–",
        ],
        "신호": [
            "🔴" if tnx_d_v > 0.05 else "🟢" if tnx_d_v < -0.05 else "⚪",
            "🟢" if spx_d_v > 0 else "🔴" if spx_d_v < 0 else "⚪",
            "🟢" if eem_d_v > 0 else "🔴" if eem_d_v < 0 else "⚪",
            "🟢" if emb_d_v > 0 else "🔴" if emb_d_v < 0 else "⚪",
            "🔴" if dxy_d_v > 0.3 else "🟢" if dxy_d_v < -0.3 else "⚪",
            "–",
            "🚨" if isinstance(basis, float) and basis < -200 else "⚠️" if isinstance(basis, float) and basis < -50 else "🟢",
            "🚨" if isinstance(friction, float) and friction > 300 else "⚠️" if isinstance(friction, float) and friction > 150 else "🟢",
        ]
    }
    df_summary = pd.DataFrame(summary_data)
    st.dataframe(df_summary, use_container_width=True, hide_index=True)

    # 바로가기 링크
    st.markdown("---")
    st.markdown("### 🔗 데이터 수집 바로가기")
    link_cols = st.columns(4)
    links = [
        ("📈 미국 10Y 금리",  "https://kr.investing.com/rates-bonds/u.s.-10-year-bond-yield"),
        ("🌏 EMB 신흥국채권", "https://kr.investing.com/etfs/ishares-jp-morgan-usd-em-bond-etf"),
        ("🇰🇷 한국 3M 금리", "https://kr.investing.com/rates-bonds/south-korea-3-month-bond-yield"),
        ("💱 USD/KRW 현물",  "https://kr.investing.com/currencies/usd-krw"),
    ]
    for i, (label, url) in enumerate(links):
        with link_cols[i]:
            st.link_button(label, url, use_container_width=True)

    st.markdown("---")
    st.markdown("""
    <div style="text-align:center; color:#718096; font-size:0.78rem; margin-top:10px; padding:12px; background:#f7f9fc; border-radius:8px; border:1px solid #e2e8f0;">
    💵 달러 강세 품질 분석 대시보드 · 데이터: yfinance (Yahoo Finance) · 스왑 데이터: 사용자 입력<br>
    <b>본 대시보드는 투자 조언이 아니며, 참고용 분석 도구입니다.</b>
    </div>
    """, unsafe_allow_html=True)
