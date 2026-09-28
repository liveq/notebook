"""
철망 바스켓(내경 214 x 88) 내부 칸막이 v2 - 탈부착 스냅 클립형

배치 (운전석 쪽 -> 창문 쪽)
- 앞벽 70 (운전석 쪽으로 떨어지는 것 방지)
- 폰 칸: 갤럭시 Z 폴드3 접은 상태 (158.2 x 67.1 x 16, 케이스 포함 약 162 x 71 x 20)
- 칸막이 50
- 무전기 칸: IDIS 라져+20 (59 x 145 x 23, 케이스 포함 약 64 x 150 x 28)
- 무전기 칸 뒷벽 32
- 남는 깊이 -> 창문 쪽 소형 수납칸 (바깥 벽 28)

고정 (필라멘트만 사용, 접착/나사 없음)
- 앞벽 2개 + 좌우 끝벽 각 1개 = 스냅 클립 4개
- 클립 = 벽에 U자 슬릿을 내서 만든 탄성 탭 + 바깥면 톱니(래칫)
- 위에서 눌러 넣으면 톱니가 바스켓 테두리 철사(지름 3) 아래로 걸림
- 톱니를 3mm 간격 여러 개로 둬서 테두리 높이(30~40)가 달라도 가장 가까운 톱니가 걸림
- 톱니 윗면 20도 경사: 흔들림에는 버티고, 손으로 세게 들어 올리면 탭이 휘면서 빠짐
- 잘 안 빠지면 탭 윗끝 안쪽의 손잡이 턱을 칸 안쪽으로 당기면서 들어 올림

출력 방향: 바닥이 베드에 닿는 그대로 -> 서포트 불필요 (톱니 아랫면 45도)

사용법:
    python3 make_insert.py
    python3 make_insert.py --radio-slot 36 --phone-slot 24 --wire-d 3.0
    python3 make_insert.py --rim-min 30 --rim-max 40   # 테두리 높이 범위

필요 패키지: pip install manifold3d trimesh matplotlib numpy
"""

import argparse
import json
import math
import os

import numpy as np
import manifold3d as m3d
import trimesh

# ---------------------------------------------------------------------------
# 파라미터 (단위 mm). X = 바스켓 길이(좌->우), Y = 깊이(운전석 0 -> 창문 +), Z = 높이
# ---------------------------------------------------------------------------
DEFAULTS = dict(
    basket_len=214.0,
    basket_depth=88.0,
    fit_clear=1.0,         # 바스켓 내경 대비 한쪽 여유 -> 본체 212 x 86

    wall=2.4,
    floor=2.4,

    phone_slot=26.0,       # 폰 칸 안쪽 폭 (폴드3 케이스 포함 약 20 + 여유 6)
    radio_slot=34.0,       # 무전기 칸 안쪽 폭 (두께 약 28 + 여유 6)
    # 남는 깊이 -> 창문 쪽 수납칸 (기본 86 - 4*2.4 - 26 - 34 = 16.4)

    h_front=70.0,          # 앞벽 (운전석 쪽)
    h_divider=50.0,        # 폰 칸 / 무전기 칸 사이
    h_radio_back=32.0,     # 무전기 칸 뒷벽
    h_back=28.0,           # 수납칸 바깥 벽 (창문 쪽)
    h_end_phone=70.0,      # 폰 칸 양 끝벽
    h_end_radio=45.0,      # 무전기 칸 양 끝벽
    h_end_pocket=28.0,     # 수납칸 양 끝벽

    cable_hole_len=22.0,
    cable_hole_w=14.0,
    cable_hole_gap=3.0,

    radio_len=150.0,
    phone_len=162.0,
    plug_room=35.0,

    # 스냅 클립
    wire_d=3.0,            # 바스켓 테두리 철사 지름
    rim_min=30.0,          # 바스켓 바닥 철사 윗면 ~ 테두리 철사 윗면 높이 (최소)
    rim_max=40.0,          # (최대)
    tooth_pitch=3.0,
    tooth_out=2.4,         # 톱니가 벽 바깥면에서 튀어나온 길이 (여유 1.0 -> 철사에 1.4 걸림)
    tab_w=10.0,            # 탭 폭
    slit=1.0,              # 탭 주위 슬릿 폭
    tab_root=10.0,         # 탭 뿌리 높이 (이 아래는 벽과 붙어 있음)
    front_tab_x=[0.25, 0.75],   # 앞벽 탭 위치 (길이 비율)
    release_deg=20.0,      # 톱니 윗면 경사 (0 = 수평: 절대 안 빠짐 / 20 = 세게 들면 빠짐)
    grip=3.0,              # 탭 윗끝 안쪽 손잡이 턱 돌출 (분리할 때 당기는 곳)
)


def box(x0, y0, z0, x1, y1, z1):
    return m3d.Manifold.cube((x1 - x0, y1 - y0, z1 - z0)).translate((x0, y0, z0))


# ---------------------------------------------------------------------------
def layout(p):
    L = p["basket_len"] - 2 * p["fit_clear"]
    D = p["basket_depth"] - 2 * p["fit_clear"]
    w = p["wall"]
    phone = (w, w + p["phone_slot"])
    radio = (phone[1] + w, phone[1] + w + p["radio_slot"])
    rest = D - radio[1] - w          # 무전기 칸 뒷벽 뒤로 남는 깊이
    if rest < 0:
        raise SystemExit(f"깊이 부족: 칸 폭 합계가 {D:.0f} 를 넘음")
    if rest >= 6 + w:                # 수납칸 생성
        pocket = (radio[1] + w, D - w)
    else:                            # 남는 깊이는 무전기 칸에 합침
        radio = (radio[0], D - w)
        pocket = None
    walls = [  # (y0, y1, 높이)
        (0, w, p["h_front"]),
        (phone[1], radio[0], p["h_divider"]),
    ]
    if pocket:
        walls += [(radio[1], pocket[0], p["h_radio_back"]), (pocket[1], D, p["h_back"])]
    else:
        walls += [(radio[1], D, p["h_radio_back"])]
    ends = [(0, phone[1] + w / 2, p["h_end_phone"]),
            (phone[1] + w / 2, radio[1] + (w / 2 if pocket else w), p["h_end_radio"])]
    if pocket:
        ends += [(radio[1] + w / 2, D, p["h_end_pocket"])]
    return dict(L=L, D=D, phone=phone, radio=radio, pocket=pocket, walls=walls, ends=ends)


def tooth_tops(p):
    """톱니 윗면(걸림면) 높이 목록: 철사 아랫면 = 테두리 높이 - 지름."""
    lo = p["rim_min"] - p["wire_d"]
    hi = p["rim_max"] - p["wire_d"]
    n = int(math.floor((hi - lo) / p["tooth_pitch"] + 1e-6)) + 1
    return [lo + i * p["tooth_pitch"] for i in range(n)]


def tabs(p, g):
    """탭 목록: (중심 좌표, 바깥 방향 벡터, 벽 따라가는 방향 벡터, 벽 두께 방향 시작점)."""
    L, w = g["L"], p["wall"]
    out = []
    for f in p["front_tab_x"]:
        out.append(dict(c=np.array([L * f, 0.0]), n=np.array([0.0, -1.0]), t=np.array([1.0, 0.0])))
    yc = sum(g["phone"]) / 2
    out.append(dict(c=np.array([0.0, yc]), n=np.array([-1.0, 0.0]), t=np.array([0.0, 1.0])))
    out.append(dict(c=np.array([L, yc]), n=np.array([1.0, 0.0]), t=np.array([0.0, 1.0])))
    return out


def place(solid_local, tab):
    """로컬 좌표(X=바깥방향 u, Y=높이 z, Z=벽 따라 폭 방향)를 월드 좌표로.
    tab['c'] = 벽 바깥면 위 탭 중심."""
    n = np.array([*tab["n"], 0.0])
    zh = np.array([0.0, 0.0, 1.0])
    t = np.array([*tab["t"], 0.0])
    if np.linalg.det(np.column_stack([n, zh, t])) < 0:
        t = -t
    o = np.array([*tab["c"], 0.0])
    M = np.column_stack([n, zh, t, o])
    return solid_local.transform(M.tolist())


def tab_features(p):
    """(자를 슬릿, 붙일 톱니) 로컬 솔리드."""
    w, s, tw = p["wall"], p["slit"], p["tab_w"]
    tops = tooth_tops(p)
    z_top = max(tops) + 3.0              # 탭 자유단 높이
    half = tw / 2
    # 슬릿: 탭 양옆 + 위 (u 방향 = 벽 두께, 바깥면 u=0, 안쪽 u=-w)
    cut = (box(-w - 1, p["tab_root"], -half - s, 1, z_top + s, -half)
           + box(-w - 1, p["tab_root"], half, 1, z_top + s, half + s)
           + box(-w - 1, z_top, -half - s, 1, z_top + s, half + s))
    # 톱니 단면 (u, z): 아랫면 45도, 윗면 수평
    teeth = None
    to = p["tooth_out"]
    for zt in tops:
        rise = to * math.tan(math.radians(p["release_deg"]))
        poly = [(-0.6, zt - to - 0.01), (0.0, zt - to), (to, zt), (0.0, zt + rise), (-0.6, zt + rise)]
        cs = m3d.CrossSection([poly])
        solid = cs.extrude(tw).translate((0, 0, -half))
        teeth = solid if teeth is None else teeth + solid
    # 분리용 손잡이 턱: 탭 윗끝 안쪽면, 아랫면 45도 (칸 안쪽에서 손가락으로 당김)
    g = p["grip"]
    grip = m3d.CrossSection([[(-w + 0.5, z_top - g - 0.5), (-w + 0.5, z_top),
                              (-w - g, z_top), (-w - g, z_top - 0.5)]])
    teeth += grip.extrude(tw).translate((0, 0, -half))
    return cut, teeth, z_top


def insert_solid(p, g):
    L, D, w, f = g["L"], g["D"], p["wall"], p["floor"]
    s = box(0, 0, 0, L, D, f)
    for y0, y1, h in g["walls"]:
        s += box(0, y0, 0, L, y1, h)
    for y0, y1, h in g["ends"]:
        s += box(0, y0, 0, w, y1, h) + box(L - w, y0, 0, L, y1, h)

    for slot in (g["phone"], g["radio"]):
        y0, y1 = slot
        yc = (y0 + y1) / 2
        hw = min(p["cable_hole_w"], y1 - y0 - 4) / 2
        for xa in (w + p["cable_hole_gap"], L - w - p["cable_hole_gap"] - p["cable_hole_len"]):
            s -= box(xa, yc - hw, -1, xa + p["cable_hole_len"], yc + hw, f + 1)

    cut, teeth, _ = tab_features(p)
    for tb in tabs(p, g):
        s -= place(cut, tb)
    for tb in tabs(p, g):
        s += place(teeth, tb)
    return s


def coupon_solid(p):
    """클립 테스트 조각: 벽 40 x 높이(톱니+여유) + 바닥 띠 20. 테두리에 끼워 보는 용도."""
    w = p["wall"]
    cut, teeth, z_top = tab_features(p)
    h = z_top + 6
    s = box(-20, 0, 0, 20, w, h) + box(-20, 0, 0, 20, 20, p["floor"])
    tb = dict(c=np.array([0.0, 0.0]), n=np.array([0.0, -1.0]), t=np.array([1.0, 0.0]))
    return s - place(cut, tb) + place(teeth, tb)


def spacer_solid(slot_w, length, height):
    w = slot_w - 1.0
    s = box(0, 0, 0, length, w, height)
    notch = m3d.Manifold.cylinder(w + 2, 7, 7, 48).rotate((-90, 0, 0)).translate(
        (length / 2, -1, height + 3))
    return s - notch


def save_stl(solid, path):
    mesh = solid.to_mesh()
    tm = trimesh.Trimesh(vertices=np.asarray(mesh.vert_properties)[:, :3],
                         faces=np.asarray(mesh.tri_verts), process=True)
    tm.apply_translation(-tm.bounds[0])
    assert tm.is_watertight, f"{path}: watertight 아님"
    assert tm.volume > 0, f"{path}: 면 방향 뒤집힘"
    tm.export(path)
    return tm


# ---------------------------------------------------------------------------
def draw(p, g, spacers, out_png, out_pdf):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    from matplotlib.patches import Rectangle, Polygon as MPoly, Circle

    for fnt in ("NanumGothic", "Noto Sans CJK KR", "Noto Sans KR"):
        if any(fnt in x.name for x in font_manager.fontManager.ttflist):
            plt.rcParams["font.family"] = fnt
            plt.rcParams["axes.unicode_minus"] = False
            break
    L, D, w, f = g["L"], g["D"], p["wall"], p["floor"]
    WALL = "#6d8fb3"
    fig = plt.figure(figsize=(16.5, 11.7))
    fig.suptitle(f"바스켓 칸막이 v2 (탈부착 스냅 클립) {L:.0f} x {D:.0f} x {p['h_front']:.0f} mm",
                 fontsize=16, x=0.04, ha="left", y=0.985)

    # 평면도
    ax = fig.add_axes([0.04, 0.44, 0.58, 0.48])
    ax.add_patch(Rectangle((-p["fit_clear"], -p["fit_clear"]), p["basket_len"], p["basket_depth"],
                           fill=False, ls="--", ec="#8b5a2b"))
    ax.add_patch(Rectangle((0, 0), L, D, fc="#dfe8f2", ec="#333"))
    for y0, y1, _ in g["walls"]:
        ax.add_patch(Rectangle((0, y0), L, y1 - y0, fc=WALL, ec="none"))
    for x0 in (0, L - w):
        ax.add_patch(Rectangle((x0, 0), w, D, fc=WALL, ec="none"))
    for (y0, y1), name, dl, dt in ((g["phone"], "폰 칸 (폴드3)", 162, 20),
                                   (g["radio"], "무전기 칸 (라져+20)", 150, 28)):
        yc = (y0 + y1) / 2
        hw = min(p["cable_hole_w"], y1 - y0 - 4) / 2
        for xa in (w + p["cable_hole_gap"], L - w - p["cable_hole_gap"] - p["cable_hole_len"]):
            ax.add_patch(Rectangle((xa, yc - hw), p["cable_hole_len"], 2 * hw, fc="white", ec="#333"))
        ax.add_patch(Rectangle(((L - dl) / 2, yc - dt / 2), dl, dt, fill=False, ec="#c0392b", ls=":"))
        ax.text(L / 2, yc, f"{name}  안쪽 {y1 - y0:.1f}", ha="center", va="center", fontsize=10)
    if g["pocket"]:
        ax.text(L / 2, sum(g["pocket"]) / 2, f"수납칸 {g['pocket'][1] - g['pocket'][0]:.1f}",
                ha="center", va="center", fontsize=9)
    for tb in tabs(p, g):
        c, n, t = tb["c"], tb["n"], tb["t"]
        pts = [c - t * p["tab_w"] / 2, c + t * p["tab_w"] / 2,
               c + t * p["tab_w"] / 2 + n * p["tooth_out"], c - t * p["tab_w"] / 2 + n * p["tooth_out"]]
        ax.add_patch(MPoly(pts, fc="#e67e22", ec="#a04000"))
    ax.annotate("", (0, -10), (L, -10), arrowprops=dict(arrowstyle="<->"))
    ax.text(L / 2, -13, f"{L:.0f} (바스켓 {p['basket_len']:.0f})", ha="center", va="top")
    ax.annotate("", (L + 9, 0), (L + 9, D), arrowprops=dict(arrowstyle="<->"))
    ax.text(L + 12, D / 2, f"{D:.0f}\n(바스켓 {p['basket_depth']:.0f})", va="center")
    ax.text(L / 2, D + 4, "창문 쪽", ha="center", color="#555")
    ax.text(L / 2, -24, "운전석 쪽 (앞벽 높음)", ha="center", color="#555")
    ax.set_xlim(-12, L + 40); ax.set_ylim(-30, D + 10)
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_title("평면도 (주황 = 스냅 클립 4개, 흰 사각형 = 케이블 구멍)", loc="left", fontsize=12)

    # 단면
    ax2 = fig.add_axes([0.66, 0.44, 0.31, 0.48])
    ax2.add_patch(Rectangle((0, 0), D, f, fc=WALL))
    for y0, y1, h in g["walls"]:
        ax2.add_patch(Rectangle((y0, 0), y1 - y0, h, fc=WALL))
        ax2.text((y0 + y1) / 2, h + 1.5, f"{h:.0f}", ha="center", fontsize=10)
    ax2.plot([-p["fit_clear"]] * 2 + [D + p["fit_clear"]] * 2,
             [p["rim_min"], 0, 0, p["rim_min"]], color="#8b5a2b", ls="--", lw=1.5)
    ax2.text(D / 2, -4, "갈색 점선 = 바스켓 (테두리 30~40)", ha="center", color="#8b5a2b", fontsize=9)
    py = g["phone"][0] + 2
    ax2.add_patch(Rectangle((py, f), 20, 71, fill=False, ec="#c0392b", ls=":"))
    ax2.text(py + 10, f + 36, "폴드3\n20x71", ha="center", fontsize=9, color="#c0392b")
    ry = g["radio"][0] + 2
    ax2.add_patch(Rectangle((ry, f), 28, 64, fill=False, ec="#c0392b", ls=":"))
    ax2.text(ry + 14, f + 32, "무전기\n28x64", ha="center", fontsize=9, color="#c0392b")
    ax2.set_xlim(-10, D + 6); ax2.set_ylim(-8, 80)
    ax2.set_aspect("equal"); ax2.set_xticks([]); ax2.set_yticks([])
    ax2.set_title("단면 (옆에서, 왼쪽 = 운전석)", loc="left", fontsize=12)

    # 클립 상세
    ax3 = fig.add_axes([0.04, 0.05, 0.30, 0.34])
    tops = tooth_tops(p)
    _, _, z_top = tab_features(p)
    ax3.add_patch(Rectangle((-w, 0), w, z_top + 12, fc="#b8c9dc"))
    ax3.add_patch(Rectangle((-w, p["tab_root"]), w, z_top - p["tab_root"], fc=WALL))
    ax3.add_patch(Rectangle((-w, z_top), w, p["slit"], fc="white"))
    to = p["tooth_out"]
    for zt in tops:
        rise = to * math.tan(math.radians(p["release_deg"]))
        ax3.add_patch(MPoly([(0, zt - to), (to, zt), (0, zt + rise)], fc=WALL))
    gp = p["grip"]
    ax3.add_patch(MPoly([(-w, z_top - gp - 0.5), (-w, z_top), (-w - gp, z_top), (-w - gp, z_top - 0.5)],
                        fc=WALL))
    ax3.text(-w - gp - 0.5, z_top - 1, "손잡이 턱", ha="right", fontsize=9)
    r = p["wire_d"] / 2
    zc = p["rim_min"] - r
    ax3.add_patch(Circle((p["fit_clear"] + r, zc), r, fc="#8b5a2b"))
    ax3.text(p["fit_clear"] + 2 * r + 1.5, zc, f"테두리 철사 Ø{p['wire_d']}\n(높이 {p['rim_min']:.0f}일 때)",
             va="center", fontsize=9)
    ax3.text(-w - 1, p["tab_root"] + 2, "탭 뿌리", ha="right", fontsize=9)
    ax3.text(-w - 1, z_top, "슬릿", ha="right", fontsize=9)
    ax3.set_xlim(-14, 18); ax3.set_ylim(p["tab_root"] - 4, z_top + 8)
    ax3.set_aspect("equal"); ax3.set_xticks([]); ax3.set_yticks([])
    ax3.set_title("스냅 클립 단면 (래칫 톱니)", loc="left", fontsize=12)

    ax4 = fig.add_axes([0.38, 0.03, 0.59, 0.36]); ax4.axis("off")
    rows = [f"본체 {L:.0f} x {D:.0f} x {p['h_front']:.0f}   벽 {w} / 바닥 {f}",
            f"폰 칸 {g['phone'][1] - g['phone'][0]:.1f}   무전기 칸 {g['radio'][1] - g['radio'][0]:.1f}"
            + (f"   수납칸 {g['pocket'][1] - g['pocket'][0]:.1f}" if g["pocket"] else ""),
            f"벽 높이: 앞 {p['h_front']:.0f} / 칸막이 {p['h_divider']:.0f} / 무전기 뒤 {p['h_radio_back']:.0f}"
            + (f" / 창문쪽 {p['h_back']:.0f}" if g["pocket"] else ""),
            f"스냅 클립 4개 (앞 2, 좌우 1씩): 톱니 {len(tops)}단 "
            f"{min(tops):.0f}~{max(tops):.0f} (간격 {p['tooth_pitch']:.0f}), 철사 걸림 "
            f"{p['tooth_out'] - p['fit_clear']:.1f}",
            f"케이블 구멍 {p['cable_hole_len']:.0f} x {p['cable_hole_w']:.0f} x 4"]
    for k, v in spacers.items():
        rows.append(f"스페이서 {k}: {v[0]:.0f} x {v[1]:.1f} x {v[2]:.0f}")
    ax4.text(0, 1, "\n".join(rows), fontsize=11, va="top", linespacing=1.7)
    notes = ("장착: 위에서 곧게 눌러 넣음 -> 톱니가 테두리 철사 아래로 딸깍\n"
             "분리: 세게 들어 올리면 빠짐 (톱니 윗면 20도) · 뻑뻑하면 손잡이 턱을 안쪽으로 당기며\n"
             "먼저 clip_test.stl 로 테두리에 걸리는지 확인\n"
             "출력: 바닥이 베드, 서포트 없음 · PETG 권장 (PLA 는 탭 피로 파손/여름 변형)\n"
             "0.2mm 레이어 · 벽 3 · 인필 15~20%")
    ax4.text(0, 0.36, notes, fontsize=11, va="top", linespacing=1.7)
    fig.savefig(out_png, dpi=110)
    fig.savefig(out_pdf)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--phone-slot", type=float)
    ap.add_argument("--radio-slot", type=float)
    ap.add_argument("--h-front", type=float)
    ap.add_argument("--h-divider", type=float)
    ap.add_argument("--wire-d", type=float)
    ap.add_argument("--rim-min", type=float)
    ap.add_argument("--rim-max", type=float)
    ap.add_argument("--params", help="파라미터 JSON")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "out"))
    a = ap.parse_args()

    p = dict(DEFAULTS)
    if a.params:
        with open(a.params, encoding="utf-8") as fh:
            p.update(json.load(fh))
    for k, v in (("phone_slot", a.phone_slot), ("radio_slot", a.radio_slot),
                 ("h_front", a.h_front), ("h_divider", a.h_divider), ("wire_d", a.wire_d),
                 ("rim_min", a.rim_min), ("rim_max", a.rim_max)):
        if v is not None:
            p[k] = v

    os.makedirs(a.out, exist_ok=True)
    g = layout(p)
    report = {}
    tm = save_stl(insert_solid(p, g), os.path.join(a.out, "insert.stl"))
    report["insert"] = dict(size=[round(float(e), 1) for e in tm.extents],
                            volume_cm3=round(tm.volume / 1000, 1))
    tm = save_stl(coupon_solid(p), os.path.join(a.out, "clip_test.stl"))
    report["clip_test"] = [round(float(e), 1) for e in tm.extents]

    inner = g["L"] - 2 * p["wall"]
    spacers = {}
    for name, slot, dev_len in (("phone", g["phone"], p["phone_len"]),
                                ("radio", g["radio"], p["radio_len"])):
        length = inner - dev_len - p["plug_room"] - 2.0
        if length >= 8:
            t = save_stl(spacer_solid(slot[1] - slot[0], length, 30.0),
                         os.path.join(a.out, f"spacer_{name}.stl"))
            spacers[name] = (length, slot[1] - slot[0] - 1, 30.0)
            report[f"spacer_{name}"] = [round(float(e), 1) for e in t.extents]

    draw(p, g, spacers, os.path.join(a.out, "drawing.png"), os.path.join(a.out, "drawing.pdf"))
    with open(os.path.join(a.out, "params_used.json"), "w", encoding="utf-8") as fh:
        json.dump(p, fh, ensure_ascii=False, indent=2)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
