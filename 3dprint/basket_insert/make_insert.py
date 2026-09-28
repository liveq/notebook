"""
철망 바스켓(내경 214 x 88) 내부 칸막이 바스켓 생성기

- 맨 앞(운전석 쪽): 좁은 수납칸 (남는 깊이 활용)
- 앞칸: 무전기 (IDIS 라져+20, 59 x 145 x 23, 케이스 포함 약 64 x 150 x 28)
- 뒤칸(창문 쪽): 폰 (갤럭시 Z 폴드3 접은 상태 158.2 x 67.1 x 16, 케이스 포함 약 162 x 71 x 20)
- 둘 다 긴 변을 바닥에 두고 세워서(눕혀서) 거치
- 바스켓 내경을 꽉 채워(212 x 86) 바스켓 벽이 위치를 잡아줌
- 각 칸 양쪽 끝 바닥에 충전 케이블 구멍
- 길이 방향 유격을 잡는 스페이서 블록 (별도 출력)
- 바닥 걸림 핀(철사 틈 2.4mm 에 끼우는 얇은 판): 위치 실측 후 --fin-y 로 활성화
  (본체 바닥 아래로 튀어나오면 서포트가 필요하므로 별도 출력 후 바닥 슬롯에 끼워 접착)

출력 방향: 바닥이 베드에 닿는 그대로 -> 서포트 불필요

사용법:
    python3 make_insert.py
    python3 make_insert.py --radio-slot 40 --phone-slot 34
    python3 make_insert.py --fin-y 43 --fin-dir x     # 걸림 핀 활성화

필요 패키지: pip install manifold3d trimesh matplotlib numpy
"""

import argparse
import json
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

    wall=2.4,              # 벽 두께 (0.4 노즐 6줄)
    floor=2.4,             # 바닥 두께

    radio_slot=34.0,       # 무전기 칸 안쪽 폭 (두께 약 28 + 여유 6)
    phone_slot=26.0,       # 폰 칸 안쪽 폭 (폴드3 케이스 포함 약 20 + 여유 6)
    # 남는 깊이는 운전석 쪽 소형 수납칸(펜/이어폰 등)으로 (기본 86 - 4*2.4 - 34 - 26 = 16.4)

    h_front=28.0,          # 맨 앞벽 높이 (수납칸 바깥)
    h_radio_front=32.0,    # 무전기 칸 앞벽 (바스켓 테두리 30~40 수준 -> 키패드 가리지 않게)
    h_divider=50.0,        # 칸막이 높이 (무전기 세운 높이 약 64 의 3/4)
    h_back=70.0,           # 뒷벽 높이 (폴드3 접은 폭 67.1 + 케이스 ~ 71)
    h_end_radio=45.0,      # 앞칸 양 끝벽 높이
    h_end_phone=70.0,      # 뒤칸 양 끝벽 높이

    cable_hole_len=22.0,   # 케이블 구멍 X 길이 (칸 끝에서부터)
    cable_hole_w=14.0,     # 케이블 구멍 Y 폭 (USB-C 플러그 몸통 약 12)
    cable_hole_gap=3.0,    # 끝벽 안쪽면에서 구멍까지 거리

    # 스페이서 블록: 기기 길이 방향 유격 메우기
    radio_len=150.0,
    phone_len=162.0,
    plug_room=35.0,        # 한쪽 끝 충전 플러그 공간

    # 바닥 걸림 핀 (철사 사이 틈 2.4 에 끼움)
    wire_gap=2.4,
    fin_thick=2.0,         # 틈 2.4 - 공차 0.4
    fin_depth=3.0,         # 바닥 아래로 튀어나오는 길이
    fin_len=40.0,
    fin_y=None,            # None 이면 핀 없음. 값 = 본체 운전석 쪽 바깥면에서 틈 중심까지 거리
    fin_dir="x",           # 철사 틈 방향: x(길이 방향) / y(깊이 방향)
    fin_pos=None,          # 핀 중심 위치 목록 (fin_dir 방향 좌표). None 이면 자동 2개
    fin_slot_clear=0.15,
)


def box(x0, y0, z0, x1, y1, z1):
    return m3d.Manifold.cube((x1 - x0, y1 - y0, z1 - z0)).translate((x0, y0, z0))


def layout(p):
    L = p["basket_len"] - 2 * p["fit_clear"]
    D = p["basket_depth"] - 2 * p["fit_clear"]
    w = p["wall"]
    y_back0 = D - w
    y_div1 = y_back0 - p["phone_slot"]
    y_div0 = y_div1 - w
    y_radio0 = y_div0 - p["radio_slot"]
    pocket = y_radio0 - 2 * w
    if pocket < 0:
        raise SystemExit(f"깊이 부족: 칸 폭 합계가 {D:.0f} 를 넘음")
    return dict(L=L, D=D, pocket=(w, w + pocket) if pocket >= 6 else None,
                radio=(y_radio0, y_div0), phone=(y_div1, y_back0),
                phone_slot=p["phone_slot"], pocket_w=pocket)


def insert_solid(p, g):
    L, D, w, f = g["L"], g["D"], p["wall"], p["floor"]
    s = box(0, 0, 0, L, D, f)
    s += box(0, 0, 0, L, w, p["h_front"])                          # 맨 앞벽
    s += box(0, g["radio"][0] - w, 0, L, g["radio"][0], p["h_radio_front"])  # 무전기 칸 앞벽
    s += box(0, g["radio"][1], 0, L, g["phone"][0], p["h_divider"])  # 칸막이
    s += box(0, g["phone"][1], 0, L, D, p["h_back"])                 # 뒷벽
    for x0 in (0, L - w):                                            # 양 끝벽
        s += box(x0, 0, 0, x0 + w, g["radio"][0], p["h_front"])
        s += box(x0, g["radio"][0] - w, 0, x0 + w, g["radio"][1] + w / 2, p["h_end_radio"])
        s += box(x0, g["phone"][0] - w / 2, 0, x0 + w, D, p["h_end_phone"])

    # 케이블 구멍 (각 칸 양쪽 끝)
    for y0, y1 in (g["radio"], g["phone"]):
        yc = (y0 + y1) / 2
        hw = min(p["cable_hole_w"], y1 - y0 - 4) / 2
        for xa in (w + p["cable_hole_gap"], L - w - p["cable_hole_gap"] - p["cable_hole_len"]):
            s -= box(xa, yc - hw, -1, xa + p["cable_hole_len"], yc + hw, f + 1)

    # 걸림 핀용 바닥 슬롯
    for fx0, fy0, fx1, fy1 in fin_rects(p, g, p["fin_slot_clear"]):
        s -= box(fx0, fy0, -1, fx1, fy1, f + 1)
    return s


def fin_rects(p, g, clear=0.0):
    """바닥 슬롯/핀 평면 사각형 목록 (x0, y0, x1, y1)."""
    if p["fin_y"] is None:
        return []
    L, D = g["L"], g["D"]
    t = p["fin_thick"] / 2 + clear
    half = p["fin_len"] / 2 + clear
    c = float(p["fin_y"])
    if p["fin_dir"] == "x":
        pos = p["fin_pos"] or [L * 0.3, L * 0.7]
        rects = [(u - half, c - t, u + half, c + t) for u in pos]
    else:
        pos = p["fin_pos"] or [D * 0.5]
        rects = [(c - t, u - half, c + t, u + half) for u in pos]
    return rects


def fin_solid(p):
    """별도 출력하는 걸림 핀: 바닥 두께만큼 슬롯에 들어가고 fin_depth 만큼 아래로 돌출.
    출력: 옆으로 눕혀서 (넓은 면이 베드)."""
    h = p["floor"] + p["fin_depth"]
    return box(0, 0, 0, p["fin_len"], h, p["fin_thick"])


def spacer_solid(slot_w, length, height):
    """칸 폭보다 1mm 좁은 블록, 위쪽에 손가락 홈."""
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
    tm.export(path)
    return tm


# ---------------------------------------------------------------------------
# 도면
# ---------------------------------------------------------------------------
def draw(p, g, spacers, out_png, out_pdf):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    from matplotlib.patches import Rectangle

    for fnt in ("NanumGothic", "Noto Sans CJK KR", "Noto Sans KR"):
        if any(fnt in x.name for x in font_manager.fontManager.ttflist):
            plt.rcParams["font.family"] = fnt
            plt.rcParams["axes.unicode_minus"] = False
            break
    L, D, w = g["L"], g["D"], p["wall"]
    fig = plt.figure(figsize=(16.5, 11.7))
    fig.suptitle(f"바스켓 내부 칸막이 {L:.0f} x {D:.0f} x {p['h_back']:.0f} mm "
                 f"(앞: 무전기 / 뒤: 폴드3)", fontsize=16, x=0.04, ha="left", y=0.985)

    # 평면도
    ax = fig.add_axes([0.04, 0.42, 0.60, 0.50])
    ax.add_patch(Rectangle((-p["fit_clear"], -p["fit_clear"]), p["basket_len"], p["basket_depth"],
                           fill=False, ls="--", ec="#999"))
    ax.add_patch(Rectangle((0, 0), L, D, fc="#dfe8f2", ec="#333"))
    for y0, y1 in ((0, w), (g["radio"][0] - w, g["radio"][0]),
                   (g["radio"][1], g["phone"][0]), (g["phone"][1], D)):
        ax.add_patch(Rectangle((0, y0), L, y1 - y0, fc="#6d8fb3", ec="none"))
    for x0 in (0, L - w):
        ax.add_patch(Rectangle((x0, 0), w, D, fc="#6d8fb3", ec="none"))
    if g["pocket"]:
        ax.text(L / 2, sum(g["pocket"]) / 2, f"수납칸 {g['pocket_w']:.1f} (펜·이어폰 등)",
                ha="center", va="center", fontsize=9)
    for (y0, y1), name, dev, dl, dt in ((g["radio"], "무전기", "라져+20", 150, 28),
                                       (g["phone"], "폰", "폴드3", 162, 20)):
        yc = (y0 + y1) / 2
        hw = min(p["cable_hole_w"], y1 - y0 - 4) / 2
        for xa in (w + p["cable_hole_gap"], L - w - p["cable_hole_gap"] - p["cable_hole_len"]):
            ax.add_patch(Rectangle((xa, yc - hw), p["cable_hole_len"], 2 * hw, fc="white", ec="#333"))
        ax.add_patch(Rectangle(((L - dl) / 2, yc - dt / 2), dl, dt, fill=False, ec="#c0392b",
                               ls=":", lw=1.2))
        ax.text(L / 2, yc, f"{name} 칸  안쪽 {y1 - y0:.1f}\n({dev} {dl}x{dt} 점선)",
                ha="center", va="center", fontsize=10)
    for fx0, fy0, fx1, fy1 in fin_rects(p, g):
        ax.add_patch(Rectangle((fx0, fy0), fx1 - fx0, fy1 - fy0, fc="#e67e22"))
    ax.annotate("", (0, -9), (L, -9), arrowprops=dict(arrowstyle="<->"))
    ax.text(L / 2, -12, f"{L:.0f} (바스켓 {p['basket_len']:.0f})", ha="center", va="top")
    ax.annotate("", (L + 8, 0), (L + 8, D), arrowprops=dict(arrowstyle="<->"))
    ax.text(L + 11, D / 2, f"{D:.0f}\n(바스켓 {p['basket_depth']:.0f})", va="center")
    ax.text(L / 2, D + 4, "창문 쪽", ha="center", fontsize=10, color="#555")
    ax.text(L / 2, -22, "운전석 쪽", ha="center", fontsize=10, color="#555")
    ax.set_xlim(-10, L + 40); ax.set_ylim(-28, D + 10)
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_title("평면도 (흰 사각형 = 케이블 구멍)", loc="left", fontsize=12)

    # 단면도 (Y-Z)
    ax2 = fig.add_axes([0.68, 0.42, 0.29, 0.50])
    f = p["floor"]
    ax2.add_patch(Rectangle((0, 0), D, f, fc="#6d8fb3"))
    for y0, y1, h in ((0, w, p["h_front"]), (g["radio"][0] - w, g["radio"][0], p["h_radio_front"]),
                      (g["radio"][1], g["phone"][0], p["h_divider"]),
                      (g["phone"][1], D, p["h_back"])):
        ax2.add_patch(Rectangle((y0, 0), y1 - y0, h, fc="#6d8fb3"))
        ax2.text((y0 + y1) / 2, h + 1.5, f"{h:.0f}", ha="center", fontsize=10)
    ax2.plot([-p["fit_clear"], -p["fit_clear"], p["basket_depth"] - p["fit_clear"],
              p["basket_depth"] - p["fit_clear"]], [35, -0.5, -0.5, 35],
             color="#8b5a2b", lw=2, ls="--")
    ax2.text(-2, 36, "바스켓\n(깊이 30~40)", fontsize=9, color="#8b5a2b")
    # 기기 단면
    ry = g["radio"][0] + 2
    ax2.add_patch(Rectangle((ry, f), 28, 64, fill=False, ec="#c0392b", ls=":", lw=1.2))
    ax2.text(ry + 14, f + 32, "무전기\n28x64", ha="center", va="center", fontsize=9, color="#c0392b")
    py = g["phone"][1] - 20 - 1
    ax2.add_patch(Rectangle((py, f), 20, 71, fill=False, ec="#c0392b", ls=":", lw=1.2))
    ax2.text(py + 10, f + 35, "폴드3\n20x71", ha="center", va="center", fontsize=9, color="#c0392b")
    ax2.set_xlim(-8, D + 6); ax2.set_ylim(-6, 82)
    ax2.set_aspect("equal"); ax2.set_xticks([]); ax2.set_yticks([])
    ax2.set_title("단면 (옆에서 본 모습)", loc="left", fontsize=12)

    # 표/메모
    ax3 = fig.add_axes([0.04, 0.03, 0.93, 0.34]); ax3.axis("off")
    rows = [f"본체  {L:.0f} x {D:.0f} x {p['h_back']:.0f}   벽 {w} / 바닥 {f}",
            f"무전기 칸 {p['radio_slot']:.1f}   폰 칸 {g['phone_slot']:.1f}   "
            f"앞 수납칸 {g['pocket_w']:.1f}  (안쪽 폭)",
            f"케이블 구멍 {p['cable_hole_len']:.0f} x {p['cable_hole_w']:.0f}  x 4개 (각 칸 양쪽 끝)"]
    for k, v in spacers.items():
        rows.append(f"스페이서 {k}: {v[0]:.0f} x {v[1]:.1f} x {v[2]:.0f}")
    rows.append("걸림 핀: " + ("없음 (철사 틈 위치 실측 후 --fin-y 로 활성화)"
                              if p["fin_y"] is None else
                              f"{p['fin_dir']} 방향, 중심 y={p['fin_y']}, 두께 {p['fin_thick']} (틈 {p['wire_gap']})"))
    ax3.text(0, 1, "\n".join(rows), fontsize=11, va="top", linespacing=1.6)
    notes = ("출력: 바닥이 베드에 닿는 그대로, 서포트 없음\n"
             "권장: PETG (차 안 여름 고온 - PLA 는 변형 위험)\n"
             "0.2mm 레이어 · 벽 3 · 인필 15~20%\n"
             "기기 크기는 공식 사양 + 케이스 여유 추정값\n"
             "  -> 케이스 끼운 실측값이 다르면 --radio-slot 등으로 재생성\n"
             "스페이서: 칸 안 빈 쪽 끝에 넣어 기기가 앞뒤로 밀리지 않게")
    ax3.text(0.52, 1, notes, fontsize=11, va="top", linespacing=1.6)
    fig.savefig(out_png, dpi=110)
    fig.savefig(out_pdf)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--radio-slot", type=float)
    ap.add_argument("--phone-slot", type=float)
    ap.add_argument("--h-front", type=float)
    ap.add_argument("--h-divider", type=float)
    ap.add_argument("--h-back", type=float)
    ap.add_argument("--fin-y", type=float, help="걸림 핀 중심 (본체 운전석 쪽 바깥면 기준 mm)")
    ap.add_argument("--fin-dir", choices=["x", "y"])
    ap.add_argument("--params", help="파라미터 JSON")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "out"))
    a = ap.parse_args()

    p = dict(DEFAULTS)
    if a.params:
        with open(a.params, encoding="utf-8") as fh:
            p.update(json.load(fh))
    for k, v in (("radio_slot", a.radio_slot), ("phone_slot", a.phone_slot), ("h_front", a.h_front), ("h_divider", a.h_divider),
                 ("h_back", a.h_back), ("fin_y", a.fin_y), ("fin_dir", a.fin_dir)):
        if v is not None:
            p[k] = v

    os.makedirs(a.out, exist_ok=True)
    g = layout(p)
    report = {}
    tm = save_stl(insert_solid(p, g), os.path.join(a.out, "insert.stl"))
    report["insert"] = dict(size=[round(float(e), 1) for e in tm.extents],
                            volume_cm3=round(tm.volume / 1000, 1))

    inner = g["L"] - 2 * p["wall"]
    spacers = {}
    for name, slot_w, dev_len, h in (("radio", p["radio_slot"], p["radio_len"], 30.0),
                                     ("phone", g["phone_slot"], p["phone_len"], 30.0)):
        length = inner - dev_len - p["plug_room"] - 2.0
        if length >= 8:
            s = spacer_solid(slot_w, length, h)
            t = save_stl(s, os.path.join(a.out, f"spacer_{name}.stl"))
            spacers[name] = (length, slot_w - 1, h)
            report[f"spacer_{name}"] = [round(float(e), 1) for e in t.extents]

    if p["fin_y"] is not None:
        t = save_stl(fin_solid(p), os.path.join(a.out, "fin.stl"))
        report["fin"] = dict(size=[round(float(e), 1) for e in t.extents],
                             count=len(fin_rects(p, g)))

    draw(p, g, spacers, os.path.join(a.out, "drawing.png"), os.path.join(a.out, "drawing.pdf"))
    with open(os.path.join(a.out, "params_used.json"), "w", encoding="utf-8") as fh:
        json.dump(p, fh, ensure_ascii=False, indent=2)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
