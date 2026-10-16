"""Business set: money, strategy, growth and deal icons for ClimbUK posts."""
import math


def _ell(cx, cy, rx, ry, a0, a1, n=None):
    """Points along an ellipse from angle a0 to a1 (degrees, screen coordinates, 90 is the bottom)."""
    n = n or max(12, int(abs(a1 - a0) / 6))
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def _knob(base, t, n, size=1.0):
    """Puzzle knob points: base point on the edge, t the travel direction, n the outward normal."""
    loc = [(0, -5), (4, -5)] + [(14 + 11 * math.cos(math.radians(a)), 11 * math.sin(math.radians(a)))
                                 for a in range(205, 516, 15)] + [(4, 5), (0, 5)]
    return [(base[0] + size * (lx * n[0] + ly * t[0]), base[1] + size * (lx * n[1] + ly * t[1])) for lx, ly in loc]


def _gear(cx, cy, r_in, r_out, teeth, rot=0):
    step = 360.0 / teeth
    pts = []
    for i in range(teeth):
        a = rot + i * step
        for f, r in ((0, r_in), (0.18, r_out), (0.48, r_out), (0.66, r_in)):
            pts.append((cx + r * math.cos(math.radians(a + f * step)), cy + r * math.sin(math.radians(a + f * step))))
    return pts


def build(k):
    line, curve, arc, circle, rrect, poly, text, turn, shift, sparkle = (k.line, k.curve, k.arc, k.circle, k.rrect,
                                                                         k.poly, k.text, k.turn, k.shift, k.sparkle)
    raw = k._s
    POUND = "\u00a3"

    def _briefcase():
        return [line((76, 62), (76, 48), (82, 40), (118, 40), (124, 48), (124, 62)),
                line((88, 62), (88, 52), (112, 52), (112, 62), w=0.8),
                rrect(24, 62, 152, 112, 12, double=True),
                curve((24, 102), (100, 116), (176, 102), w=0.9),
                rrect(84, 98, 32, 26, 6, fill="ink"),
                line((92, 112), (108, 112), knock=True, w=0.8),
                line((40, 150), (40, 160), w=0.7), line((160, 150), (160, 160), w=0.7)]

    def _coin_stack():
        def stack(cx, ytop, count, rx=34, ry=10, h=14, inked=True):
            s = []
            for i in range(count):
                y = ytop + i * h
                s.append(raw([(cx + rx, y), (cx + rx, y + h)] + _ell(cx, y + h, rx, ry, 0, 180)[1:] + [(cx - rx, y)],
                              fill="tone" if i % 2 else None))
            top = circle(cx, ytop, 1, fill="ink" if inked else None, double=not inked)
            top["pts"] = _ell(cx, ytop, rx, ry, 0, 360)[:-1]
            s.append(top)
            if inked:
                s.append(text(cx, ytop + 5, 15, POUND, slot="symbol", colour="ground"))
            return s
        s = stack(64, 94, 5, h=16, inked=False) + stack(138, 126, 3, h=16)
        s.append(line((14, 184), (186, 184), w=0.8))
        s += sparkle(140, 76, 8) + sparkle(166, 100, 5, w=0.8)
        return shift(s, 0, -14, 1.14, (100, 184))

    def _piggy_bank():
        return [curve((152, 110), (148, 72), (110, 58), (76, 62), (40, 80), (34, 116), (52, 146), (100, 156),
                      (140, 144), (152, 110), closed=True, fill="ink", double=True),
                poly((64, 70), (72, 44), (90, 62), fill="ink"),
                rrect(148, 94, 22, 30, 9, fill="ink"),
                circle(156, 104, 2.4, knock=True, w=0.6), circle(156, 114, 2.4, knock=True, w=0.6),
                circle(124, 92, 4, fill="ground", ink=False),
                line((86, 72), (114, 70), knock=True, w=1.0),
                rrect(58, 146, 18, 26, 5), rrect(114, 146, 18, 26, 5),
                curve((36, 108), (22, 102), (16, 112), (26, 120), (30, 110), (18, 96), w=0.8),
                circle(100, 34, 16, double=True), line((100, 26), (100, 42), w=0.8),
                line((100, 52), (100, 60), w=0.7, dash=(3, 4))]

    def _growth_bars():
        s = [rrect(28, 128, 30, 50, 5, double=True), rrect(70, 104, 30, 74, 5, double=True),
             rrect(112, 78, 30, 100, 5, double=True), rrect(154, 46, 30, 132, 5, fill="ink"),
             line((14, 184), (192, 184)),
             curve((22, 108), (56, 92), (90, 76), (124, 48), (146, 26)),
             line((126, 22), (148, 24), (146, 46))]
        return s

    def _pie_chart():
        cx, cy, r = 92, 108, 66
        rest = raw([(cx, cy)] + _ell(cx, cy, r, r, 0, 270), closed=True, double=True)
        sl = shift([raw([(cx, cy)] + _ell(cx, cy, r, r, 270, 360), closed=True, fill="ink")], 14, -14)
        return [rest] + sl + [line((cx, cy), (cx - r * 0.71, cy + r * 0.71), w=0.9)] + sparkle(176, 160, 7)

    def _target():
        cx, cy = 92, 110
        s = [circle(cx, cy, 72, double=True), circle(cx, cy, 50), circle(cx, cy, 28, fill="ink"),
             circle(cx, cy, 9, fill="ground", ink=False),
             line((cx + 4, cy - 4), (174, 28)),
             line((160, 26), (168, 34), (164, 14), w=0.9), line((172, 42), (164, 34), (186, 38), w=0.9),
             line((176, 20), (168, 28), w=0.8)]
        s += sparkle(32, 32, 7) + sparkle(178, 96, 5, w=0.8)
        return s

    def _compass():
        cx, cy = 100, 104
        case = [circle(cx, cy, 76, double=True), circle(cx, cy, 62, w=0.6),
                rrect(88, 14, 24, 16, 6, fill="ink")]
        s = [poly((cx, cy - 50), (cx + 14, cy), (cx - 14, cy), fill="ink"),
             poly((cx, cy + 50), (cx + 14, cy), (cx - 14, cy)),
             circle(cx, cy, 4.5, fill="ground", ink=False, knock=True, w=0.6)]
        for a in range(0, 360, 90):
            ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
            case.append(line((cx + 52 * ca, cy + 52 * sa), (cx + 62 * ca, cy + 62 * sa), w=0.9))
        return case + turn(s, 28, (cx, cy))

    def _ladder():
        s = [line((70, 10), (70, 192)), line((130, 10), (130, 192))]
        for i, y in enumerate(range(32, 192, 30)):
            if i == 0:
                s.append(rrect(70, y - 6, 60, 12, 4, fill="ink"))
            else:
                s.append(line((70, y), (130, y), w=0.9))
        s = shift(turn(s, 10, (100, 192)), -12, 0)
        s += sparkle(146, 34, 9) + sparkle(166, 60, 5, w=0.8) + [line((14, 192), (186, 192), w=0.8)]
        return s

    def _steps_up():
        s = [poly((18, 180), (18, 148), (58, 148), (58, 116), (98, 116), (98, 84), (138, 84), (138, 52), (182, 52),
                  (182, 180), double=True),
             poly((138, 52), (182, 52), (182, 180), (138, 180), fill="ink", ink=False),
             line((138, 180), (138, 84), w=0.8), line((98, 180), (98, 116), w=0.7), line((58, 180), (58, 148), w=0.7),
             curve((22, 128), (46, 96), (82, 86), (112, 58), (134, 24)),
             line((116, 22), (136, 22), (138, 42))]
        return s

    def _magnifier():
        s = [circle(84, 84, 52, double=True), circle(84, 84, 42, w=0.6),
             arc(84, 84, 32, 32, 200, 260, w=0.8),
             line((60, 104), (78, 88), (90, 96), (110, 70), w=0.9),
             line((98, 70), (110, 70), (110, 82), w=0.9)]
        handle = [rrect(122, 116, 26, 72, 12, fill="ink"), rrect(126, 106, 18, 16, 4)]
        return s + turn(handle, -45, (122, 122))

    def _puzzle():
        # Left piece: knob on its right edge.
        left = [(26, 58), (98, 58), (98, 94)] + _knob((98, 100), (0, 1), (1, 0)) + [(98, 142), (26, 142)]
        # Right piece: hole on its left edge (the same knob), knob on its top edge.
        right = ([(98, 58), (124, 58)] + _knob((134, 58), (1, 0), (0, -1)) + [(174, 58), (174, 142), (98, 142),
                                                                              (98, 106)]
                 + list(reversed(_knob((98, 100), (0, 1), (1, 0)))) + [(98, 58)])
        s = [raw(left, closed=True, double=True)]
        s += turn(shift([raw(right, closed=True, fill="ink")], 16, -12), 8, (130, 100))
        s += [line((40, 72), (40, 90), w=0.7)]
        s += sparkle(176, 168, 7) + sparkle(30, 168, 5, w=0.8)
        return s

    def _gears():
        return [raw(_gear(80, 112, 46, 60, 10), closed=True, fill="ink"),
                circle(80, 112, 18, fill="ground", knock=True, w=0.8),
                circle(80, 112, 32, knock=True, w=0.6, dash=(5, 6)),
                raw(_gear(146, 58, 28, 40, 8, rot=12), closed=True, double=True),
                circle(146, 58, 10)]

    def _key():
        s = [circle(52, 100, 34, fill="ink", double=True), circle(42, 100, 10, fill="ground", knock=True, w=0.7),
             line((86, 92), (180, 92), (188, 100), (180, 108), (86, 108)),
             line((134, 108), (134, 128), (148, 128), (148, 118), (160, 118), (160, 108)),
             line((96, 100), (170, 100), w=0.6)]
        return turn(shift(s, -6, 0, 1.08, (110, 100)), -36, (110, 100))

    def _padlock_open():
        return [line((60, 96), (60, 62)) if False else curve((68, 98), (66, 54), (80, 30), (104, 26), (128, 34),
                                                              (140, 58), (140, 72)),
                curve((84, 98), (82, 62), (92, 44), (106, 42), (120, 50), (124, 72), w=0.8),
                line((124, 72), (140, 72), w=0.8),
                rrect(44, 96, 112, 86, 14, fill="ink", double=True),
                circle(100, 128, 10, fill="ground", ink=False),
                poly((95, 132), (105, 132), (108, 156), (92, 156), fill="ground", ink=False),
                line((58, 108), (142, 108), knock=True, w=0.6)] + sparkle(170, 32, 7) + sparkle(162, 70, 4, w=0.8)

    def _contract():
        doc = [poly((44, 20), (130, 20), (156, 46), (156, 184), (44, 184), double=True),
               line((130, 20), (130, 46), (156, 46), w=0.8),
               line((60, 50), (112, 50)), line((60, 70), (140, 70), w=0.8), line((60, 88), (140, 88), w=0.8),
               line((60, 106), (126, 106), w=0.8),
               curve((60, 148), (70, 132), (76, 152), (88, 138), (94, 150), (104, 142), (116, 146)),
               line((58, 160), (118, 160), w=0.6)]
        seal = [circle(146, 158, 22, fill="ink"), circle(146, 158, 13, knock=True, w=0.7),
                line((136, 176), (128, 196), (138, 192), (142, 198), (144, 180), w=0.9),
                line((156, 176), (164, 196), (154, 192), (150, 198), (148, 180), w=0.9)]
        return turn(doc, -6, (100, 100)) + seal

    def _fountain_pen():
        pen = [rrect(84, 4, 32, 88, 12, double=True),
               line((110, 14), (110, 64), w=0.8),
               rrect(80, 88, 40, 14, 5, fill="ink"),
               poly((86, 102), (114, 102), (114, 124), (100, 158), (86, 124), fill="ink"),
               line((100, 128), (100, 152), knock=True, w=0.8),
               circle(100, 122, 3.6, fill="ground", ink=False)]
        out = turn(pen, 32, (100, 100))
        out.append(curve((56, 166), (40, 178), (22, 176), (34, 162), (48, 186), (66, 170), (84, 182), (110, 176),
                         (150, 182), (184, 176), w=0.9))
        return out

    def _money_bag():
        return [curve((80, 62), (52, 90), (36, 130), (46, 170), (100, 182), (154, 170), (164, 130), (148, 90),
                      (120, 62), fill="ink", double=True),
                line((80, 62), (120, 62), w=0.5, ink=False),
                curve((80, 62), (66, 44), (72, 26), (88, 36), (100, 22), (112, 36), (128, 26), (134, 44), (120, 62)),
                rrect(74, 56, 52, 12, 5, fill="ink"),
                line((80, 62), (120, 62), knock=True, w=0.7),
                text(100, 146, 56, POUND, slot="symbol", colour="ground")] + sparkle(176, 60, 8) + sparkle(28, 72, 5)

    def _calculator():
        s = [rrect(46, 18, 108, 166, 14, double=True),
             rrect(60, 32, 80, 34, 6, fill="ink"),
             line((100, 54), (128, 54), knock=True, w=1.0), line((80, 54), (92, 54), knock=True, w=1.0)]
        for r, y in enumerate((80, 106, 132, 158)):
            for c, x in enumerate((60, 88, 116)):
                if c == 2 and r >= 2:
                    continue
                s.append(rrect(x, y, 22, 18, 5, w=0.8))
        s.append(rrect(116, 132, 22, 44, 6, fill="ink"))
        s.append(line((121, 150), (133, 150), knock=True, w=0.8))
        s.append(line((121, 158), (133, 158), knock=True, w=0.8))
        return s

    def _scales():
        def pan(cx, fill):
            return [line((cx, 52), (cx - 26, 116), w=0.8), line((cx, 52), (cx + 26, 116), w=0.8),
                    raw(_ell(cx, 116, 32, 22, 0, 180), closed=True, fill=fill, double=fill is None),
                    line((cx - 32, 116), (cx + 32, 116))]
        return ([line((100, 40), (100, 168)), line((36, 52), (164, 52)),
                 circle(100, 32, 9, fill="ink"),
                 poly((84, 168), (116, 168), (128, 182), (72, 182), fill="ink"),
                 line((60, 184), (140, 184), w=0.8)]
                + pan(42, "ink") + pan(158, None))

    def _seedling():
        return [curve((100, 150), (98, 120), (102, 92), (100, 70)),
                curve((100, 92), (78, 96), (52, 84), (36, 58), (64, 54), (88, 66), (100, 92), double=True),
                curve((50, 70), (78, 80), (98, 90), w=0.7),
                curve((100, 70), (110, 44), (136, 26), (168, 26), (158, 56), (130, 70), (100, 70), fill="ink"),
                curve((106, 66), (130, 50), (156, 34), knock=True, w=0.7),
                curve((30, 172), (62, 148), (138, 148), (170, 172), fill="ink"),
                line((30, 172), (170, 172), w=0.9),
                line((12, 184), (188, 184), w=0.8),
                line((70, 160), (78, 160), knock=True, w=0.8), line((116, 164), (124, 164), knock=True, w=0.8)]

    def _tree():
        s = [curve((56, 120), (30, 104), (34, 70), (58, 60), (66, 30), (100, 20), (130, 30), (144, 58), (170, 70),
                   (170, 106), (144, 122), (100, 126), (56, 120), double=True),
             poly((90, 182), (94, 120), (106, 120), (110, 182), fill="ink"),
             line((100, 140), (100, 124), knock=True, w=0.6),
             line((96, 132), (76, 110), w=0.8), line((104, 128), (124, 106), w=0.8),
             line((24, 184), (176, 184), w=0.9)]
        for x, y in ((70, 82), (100, 56), (132, 80), (112, 98), (82, 104)):
            s.append(circle(x, y, 8, fill="ink"))
        return s

    def _chess_knight():
        return [curve((80, 150), (84, 128), (76, 114), (56, 112), (40, 104), (40, 88), (56, 72), (72, 56),
                      (82, 30), (96, 46), (118, 50), (138, 70), (142, 104), (134, 132), (126, 150),
                      closed=True, fill="ink", double=True),
                circle(78, 76, 4.5, fill="ground", ink=False),
                circle(50, 96, 2.4, fill="ground", ink=False),
                curve((100, 54), (122, 66), (130, 92), (124, 124), knock=True, w=0.8),
                curve((60, 112), (70, 104), (80, 102), knock=True, w=0.7),
                rrect(70, 150, 60, 14, 5),
                rrect(56, 164, 88, 20, 6, fill="ink")]

    def _telescope():
        tube = [rrect(48, 86, 92, 32, 8, double=True),
                rrect(140, 80, 30, 44, 8, fill="ink"),
                rrect(26, 92, 22, 20, 5),
                line((68, 88), (68, 116), w=0.7), line((120, 88), (120, 116), w=0.7)]
        s = turn(tube, -26, (100, 110))
        s += [circle(100, 116, 5, fill="ink"),
              line((100, 120), (66, 186)), line((100, 120), (134, 186)), line((100, 120), (100, 186), w=0.8)]
        s += sparkle(170, 32, 9) + sparkle(130, 26, 4, w=0.8) + sparkle(186, 70, 5, w=0.8)
        return s

    def _hourglass():
        return [rrect(46, 16, 108, 18, 6, fill="ink"), rrect(46, 166, 108, 18, 6, fill="ink"),
                curve((60, 34), (62, 70), (92, 92), (92, 108), (62, 130), (60, 166)),
                curve((140, 34), (138, 70), (108, 92), (108, 108), (138, 130), (140, 166)),
                poly((76, 66), (124, 66), (104, 90), (96, 90), fill="ink", ink=False),
                line((100, 92), (100, 146), w=0.6, dash=(3, 5)),
                curve((64, 164), (82, 142), (100, 138), (118, 142), (136, 164), fill="ink"),
                line((58, 34), (58, 166), w=0.5, ink=False)]

    def _pound_note():
        back = [rrect(28, 52, 140, 80, 8, double=True), circle(140, 92, 14, w=0.7)]
        front = [rrect(32, 72, 140, 80, 8, fill="ink"),
                 rrect(42, 82, 120, 60, 5, knock=True, w=0.6),
                 circle(102, 112, 21, fill="ground", ink=False),
                 text(102, 125, 34, POUND, slot="symbol", colour="ink"),
                 circle(58, 98, 4, knock=True, w=0.7), circle(146, 126, 4, knock=True, w=0.7)]
        return turn(back, -12, (100, 92)) + turn(shift(front, 0, 18), 8, (100, 112)) + sparkle(30, 34, 7)

    def _rocket_launch_pad():
        rocket = [curve((100, 14), (116, 34), (122, 64), (122, 126)),
                  curve((100, 14), (84, 34), (78, 64), (78, 126)),
                  poly((88, 36), (100, 14), (112, 36), (118, 46), (82, 46), fill="ink", ink=False),
                  line((82, 46), (118, 46), w=0.9),
                  circle(100, 74, 11, double=True), circle(100, 74, 5, fill="ink", ink=False),
                  line((78, 98), (62, 126), (78, 126)), line((122, 98), (138, 126), (122, 126)),
                  line((78, 126), (122, 126)),
                  curve((90, 130), (92, 142), (100, 156), (108, 142), (110, 130), fill="ink")]
        pad = [rrect(44, 156, 112, 12, 5, fill="ink"),
               line((60, 168), (52, 186), w=0.9), line((140, 168), (148, 186), w=0.9),
               line((20, 186), (180, 186), w=0.8)]
        smoke = [curve((46, 172), (22, 176), (10, 160), (22, 146), (34, 150), (42, 136), (58, 144), (56, 158),
                       closed=True, double=True),
                 curve((154, 172), (178, 176), (190, 160), (178, 146), (166, 150), (158, 136), (142, 144),
                       (144, 158), closed=True, double=True)]
        return rocket + pad + smoke + sparkle(40, 40, 8) + sparkle(160, 52, 6) + sparkle(56, 84, 4, w=0.8)

    return {
        "briefcase": _briefcase,
        "coin-stack": _coin_stack,
        "piggy-bank": _piggy_bank,
        "growth-bars": _growth_bars,
        "pie-chart": _pie_chart,
        "target": _target,
        "compass": _compass,
        "ladder": _ladder,
        "steps-up": _steps_up,
        "magnifier": _magnifier,
        "puzzle": _puzzle,
        "gears": _gears,
        "key": _key,
        "padlock-open": _padlock_open,
        "contract": _contract,
        "fountain-pen": _fountain_pen,
        "money-bag": _money_bag,
        "calculator": _calculator,
        "scales": _scales,
        "seedling": _seedling,
        "tree": _tree,
        "chess-knight": _chess_knight,
        "telescope": _telescope,
        "hourglass": _hourglass,
        "pound-note": _pound_note,
        "rocket-launch-pad": _rocket_launch_pad,
    }
