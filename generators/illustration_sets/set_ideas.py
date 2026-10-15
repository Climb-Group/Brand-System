"""Ideas, recognition, social, travel and places: learning, awards, social media actions, getting there and the
kinds of buildings our businesses work in. Drawn in the house style of illustrations.py."""
import math


def build(k):
    """k is the illustrations module. Return {name: builder_fn}; what each drawing says is in illustrations/illustrations.copy.md."""
    line, curve, arc, circle, rrect, poly, text, turn, shift, sparkle = (k.line, k.curve, k.arc, k.circle, k.rrect,
                                                                         k.poly, k.text, k.turn, k.shift, k.sparkle)

    def spline(*pts, n=10):
        return k._catmull(list(pts), n=n)

    def path(*segs, **kw):
        """A closed shape joined from point lists (straight runs and spline runs)."""
        pts = []
        for seg in segs:
            pts += seg
        return k._s(pts, closed=True, **kw)

    def star_pts(cx, cy, r0, r1, n=5, rot=-90):
        return [(cx + (r0 if i % 2 == 0 else r1) * math.cos(math.radians(rot + 180 * i / n)),
                 cy + (r0 if i % 2 == 0 else r1) * math.sin(math.radians(rot + 180 * i / n))) for i in range(2 * n)]

    def heart(cx, cy, s, **kw):
        pts = []
        for i in range(48):
            t = math.tau * i / 48
            x = 16 * math.sin(t) ** 3
            y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
            pts.append((cx + x * s, cy - y * s))
        return k._s(pts, closed=True, **kw)

    def scallop_ring(cx, cy, r, bumps, depth, **kw):
        n = bumps * 10
        pts = [(cx + (r + depth * abs(math.sin(math.pi * bumps * i / n))) * math.cos(math.tau * i / n),
                cy + (r + depth * abs(math.sin(math.pi * bumps * i / n))) * math.sin(math.tau * i / n))
               for i in range(n)]
        return k._s(pts, closed=True, **kw)

    # ------------------------------------------------------------ learning and ideas

    def _grad_cap():
        base = [line((54, 98), (54, 132)), line((146, 98), (146, 132)),
                curve((54, 132), (78, 146), (100, 150), (122, 146), (146, 132), fill="tone", ink=False),
                curve((54, 132), (78, 146), (100, 150), (122, 146), (146, 132))]
        top = [poly((100, 48), (184, 82), (100, 116), (16, 82), fill="ink", double=True),
               line((100, 82), (164, 90), knock=True, w=0.8),
               circle(100, 82, 5, fill="ground", ink=False)]
        tassel = [line((164, 90), (164, 140), w=0.9), rrect(158, 136, 12, 26, 5, fill="ink")]
        return turn(base + top + tassel, -8, (100, 100))

    def _book_open():
        cover = [line((14, 66), (14, 166), (100, 180), (186, 166), (186, 66), w=0.9)]
        left = path(spline((100, 62), (66, 46), (26, 52)), [(26, 52), (26, 154)],
                    spline((26, 154), (66, 150), (100, 168)), double=True)
        right = path(spline((100, 62), (134, 46), (174, 52)), [(174, 52), (174, 154)],
                     spline((174, 154), (134, 150), (100, 168)), fill="ink")
        lines = [curve((40, 76), (64, 72), (88, 82), w=0.7), curve((40, 98), (64, 94), (88, 104), w=0.7),
                 curve((40, 120), (64, 116), (88, 126), w=0.7),
                 curve((112, 82), (136, 72), (160, 76), knock=True, w=0.7),
                 curve((112, 104), (136, 94), (160, 98), knock=True, w=0.7),
                 curve((112, 126), (136, 116), (160, 120), knock=True, w=0.7)]
        return cover + [left, right] + lines

    def _brain():
        left = curve((98, 44), (80, 32), (58, 38), (44, 54), (34, 76), (36, 100), (30, 120), (40, 142), (60, 156),
                     (80, 162), (98, 154), closed=True, fill="ink", double=True)
        right = curve((102, 44), (120, 32), (142, 38), (156, 54), (166, 76), (164, 100), (170, 120), (160, 142),
                      (140, 156), (120, 162), (102, 154), closed=True, double=True)
        folds = [curve((86, 52), (70, 60), (72, 80), (56, 86), knock=True, w=0.8),
                 curve((90, 96), (68, 98), (60, 116), knock=True, w=0.8),
                 curve((88, 134), (72, 128), (58, 138), knock=True, w=0.8),
                 curve((114, 52), (130, 60), (128, 80), (144, 86), w=0.8),
                 curve((110, 96), (132, 98), (140, 116), w=0.8),
                 curve((112, 134), (128, 128), (142, 138), w=0.8)]
        stem = [curve((100, 158), (104, 174), (112, 186), w=0.9)]
        return [left, right] + folds + stem

    def _lightning():
        bolt = [poly((114, 12), (52, 108), (94, 108), (78, 188), (150, 84), (108, 84), (140, 12), fill="ink",
                     double=True),
                line((112, 30), (90, 66), knock=True, w=0.7)]
        marks = [line((40, 52), (52, 62), w=0.8), line((30, 82), (44, 84), w=0.8),
                 line((160, 128), (172, 138), w=0.8), line((164, 106), (178, 104), w=0.8)]
        return turn(bolt, 6) + marks + sparkle(160, 40, 8) + sparkle(42, 150, 6, w=0.8)

    def _star():
        s = [k._s(star_pts(100, 106, 80, 36), closed=True, fill="ink", double=True),
             ]
        return turn(s, -8, (100, 106)) + sparkle(168, 32, 8) + sparkle(30, 34, 6, w=0.8) + sparkle(172, 170, 5, w=0.8)

    # ------------------------------------------------------------ recognition

    def _medal():
        straps = [poly((58, 14), (86, 14), (112, 96), (86, 100), double=True),
                  poly((142, 14), (114, 14), (88, 96), (114, 100), double=True)]
        disc = [circle(100, 134, 46, fill="ink"),
                circle(100, 134, 33, knock=True, w=0.7),
                k._s(star_pts(100, 136, 18, 8), closed=True, knock=True, w=0.8)]
        return straps + [rrect(86, 84, 28, 12, 4)] + disc + sparkle(160, 120, 6) + sparkle(38, 150, 5, w=0.8)

    def _rosette():
        tails = [poly((80, 124), (58, 190), (76, 180), (90, 194), (106, 130), double=True),
                 poly((120, 124), (142, 190), (124, 180), (110, 194), (94, 130), double=True)]
        head = [scallop_ring(100, 82, 54, 12, 9, fill="ink"),
                circle(100, 82, 36, knock=True, w=0.8),
                text(100, 82, 26, k.word("rosette", "label"), slot="label", width=44)]
        return turn(tails + head, 6, (100, 100))

    def _crown():
        s = [poly((34, 146), (26, 62), (68, 102), (100, 40), (132, 102), (174, 62), (166, 146), fill="ink"),
             circle(26, 56, 8, double=True), circle(100, 32, 9, double=True), circle(174, 56, 8, double=True),
             rrect(30, 140, 140, 30, 8, double=True),
             circle(66, 155, 5, fill="ink", ink=False), circle(100, 155, 6, fill="ink", ink=False),
             circle(134, 155, 5, fill="ink", ink=False)]
        return turn(s, -6, (100, 110))

    def _winners_podium():
        s = [rrect(20, 114, 54, 66, 4, double=True),
             rrect(126, 132, 54, 48, 4, double=True),
             rrect(73, 82, 54, 98, 4, fill="ink"),
             text(100, 130, 44, k.word("winners-podium", "first"), slot="first", colour="ground"),
             text(47, 148, 30, k.word("winners-podium", "second"), slot="second", colour="ink"),
             text(153, 158, 26, k.word("winners-podium", "third"), slot="third", colour="ink"),
             line((8, 180), (192, 180), w=0.9),
             k._s(star_pts(100, 50, 22, 10), closed=True, fill="ink")]
        s += [line((66, 40), (74, 46), w=0.8), line((134, 40), (126, 46), w=0.8), line((100, 14), (100, 22), w=0.8)]
        return s

    def _certificate():
        paper = [rrect(18, 36, 164, 118, 8, double=True),
                 line((56, 70), (144, 70), w=1.3), line((46, 96), (154, 96), w=0.9),
                 line((46, 118), (112, 118), w=0.9)]
        seal = [poly((134, 140), (126, 182), (138, 174), (146, 184), (150, 146), fill="ink"),
                poly((156, 140), (166, 180), (154, 172), (146, 184), (142, 146), fill="ink"),
                scallop_ring(146, 132, 20, 8, 5, fill="ink", double=True),
                circle(146, 132, 12, knock=True, w=0.7)]
        return turn(paper, -6, (100, 96)) + seal

    def _cpd_badge():
        shield = [path(spline((100, 18), (130, 30), (164, 32)), spline((164, 32), (166, 92), (150, 136), (100, 184)),
                       spline((100, 184), (50, 136), (34, 92), (36, 32)), spline((36, 32), (70, 30), (100, 18)),
                       fill="ink", double=True),
                  path(spline((100, 34), (126, 44), (150, 46)), spline((150, 46), (150, 96), (136, 128), (100, 164)),
                       spline((100, 164), (64, 128), (50, 96), (50, 46)), spline((50, 46), (74, 44), (100, 34)),
                       knock=True, w=0.7),
                  text(100, 92, 34, k.word("cpd-badge", "label"), slot="label", width=86),
                  line((80, 116), (94, 130), (122, 104), knock=True, w=1.1)]
        return turn(shield, 5, (100, 100)) + sparkle(178, 42, 7) + sparkle(24, 150, 5, w=0.8)

    # ------------------------------------------------------------ social

    def _hashtag():
        tile = [rrect(30, 30, 140, 140, 30, fill="ink", double=True),
                line((88, 56), (76, 146), knock=True, w=1.4), line((126, 56), (114, 146), knock=True, w=1.4),
                line((60, 84), (146, 84), knock=True, w=1.4), line((54, 118), (140, 118), knock=True, w=1.4)]
        return turn(tile, 8)

    def _at_sign():
        return [circle(100, 100, 78, fill="tone", ink=False),
                circle(100, 100, 22, fill="ink"),
                curve((124, 76), (124, 116), (136, 128), (154, 120), (164, 98), (158, 66), (134, 40), (100, 30),
                      (64, 40), (38, 70), (32, 104), (46, 140), (76, 164), (112, 168), (142, 156), w=1.2)]

    def _like_bubble():
        bubble = [rrect(28, 34, 144, 106, 26, fill="ink", double=True),
                  poly((66, 136), (58, 174), (102, 136), fill="ink", ink=False),
                  line((66, 140), (58, 174), (102, 140)),
                  heart(100, 88, 2.6, fill="ground", ink=False)]
        return turn(bubble, -5) + sparkle(176, 30, 8) + sparkle(168, 168, 5, w=0.8)

    def _share():
        a, b, c = (142, 46), (54, 100), (142, 154)
        return [line((124, 56), (72, 90), w=1.1), line((72, 110), (124, 144), w=1.1),
                circle(a[0], a[1], 24, fill="ink"), circle(b[0], b[1], 24, double=True),
                circle(c[0], c[1], 24, double=True)]

    def _notification_bell():
        bell = [path(spline((54, 142), (64, 116), (64, 84), (78, 56), (100, 46), (122, 56), (136, 84), (136, 116),
                            (146, 142)), fill="ink"),
                rrect(42, 138, 116, 16, 8, double=True),
                curve((76, 120), (76, 92), (86, 68), knock=True, w=0.7),
                circle(100, 40, 7),
                circle(100, 166, 11, fill="tone")]
        waves = [arc(100, 100, 74, 74, 200, 230, w=0.8), arc(100, 100, 74, 74, 330, 350, w=0.8)]
        dot = [circle(146, 40, 14, fill="ink")]
        return turn(bell, 10, (100, 40)) + waves + dot

    # ------------------------------------------------------------ travel

    def _globe():
        return [circle(100, 96, 72, fill="ink", double=True),
                arc(100, 96, 32, 72, 0, 360, knock=True, w=0.8),
                line((100, 24), (100, 168), knock=True, w=0.8),
                line((28, 96), (172, 96), knock=True, w=0.8),
                curve((40, 58), (100, 68), (160, 58), knock=True, w=0.8),
                curve((40, 134), (100, 124), (160, 134), knock=True, w=0.8),
                curve((60, 180), (100, 188), (140, 180), w=0.9)]

    def _plane():
        body = [poly((100, 16), (110, 30), (110, 78), (178, 116), (178, 132), (110, 112), (110, 152), (132, 168),
                     (132, 180), (100, 172), (68, 180), (68, 168), (90, 152), (90, 112), (22, 132), (22, 116),
                     (90, 78), (90, 30), fill="ink", double=True),
                line((100, 36), (100, 140), knock=True, w=0.7)]
        trail = [curve((14, 186), (30, 160), (40, 146), dash=(7, 7), w=0.8)]
        return turn(shift(body, 6, -6, 0.86), 45) + trail

    def _train():
        s = [line((70, 166), (44, 194), w=0.9), line((130, 166), (156, 194), w=0.9),
             line((62, 180), (138, 180), w=0.7),
             rrect(50, 24, 100, 140, 26, fill="ink", double=True),
             rrect(64, 44, 72, 46, 10, fill="ground", ink=False),
             line((100, 44), (100, 90), w=0.8),
             line((60, 106), (140, 106), knock=True, w=0.7),
             circle(72, 132, 8, fill="ground", ink=False), circle(128, 132, 8, fill="ground", ink=False),
             rrect(90, 126, 20, 12, 4, knock=True, w=0.7)]
        return s

    def _suitcase():
        s = [rrect(76, 38, 48, 32, 10),
             rrect(28, 64, 144, 106, 14, fill="ink", double=True),
             line((64, 64), (64, 170), knock=True, w=0.8), line((136, 64), (136, 170), knock=True, w=0.8),
             rrect(90, 110, 20, 14, 4, knock=True, w=0.7),
             circle(52, 178, 7, w=0.9), circle(148, 178, 7, w=0.9)]
        return turn(s, -6, (100, 110))

    def _hotel_bed():
        s = [rrect(16, 66, 18, 112, 6, fill="ink"),
             line((34, 146), (184, 146), (184, 112)),
             rrect(34, 110, 150, 28, 8, double=True),
             rrect(40, 90, 46, 24, 11),
             path(spline((92, 110), (110, 98), (184, 104)), [(184, 104), (184, 138)], [(184, 138), (92, 138)],
                  fill="ink"),
             line((40, 146), (40, 172)), line((178, 146), (178, 172)),
             line((112, 116), (176, 116), knock=True, w=0.7)]
        s += [line((120, 40), (138, 40), (120, 60), (138, 60), w=0.9),
              line((148, 22), (160, 22), (148, 36), (160, 36), w=0.8)]
        return s

    # ------------------------------------------------------------ places

    def _university():
        s = [poly((100, 18), (182, 62), (18, 62), fill="ink", double=True),
             circle(100, 46, 8, knock=True, w=0.8),
             rrect(24, 62, 152, 16, 3)]
        for x in (36, 74, 112, 150):
            s.append(rrect(x, 78, 14, 66, 4, double=True))
        s += [rrect(20, 144, 160, 14, 3, double=True), rrect(10, 158, 180, 18, 3, fill="ink")]
        return s

    def _factory():
        s = [rrect(140, 34, 28, 146, 4, fill="ink"),
             line((140, 60), (168, 60), knock=True, w=0.8), line((140, 74), (168, 74), knock=True, w=0.8),
             poly((16, 180), (16, 98), (56, 72), (56, 98), (96, 72), (96, 98), (140, 72), (140, 180), double=True),
             rrect(28, 120, 22, 18, 3, w=0.8), rrect(64, 120, 22, 18, 3, w=0.8), rrect(100, 120, 22, 18, 3, w=0.8),
             rrect(60, 150, 30, 30, 3, w=0.9),
             line((6, 180), (194, 180), w=0.9),
             curve((150, 26), (144, 14), (158, 6), (176, 10), (184, 22), w=0.9),
             curve((174, 30), (188, 34), (194, 26), w=0.7)]
        return s

    def _shopfront():
        awning_bottom = k._scallop((186, 84), (14, 84), 6, -10)
        s = [rrect(26, 84, 148, 94, 4, double=True),
             rrect(40, 104, 62, 46, 4),
             line((40, 128), (102, 128), w=0.6),
             rrect(116, 108, 42, 70, 4, fill="tone"),
             circle(150, 144, 3, fill="ink", ink=False),
             k._s([(28, 40), (172, 40)] + awning_bottom, closed=True, fill="ink"),
             line((6, 178), (194, 178), w=0.9)]
        for x0, x1 in ((57, 42), (86, 76), (114, 124), (143, 158)):
            s.append(line((x0, 42), (x1, 82), knock=True, w=0.8))
        return s

    def _office_block():
        s = [rrect(128, 84, 54, 98, 4, double=True),
             rrect(18, 110, 40, 72, 4, double=True),
             rrect(54, 18, 84, 164, 6, fill="ink")]
        for row in range(4):
            for col in range(2):
                x, y = 68 + col * 34, 34 + row * 28
                s.append(rrect(x, y, 22, 14, 4, knock=True, w=0.8))
        s += [rrect(84, 156, 24, 26, 3, knock=True, w=0.8),
              line((140, 104), (170, 104), w=0.6), line((140, 124), (170, 124), w=0.6),
              line((140, 144), (170, 144), w=0.6),
              line((6, 182), (194, 182), w=0.9)]
        return s

    def _skyline_generic():
        s = [rrect(10, 104, 38, 76, 3, double=True),
             poly((84, 180), (84, 88), (101, 70), (118, 88), (118, 180), double=True),
             rrect(150, 116, 40, 64, 3, double=True),
             rrect(46, 52, 40, 128, 3, fill="ink"),
             rrect(116, 36, 36, 144, 3, fill="ink"),
             line((134, 36), (134, 12), w=0.9)]
        for y in (70, 98, 126):
            s.append(line((56, y), (76, y), knock=True, w=0.9))
        for y in (58, 86, 114, 142):
            s.append(line((126, y), (142, y), knock=True, w=0.9))
        s += [line((2, 180), (198, 180), w=0.9)]
        s += sparkle(30, 70, 6, w=0.8) + sparkle(176, 82, 5, w=0.8)
        return s

    return {
        "grad-cap": _grad_cap,
        "book-open": _book_open,
        "brain": _brain,
        "lightning": _lightning,
        "star": _star,
        "medal": _medal,
        "rosette": _rosette,
        "crown": _crown,
        "winners-podium": _winners_podium,
        "certificate": _certificate,
        "hashtag": _hashtag,
        "at-sign": _at_sign,
        "like-bubble": _like_bubble,
        "share": _share,
        "notification-bell": _notification_bell,
        "globe": _globe,
        "plane": _plane,
        "train": _train,
        "suitcase": _suitcase,
        "hotel-bed": _hotel_bed,
        "university": _university,
        "factory": _factory,
        "shopfront": _shopfront,
        "office-block": _office_block,
        "skyline-generic": _skyline_generic,
        "cpd-badge": _cpd_badge,
    }
