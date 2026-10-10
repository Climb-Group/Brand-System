"""Festival set: food, drinks, merch and party icons for Climb27 socials."""
import math


def build(k):
    """k is the illustrations module. Return {name: (builder_fn, "what it says")}."""
    line, curve, arc, circle, rrect, poly, text, turn, shift, sparkle = (k.line, k.curve, k.arc, k.circle, k.rrect,
                                                                         k.poly, k.text, k.turn, k.shift, k.sparkle)

    def shape(pts, **kw):
        """A closed shape from a ready list of points."""
        return k._s(list(pts), closed=True, **kw)

    def spline(*pts):
        return k._catmull(list(pts))

    # ------------------------------------------------------------ food

    def _food_truck():
        body = [rrect(14, 52, 128, 96, 10, double=True),
                # Serving hatch under a scalloped awning.
                rrect(30, 78, 84, 36, 4, fill="ink"),
                line((38, 104), (106, 104), knock=True, w=0.8),
                shape([(24, 62), (120, 62)] + k._scallop((120, 66), (24, 66), 4, 9), fill="tone"),
                line((30, 126), (114, 126), w=0.8),
                # Cab.
                line((142, 72), (166, 72), (186, 106), (186, 148), (142, 148)),
                poly((150, 82), (164, 82), (176, 104), (150, 104), fill="tone", w=0.9),
                line((150, 120), (160, 120), w=0.8),
                circle(52, 150, 16, fill="ground"), circle(52, 150, 6, fill="ink", ink=False),
                circle(150, 150, 16, fill="ground"), circle(150, 150, 6, fill="ink", ink=False),
                line((4, 176), (196, 176), w=0.7)]
        steam = [curve((56, 46), (52, 36), (58, 26), (54, 16), w=0.7), curve((74, 46), (70, 34), (77, 24), (72, 12), w=0.7)]
        return shift(body, 0, 4) + steam

    def _pizza_slice():
        cheese = [(100, 186)] + arc(100, 196, 132, 132, -117, -63)["pts"]
        s = [shape(cheese, fill="ink", double=True),
             shape(arc(100, 196, 132, 132, -117, -63)["pts"] + arc(100, 196, 152, 152, -64, -116)["pts"],
                   fill="ground"),
             circle(96, 96, 11, fill="ground", knock=True, w=0.7),
             circle(78, 126, 8, fill="ground", knock=True, w=0.7),
             circle(116, 132, 9, fill="ground", knock=True, w=0.7),
             circle(100, 160, 5, fill="ground", knock=True, w=0.7),
             # A cheese drip off the edge.
             curve((134, 98), (140, 112), (136, 124), w=0.9)]
        s += [line((70, 58), (74, 50), w=0.6), line((100, 50), (100, 42), w=0.6), line((130, 58), (126, 50), w=0.6)]
        return turn(shift(s, 0, -4), 14, (100, 110))

    def _burger():
        dome = arc(100, 92, 68, 54, 180, 360)["pts"]
        s = [shape(dome, double=True),
             line((70, 62), (76, 58), w=0.8), line((96, 52), (104, 52), w=0.8), line((126, 58), (132, 62), w=0.8),
             line((82, 76), (88, 74), w=0.8), line((114, 74), (120, 76), w=0.8),
             # Lettuce frill.
             curve((26, 96), (38, 108), (52, 98), (66, 108), (80, 98), (94, 108), (108, 98), (122, 108), (136, 98),
                   (150, 108), (164, 98), (176, 104), w=0.9),
             # Cheese with a corner hanging down.
             poly((34, 110), (166, 110), (150, 126), (128, 110), fill="tone", w=0.8),
             rrect(28, 112, 144, 28, 14, fill="ink"),
             line((48, 126), (60, 126), knock=True, w=0.7), line((90, 128), (104, 128), knock=True, w=0.7),
             line((134, 126), (148, 126), knock=True, w=0.7),
             rrect(34, 146, 132, 30, 13)]
        return shift(s, 0, 4)

    def _ice_cream():
        scoop = curve(*(arc(100, 80, 40, 40, 175, 365)["pts"][::2]),
                      (142, 92), (134, 104), (124, 98), (114, 112), (102, 102), (90, 110), (78, 100), (66, 106),
                      (58, 92), closed=True, fill="ink", double=True)
        s = [poly((66, 96), (134, 96), (100, 190)),
             line((76, 112), (110, 160), w=0.7), line((96, 106), (118, 136), w=0.7),
             line((124, 112), (90, 160), w=0.7), line((104, 106), (82, 136), w=0.7),
             scoop,
             curve((76, 66), (82, 52), (96, 46), knock=True, w=0.8),
             circle(112, 32, 10, fill="ground"),
             curve((114, 22), (118, 12), (128, 8), w=0.8)]
        s += sparkle(160, 50, 7) + sparkle(42, 132, 5, w=0.8)
        return turn(s, 8, (100, 110))

    def _cupcake():
        s = [poly((52, 114), (148, 114), (134, 184), (66, 184), double=True),
             line((72, 118), (78, 180), w=0.7), line((92, 118), (94, 180), w=0.7),
             line((108, 118), (106, 180), w=0.7), line((128, 118), (122, 180), w=0.7),
             curve((40, 114), (40, 96), (56, 86), (60, 70), (78, 62), (86, 46), (102, 40), (116, 48), (122, 62),
                   (140, 70), (146, 86), (160, 98), (160, 114), closed=True, fill="ink"),
             curve((56, 96), (100, 104), (146, 94), knock=True, w=0.8),
             curve((72, 72), (100, 80), (128, 72), knock=True, w=0.8),
             line((70, 108), (76, 104), knock=True, w=0.7), line((120, 106), (128, 108), knock=True, w=0.7),
             line((96, 88), (102, 92), knock=True, w=0.7),
             circle(102, 30, 10, fill="ground"),
             curve((104, 20), (106, 10), (118, 4), w=0.8)]
        return shift(s, 0, 6)

    def _popcorn():
        def bx(t, y):
            l = 52 + (66 - 52) * (y - 92) / 94
            r = 148 - (148 - 134) * (y - 92) / 94
            return l + (r - l) * t
        s = []
        for x, y, r in ((66, 76, 18), (134, 76, 18), (84, 50, 19), (118, 48, 19), (100, 78, 19)):
            s.append(circle(x, y, r, fill="ground"))
            s.append(arc(x, y, r * 0.55, r * 0.55, 200, 290, w=0.7))
        s.append(poly((52, 92), (148, 92), (134, 186), (66, 186), double=True))
        for t0, t1 in ((0.2, 0.4), (0.6, 0.8)):
            s.append(poly((bx(t0, 92), 92), (bx(t1, 92), 92), (bx(t1, 186), 186), (bx(t0, 186), 186),
                          fill="ink", ink=False))
        s.append(poly((52, 92), (148, 92), (134, 186), (66, 186)))
        s.append(rrect(44, 88, 112, 14, 5, fill="ground"))
        s += [circle(166, 120, 7, w=0.8), circle(30, 128, 6, w=0.8)]
        return shift(s, 0, -2)

    def _doughnut():
        icing = [(100 + (56 + 5 * math.sin(7 * a)) * math.cos(a), 100 + (56 + 5 * math.sin(7 * a)) * math.sin(a))
                 for a in [i * math.tau / 56 for i in range(56)]]
        s = [circle(100, 100, 74, double=True),
             shape(icing, fill="ink"),
             circle(100, 100, 22, fill="ground")]
        for i, a in enumerate(range(10, 360, 36)):
            r = 40 if i % 2 else 34
            cx, cy = 100 + r * math.cos(math.radians(a)), 100 + r * math.sin(math.radians(a))
            d = math.radians(a + 60 + 40 * (i % 3))
            s.append(line((cx - 5 * math.cos(d), cy - 5 * math.sin(d)), (cx + 5 * math.cos(d), cy + 5 * math.sin(d)),
                          knock=True, w=0.8))
        s.append(arc(100, 100, 66, 66, 120, 160, w=0.6))
        return s

    def _taco():
        shell = arc(100, 80, 84, 84, 0, 180)["pts"]
        s = [curve((20, 84), (24, 60), (40, 66), (48, 46), (66, 54), (78, 34), (96, 46), (110, 30), (126, 44),
                   (142, 36), (152, 54), (170, 52), (180, 84), fill="tone", w=0.9),
             circle(64, 70, 10, fill="ground"), circle(118, 62, 10, fill="ground"),
             line((88, 70), (96, 58), w=0.8), line((140, 74), (150, 62), w=0.8), line((40, 78), (48, 68), w=0.8),
             shape(shell, fill="ink", double=True),
             arc(100, 80, 68, 68, 22, 158, knock=True, w=0.8),
             curve((44, 100), (52, 112), (62, 110), knock=True, w=0.7),
             curve((132, 126), (140, 118), (150, 116), knock=True, w=0.7)]
        return shift(turn(shift(s, 0, 16), -12, (100, 110)), 8, 0)

    # ------------------------------------------------------------ drinks

    def _cocktail():
        s = [poly((40, 50), (160, 50), (100, 116)),
             poly((52, 62), (148, 62), (100, 110), fill="ink", ink=False),
             line((52, 62), (148, 62), w=0.8),
             line((100, 116), (100, 172)),
             arc(100, 176, 34, 7, 0, 360, w=0.9),
             # Pick with an olive, a slice on the rim.
             line((62, 24), (114, 92), w=0.8),
             circle(104, 80, 10, fill="ground", knock=True, w=0.8),
             arc(150, 50, 18, 18, 180, 360, fill="tone", w=0.9),
             line((150, 50), (150, 34), w=0.6), line((150, 50), (138, 40), w=0.6), line((150, 50), (162, 40), w=0.6)]
        s += sparkle(30, 96, 6) + sparkle(172, 104, 5, w=0.8)
        return turn(s, -6, (100, 110))

    def _pint():
        s = [line((56, 46), (68, 182), (132, 182), (144, 46)),
             poly((59, 72), (141, 72), (131, 176), (69, 176), fill="ink", ink=False),
             curve((50, 56), (54, 36), (70, 34), (80, 22), (100, 28), (118, 18), (134, 32), (148, 36), (150, 56),
                   (124, 62), (100, 58), (76, 64), closed=True, fill="tone"),
             circle(84, 106, 3.5, knock=True, w=0.6), circle(110, 128, 3, knock=True, w=0.6),
             circle(96, 150, 3.5, knock=True, w=0.6), circle(118, 94, 2.5, knock=True, w=0.6),
             line((124, 90), (118, 164), knock=True, w=0.8),
             line((66, 170), (134, 170), w=0.7)]
        s += [curve((150, 64), (156, 74), (150, 84), w=0.7)]
        return turn(s, 6, (100, 110))

    def _wine_bottle():
        bottle = [line((88, 18), (88, 58)), curve((88, 58), (70, 76), (66, 100)),
                  line((66, 100), (66, 182), (134, 182), (134, 100)),
                  curve((134, 100), (130, 76), (112, 58)), line((112, 58), (112, 18)),
                  rrect(84, 10, 32, 30, 5, fill="ink"),
                  rrect(66, 112, 68, 50, 4, fill="ink", ink=False),
                  line((66, 112), (134, 112), w=0.9), line((66, 162), (134, 162), w=0.9),
                  line((80, 130), (120, 130), knock=True, w=0.8), line((86, 144), (114, 144), knock=True, w=0.7),
                  curve((122, 84), (126, 100), (126, 106), w=0.6)]
        return turn(bottle, -14, (100, 110)) + sparkle(160, 46, 8) + sparkle(42, 54, 5, w=0.8)

    def _bottle(clink):
        b = [line((92, 22), (92, 54)), curve((92, 54), (80, 70), (78, 88)),
             line((78, 88), (78, 182), (122, 182), (122, 88)),
             curve((122, 88), (120, 70), (108, 54)), line((108, 54), (108, 22)),
             rrect(88, 14, 24, 12, 3, fill="ink" if clink else "ground"),
             rrect(78, 108, 44, 46, 3, fill="ink" if clink else "tone", ink=False),
             line((78, 108), (122, 108), w=0.9), line((78, 154), (122, 154), w=0.9)]
        if clink:
            b += [line((88, 124), (112, 124), knock=True, w=0.8), line((92, 138), (108, 138), knock=True, w=0.7)]
        else:
            b += [line((88, 124), (112, 124), w=0.7), line((92, 138), (108, 138), w=0.7)]
        return b

    def _cheers_bottles():
        left = turn(shift(_bottle(True), -44, 4), 12, (56, 186))
        right = turn(shift(_bottle(False), 44, 4), -12, (144, 186))
        burst = [line((100, 14), (100, 2), w=0.9), line((84, 18), (76, 8), w=0.8), line((116, 18), (124, 8), w=0.8)]
        return shift(right + left + burst, 0, 4) + sparkle(28, 60, 6) + sparkle(172, 64, 5, w=0.8)

    def _water_bottle():
        s = [rrect(82, 16, 36, 24, 6, fill="ink"),
             arc(118, 28, 14, 10, -90, 90, w=0.8),
             rrect(86, 40, 28, 12, 3),
             rrect(62, 52, 76, 134, 20, double=True),
             rrect(62, 98, 76, 50, 2, fill="ink", ink=False),
             line((62, 98), (138, 98), w=0.9), line((62, 148), (138, 148), w=0.9),
             curve((100, 108), (92, 122), (94, 132), (100, 136), (106, 132), (108, 122), (100, 108), knock=True,
                   w=0.8),
             curve((62, 80), (80, 74), (100, 82), (120, 74), (138, 80), w=0.7),
             line((76, 160), (76, 172), w=0.6)]
        return turn(s, 10, (100, 110))

    # ------------------------------------------------------------ gear and merch

    def _festival_tent():
        roof = (spline((100, 32), (72, 62), (22, 96))
                + k._scallop((22, 96), (178, 96), 6, -8)
                + spline((178, 96), (128, 62), (100, 32)))
        s = [line((100, 32), (100, 8)),
             poly((100, 8), (130, 15), (100, 22), fill="ink", w=0.9),
             line((34, 104), (34, 178)), line((166, 104), (166, 178)),
             shape(roof, fill="ink", double=True),
             curve((100, 36), (82, 66), (66, 100), knock=True, w=0.8),
             curve((100, 36), (118, 66), (134, 100), knock=True, w=0.8),
             line((100, 36), (100, 102), knock=True, w=0.8),
             # Door flaps tied back.
             curve((100, 112), (86, 136), (76, 178)), curve((100, 112), (114, 136), (124, 178)),
             line((100, 112), (100, 178), w=0.6, dash=(4, 6)),
             line((22, 96), (6, 178), w=0.6), line((178, 96), (194, 178), w=0.6),
             line((4, 180), (196, 180), w=0.8)]
        return s

    def _sunglasses():
        lens_l = [(28, 82), (94, 82), (92, 108), (80, 126), (50, 128), (34, 114)]
        lens_r = [(200 - x, y) for x, y in lens_l]
        s = [line((14, 74), (28, 82)), line((186, 74), (172, 82)),
             line((22, 80), (178, 80), w=1.0),
             curve(*lens_l, closed=True, fill="ink", double=True),
             curve(*lens_r, closed=True, fill="ink", double=True),
             curve((94, 88), (100, 82), (106, 88), w=0.9),
             line((50, 116), (72, 92), knock=True, w=0.8), line((62, 118), (78, 100), knock=True, w=0.7),
             line((122, 116), (144, 92), knock=True, w=0.8), line((134, 118), (150, 100), knock=True, w=0.7)]
        s += sparkle(160, 46, 9) + sparkle(42, 156, 5, w=0.8)
        return turn(s, -8, (100, 100))

    def _sun():
        s = [circle(100, 100, 42, fill="ink", double=True),
             arc(100, 100, 32, 32, 200, 260, knock=True, w=0.8)]
        for i in range(12):
            a = math.radians(i * 30 - 75)
            r0, r1 = 56, (84 if i % 2 == 0 else 72)
            s.append(line((100 + r0 * math.cos(a), 100 + r0 * math.sin(a)),
                          (100 + r1 * math.cos(a), 100 + r1 * math.sin(a)), w=1.0 if i % 2 == 0 else 0.8))
        return s

    def _umbrella():
        canopy = arc(100, 104, 82, 70, 180, 360)["pts"] + k._scallop((182, 104), (18, 104), 4, -10)
        s = [line((100, 34), (100, 22)),
             shape(canopy, fill="ink", double=True),
             curve((100, 36), (76, 60), (59, 104), knock=True, w=0.8),
             curve((100, 36), (124, 60), (141, 104), knock=True, w=0.8),
             line((100, 36), (100, 104), knock=True, w=0.8),
             line((100, 104), (100, 168)),
             curve((100, 168), (102, 184), (116, 186), (122, 174))]
        return turn(shift(s, 0, 0), -14, (100, 110))

    def _tote_bag():
        s = [curve((70, 80), (68, 36), (100, 24), (132, 36), (130, 80), w=1.0),
             curve((80, 80), (80, 44), (100, 36), (120, 44), (120, 80), w=0.8),
             poly((42, 78), (158, 78), (164, 184), (36, 184), fill="ink", double=True),
             line((44, 92), (156, 92), knock=True, w=0.7, dash=(5, 5)),
             rrect(64, 66, 12, 26, 3, fill="ground"), rrect(124, 66, 12, 26, 3, fill="ground")]
        s += sparkle(100, 136, 18, knock=True) + sparkle(130, 112, 6, knock=True, w=0.8)
        return s

    def _t_shirt():
        neck = spline((126, 28), (114, 44), (100, 48), (86, 44), (74, 28))
        body = [(74, 28), (44, 38), (12, 76), (38, 104), (54, 90), (54, 182), (146, 182), (146, 90), (162, 104),
                (188, 76), (156, 38), (126, 28)] + neck
        s = [shape(body, fill="ink", double=True),
             curve((80, 32), (100, 54), (120, 32), knock=True, w=0.7),
             line((54, 90), (48, 66), knock=True, w=0.7), line((146, 90), (152, 66), knock=True, w=0.7),
             line((30, 84), (42, 70), knock=True, w=0.6), line((170, 84), (158, 70), knock=True, w=0.6)]
        s += sparkle(100, 116, 16, knock=True) + sparkle(124, 98, 5, knock=True, w=0.8)
        return s

    def _cap():
        s = [curve((150, 118), (178, 112), (198, 124), (194, 140), (152, 142), closed=True, fill="tone", w=1.0),
             curve((24, 128), (28, 86), (64, 56), (102, 56), (138, 76), (156, 128), fill="ink"),
             line((24, 128), (156, 128)),
             curve((96, 58), (112, 86), (116, 128), knock=True, w=0.8),
             curve((60, 64), (54, 92), (56, 128), knock=True, w=0.7),
             line((28, 118), (152, 118), knock=True, w=0.7, dash=(5, 5)),
             rrect(90, 48, 16, 9, 4, fill="ink"),
             circle(126, 94, 3, fill="ground", ink=False)]
        return turn(shift(s, -6, 6), -6, (100, 110))

    def _bucket_hat():
        brim = [(54, 112), (100, 114), (146, 112), (170, 126), (190, 150), (160, 156), (100, 148), (40, 156), (10, 150),
                (30, 126)]
        s = [curve(*brim, closed=True, fill="tone"),
             curve((60, 112), (62, 72), (80, 56), (100, 54), (120, 56), (138, 72), (140, 112), fill="ground"),
             line((60, 112), (140, 112)),
             rrect(58, 94, 84, 20, 4, fill="ink"),
             curve((32, 136), (100, 128), (168, 136), w=0.6, dash=(5, 5)),
             curve((76, 62), (100, 70), (124, 62), w=0.6, dash=(5, 5)),
             circle(124, 82, 2.6, fill="ink", ink=False)]
        return shift(s, 0, 6)

    def _goodie_bag():
        s = [curve((58, 86), (62, 54), (72, 46), (84, 66), (94, 40), (106, 38), (114, 62), (128, 46), (138, 54), (142, 86), fill="tone", w=0.9),
             arc(80, 86, 14, 30, 180, 360, w=0.9), arc(120, 86, 14, 30, 180, 360, w=0.9),
             poly((44, 84), (156, 84), (150, 184), (50, 184), fill="ink", double=True),
             line((44, 84), (52, 96), (148, 96), (156, 84), knock=True, w=0.7),
             circle(80, 100, 3, fill="ground", ink=False), circle(120, 100, 3, fill="ground", ink=False)]
        star = [line((100, 116), (108, 132), (126, 134), (112, 146), (116, 164), (100, 154), (84, 164), (88, 146),
                     (74, 134), (92, 132), (100, 116), knock=True, w=0.9)]
        return shift(s + star, 0, 2) + sparkle(170, 70, 6) + sparkle(28, 112, 5, w=0.8)

    def _gift_box():
        s = [curve((100, 70), (74, 34), (56, 46), (64, 66), (100, 70), w=1.0),
             curve((100, 70), (126, 34), (144, 46), (136, 66), (100, 70), w=1.0),
             rrect(40, 96, 120, 88, 6, fill="ink"),
             line((92, 98), (92, 184), knock=True, w=0.9), line((108, 98), (108, 184), knock=True, w=0.9),
             rrect(30, 70, 140, 30, 6, fill="ground", double=True),
             rrect(90, 70, 20, 30, 2, fill="ink", ink=False),
             line((90, 70), (90, 100), w=0.8), line((110, 70), (110, 100), w=0.8),
             circle(100, 70, 7, fill="ink")]
        s += sparkle(166, 40, 8) + sparkle(30, 140, 5, w=0.8)
        return shift(s, 0, 2)

    def _party_popper():
        cone = [poly((72, 96), (128, 96), (100, 192), fill="ink"),
                line((80, 120), (122, 108), knock=True, w=0.8),
                line((86, 144), (116, 134), knock=True, w=0.8),
                line((92, 166), (110, 160), knock=True, w=0.8),
                arc(100, 96, 28, 8, 0, 360, fill="ground")]
        cone = turn(cone, 40, (100, 150))
        cone = shift(cone, -2, -6, 1.25)
        bits = [curve((96, 70), (90, 52), (104, 46), (100, 28), w=0.9),
                curve((116, 84), (134, 70), (130, 56), (148, 44), w=0.9),
                curve((124, 108), (146, 104), (158, 116), (178, 106), w=0.9),
                turn([rrect(150, 30, 14, 8, 2, fill="ink")], 30, (157, 34))[0],
                turn([rrect(70, 32, 12, 7, 2, fill="ink")], -30, (76, 35))[0],
                turn([rrect(168, 80, 14, 8, 2, fill="ink")], 70, (175, 84))[0],
                circle(124, 22, 4, fill="ink", ink=False), circle(176, 140, 4, fill="ink", ink=False),
                circle(150, 82, 3, w=0.8)]
        bits += sparkle(122, 50, 6, w=0.8) + sparkle(182, 52, 7)
        return cone + shift(bits, 8, 0)

    def _balloon(cx, cy, fill):
        b = [curve((cx, cy - 34), (cx + 26, cy - 22), (cx + 26, cy + 6), (cx + 8, cy + 32), (cx, cy + 36),
                   (cx - 8, cy + 32), (cx - 26, cy + 6), (cx - 26, cy - 22), closed=True,
                   fill=fill, double=fill is None),
             poly((cx, cy + 36), (cx + 6, cy + 44), (cx - 6, cy + 44), fill="ink", w=0.8)]
        if fill == "ink":
            b.append(arc(cx, cy - 6, 16, 20, 200, 250, knock=True, w=0.8))
        else:
            b.append(arc(cx, cy - 6, 16, 20, 200, 250, w=0.7))
        return b

    def _balloons():
        s = [curve((58, 108), (66, 136), (86, 160), (100, 188), w=0.8),
             curve((142, 106), (134, 136), (114, 160), (100, 188), w=0.8),
             curve((100, 98), (106, 130), (96, 160), (100, 188), w=0.8)]
        s += turn(_balloon(58, 64, None), -12, (58, 100))
        s += turn(_balloon(142, 62, None), 12, (142, 100))
        s += _balloon(100, 56, "ink")
        return s

    def _string_lights():
        s = []
        for (a, b, c, d), bulbs in ((((6, 22), (54, 60), (100, 44), (194, 22)), (0.18, 0.42, 0.7, 0.9)),
                                    (((6, 104), (60, 134), (130, 122), (194, 104)), (0.14, 0.36, 0.6, 0.84))):
            pts = k._catmull([a, b, c, d], n=24)
            s.append(k._s(pts, w=0.9))
            for j, t in enumerate(bulbs):
                x, y = pts[int(t * (len(pts) - 1))]
                filled = j % 2 == 0
                s.append(rrect(x - 6, y - 2, 12, 12, 3, fill="ground"))
                s.append(curve((x, y + 10), (x + 12, y + 22), (x + 10, y + 36), (x, y + 44), (x - 10, y + 36),
                               (x - 12, y + 22), closed=True, fill="ink" if filled else "tone"))
                if filled:
                    s += [line((x - 18, y + 30), (x - 25, y + 32), w=0.7), line((x + 18, y + 30), (x + 25, y + 32), w=0.7),
                          line((x, y + 52), (x, y + 58), w=0.7)]
        return shift(s, 0, 0)

    return {
        "food-truck": (_food_truck, "Street food, the food village"),
        "pizza-slice": (_pizza_slice, "Food stalls, grab a slice between talks"),
        "burger": (_burger, "Street food, lunch on the festival site"),
        "ice-cream": (_ice_cream, "Summer treats, sunny festival days"),
        "cocktail": (_cocktail, "Drinks reception, cocktail hour"),
        "pint": (_pint, "Bar, a pint after the talks"),
        "wine-bottle": (_wine_bottle, "Drinks reception, celebrating"),
        "cupcake": (_cupcake, "Treats, birthdays, celebrations"),
        "popcorn": (_popcorn, "Snacks, watch the show"),
        "festival-tent": (_festival_tent, "Festival marquee, the festival site"),
        "sunglasses": (_sunglasses, "Summer festival vibes, looking cool"),
        "sun": (_sun, "Sunshine, summer dates, outdoor festival"),
        "umbrella": (_umbrella, "Whatever the weather, rain or shine"),
        "tote-bag": (_tote_bag, "Merch tote, take something home"),
        "t-shirt": (_t_shirt, "Merch tee, crew and volunteers"),
        "cap": (_cap, "Merch cap, crew"),
        "water-bottle": (_water_bottle, "Stay hydrated, refill stations, reusable"),
        "goodie-bag": (_goodie_bag, "Goodie bags, delegate gifts, freebies"),
        "gift-box": (_gift_box, "Giveaways, prizes, competitions"),
        "party-popper": (_party_popper, "Celebrate, announcements, we did it"),
        "balloons": (_balloons, "Party, celebration, anniversaries"),
        "bucket-hat": (_bucket_hat, "Festival merch, festival style"),
        "doughnut": (_doughnut, "Sweet treats, coffee and a doughnut"),
        "cheers-bottles": (_cheers_bottles, "Cheers, after party, drinks on us"),
        "string-lights": (_string_lights, "Evening party, festoon lights, after dark"),
    }
