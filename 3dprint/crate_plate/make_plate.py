"""
상자 격자 덧판 (480 x 330 x 4 mm) 생성기

- P1S 베드(256 x 256)에 맞도록 2 x 2 = 4조각으로 분할
- 조각 사이는 퍼즐형 도브테일로 결합
- 밑면에 핀을 달아 상자 바닥의 45도 다이아몬드 격자 칸에 끼움
- 출력 방향: 윗면(평평한 면)이 베드에 닿고 핀이 위를 향함 -> 서포트 불필요

사용법:
    python3 make_plate.py                 # 기본값으로 STL/도면 생성
    python3 make_plate.py --pitch 21.5    # 격자 실측값 반영
    python3 make_plate.py --help

필요 패키지: pip install shapely manifold3d trimesh matplotlib numpy
"""

import argparse
import json
import math
import os

import numpy as np
import manifold3d as m3d
import trimesh
from shapely.affinity import rotate as srotate
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

# ---------------------------------------------------------------------------
# 파라미터 (단위 mm)
# ---------------------------------------------------------------------------
DEFAULTS = dict(
    # 완성판 외곽
    width=480.0,          # X (긴 변)
    depth=330.0,          # Y (짧은 변)
    thickness=4.0,
    corner_r=5.0,         # 평면 모서리 라운드

    # 분할 / 도브테일
    split_x=240.0,        # 세로 이음선 위치
    split_y=165.0,        # 가로 이음선 위치
    dt_neck=12.0,         # 도브테일 목 폭 (이음선 쪽)
    dt_head=18.0,         # 도브테일 머리 폭
    dt_len=10.0,          # 도브테일 돌출 길이
    dt_clear=0.15,        # 한쪽 면당 공차 (총 틈 = 2배)
    dt_v_pos=[55.0, 110.0, 220.0, 275.0],   # 세로 이음선 위 도브테일 Y 위치
    dt_h_pos=[80.0, 160.0, 320.0, 400.0],   # 가로 이음선 위 도브테일 X 위치

    # 상자 바닥 격자 (45도 회전된 정사각 칸) - 실측 필요!
    grid_pitch=20.0,      # 평행한 살(rib) 중심 간 수직 거리
    grid_rib=2.5,         # 살 두께
    grid_angle=45.0,      # 판 가장자리 대비 살 각도
    grid_origin=[240.0, 165.0],  # 살 교차점(노드) 하나의 판 좌표 (기본: 판 중앙)

    # 핀
    pin_d=7.0,            # 핀 지름 (칸 안쪽 폭보다 충분히 작게)
    pin_h=5.0,            # 핀 높이 (격자 살 깊이보다 짧게)
    pin_chamfer=1.0,      # 핀 끝 모따기
    pin_every=3,          # 몇 칸마다 핀 하나 (u, v 방향 공통)
    pin_margin=8.0,       # 조각 가장자리/이음선에서 핀까지 최소 거리

    # 테스트 쿠폰 (본 출력 전 공차/격자 확인용)
    coupon_w=110.0,
    coupon_d=70.0,

    bed=256.0,            # 프린터 베드 한 변
)


# ---------------------------------------------------------------------------
# 2D 형상
# ---------------------------------------------------------------------------
def rounded_rect(x0, y0, x1, y1, r):
    return box(x0 + r, y0 + r, x1 - r, y1 - r).buffer(r, resolution=16)


def dovetail(neck, head, length):
    """이음선(y=0)에서 +y 방향으로 튀어나오는 도브테일 (x 중심 0).
    이음선 아래로 1mm 겹치게 만들어 합칠 때 틈이 안 생기도록 함."""
    return Polygon([(-neck / 2, -1.0), (neck / 2, -1.0), (neck / 2, 0.0),
                    (head / 2, length), (-head / 2, length), (-neck / 2, 0.0)])


def split_regions(p):
    """이음선 기준 영역: left(x<split_x + 도브테일), bottom(y<split_y + 도브테일).
    영역은 판 밖으로 크게 확장해 둔다 -> 판과의 경계에는 이음선만 남음."""
    big = 1000.0
    dt = dovetail(p["dt_neck"], p["dt_head"], p["dt_len"])

    # 세로 이음선: 왼쪽 조각의 도브테일이 +x 방향으로 돌출
    left = box(-big, -big, p["split_x"], big)
    tabs = [srotate(dt, -90, origin=(0, 0)) for _ in p["dt_v_pos"]]
    tabs = [Polygon([(x + p["split_x"], y + yy) for x, y in t.exterior.coords])
            for t, yy in zip(tabs, p["dt_v_pos"])]
    left = unary_union([left] + tabs)

    # 가로 이음선: 아래 조각의 도브테일이 +y 방향으로 돌출
    bottom = box(-big, -big, big, p["split_y"])
    tabs = [Polygon([(x + xx, y + p["split_y"]) for x, y in dt.exterior.coords])
            for xx in p["dt_h_pos"]]
    bottom = unary_union([bottom] + tabs)
    return left, bottom


def make_pieces_2d(p):
    plate = rounded_rect(0, 0, p["width"], p["depth"], p["corner_r"])
    left, bottom = split_regions(p)
    # 이음선 = 영역 경계 중 판 내부에 있는 부분 -> 공차만큼 두껍게 해서 빼기
    seams = unary_union([left.boundary, bottom.boundary]).intersection(plate.buffer(1))
    cut = seams.buffer(p["dt_clear"], cap_style="flat", join_style="mitre")
    whole = plate.difference(cut)

    names = {
        "A_bottom_left": left.intersection(bottom),
        "B_bottom_right": bottom.difference(left),
        "C_top_left": left.difference(bottom),
        "D_top_right": plate.difference(left).difference(bottom),
    }
    pieces = {}
    for k, region in names.items():
        g = whole.intersection(region)
        if g.geom_type != "Polygon":  # 미세 파편 제거
            g = max(g.geoms, key=lambda s: s.area)
        pieces[k] = g
    return plate, pieces


def grid_to_xy(p, u, v):
    """격자 좌표(u, v: 살 방향 축)를 판 좌표로."""
    a = math.radians(p["grid_angle"])
    ox, oy = p["grid_origin"]
    return (ox + u * math.cos(a) - v * math.sin(a),
            oy + u * math.sin(a) + v * math.cos(a))


def pin_centers(p, region):
    """region(조각) 안에 들어가는 핀 중심 목록 (격자 칸 중심, pin_every 칸 간격)."""
    pitch, n = p["grid_pitch"], int(p["pin_every"])
    reach = int(math.hypot(p["width"], p["depth"]) / pitch) + 2
    safe = region.buffer(-(p["pin_margin"] + p["pin_d"] / 2))
    pts = []
    for i in range(-reach, reach + 1):
        for j in range(-reach, reach + 1):
            if i % n or j % n:
                continue
            x, y = grid_to_xy(p, (i + 0.5) * pitch, (j + 0.5) * pitch)
            if safe.contains(Point(x, y)):
                pts.append((x, y))
    return pts


def grid_lines(p, bounds):
    """도면용 격자 살 선분."""
    x0, y0, x1, y1 = bounds
    reach = int(math.hypot(x1 - x0, y1 - y0) / p["grid_pitch"]) + 4
    L = 2 * math.hypot(x1 - x0, y1 - y0)
    frame = box(x0, y0, x1, y1)
    lines = []
    for k in range(-reach, reach + 1):
        c = k * p["grid_pitch"]
        for seg in (LineString([grid_to_xy(p, c, -L), grid_to_xy(p, c, L)]),
                    LineString([grid_to_xy(p, -L, c), grid_to_xy(p, L, c)])):
            s = seg.intersection(frame)
            if not s.is_empty:
                lines.append(s)
    return lines


# ---------------------------------------------------------------------------
# 3D
# ---------------------------------------------------------------------------
def extrude(poly, h):
    rings = [np.asarray(poly.exterior.coords[:-1])]
    rings += [np.asarray(r.coords[:-1]) for r in poly.interiors]
    return m3d.CrossSection(rings, m3d.FillRule.EvenOdd).extrude(h)


def pin_solid(p):
    r, h, c = p["pin_d"] / 2, p["pin_h"], p["pin_chamfer"]
    body = m3d.Manifold.cylinder(h - c, r, r, 48)
    tip = m3d.Manifold.cylinder(c, r, r - c, 48).translate((0, 0, h - c))
    return body + tip


def piece_solid(p, poly, pins):
    """z=0 이 판 윗면(베드 접촉면), 핀은 +z 방향."""
    t = p["thickness"]
    solid = extrude(poly, t)
    pin = pin_solid(p)
    for x, y in pins:
        solid += pin.translate((x, y, t))
    return solid


def save_stl(solid, path, recenter=True):
    mesh = solid.to_mesh()
    tm = trimesh.Trimesh(vertices=np.asarray(mesh.vert_properties)[:, :3],
                         faces=np.asarray(mesh.tri_verts), process=True)
    if recenter:  # 베드 원점 기준으로 옮김
        tm.apply_translation(-tm.bounds[0])
    assert tm.is_watertight, f"{path}: watertight 아님"
    tm.export(path)
    return tm


# ---------------------------------------------------------------------------
# 테스트 쿠폰: 도브테일 1개 + 핀 몇 개로 공차와 격자 간격 검증
# ---------------------------------------------------------------------------
def make_coupon_2d(p):
    w, d = p["coupon_w"], p["coupon_d"]
    q = dict(p, width=w, depth=d, split_x=w / 2, split_y=-1000.0,
             dt_v_pos=[d / 2], dt_h_pos=[],
             grid_origin=[w / 2, d / 2])
    plate = rounded_rect(0, 0, w, d, 3)
    left, _ = split_regions(q)
    seam = left.boundary.intersection(plate.buffer(1))
    whole = plate.difference(seam.buffer(q["dt_clear"], cap_style="flat",
                                         join_style="mitre"))
    parts = {"coupon_L": whole.intersection(left), "coupon_R": whole.difference(left)}
    # 쿠폰은 모든 칸에 핀을 촘촘히 (간격 검증용)
    q["pin_every"], q["pin_margin"] = 1, 3.0
    return q, parts


# ---------------------------------------------------------------------------
# 도면
# ---------------------------------------------------------------------------
def draw(p, plate, pieces, pins, out_png, out_pdf):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import font_manager

    for f in ("NanumGothic", "Noto Sans CJK KR", "Noto Sans KR", "UnDotum"):
        if any(f in x.name for x in font_manager.fontManager.ttflist):
            plt.rcParams["font.family"] = f
            break
    has_kr = plt.rcParams["font.family"][0] not in ("sans-serif", "DejaVu Sans")
    T = (lambda ko, en: ko) if has_kr else (lambda ko, en: en)

    colors = {"A_bottom_left": "#8fb8de", "B_bottom_right": "#f2b880",
              "C_top_left": "#a8d5a2", "D_top_right": "#e8a0bf"}
    fig = plt.figure(figsize=(16.5, 11.7))  # A3 가로
    ax = fig.add_axes([0.04, 0.30, 0.66, 0.64])
    W, D = p["width"], p["depth"]

    for ln in grid_lines(p, (0, 0, W, D)):
        xs, ys = ln.xy
        ax.plot(xs, ys, color="#bbbbbb", lw=0.5, zorder=0)
    for k, g in pieces.items():
        xs, ys = g.exterior.xy
        ax.fill(xs, ys, color=colors[k], alpha=0.85, ec="#333", lw=0.8, zorder=1)
        cx, cy = g.representative_point().coords[0]
        b = g.bounds
        ax.text(cx, cy, f"{k.split('_')[0]}\n{b[2]-b[0]:.1f} x {b[3]-b[1]:.1f}",
                ha="center", va="center", fontsize=11, weight="bold", zorder=4)
        for x, y in pins[k]:
            ax.add_patch(plt.Circle((x, y), p["pin_d"] / 2, color="#222", zorder=3))

    def dim(x0, y0, x1, y1, text, off, vertical=False):
        if vertical:
            ax.annotate("", (x0 + off, y0), (x0 + off, y1),
                        arrowprops=dict(arrowstyle="<->", lw=0.9))
            ax.text(x0 + off - 4, (y0 + y1) / 2, text, rotation=90,
                    ha="right", va="center", fontsize=10)
        else:
            ax.annotate("", (x0, y0 + off), (x1, y0 + off),
                        arrowprops=dict(arrowstyle="<->", lw=0.9))
            ax.text((x0 + x1) / 2, y0 + off - 4, text, ha="center", va="top", fontsize=10)

    dim(0, 0, W, 0, f"{W:.0f}", -14)
    dim(0, 0, p["split_x"], 0, f"{p['split_x']:.0f}", -30)
    dim(0, 0, 0, D, f"{D:.0f}", -14, vertical=True)
    dim(0, 0, 0, p["split_y"], f"{p['split_y']:.0f}", -30, vertical=True)
    ax.set_xlim(-45, W + 10)
    ax.set_ylim(-45, D + 10)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(T("평면도 (밑면에서 본 모습 · 검은 점 = 핀 · 회색선 = 상자 격자살)",
                   "Plan view from underside (black = pins, grey = crate ribs)"),
                 fontsize=13, loc="left")

    # 도브테일 상세
    ax2 = fig.add_axes([0.73, 0.62, 0.24, 0.30])
    sx, sy = p["split_x"], p["dt_v_pos"][1]
    win = box(sx - 18, sy - 18, sx + 22, sy + 18)
    for k, g in pieces.items():
        c = g.intersection(win)
        for part in getattr(c, "geoms", [c]):
            if part.is_empty or part.geom_type != "Polygon":
                continue
            xs, ys = part.exterior.xy
            ax2.fill(xs, ys, color=colors[k], ec="#333", lw=0.8)
    ax2.set_aspect("equal")
    ax2.set_title(T("도브테일 상세", "Dovetail detail"), fontsize=12, loc="left")
    ax2.text(sx - 17, sy - 17,
             T(f"목 {p['dt_neck']} / 머리 {p['dt_head']} / 길이 {p['dt_len']}\n"
               f"공차 한쪽 {p['dt_clear']} (틈 {2*p['dt_clear']:.2f})",
               f"neck {p['dt_neck']} / head {p['dt_head']} / len {p['dt_len']}\n"
               f"clearance {p['dt_clear']}/side"), fontsize=9, va="bottom")
    ax2.set_xticks([]); ax2.set_yticks([])

    # 단면
    ax3 = fig.add_axes([0.73, 0.33, 0.24, 0.24])
    t, ph, pd, pitch, rib = p["thickness"], p["pin_h"], p["pin_d"], p["grid_pitch"], p["grid_rib"]
    ax3.fill([-30, 30, 30, -30], [0, 0, t, t], color="#8fb8de", ec="#333")
    c = p["pin_chamfer"]
    ax3.fill([-pd/2, pd/2, pd/2, pd/2 - c, -pd/2 + c, -pd/2],
             [t, t, t + ph - c, t + ph, t + ph, t + ph - c], color="#555")
    for sgn in (-1, 1):  # 칸 양옆 살 (45도 격자를 칸 중심 수직 단면으로)
        xr = sgn * pitch / 2
        ax3.fill([xr - rib/2, xr + rib/2, xr + rib/2, xr - rib/2],
                 [t + 0.2, t + 0.2, t + 12, t + 12], color="#bbb", ec="#777", hatch="//")
    ax3.set_aspect("equal")
    ax3.set_ylim(-3, t + 15)
    ax3.set_title(T("단면 (핀이 격자 칸에 들어간 모습, 위아래 반전)",
                    "Section (pin in crate cell, inverted)"), fontsize=11, loc="left")
    ax3.text(0, -2.5, T(f"판 {t}t · 핀 Ø{pd} x {ph} · 칸 간격 {pitch} · 살 {rib}",
                        f"plate {t} · pin Ø{pd}x{ph} · pitch {pitch} · rib {rib}"),
             ha="center", fontsize=9)
    ax3.set_xticks([]); ax3.set_yticks([])

    # 표
    ax4 = fig.add_axes([0.04, 0.03, 0.93, 0.23]); ax4.axis("off")
    lines = [T("조각", "Piece") + "   " + T("크기(mm)", "Size") + "   " + T("핀 수", "Pins")]
    for k, g in pieces.items():
        b = g.bounds
        ok = max(b[2]-b[0], b[3]-b[1]) <= p["bed"]
        lines.append(f"{k:<16} {b[2]-b[0]:6.1f} x {b[3]-b[1]:6.1f} x {p['thickness']}"
                     f"   {len(pins[k]):2d}   {'OK' if ok else 'BED OVER'}")
    mono = "NanumGothicCoding" if any("NanumGothicCoding" in x.name
                                      for x in font_manager.fontManager.ttflist) else "monospace"
    ax4.text(0, 1, "\n".join(lines), family=mono, fontsize=10, va="top")
    notes = T(
        "출력: 윗면(평평한 면)을 베드에 두고 핀이 위로 향하게 (서포트 없음)\n"
        "권장: PETG 또는 PLA · 0.2mm 레이어 · 벽 3 · 인필 15~20% 그리드\n"
        "조립: A-B, C-D를 먼저 끼운 뒤 두 줄을 가로 이음선으로 결합\n"
        "※ 격자 간격/살 두께는 사진 추정값 - 반드시 실측 후 --pitch --rib 로 재생성\n"
        "※ 본 출력 전 test_coupon 으로 도브테일 공차와 핀 위치 먼저 확인",
        "Print top-face down, pins up, no supports. PETG/PLA, 0.2mm, 3 walls, 15-20% infill.\n"
        "Assemble A-B and C-D first, then join rows.\n"
        "Grid pitch/rib are photo estimates: measure and regenerate. Print test coupon first.")
    ax4.text(0.45, 1, notes, fontsize=10, va="top")
    fig.suptitle(T(f"상자 격자 덧판 {W:.0f} x {D:.0f} x {p['thickness']} mm — 4분할 (P1S)",
                   f"Crate lattice plate {W:.0f} x {D:.0f} x {p['thickness']} mm — 4 pieces"),
                 fontsize=16, x=0.04, ha="left", y=0.985)
    fig.savefig(out_png, dpi=110)
    fig.savefig(out_pdf)
    plt.close(fig)


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pitch", type=float, help="격자 살 간격 (mm)")
    ap.add_argument("--rib", type=float, help="격자 살 두께 (mm)")
    ap.add_argument("--pin-d", type=float, help="핀 지름 (mm)")
    ap.add_argument("--pin-h", type=float, help="핀 높이 (mm)")
    ap.add_argument("--thickness", type=float, help="판 두께 (mm)")
    ap.add_argument("--clear", type=float, help="도브테일 한쪽 공차 (mm)")
    ap.add_argument("--params", help="파라미터 JSON 파일 (DEFAULTS 덮어쓰기)")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "out"))
    a = ap.parse_args()

    p = dict(DEFAULTS)
    if a.params:
        with open(a.params, encoding="utf-8") as f:
            p.update(json.load(f))
    for key, val in (("grid_pitch", a.pitch), ("grid_rib", a.rib), ("pin_d", a.pin_d),
                     ("pin_h", a.pin_h), ("thickness", a.thickness), ("dt_clear", a.clear)):
        if val is not None:
            p[key] = val

    inner = p["grid_pitch"] - p["grid_rib"]
    if p["pin_d"] > inner - 2:
        raise SystemExit(f"핀 지름 {p['pin_d']} 이 칸 안쪽 폭 {inner:.1f} 에 비해 너무 큼")

    os.makedirs(p_out := a.out, exist_ok=True)
    plate, pieces = make_pieces_2d(p)
    pins = {k: pin_centers(p, g) for k, g in pieces.items()}

    report = {}
    for k, g in pieces.items():
        tm = save_stl(piece_solid(p, g, pins[k]), os.path.join(p_out, f"plate_{k}.stl"))
        ext = tm.extents
        report[k] = dict(size_mm=[round(float(e), 1) for e in ext], pins=len(pins[k]),
                         volume_cm3=round(tm.volume / 1000, 1),
                         fits_bed=bool(max(ext[:2]) <= p["bed"]))

    # 조립 상태 미리보기 (한 파일, 출력용 아님)
    whole = None
    for k, g in pieces.items():
        s = piece_solid(p, g, pins[k])
        whole = s if whole is None else whole + s
    save_stl(whole, os.path.join(p_out, "preview_assembled.stl"), recenter=False)

    q, cparts = make_coupon_2d(p)
    for k, g in cparts.items():
        save_stl(piece_solid(q, g, pin_centers(q, g)), os.path.join(p_out, f"test_{k}.stl"))

    draw(p, plate, pieces, pins, os.path.join(p_out, "drawing.png"),
         os.path.join(p_out, "drawing.pdf"))
    with open(os.path.join(p_out, "params_used.json"), "w", encoding="utf-8") as f:
        json.dump(p, f, ensure_ascii=False, indent=2)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
