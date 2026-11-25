"""
Projekt Müts – 3D-prinditav korpus "kaasaskantava sõjaväeradari" stiilis.

Osad (kõik prinditakse ilma tugedeta, selles asendis nagu STL-is):
  korpus.stl  – kast Arduino UNO R4 WiFi + sensorkilbi jaoks (USB-C ja toitepesa ava, käepidemed)
  kaas.stl    – kaas, mille avasse läheb servo HS-322HD
  mast.stl    – telg, mis liimitakse/kruvitakse servo ümmarguse hoova peale
  antenn.stl  – kõver antenniketas koos HC-SR04 hoidikuga

Käivitamine:  pip install manifold3d trimesh numpy  &&  python radar_model.py
Kõik mõõdud on millimeetrites. Muuda allolevaid konstante, kui osad ei sobi.
"""
from pathlib import Path

import numpy as np
import trimesh
from manifold3d import CrossSection, Manifold

# === KALIBREERIMINE – muuda, kui prinditud osad ei sobi ===
TOL = 0.3            # lõtk sobituvate osade vahel (kaas ↔ kast, tapp ↔ pesa)
WALL = 2.4           # seina paksus
FLOOR = 2.4          # põhja paksus
IN_X, IN_Y, IN_H = 76, 60, 66   # kasti sisemõõdud

BOARD = (68.6, 53.3)                                        # UNO plaadi mõõdud
BOARD_HOLES = [(13.97, 2.54), (15.24, 50.8), (66.04, 7.62), (66.04, 35.56)]
STANDOFF_H = 5
USB_Y, USB_W, USB_H = 38.0, 14, 9      # USB-C ava keskkoht plaadi koordinaatides
JACK_Y, JACK_W, JACK_H = 7.6, 11, 12   # toitepesa ava

SERVO_BODY = (40.6, 19.8)   # HS-322HD korpus
SERVO_SHAFT = 10.1          # võlli kaugus korpuse keskelt (piki pikemat külge)
SERVO_HOLES = (48.0, 10.0)  # kinnitusaukude vahed (piki, risti)
LID_T = 3

HORN_D, HORN_T = 24.0, 2.5  # servo ümmarguse hoova läbimõõt ja paksus
MAST_H = 22
PEG_R, PEG_H, PEG_FLAT = 6.0, 8.0, 4.5

DISH_R, DISH_T = 110, 3     # antenni kõverusraadius ja paksus
DISH_W_TOP, DISH_W_BOT, DISH_H = 110, 70, 65
PCB = (45.0, 20.0, 1.6)     # HC-SR04 plaat
SENSOR_Z = 20               # anduri plaadi alumise serva kõrgus

SEG = 96


def box(x0, x1, y0, y1, z0, z1):
    return Manifold.cube((x1 - x0, y1 - y0, z1 - z0)).translate((x0, y0, z0))


def cyl(r, h, x=0, y=0, z=0, r2=None):
    return Manifold.cylinder(h, r, r if r2 is None else r2, SEG).translate((x, y, z))


def chamfer_rect(w, d, c):
    """Ristkülik, mille nurgad on lõigatud (sõjatehnika välimus)."""
    x, y = w / 2, d / 2
    return CrossSection([[(-x + c, -y), (x - c, -y), (x, -y + c), (x, y - c),
                          (x - c, y), (-x + c, y), (-x, y - c), (-x, -y + c)]])


OUT_X, OUT_Y = IN_X + 2 * WALL, IN_Y + 2 * WALL


def korpus():
    outer = Manifold.extrude(chamfer_rect(OUT_X, OUT_Y, 5), FLOOR + IN_H)
    inner = box(-IN_X / 2, IN_X / 2, -IN_Y / 2, IN_Y / 2, FLOOR, FLOOR + IN_H + 1)
    body = outer - inner

    # plaat on USB-poolse seina (–x) ääres
    bx0, by0 = -IN_X / 2 + 1.0, -BOARD[1] / 2
    for hx, hy in BOARD_HOLES:
        body += cyl(3, STANDOFF_H, bx0 + hx, by0 + hy, FLOOR) - cyl(1.25, STANDOFF_H + 1, bx0 + hx, by0 + hy, FLOOR)

    pcb_top = FLOOR + STANDOFF_H + 1.6
    wall = (-OUT_X / 2 - 1, -IN_X / 2 + 1)
    body -= box(*wall, by0 + USB_Y - USB_W / 2, by0 + USB_Y + USB_W / 2, pcb_top - 2, pcb_top - 2 + USB_H)
    body -= box(*wall, by0 + JACK_Y - JACK_W / 2, by0 + JACK_Y + JACK_W / 2, pcb_top - 1, pcb_top - 1 + JACK_H)

    # ventilatsioonipilud vastasseinas (+x)
    for i in range(-2, 3):
        body -= box(IN_X / 2 - 1, OUT_X / 2 + 1, i * 8 - 1.5, i * 8 + 1.5, 25, 49)

    # ribid ja käepidemed pikkadel külgedel
    for s in (1, -1):
        y_wall = s * OUT_Y / 2
        for z in (15, 50):
            body += box(-OUT_X / 2 + 6, OUT_X / 2 - 6, *sorted((y_wall - s, y_wall + s * 1.5)), z, z + 3)
        for x in (-18, 18):  # 45° kaldega jalg, et printida ilma toeta
            body += (box(x - 2.5, x + 2.5, *sorted((y_wall - s * 2, y_wall - s)), 46, 61)
                     + box(x - 2.5, x + 2.5, *sorted((y_wall, y_wall + s * 9)), 56, 61)).hull()
        body += box(-20.5, 20.5, *sorted((y_wall + s * 5.5, y_wall + s * 8.5)), 56.5, 61)
    return body


def kaas():
    lid = Manifold.extrude(chamfer_rect(OUT_X, OUT_Y, 5), LID_T)
    lx, ly = IN_X / 2 - TOL, IN_Y / 2 - TOL
    lid += box(-lx, lx, -ly, ly, -5, 0) - box(-lx + 2, lx - 2, -ly + 2, ly - 2, -6, 1)

    # servo: võll on kaane keskel, korpus nihkub +x suunas
    sx = SERVO_SHAFT
    for hx in (sx - SERVO_HOLES[0] / 2, sx + SERVO_HOLES[0] / 2):
        lid += cyl(3.5, 6, hx, 0, -6)
    bw, bd = SERVO_BODY[0] / 2 + 0.4, SERVO_BODY[1] / 2 + 0.4
    lid -= box(sx - bw, sx + bw, -bd, bd, -7, LID_T + 1)
    for hx in (sx - SERVO_HOLES[0] / 2, sx + SERVO_HOLES[0] / 2):
        for hy in (-SERVO_HOLES[1] / 2, SERVO_HOLES[1] / 2):
            lid -= cyl(1.25, 12, hx, hy, -7)

    lid -= box(-30, -20, -8, 8, -7, LID_T + 1)       # ava anduri juhtmetele
    for x in (-30, 30):                               # dekoratiivsed luugid
        lid -= box(x - 6, x + 6, -24, -14, LID_T - 0.6, LID_T + 1)
    return lid


def peg(r, flat, h, z=0):
    return cyl(r, h, z=z) ^ box(-r - 1, flat, -r - 1, r + 1, z - 1, z + h + 1)


def mast():
    m = cyl(17, 3) + cyl(15, MAST_H, r2=11) + peg(PEG_R, PEG_FLAT, PEG_H, MAST_H)
    m -= cyl(HORN_D / 2 + TOL, HORN_T)               # süvend servo hoovale
    m -= cyl(2.75, MAST_H + PEG_H + 2, z=-1)         # ava kruvikeeraja jaoks
    return m


def dish():
    def band(r_in, r_out):
        ring = CrossSection.circle(r_out, 512) - CrossSection.circle(r_in, 512)
        return Manifold.extrude(ring.translate((0, DISH_R)), DISH_H)

    # vaatesiluett eest: allservas kitsam, ülal laiem
    t, b = DISH_W_TOP / 2, DISH_W_BOT / 2
    outline = CrossSection([[(-b, 0), (b, 0), (t, DISH_H), (-t, DISH_H)]])
    prism = Manifold.extrude(outline, 60).rotate((90, 0, 0)).translate((0, 40, 0))

    d = band(DISH_R - DISH_T, DISH_R) ^ prism
    grooves = box(-60, 60, -20, 40, 21.5, 22.5) + box(-60, 60, -20, 40, 43, 44) \
        + box(-30.5, -29.5, -20, 40, 0, DISH_H) + box(29.5, 30.5, -20, 40, 0, DISH_H)
    d -= band(DISH_R - DISH_T - 1, DISH_R - DISH_T + 0.6) ^ grooves

    # HC-SR04 hoidik: kaks soonega rööbast, plaat lükatakse ülevalt sisse
    gw, lip = PCB[0] / 2 + TOL, 21.5
    y_back, y_slot = 6.0, 6.0 + 2.0
    y_front = y_slot + PCB[2] + 0.5
    top = SENSOR_Z + PCB[1]
    for s in (1, -1):
        rail = box(lip, gw + 2.5, 2, y_front + 2, 0, top)
        rail += box(15, gw + 2.5, 2, y_front + 2, 0, SENSOR_Z)
        rail -= box(lip - 1, gw, y_slot, y_front, SENSOR_Z, top + 1)
        if s < 0:
            rail = rail.mirror((1, 0, 0))
        d += rail

    # pesa masti tapile antenni taga
    d += cyl(10, 14, y=-7)
    d -= peg(PEG_R + TOL, PEG_FLAT + TOL, PEG_H + 0.5, -1).translate((0, -7, 0))
    return d


def to_trimesh(m):
    mesh = m.to_mesh()
    return trimesh.Trimesh(mesh.vert_properties[:, :3], mesh.tri_verts)


PARTS = {"korpus": korpus, "kaas": kaas, "mast": mast, "antenn": dish}
PRINT_FLIP = {"kaas"}   # kaas prinditakse tagurpidi (pealispind alusel)

if __name__ == "__main__":
    out = Path(__file__).parent
    for name, make in PARTS.items():
        m = make()
        if name in PRINT_FLIP:
            m = m.rotate((180, 0, 0))
        m = m.translate((0, 0, -m.bounding_box()[2]))
        assert m.status().name == "NoError" and m.volume() > 0, name
        tm = to_trimesh(m)
        assert tm.is_watertight, name
        tm.export(out / f"{name}.stl")
        print(f"{name}.stl  {np.round(tm.extents, 1)} mm  {m.volume() / 1000:.1f} cm³")
