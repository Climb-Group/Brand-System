"""Networking icons: saying hello, swapping details, meeting people, following up."""
import math


def build(k):
    """k is the illustrations module. Return {name: builder_fn}; what each drawing says is in illustrations/illustrations.copy.md."""
    line, curve, arc, circle, rrect, poly, text, turn, shift, sparkle = (k.line, k.curve, k.arc, k.circle, k.rrect,
                                                                         k.poly, k.text, k.turn, k.shift, k.sparkle)
    layer, solid_ = k.layer, k.solid

    # ------------------------------------------------------------ helpers

    def mirror(strokes, cx=100):
        out = []
        for s in strokes:
            s = dict(s)
            if "text" in s:
                s["x"] = 2 * cx - s["x"]
            else:
                s["pts"] = [(2 * cx - x, y) for x, y in s["pts"]]
            out.append(s)
        return out

    def capsule(p, q, r, **kw):
        """A pill from p to q with radius r."""
        a = math.atan2(q[1] - p[1], q[0] - p[0])
        pts = []
        for c, a0 in ((q, a - math.pi / 2), (p, a + math.pi / 2)):
            pts += [(c[0] + r * math.cos(a0 + math.pi * i / 10), c[1] + r * math.sin(a0 + math.pi * i / 10))
                    for i in range(11)]
        return poly(*pts, **kw)

    def corner_pts(x, y, wd, ht, r, tl=True, tr=True, br=True, bl=True):
        """Rounded rectangle points clockwise from the top right; corners can be square."""
        out = []
        for (cx, cy, a, on) in ((x + wd - r, y + r, -90, tr), (x + wd - r, y + ht - r, 0, br),
                                (x + r, y + ht - r, 90, bl), (x + r, y + r, 180, tl)):
            if on:
                out += [(cx + r * math.cos(math.radians(a + 90 * i / 6)), cy + r * math.sin(math.radians(a + 90 * i / 6)))
                        for i in range(7)]
            else:
                out.append((cx + r * math.cos(math.radians(a + 45)) * math.sqrt(2),
                            cy + r * math.sin(math.radians(a + 45)) * math.sqrt(2)))
        return out

    def bubble_pts(x, y, wd, ht, r, tail_x, tail_dx=-14, tail_len=24, tail_w=22):
        """Rounded speech bubble with a tail on the bottom edge (tail_x is where the tail leaves)."""
        pts = []
        for cx, cy, a in ((x + wd - r, y + r, -90), (x + wd - r, y + ht - r, 0)):
            pts += [(cx + r * math.cos(math.radians(a + 90 * i / 6)), cy + r * math.sin(math.radians(a + 90 * i / 6)))
                    for i in range(7)]
        pts += [(tail_x + tail_w, y + ht), (tail_x + tail_dx, y + ht + tail_len), (tail_x, y + ht)]
        for cx, cy, a in ((x + r, y + ht - r, 90), (x + r, y + r, 180)):
            pts += [(cx + r * math.cos(math.radians(a + 90 * i / 6)), cy + r * math.sin(math.radians(a + 90 * i / 6)))
                    for i in range(7)]
        return pts

    HAND = [(84, 192), (81, 162), (72, 146), (58, 128), (46, 112), (43, 100), (49, 93), (59, 96), (71, 110),
            (79, 117),
            (77, 96), (74, 64), (74, 52), (80, 45), (87, 48), (89, 58), (91, 88),
            (92, 46), (94, 35), (101, 30), (108, 35), (109, 46), (109, 88),
            (111, 54), (114, 44), (121, 42), (126, 48), (126, 60), (124, 94),
            (127, 76), (131, 68), (137, 68), (141, 74), (139, 102), (137, 126),
            (130, 150), (122, 166), (119, 192)]

    def hand(fill="ink", knock_lines=True):
        """An open right hand, palm to the viewer, fingers up, cuff at the wrist."""
        s = [curve(*HAND, closed=True, fill=fill, ink=fill != "ink")]
        if knock_lines:
            s += [curve((84, 150), (100, 140), (114, 126), knock=fill == "ink", w=0.7),
                  ]
        s += [rrect(76, 166, 52, 26, 6, fill=None if fill == "ink" else "ink", double=fill == "ink")]
        return s

    # ------------------------------------------------------------ drawings

    def _hello_tag():
        band = corner_pts(26, 50, 148, 44, 14, bl=False, br=False)
        s = [rrect(26, 50, 148, 104, 14, double=True),
             poly(*band, fill="ink", ink=False),
             line((26, 94), (174, 94), w=0.9),
             text(100, 82, 26, k.word("hello-tag", "label"), width=100),
             curve((50, 130), (60, 114), (70, 132), (82, 116), (92, 134), (104, 118), (116, 130), (130, 120),
                   (150, 126), w=0.9)]
        return turn(s, -8) + sparkle(172, 34, 7) + sparkle(30, 168, 5, w=0.8)

    def _business_card():
        # Back card, its hidden edges left out, then the front card.
        back = [line((60, 72), (60, 44), (166, 44), (166, 106), (148, 106), w=0.9),
                poly((60, 44), (166, 44), (166, 106), (148, 106), (148, 72), (60, 72), fill="tone", ink=False)]
        front = [rrect(28, 72, 120, 78, 9, fill="ink", double=True),
                 circle(58, 102, 13, fill="ground", ink=False),
                 line((84, 96), (132, 96), knock=True, w=0.9),
                 line((84, 112), (120, 112), knock=True, w=0.7),
                 line((44, 132), (132, 132), knock=True, w=0.7)]
        return turn(back + front, -10, (100, 100))

    def _wave_hand():
        s = turn(shift(hand(), 0, -6), -16, (100, 120))
        s += [arc(100, 100, 82, 82, 206, 236, w=0.9), arc(100, 100, 66, 66, 214, 234, w=0.8),
              arc(100, 100, 82, 82, -56, -26, w=0.9), arc(100, 100, 66, 66, -54, -34, w=0.8)]
        return s

    def _high_five():
        # Two hands meeting palm to palm. The right hand sits behind; the left hand is in front, its ground fill
        # hiding the right hand where they touch, so the palms read as pressed together, not laid over each other.
        left = turn(shift(hand(fill="tone", knock_lines=False), 0, 0, 0.8), -12, (100, 150))
        left = shift(mirror(left), -36, 12)
        right = shift(turn(shift(hand(), 0, 0, 0.8), -12, (100, 150)), 36, 12)
        cover = [dict(st, fill="ground", ink=False) for st in left if st["closed"]]
        burst = [line((100, 26), (100, 8)), line((78, 32), (68, 18), w=0.9), line((122, 32), (132, 18), w=0.9)]
        return right + layer(cover, 1) + layer(left, 2) + burst

    def _thumbs_up():
        # One closed hand-drawn outline: the thumb up, the top of the fist, four rounded finger tips down the front
        # (each a little shorter than the one above) and the heel of the hand back to the cuff. Short creases from
        # each gap between fingers, kept inside the outline.
        tips = [(146, 92), (144, 112), (141, 132), (137, 152)]
        front = []
        for cx, y0 in tips:
            front += [(cx - 4 + 10 * math.sin(math.pi * i / 10), y0 + 10 - 10 * math.cos(math.pi * i / 10))
                      for i in range(11)]
        outline = ([(80, 102), (86, 90), (92, 72), (96, 56), (101, 45), (109, 42), (116, 47), (118, 62),
                    (116, 80), (114, 92)] + front + [(118, 174), (98, 178), (84, 172), (80, 164)])
        s = [curve(*outline, closed=True, fill="tone", double=True),
             rrect(40, 94, 40, 86, 6, fill="ink"),
             line((52, 104), (52, 170), knock=True, w=0.7)]
        s += [curve((cx - 4.5, y0 + 20), (cx - 12, y0 + 20.5), (cx - 20, y0 + 22), w=0.8)
              for cx, y0 in tips[:3]]
        s = turn(s, -6, (100, 110))
        return s + sparkle(160, 46, 9) + sparkle(42, 54, 6, w=0.8)

    def _heart():
        pts = [(100, 172), (64, 140), (34, 104), (30, 70), (48, 44), (78, 40), (100, 64), (122, 40), (152, 44),
               (170, 70), (166, 104), (136, 140)]
        s = [curve(*pts, closed=True, fill="ink", double=True),
             curve((52, 72), (58, 58), (72, 54), knock=True, w=0.9)]
        s = turn(s, 6, (100, 104))
        return s + sparkle(176, 34, 8) + sparkle(24, 150, 6, w=0.8) + [circle(172, 150, 3.5, fill="ink", ink=False)]

    def _smiley():
        return [circle(100, 100, 70, fill="ink", double=True),
                rrect(73, 70, 12, 22, 6, fill="ground", ink=False),
                rrect(115, 70, 12, 22, 6, fill="ground", ink=False),
                curve((64, 112), (82, 138), (100, 142), (118, 138), (136, 112), knock=True, w=1.1),
                line((58, 108), (68, 116), knock=True, w=0.8), line((142, 108), (132, 116), knock=True, w=0.8)]

    def _selfie():
        s = [rrect(56, 22, 88, 156, 14, double=True),
             rrect(66, 42, 68, 104, 6, fill="ink", ink=False),
             circle(100, 30, 3, w=0.8),
             circle(100, 82, 16, fill="ground", ink=False),
             curve((72, 146), (74, 116), (100, 104), (126, 116), (128, 146), fill="ground", ink=False),
             line((88, 162), (112, 162), w=0.8)]
        s = turn(s, 12, (100, 100))
        return s + sparkle(36, 44, 9) + sparkle(168, 150, 7) + [circle(44, 82, 3, fill="ink", ink=False)]

    def _qr_scan():
        s = []
        for sx, sy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
            cx, cy = 100 - sx * 82, 100 - sy * 82
            s.append(line((cx, cy + sy * 30), (cx, cy), (cx + sx * 30, cy), w=1.1))
        for x, y in ((46, 46), (110, 46), (46, 110)):
            s += [rrect(x, y, 44, 44, 6), rrect(x + 12, y + 12, 20, 20, 3, fill="ink", ink=False)]
        for x, y in ((112, 112), (138, 112), (124, 126), (112, 140), (140, 140)):
            s.append(rrect(x, y, 14, 14, 2, fill="ink", ink=False))
        s.append(line((18, 100), (182, 100), w=0.7, dash=(6, 6)))
        return s

    def _contact_card():
        s = [rrect(48, 22, 114, 160, 12, double=True),
             circle(105, 70, 22, fill="ink"),
             curve((71, 132), (76, 104), (105, 96), (134, 104), (139, 132), fill="ink"),
             line((71, 132), (139, 132), w=0.9),
             line((72, 150), (138, 150), w=0.9), line((80, 164), (130, 164), w=0.7)]
        for y in (48, 92, 136):
            s.append(rrect(38, y - 5, 20, 10, 5, fill="ink"))
        return turn(s, -6, (100, 100))

    def _chain_link():
        # Two links that really interlock: each pill is split into a top and a bottom half so the links can pass
        # over and under each other. A runs over B at the top and B runs over A at the bottom, with a cut in the
        # ground colour wherever one link crosses in front of the other.
        def half(x, y, wd, ht, t, top=True, grow=0.0):
            mid, ro = y + ht / 2, ht / 2 + grow
            ri = ht / 2 - t - grow
            lx, rx = x + ht / 2, x + wd - ht / 2
            sign = -1 if top else 1
            k0 = -3 if not grow else 2  # the halves overlap along the arc at the seam; a cut stops short of it
            def side(r):
                pts = [(lx - r * math.cos(math.pi * i / 24), mid + sign * r * math.sin(math.pi * i / 24))
                       for i in range(k0, 13)]
                pts += [(rx + r * math.sin(math.pi * i / 24), mid + sign * r * math.cos(math.pi * i / 24))
                        for i in range(0, 13 - k0)]
                return pts
            return side(ro) + side(ri)[::-1]

        A, B, T = (20, 76, 102, 48), (78, 76, 102, 48), 14
        gap = dict(fill="ground", ink=False, amp=0)
        solid = dict(fill="ink", ink=False, amp=0)
        s = [poly(*half(*B, T, top=True), **solid),
             poly(*half(*A, T, top=True, grow=3.5), **gap), poly(*half(*A, T, top=True), **solid),
             poly(*half(*A, T, top=False), **solid),
             poly(*half(*B, T, top=False, grow=3.5), **gap), poly(*half(*B, T, top=False), **solid)]
        s = [poly(*half(*A, T, top=True), fill="tone", ink=False, amp=0.3),
             poly(*half(*A, T, top=False), fill="tone", ink=False, amp=0.3)] + s
        s = turn(s, -35, (100, 100))
        return s + [line((162, 30), (172, 18), w=0.9), line((174, 44), (188, 40), w=0.8),
                    line((36, 170), (26, 182), w=0.9), line((24, 154), (10, 158), w=0.8)]

    def _wifi():
        c = (100, 158)
        return [arc(c[0], c[1], 112, 112, 225, 315, w=1.1), arc(c[0], c[1], 80, 80, 228, 312, w=1.1),
                arc(c[0], c[1], 48, 48, 232, 308, w=1.1), circle(c[0], c[1], 13, fill="ink")]

    def _meeting_table():
        s = [rrect(46, 66, 108, 68, 12, fill="ink", double=True),
             rrect(64, 82, 24, 18, 3, fill="ground", ink=False), line((104, 116), (136, 116), knock=True, w=0.8)]
        for x in (58, 88, 118):
            s.append(rrect(x + 4, 40, 18, 16, 6))
            s.append(rrect(x + 4, 144, 18, 16, 6))
        s += [rrect(18, 90, 16, 20, 6), rrect(166, 90, 16, 20, 6)]
        return turn(s, -6)

    def _round_table():
        s = [circle(100, 100, 46, fill="ink", double=True),
             circle(100, 100, 12, knock=True, w=0.7)]
        for i in range(6):
            a = math.radians(-90 + i * 60)
            x, y = 100 + 70 * math.cos(a), 100 + 70 * math.sin(a)
            s.append(circle(x, y, 12))
        return s

    def _invite():
        card = [rrect(48, 30, 104, 110, 8, fill="ink"),
                line((70, 52), (130, 52), knock=True, w=0.8),
                line((100, 66), (105, 79), (119, 79), (108, 87), (112, 100), (100, 92), (88, 100), (92, 87),
                     (81, 79), (95, 79), (100, 66), knock=True, w=0.8)]
        env = [line((30, 98), (48, 86), w=0.9), line((170, 98), (152, 86), w=0.9),
               poly((30, 98), (170, 98), (170, 180), (30, 180), fill="ground"),
               line((30, 98), (100, 146), (170, 98), w=0.9),
               line((30, 180), (82, 136), w=0.7), line((170, 180), (118, 136), w=0.7)]
        return turn(card + env, -4) + sparkle(172, 40, 8) + sparkle(28, 54, 6, w=0.8)

    def _clock():
        c = (100, 106)
        s = [circle(c[0], c[1], 72, fill="ink", double=True)]
        for a in (0, 90, 180, 270):
            ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
            s.append(line((c[0] + 52 * ca, c[1] + 52 * sa), (c[0] + 60 * ca, c[1] + 60 * sa), knock=True, w=0.9))
        s += [line(c, (100, 62), knock=True, w=1.1), line(c, (130, 92), knock=True, w=1.1),
              circle(c[0], c[1], 6, fill="ground", ink=False),
              curve((58, 30), (44, 34), (36, 48), w=1.0), curve((142, 30), (156, 34), (164, 48), w=1.0),
              line((76, 170), (66, 186), w=0.9), line((124, 170), (134, 186), w=0.9)]
        return s

    def _notebook():
        s = [rrect(56, 22, 106, 160, 10, fill="ink", double=True),
             rrect(82, 48, 60, 24, 4, fill="ground", ink=False),
             line((90, 60), (134, 60), w=0.8),
             line((74, 22), (74, 182), knock=True, w=0.8),
             poly((124, 180), (138, 180), (138, 198), (131, 191), (124, 198), fill="ink")]
        return turn(s, 6, (100, 100))

    def _sticky_notes():
        back = [line((60, 140), (30, 140), (30, 30), (140, 30), (140, 60)),
                poly((30, 30), (140, 30), (140, 60), (60, 60), (60, 140), (30, 140), fill="tone", ink=False)]
        front = [poly((60, 60), (170, 60), (170, 140), (140, 170), (60, 170), fill="ink", double=True),
                 poly((170, 140), (144, 144), (140, 170), fill="ground", knock=False, w=0.9),
                 line((76, 88), (150, 88), knock=True, w=0.8), line((76, 108), (150, 108), knock=True, w=0.8),
                 line((76, 128), (124, 128), knock=True, w=0.8)]
        return turn(back + front, -6)

    def _pencil():
        s = [poly((52, 86), (140, 86), (140, 114), (52, 114), fill="ink"),
             line((56, 100), (136, 100), knock=True, w=0.7),
             poly((140, 86), (180, 100), (140, 114)),
             poly((168, 96), (180, 100), (168, 104), fill="ink"),
             rrect(36, 84, 18, 32, 2),
             line((42, 86), (42, 114), w=0.6), line((48, 86), (48, 114), w=0.6),
             rrect(16, 84, 22, 32, 8, double=True)]
        s = turn(s, -40, (100, 100))
        return s + [curve((36, 176), (60, 162), (74, 178), (96, 160), (112, 174), (140, 168), w=0.9)]

    def _video_call():
        s = [rrect(16, 30, 168, 118, 12, double=True),
             rrect(28, 42, 70, 94, 6, fill="ink", ink=False),
             circle(63, 76, 14, fill="ground", ink=False),
             curve((40, 136), (42, 108), (63, 98), (84, 108), (86, 136), fill="ground", ink=False),
             rrect(102, 42, 70, 94, 6, w=0.8),
             circle(137, 76, 14, w=0.9),
             curve((114, 136), (116, 108), (137, 98), (158, 108), (160, 136), w=0.9),
             line((100, 148), (100, 168)), line((70, 172), (130, 172))]
        s += [circle(158, 54, 3.5, fill="ground", ink=False)]
        return s

    def _map():
        outline = [(22, 46), (72, 30), (128, 46), (178, 30), (178, 152), (128, 168), (72, 152), (22, 168)]
        s = [poly(*outline),
             poly((72, 30), (128, 46), (128, 168), (72, 152), fill="tone", ink=False),
             line((72, 30), (72, 152), w=0.9), line((128, 46), (128, 168), w=0.9),
             curve((36, 146), (60, 126), (86, 140), (110, 112), (124, 94), dash=(6, 7), w=0.8),
             line((34, 70), (46, 82), w=0.8), line((46, 70), (34, 82), w=0.8)]
        pin = [curve((142, 104), (130, 86), (126, 72), (130, 60), (142, 54), (154, 60), (158, 72), (154, 86),
                     (142, 104), closed=True, fill="ink"),
               circle(142, 72, 6, fill="ground", ink=False)]
        return s + shift(pin, 0, -8)

    def _signpost():
        s = [line((100, 28), (100, 44)), line((100, 76), (100, 92)), line((100, 124), (100, 184)),
             circle(100, 24, 5, fill="ink"),
             poly((50, 44), (146, 44), (166, 60), (146, 76), (50, 76), fill="ink"),
             line((64, 60), (130, 60), knock=True, w=0.8),
             poly((150, 92), (54, 92), (34, 108), (54, 124), (150, 124), double=True),
             line((66, 108), (136, 108), w=0.8),
             curve((54, 186), (80, 180), (120, 180), (146, 186), w=0.9)]
        return turn(s, 3, (100, 184))

    def _open_door():
        s = [poly((64, 26), (140, 26), (140, 176), (64, 176), fill="ink", ink=False),
             line((56, 178), (56, 18), (148, 18), (148, 178)),
             poly((64, 26), (30, 14), (30, 188), (64, 176), double=True),
             circle(40, 104, 4.5, fill="ink"),
             poly((64, 176), (140, 176), (188, 194), (96, 194), fill="tone", ink=False),
             line((10, 178), (56, 178), w=0.9), line((148, 178), (190, 178), w=0.9)]
        s += sparkle(102, 92, 12, knock=True, w=0.9)
        return s + sparkle(176, 50, 8) + sparkle(166, 96, 5, w=0.8)

    def _chat_dots():
        s = [poly(*bubble_pts(22, 34, 156, 110, 26, 52), double=True)]
        for x in (64, 100, 136):
            s.append(circle(x, 89, 11, fill="ink", ink=False))
        return turn(s, -4) + sparkle(172, 172, 7)

    def _person_plus():
        s = [circle(82, 66, 30, double=True),
             curve((24, 182), (28, 128), (82, 110), (122, 120)),
             line((24, 182), (98, 182)),
             circle(146, 140, 32, fill="ink", double=True),
             line((146, 122), (146, 158), knock=True, w=1.1), line((128, 140), (164, 140), knock=True, w=1.1)]
        return s

    def _speech_quote():
        s = [poly(*bubble_pts(22, 28, 156, 120, 24, 120, tail_dx=34, tail_len=28), fill="ink", double=True)]
        for x in (76, 122):
            s += [circle(x, 98, 15, fill="ground", ink=False),
                  curve((x - 15, 98), (x - 14, 80), (x - 4, 66), (x + 10, 58), (x + 2, 72), (x - 1, 86),
                        closed=True, fill="ground", ink=False)]
        return turn(s, 4)

    return {
        "hello-tag": _hello_tag,
        "business-card": _business_card,
        "wave-hand": _wave_hand,
        "high-five": _high_five,
        "thumbs-up": _thumbs_up,
        "heart": _heart,
        "smiley": _smiley,
        "selfie": _selfie,
        "qr-scan": _qr_scan,
        "contact-card": _contact_card,
        "chain-link": _chain_link,
        "wifi": _wifi,
        "meeting-table": _meeting_table,
        "round-table": _round_table,
        "invite": _invite,
        "clock": _clock,
        "notebook": _notebook,
        "sticky-notes": _sticky_notes,
        "pencil": _pencil,
        "video-call": _video_call,
        "map": _map,
        "signpost": _signpost,
        "open-door": _open_door,
        "chat-dots": _chat_dots,
        "person-plus": _person_plus,
        "speech-quote": _speech_quote,
    }
