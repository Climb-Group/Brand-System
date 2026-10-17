"""Stage, AV and party icons for the ClimbUK illustration library."""
import math


def build(k):
    """k is the illustrations module. Return {name: builder_fn}; what each drawing says is in illustrations/illustrations.copy.md."""
    line, curve, arc, circle, rrect, poly, text, turn, shift, sparkle = (k.line, k.curve, k.arc, k.circle, k.rrect,
                                                                         k.poly, k.text, k.turn, k.shift, k.sparkle)

    def arc_pts(cx, cy, rx, ry, a0, a1, n=24):
        return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
                 cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]

    def star(cx, cy, r, ri=None, **kw):
        ri = ri or r * 0.45
        pts = []
        for i in range(10):
            a = math.radians(-90 + i * 36)
            rr = r if i % 2 == 0 else ri
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
        return poly(*pts, **kw)

    def note(x, y, stem=50, **kw):
        """A single note head at x,y with a stem going up from its right side."""
        head = turn([arc(x, y, 13, 9, 0, 360, **kw)], -22, (x, y))
        return head + [line((x + 12, y - 4), (x + 12, y - stem))]

    # ------------------------------------------------------------ drawings

    def _headset_mic():
        s = [arc(100, 104, 62, 66, 180, 360),
             arc(100, 104, 50, 54, 196, 344, w=0.7),
             rrect(26, 92, 26, 48, 10, fill="ink"),
             line((34, 104), (34, 128), knock=True, w=0.7),
             rrect(148, 92, 26, 48, 10, double=True),
             curve((40, 140), (46, 162), (66, 172), (92, 170)),
             rrect(88, 160, 28, 18, 9, fill="ink")]
        s += sparkle(160, 36, 7) + sparkle(176, 58, 4, w=0.8)
        return turn(s, -6, (100, 110))

    def _lectern():
        s = [poly((44, 62), (156, 62), (166, 84), (34, 84), fill="ink"),
             line((52, 74), (148, 74), knock=True, w=0.7),
             poly((58, 84), (142, 84), (134, 170), (66, 170), double=True),
             star(100, 124, 17, fill="ink", ink=False),
             rrect(52, 170, 96, 14, 4),
             curve((124, 62), (128, 44), (118, 30), (104, 26), w=0.9),
             rrect(90, 16, 18, 16, 7, fill="ink")]
        s += [line((70, 20), (80, 30), w=0.8), line((62, 40), (76, 44), w=0.7)]
        return s

    def _lighting_rig():
        s = [line((12, 30), (188, 30)), line((12, 46), (188, 46)),
             line((12, 46), (34, 30), (56, 46), (78, 30), (100, 46), (122, 30), (144, 46), (166, 30), (188, 46),
                  w=0.7)]
        for x, deg, f in ((46, 22, None), (100, 0, "ink"), (154, -22, None)):
            lamp = [line((x, 46), (x, 58), w=0.9),
                    arc(x, 70, 12, 12, 180, 360, w=0.9),
                    rrect(x - 16, 64, 32, 36, 8, fill=f, double=f is None),
                    arc(x, 104, 14, 4, 0, 360, fill="ink" if f is None else "ground", ink=f is None, w=0.8)]
            s += turn(lamp, deg, (x, 52))
        s += [poly((88, 108), (112, 108), (150, 188), (50, 188), fill="tone", ink=False),
              line((22, 104), (6, 150), dash=(6, 6), w=0.7), line((178, 104), (194, 150), dash=(6, 6), w=0.7),
              line((88, 110), (60, 180), dash=(6, 6), w=0.7), line((112, 110), (140, 180), dash=(6, 6), w=0.7)]
        return s

    def _loudspeaker():
        s = [rrect(36, 22, 92, 160, 12, double=True),
             circle(82, 124, 34, fill="ink"),
             circle(82, 124, 20, knock=True, w=0.8),
             circle(82, 124, 6, fill="ground", ink=False),
             circle(82, 62, 16),
             circle(82, 62, 6, fill="ink", ink=False),
             line((50, 168), (60, 168), w=0.7), line((104, 168), (114, 168), w=0.7),
             arc(142, 110, 14, 22, -50, 50), arc(148, 110, 26, 40, -48, 48, w=0.9),
             arc(154, 110, 38, 58, -46, 46, w=0.8)]
        return s

    def _video_camera():
        s = [circle(60, 52, 22, double=True), circle(60, 52, 6, w=0.8),
             circle(110, 52, 22, double=True), circle(110, 52, 6, w=0.8),
             rrect(24, 76, 112, 70, 10, fill="ink"),
             line((38, 92), (70, 92), knock=True, w=0.8),
             circle(116, 94, 6, fill="ground", ink=False),
             poly((136, 96), (176, 74), (176, 148), (136, 126), double=True),
             line((60, 146), (52, 186), w=0.9), line((100, 146), (108, 186), w=0.9),
             line((80, 146), (80, 186), w=0.8)]
        return turn(s, -6, (100, 110))

    def _clapperboard():
        board = [rrect(34, 86, 132, 92, 8, fill="ink", double=True),
                 line((50, 114), (150, 114), knock=True, w=0.8),
                 line((50, 136), (126, 136), knock=True, w=0.8),
                 line((100, 114), (100, 162), knock=True, w=0.7),
                 line((50, 158), (86, 158), knock=True, w=0.7)]
        lower = [rrect(34, 66, 132, 20, 4)]
        for x in (46, 82, 118):
            lower.append(poly((x, 66), (x + 16, 66), (x + 8, 86), (x - 8, 86), fill="ink", ink=False))
        upper = [rrect(34, 44, 132, 20, 4)]
        for x in (46, 82, 118, 154):
            upper.append(poly((x, 44), (x + 16, 44), (x + 8, 64), (x - 8, 64), fill="ink", ink=False))
        upper = [dict(s) for s in upper]
        hinge = [circle(40, 66, 5, fill="ground", w=0.8)]
        s = board + lower + turn(upper, -18, (36, 64)) + hinge
        s += [line((150, 20), (158, 8), w=0.8), line((166, 30), (180, 22), w=0.8)]
        return shift(s, 0, 6)

    def _projector_screen():
        s = [rrect(20, 24, 160, 12, 6, fill="ink"),
             rrect(30, 36, 140, 96, 3, double=True),
             line((48, 112), (76, 88), (98, 100), (124, 70), (150, 60), w=0.9),
             line((136, 58), (152, 58), (150, 74), w=0.9),
             line((48, 54), (92, 54), w=0.7),
             line((100, 132), (100, 152)),
             line((100, 132), (100, 194), w=0.8),
             line((66, 194), (100, 152), (134, 194)),
             rrect(96, 132, 8, 12, 3, fill="ink")]
        return s

    def _slide_deck():
        back = [rrect(36, 46, 128, 88, 8, double=True)]
        front = [rrect(36, 58, 128, 88, 8, fill="ink"),
                 line((52, 78), (110, 78), knock=True),
                 line((52, 96), (90, 96), knock=True, w=0.7),
                 line((52, 108), (82, 108), knock=True, w=0.7),
                 line((52, 120), (88, 120), knock=True, w=0.7),
                 rrect(104, 112, 10, 20, 2, fill="ground", ink=False),
                 rrect(120, 100, 10, 32, 2, fill="ground", ink=False),
                 rrect(136, 88, 10, 44, 2, fill="ground", ink=False)]
        clicker = [rrect(140, 150, 24, 44, 8), circle(152, 164, 4, fill="ink", ink=False)]
        s = turn(back, -9, (100, 100)) + turn(front, 4, (100, 100))
        s += turn(clicker, 20, (152, 170))
        s += [line((168, 140), (180, 130), w=0.8), line((174, 154), (190, 150), w=0.7)]
        return shift(s, -4, -6)

    def _confetti_cannon():
        apex, m1, m2 = (34, 176), (88, 90), (130, 132)

        def at(t, m):
            return (apex[0] + (m[0] - apex[0]) * t, apex[1] + (m[1] - apex[1]) * t)
        cone = [poly(apex, m1, m2, double=True)]
        for t0, t1 in ((0.0, 0.34), (0.6, 0.84)):
            cone.append(poly(at(t0, m1), at(t1, m1), at(t1, m2), at(t0, m2), fill="ink", ink=False))
        cone.append(turn([arc(109, 111, 30, 11, 0, 360, fill="ink")], 45, (109, 111))[0])
        bits = [rrect(140, 64, 14, 8, 2, fill="ink", ink=False),
                rrect(104, 44, 14, 8, 2, fill="ink", ink=False),
                rrect(162, 110, 14, 8, 2, fill="ink", ink=False),
                circle(146, 92, 5, fill="ink", ink=False),
                circle(128, 40, 4.5, fill="ink", ink=False),
                circle(178, 76, 4.5, fill="ink", ink=False),
                curve((150, 24), (158, 32), (152, 42), (160, 50), w=0.9),
                curve((156, 150), (166, 144), (170, 156), (180, 152), w=0.9),
                curve((72, 54), (80, 48), (82, 60), (90, 56), w=0.9)]
        bits = [turn([b], a, (b["pts"][0][0], b["pts"][0][1]))[0] for b, a in zip(bits, (30, -20, 50, 0, 0, 0, 0, 0, 0))]
        return shift(cone, -6, 0, 1.15, (90, 140)) + bits + sparkle(184, 30, 8) + sparkle(46, 40, 6, w=0.8)

    def _wristband():
        top_back = arc_pts(100, 86, 74, 30, 180, 360)
        bot_back = arc_pts(100, 112, 74, 30, 180, 360)
        top_front = arc_pts(100, 86, 74, 30, 0, 180)
        bot_front = arc_pts(100, 112, 74, 30, 0, 180)
        s = [poly(*(top_back + bot_back[::-1]), fill="tone", ink=False),
             line(*top_back),
             line(*bot_back, w=0.6),
             poly(*(top_front + bot_front[::-1]), fill="ink"),
             line((26, 86), (26, 112)), line((174, 86), (174, 112)),
             text(100, 132, 15, k.word("wristband", "label"), slot="label", width=40),
             rrect(140, 132, 16, 34, 4, fill="ground", w=0.9),
             line((148, 140), (148, 158), w=0.7)]
        s += sparkle(36, 40, 7) + sparkle(170, 34, 5, w=0.8)
        return turn(s, -8, (100, 100))

    def _bunting():
        s = []

        def row(y0, sag, x0, x1, n, size, start):
            def yat(x):
                t = (x - (x0 + x1) / 2) / ((x1 - x0) / 2)
                return y0 + sag * (1 - t * t)
            out = [curve(*[(x0 + (x1 - x0) * i / 8, yat(x0 + (x1 - x0) * i / 8)) for i in range(9)], w=0.9)]
            step = (x1 - x0) / (n + 1)
            for i in range(n):
                cx = x0 + step * (i + 1)
                a, b = (cx - size / 2, yat(cx - size / 2)), (cx + size / 2, yat(cx + size / 2))
                tip = (cx, (a[1] + b[1]) / 2 + size * 1.15)
                filled = (i + start) % 2 == 0
                out.append(poly(a, b, tip, fill="ink" if filled else None, double=not filled))
            return out
        s += row(26, 44, 8, 192, 5, 28, 0)
        s += row(98, 34, 30, 170, 4, 24, 1)
        return s

    def _big_screen():
        s = [rrect(16, 22, 168, 108, 8, double=True),
             rrect(26, 32, 148, 88, 4, fill="ink", ink=False),
             circle(100, 66, 15, fill="ground", ink=False),
             curve((68, 120), (72, 96), (100, 86), (128, 96), (132, 120), fill="ground", ink=False),
             line((60, 130), (52, 150), w=0.9), line((140, 130), (148, 150), w=0.9)]
        for x, y, r in ((30, 172, 12), (66, 166, 13), (104, 170, 12), (140, 165, 13), (174, 172, 11)):
            s.append(arc(x, y, r, r, 180, 360, w=0.9))
            s.append(line((x - r, y), (x - r - 4, 196), w=0.8))
            s.append(line((x + r, y), (x + r + 4, 196), w=0.8))
        s += sparkle(44, 48, 5, knock=True, w=0.8)
        return s

    def _stopwatch():
        cx, cy, r = 100, 112, 64
        wedge = [(cx, cy)] + arc_pts(cx, cy, r - 12, r - 12, -90, 20)
        s = [circle(cx, cy, r, double=True),
             poly(*wedge, fill="ink", ink=False),
             rrect(88, 28, 24, 14, 5, fill="ink"),
             line((100, 42), (100, 48)),
             turn([rrect(146, 44, 16, 12, 4)], 40, (154, 50))[0]]
        for a in range(0, 360, 30):
            ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
            r0 = r - 8 if a % 90 else r - 14
            s.append(line((cx + r0 * ca, cy + r0 * sa), (cx + (r - 4) * ca, cy + (r - 4) * sa), w=0.7))
        s += [line((cx, cy), (cx + 40 * math.cos(math.radians(20)), cy + 40 * math.sin(math.radians(20))),
                   knock=True),
              circle(cx, cy, 5, fill="ground")]
        s += [line((22, 70), (8, 70), w=0.8), line((20, 90), (2, 90), w=0.7), line((24, 50), (12, 50), w=0.7)]
        return s

    def _hand_pts():
        return [(88, 184), (86, 154), (74, 138), (60, 122), (50, 106), (54, 96), (64, 98), (78, 114),
                (76, 64), (77, 54), (84, 50), (90, 54), (91, 64), (92, 100),
                (93, 54), (94, 42), (100, 38), (106, 42), (107, 54), (108, 100),
                (109, 60), (110, 50), (116, 46), (122, 50), (123, 60), (124, 102),
                (125, 78), (126, 70), (131, 66), (136, 70), (137, 78), (138, 124), (130, 154), (122, 184)]

    def _hand(fill=None, knock_lines=True):
        pts = _hand_pts()
        s = [curve(*pts, fill=fill, double=fill is None)]
        if fill and knock_lines:
            s += [line((92, 112), (91.5, 66), knock=True, w=0.8), line((108, 112), (108.5, 62), knock=True, w=0.8),
                  line((124, 112), (124.5, 82), knock=True, w=0.8)]
        return s

    def _applause():
        left = turn(shift(_hand("ink"), 0, 0), -28, (100, 186))
        right = [dict(st, pts=[(200 - x, y) for x, y in st["pts"]]) for st in _hand(None)]
        right = turn(right, 28, (100, 186))
        s = shift(left, -16, 2) + shift(right, 16, 2)
        s += [line((88, 24), (84, 6), w=0.9), line((112, 24), (116, 6), w=0.9),
              line((62, 34), (48, 20), w=0.8), line((138, 34), (152, 20), w=0.8)]
        s += sparkle(28, 70, 6) + sparkle(174, 70, 6, w=0.8)
        return s

    def _hand_raised():
        s = _hand("ink")
        s += [poly((78, 172), (132, 172), (138, 196), (72, 196), double=True)]
        s += [arc(100, 84, 62, 62, 200, 236, w=0.8), arc(100, 84, 74, 74, 204, 232, w=0.7),
              arc(100, 84, 62, 62, -56, -20, w=0.8), arc(100, 84, 74, 74, -52, -24, w=0.7)]
        s += sparkle(162, 128, 7)
        return turn(s, 8, (100, 180))

    def _qmark(x, y, sc=1.0, **kw):
        q = [curve((x - 12, y - 14), (x - 6, y - 26), (x + 6, y - 26), (x + 13, y - 16), (x + 6, y - 4), (x, y + 2),
                   (x, y + 10), **kw),
             circle(x, y + 22, 3.5, fill="ink" if not kw.get("knock") else "ground", ink=False)]
        return shift(q, 0, 0, sc, (x, y))

    def _qa_card():
        bubble = [curve((60, 26), (150, 22), (176, 40), (178, 80), (156, 100), (148, 120), (136, 100), (64, 104),
                        (40, 86), (36, 50), (60, 26), double=True)]
        bubble += _qmark(108, 60, 1.0)
        card = [rrect(22, 92, 118, 82, 10, fill="ink"),
                text(81, 135, 30, k.word("qa-card", "label"), slot="label", width=86),
                line((40, 154), (122, 154), knock=True, w=0.7)]
        return bubble + turn(card, -8, (80, 134))

    def _dj_decks():
        s = [rrect(10, 64, 180, 104, 12, double=True),
             circle(54, 116, 34, fill="ink"),
             circle(54, 116, 22, knock=True, w=0.7),
             circle(54, 116, 5, fill="ground", ink=False),
             circle(146, 116, 34),
             circle(146, 116, 22, w=0.6),
             circle(146, 116, 5, fill="ink", ink=False),
             line((84, 74), (80, 102), (66, 110), w=0.9),
             line((176, 74), (174, 104), (160, 112), w=0.9),
             rrect(92, 78, 16, 76, 4),
             line((100, 92), (100, 120), w=0.6),
             rrect(94, 98, 12, 7, 2, fill="ink", ink=False),
             circle(100, 138, 4, fill="ink", ink=False)]
        s += [arc(100, 50, 12, 12, 200, 340, w=0.8), arc(100, 50, 24, 24, 210, 330, w=0.7)]
        return s

    def _headphones():
        s = [arc(100, 108, 64, 70, 180, 360, w=1.1),
             arc(100, 108, 52, 58, 190, 350, w=0.7),
             rrect(20, 96, 34, 62, 14, fill="ink"),
             line((30, 112), (30, 142), knock=True, w=0.7),
             rrect(146, 96, 34, 62, 14, double=True),
             line((170, 112), (170, 142), w=0.7)]
        s += note(150, 40, 0)[:0]
        return turn(s, -8, (100, 110)) + [line((154, 22), (154, 50)), arc(154, 50, 7, 5, 0, 360, fill="ink"),
                                           line((154, 22), (166, 30), w=0.9)]

    def _mixing_desk():
        s = [poly((34, 46), (166, 46), (188, 150), (12, 150), double=True),
             rrect(8, 150, 184, 22, 6, fill="ink"),
             line((24, 161), (176, 161), knock=True, w=0.6, dash=(4, 6))]
        cols = [(52, 118), (76, 96), (100, 126), (124, 88), (148, 108)]
        for i, (x, ky) in enumerate(cols):
            bx = x + (x - 100) * 0.12
            s.append(circle(x, 62, 6, w=0.8, fill="ink" if i == 2 else None))
            s.append(line((x + (x - 100) * 0.03, 80), (bx, 140), w=0.6))
            s.append(rrect(bx - 8 + (ky - 80) * (x - 100) * 0.002, ky - 5, 16, 10, 3, fill="ink", ink=False))
        return shift(s, 0, -4)

    def _disco_ball():
        cx, cy, r = 100, 114, 62
        s = [line((100, 6), (100, cy - r)),
             circle(cx, cy, r, fill="ink", double=True)]
        for dy in (-32, 0, 32):
            rr = math.sqrt(r * r - dy * dy)
            s.append(arc(cx, cy + dy, rr, 7, 0, 180, knock=True, w=0.7))
        for rx in (36,):
            s.append(arc(cx, cy, rx, r, -90, 90, knock=True, w=0.7))
            s.append(arc(cx, cy, rx, r, 90, 270, knock=True, w=0.7))
        s.append(line((cx, cy - r), (cx, cy + r), knock=True, w=0.7))
        s.append(rrect(74, 78, 14, 12, 3, fill="ground", ink=False))
        s += sparkle(30, 46, 9) + sparkle(172, 48, 7) + sparkle(178, 168, 6, w=0.8) + sparkle(22, 168, 5, w=0.8)
        return s

    def _fireworks():
        s = []

        def burst(cx, cy, r0, r1, n, dots, rot=0, w=1.0):
            out = []
            for i in range(n):
                a = math.radians(rot + 360 * i / n)
                ca, sa = math.cos(a), math.sin(a)
                out.append(line((cx + r0 * ca, cy + r0 * sa), (cx + r1 * ca, cy + r1 * sa), w=w))
                if dots:
                    out.append(circle(cx + (r1 + 8) * ca, cy + (r1 + 8) * sa, 3.2, fill="ink", ink=False))
            return out
        s.append(circle(78, 72, 12, fill="ink"))
        s += burst(78, 72, 20, 48, 12, True)
        s += [circle(148, 112, 22, fill="tone", ink=False)]
        s += burst(148, 112, 10, 30, 10, False, 18, 0.8)
        s += [curve((96, 196), (90, 160), (80, 120), (78, 92), dash=(6, 7), w=0.7),
              curve((150, 196), (152, 170), (148, 142), dash=(6, 7), w=0.7)]
        s += sparkle(164, 40, 8) + sparkle(30, 150, 5, w=0.8)
        return s

    def _music_notes():
        s = [turn([arc(62, 150, 18, 12, 0, 360, fill="ink")], -22, (62, 150))[0],
             turn([arc(138, 128, 18, 12, 0, 360, fill="ink")], -22, (138, 128))[0],
             line((78, 144), (78, 54)),
             line((154, 122), (154, 34)),
             poly((78, 54), (154, 34), (154, 52), (78, 72), fill="ink"),
             line((78, 88), (154, 68), w=0.8)]
        small = [arc(34, 76, 11, 8, 0, 360, double=True), line((44, 73), (44, 28)),
                 curve((44, 28), (58, 38), (60, 52), (54, 62), w=0.9)]
        s += turn(small[:1], -22, (34, 76)) + small[1:]
        s += sparkle(176, 168, 7) + sparkle(110, 176, 4, w=0.8)
        return s

    def _ticket_qr():
        t = [k.ticket_outline(20, 56, 160, 92, 11, fill="ink", double=True),
             line((60, 62), (60, 142), knock=True, dash=(5, 6), w=0.8),
             line((34, 80), (34, 124), knock=True, w=0.8),
             line((46, 80), (46, 124), knock=True, w=0.6),
             rrect(78, 70, 64, 64, 6, fill="ground", ink=False)]
        for fx, fy in ((84, 76), (118, 76), (84, 110)):
            t.append(rrect(fx, fy, 18, 18, 3, w=0.7))
            t.append(rrect(fx + 5, fy + 5, 8, 8, 1.5, fill="ink", ink=False))
        for px, py in ((108, 78), (108, 92), (122, 102), (110, 112), (126, 116), (110, 124), (122, 126)):
            t.append(rrect(px, py, 7, 7, 1, fill="ink", ink=False))
        t += [line((154, 86), (166, 86), knock=True, w=0.8), line((154, 102), (166, 102), knock=True, w=0.8),
              line((154, 118), (162, 118), knock=True, w=0.8)]
        t = turn(t, -10, (100, 102))
        return t + sparkle(36, 30, 7) + sparkle(172, 172, 6, w=0.8)

    def _stage_pass():
        cord = [curve((60, 4), (74, 34), (100, 50)), curve((140, 4), (126, 34), (100, 50)),
                circle(100, 56, 7, w=0.9)]
        card = [rrect(50, 64, 100, 130, 12, double=True),
                rrect(86, 74, 28, 8, 4, w=0.8),
                poly((50, 136), (150, 98), (150, 136), (50, 174), fill="ink", ink=False),
                text(100, 142, 16, k.word("stage-pass", "label"), slot="label", width=78, rotate=-21),
                star(100, 104, 12, fill="ink", ink=False),
                line((66, 182), (110, 182), w=0.7)]
        return cord + turn(card, 6, (100, 60))

    def _backstage_door():
        s = [line((8, 184), (192, 184), w=0.8),
             rrect(52, 22, 92, 162, 4, w=1.0),
             poly((124, 30), (144, 22), (144, 184), (124, 180), fill="tone", ink=False),
             poly((52, 22), (124, 30), (124, 180), (52, 184), fill="ink"),
             star(88, 76, 18, knock=True, w=0.8),
             circle(112, 112, 5, fill="ground", ink=False),
             line((148, 60), (176, 52), dash=(6, 6), w=0.7),
             line((148, 110), (184, 112), dash=(6, 6), w=0.7),
             line((148, 160), (178, 176), dash=(6, 6), w=0.7)]
        s += sparkle(176, 22, 7)
        return s

    def _spotlight_beam():
        s = [rrect(78, 8, 44, 26, 8, fill="ink"),
             line((86, 34), (114, 34), w=0.9),
             poly((84, 36), (116, 36), (164, 166), (36, 166), fill="tone", ink=False),
             line((84, 36), (38, 162), dash=(8, 6), w=0.8), line((116, 36), (162, 162), dash=(8, 6), w=0.8),
             arc(100, 168, 66, 16, 0, 360, fill="ink"),
             circle(100, 104, 12),
             curve((78, 166), (80, 134), (100, 122), (120, 134), (122, 166), double=True)]
        s += sparkle(28, 60, 7) + sparkle(172, 64, 6, w=0.8)
        return s

    return {
        "headset-mic": _headset_mic,
        "lectern": _lectern,
        "lighting-rig": _lighting_rig,
        "loudspeaker": _loudspeaker,
        "video-camera": _video_camera,
        "clapperboard": _clapperboard,
        "projector-screen": _projector_screen,
        "slide-deck": _slide_deck,
        "confetti-cannon": _confetti_cannon,
        "wristband": _wristband,
        "bunting": _bunting,
        "big-screen": _big_screen,
        "stopwatch": _stopwatch,
        "applause": _applause,
        "hand-raised": _hand_raised,
        "qa-card": _qa_card,
        "dj-decks": _dj_decks,
        "headphones": _headphones,
        "mixing-desk": _mixing_desk,
        "disco-ball": _disco_ball,
        "fireworks": _fireworks,
        "music-notes": _music_notes,
        "ticket-qr": _ticket_qr,
        "stage-pass": _stage_pass,
        "backstage-door": _backstage_door,
        "spotlight-beam": _spotlight_beam,
    }
