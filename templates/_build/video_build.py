"""4K motion graphics for Premiere Pro, DaVinci Resolve and any editor: lower thirds, stickers, a slab wipe, title and
end cards, background loops, a bug and safe-area guides.

Values from the tokens and guidelines/video.md + motion.md: 3840x2160 at 25fps; lower third on a Dark Brown bar at 85%
with a Climb Orange rule on the left, name in Montserrat Bold White, role in Open Sans; things rise into place
(cubic-bezier(0.16, 1, 0.3, 1)), never bounce, except the sticker pop (spring). Transparent clips are ProRes 4444 with
alpha; opaque clips are H.264 High at a high bitrate. Stills are PNG.

python3 video_build.py [Brand ...]   (shared clips are built once under video/_shared)
"""
import json
import math
import os
import shutil
import subprocess
import sys

from PIL import Image

import art
import brand as B
import copy_io as C
import motifs as M

FPS = 25
W, H = 3840, 2160
TMP = os.path.join(B.OUT, "_video_tmp")
VOUT = os.path.join(B.OUT, "video")
SHARED_COPY = "video/_shared/stills/shared-stills.copy.md"


def words(b=None):
    """The copy file with the words of the shared stills, or of one brand's stills and clips."""
    return C.load("video/%s/stills/%s-stills.copy.md" % (b, b) if b else SHARED_COPY)


# ---------- easing ----------

def bezier(x1, y1, x2, y2):
    def f(t):
        if t <= 0:
            return 0.0
        if t >= 1:
            return 1.0
        lo, hi = 0.0, 1.0
        for _ in range(40):
            mid = (lo + hi) / 2
            x = 3 * (1 - mid) ** 2 * mid * x1 + 3 * (1 - mid) * mid ** 2 * x2 + mid ** 3
            if x < t:
                lo = mid
            else:
                hi = mid
        s = (lo + hi) / 2
        return 3 * (1 - s) ** 2 * s * y1 + 3 * (1 - s) * s ** 2 * y2 + s ** 3
    return f


RISE = bezier(0.16, 1, 0.3, 1)
SPRING = bezier(0.34, 1.56, 0.64, 1)
EXIT = bezier(0.4, 0, 1, 1)


def prog(frame, start, dur_ms):
    return max(0.0, min(1.0, (frame - start) / (dur_ms / 1000 * FPS)))


# ---------- layers ----------

class Layer:
    def __init__(self, path):
        im = Image.open(path).convert("RGBA")
        box = im.getbbox() or (0, 0, 1, 1)
        self.im = im.crop(box)
        self.x, self.y = box[0], box[1]


def render_layers(specs, w=W, h=H):
    """specs: {name: html body}. Returns {name: Layer} rendered transparent at full frame size."""
    os.makedirs(TMP, exist_ok=True)
    jobs = []
    for name, body in specs.items():
        hp = os.path.join(TMP, name + ".html")
        open(hp, "w").write(art.page(w, h, body, extra_css=CSS))
        jobs.append(dict(html=hp, out=os.path.join(TMP, name + ".png"), w=w, h=h, transparent=True))
    jp = os.path.join(TMP, "jobs_%s.json" % abs(hash(tuple(specs))))
    json.dump(jobs, open(jp, "w"))
    subprocess.run(["node", os.path.join(B.ROOT, "render.mjs"), jp], check=True, capture_output=True)
    return {n: Layer(os.path.join(TMP, n + ".png")) for n in specs}


def render_ground(name, body, w=W, h=H, bg="#1E0F05"):
    hp = os.path.join(TMP, name + ".html")
    open(hp, "w").write(art.page(w, h, body, bg=bg, extra_css=CSS))
    out = os.path.join(TMP, name + ".png")
    jp = os.path.join(TMP, "jobs_%s.json" % name)
    json.dump([dict(html=hp, out=out, w=w, h=h, transparent=False)], open(jp, "w"))
    subprocess.run(["node", os.path.join(B.ROOT, "render.mjs"), jp], check=True, capture_output=True)
    return Image.open(out).convert("RGBA")


CSS = """
.disp{font-family:'Montserrat';font-weight:800;text-transform:uppercase;letter-spacing:-0.01em;line-height:1.0;color:#fff}
.black{font-family:'Montserrat';font-weight:900}
.body{font-family:'Open Sans'}
.o{color:#E8712A}
.i{font-style:italic}
"""


def place(frame_im, layer, dx=0, dy=0, alpha=1.0, scale=1.0, clip_w=None, rotate=0.0, origin=None):
    im = layer.im
    if clip_w is not None:
        cw = max(1, int(im.width * clip_w))
        im = im.crop((0, 0, cw, im.height))
    if scale != 1.0:
        nw, nh = max(1, int(im.width * scale)), max(1, int(im.height * scale))
        cx, cy = origin or (layer.x + layer.im.width / 2, layer.y + layer.im.height / 2)
        im = im.resize((nw, nh), Image.LANCZOS)
        x = cx - (cx - layer.x) * scale
        y = cy - (cy - layer.y) * scale
    else:
        x, y = layer.x, layer.y
    if alpha < 1.0:
        a = im.getchannel("A").point(lambda v: int(v * alpha))
        im = im.copy()
        im.putalpha(a)
    if alpha <= 0:
        return
    frame_im.alpha_composite(im, (int(round(x + dx)), int(round(y + dy))))


# ---------- encoding ----------

def encode(frames, out, alpha=True, w=W, h=H):
    """frames: iterable of RGBA images. ProRes 4444 with alpha, or H.264 High for opaque clips."""
    os.makedirs(os.path.dirname(out), exist_ok=True)
    if alpha:
        codec = ["-c:v", "prores_ks", "-profile:v", "4", "-pix_fmt", "yuva444p10le", "-alpha_bits", "16", "-vendor", "apl0"]
    else:
        codec = ["-c:v", "libx264", "-profile:v", "high", "-preset", "slow", "-crf", "14", "-pix_fmt", "yuv420p",
                 "-tune", "animation", "-movflags", "+faststart"]
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", "%dx%d" % (w, h), "-r", str(FPS),
           "-i", "-"] + codec + ["-r", str(FPS), "-metadata", "comment=ClimbUK brand template", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n = 0
    for f in frames:
        p.stdin.write(f.tobytes())
        n += 1
    p.stdin.close()
    if p.wait():
        raise SystemExit("ffmpeg failed for %s" % out)
    print("  %s (%d frames, %.1f MB)" % (os.path.relpath(out, B.OUT), n, os.path.getsize(out) / 1e6))


def still(im, out):
    """Transparent stills as PNG; opaque ones (no alpha left) as JPG at quality 92."""
    os.makedirs(os.path.dirname(out), exist_ok=True)
    if im.mode == "RGBA" and im.getchannel("A").getextrema()[0] == 255:
        im = im.convert("RGB")
    if im.mode == "RGB":
        im.save(os.path.splitext(out)[0] + ".jpg", quality=92, optimize=True, progressive=True)
    else:
        im.save(out, optimize=True)


# ---------- lower thirds ----------

SAFE_X, SAFE_BOTTOM = 192, 2052   # 5% title safe at 4K


def lt_classic_specs(name=None, role=None, plate=False):
    """guidelines/video.md lower third: Dark Brown bar at 85%, 12px Climb Orange rule on the left (6px at HD)."""
    bx, by, bw, bh = SAFE_X, 1640, 1720, 300
    name = C.html(words().one("lower-third.name").text) if name is None else name
    role = C.html(words().one("lower-third.role").text) if role is None else role
    specs = {
        "bar": '<div style="position:absolute;left:%dpx;top:%dpx;width:%dpx;height:%dpx;background:rgba(30,15,5,.85)"></div>'
               % (bx, by, bw, bh),
        "rule": '<div style="position:absolute;left:%dpx;top:%dpx;width:12px;height:%dpx;background:#E8712A"></div>' % (bx, by, bh),
    }
    if not plate:
        specs["name"] = ('<div class="body" style="position:absolute;left:%dpx;top:%dpx;font-family:Montserrat;font-weight:700;'
                         'font-size:104px;color:#fff;line-height:1;white-space:nowrap">%s</div>' % (bx + 72, by + 54, name))
        specs["role"] = ('<div class="body" style="position:absolute;left:%dpx;top:%dpx;font-size:60px;color:#E9E9E9;'
                         'line-height:1;white-space:nowrap">%s</div>' % (bx + 74, by + 184, role))
    return specs


def lt_pill_specs(b, first=None, last=None, role=None, plate=False):
    """Festival kit lower third v2: Dark Brown panel, huge name with the orange pill bar, edition mark, slab corner."""
    px, py, pw, ph = SAFE_X, 1420, 2000, 560
    first = C.html(words(b).one("lower-third.first").text) if first is None else first
    last = C.html(words(b).one("lower-third.last").text) if last is None else last
    role = C.html(words(b).one("lower-third.role").text) if role is None else role
    mark = B.logo(b, "reversed-dark", 1024)
    specs = {
        "panel": ('<div style="position:absolute;left:%dpx;top:%dpx;width:%dpx;height:%dpx;background:#1E0F05;'
                  'clip-path:polygon(0 0,100%% 0,100%% 100%%,0 100%%)"></div>' % (px, py, pw, ph)),
        "slab": ('<svg style="position:absolute;left:%dpx;top:%dpx" width="420" height="44"><polygon points="0,0 420,0 371,44 0,44" '
                 'fill="#E8712A"/></svg>' % (px, py + ph)),
        "mark": '<img src="file://%s" style="position:absolute;left:%dpx;top:%dpx;height:58px">' % (mark, px + pw - 470, py + 52),
    }
    if not plate:
        specs["pill"] = ('<div style="position:absolute;left:%dpx;top:%dpx;width:520px;height:30px;border-radius:15px;'
                         'background:#E8712A"></div>' % (px + 90, py + 182))
        specs["name"] = ('<div class="disp black" style="position:absolute;left:%dpx;top:%dpx;font-size:132px;line-height:.98">'
                         '%s<br>%s</div>' % (px + 90, py + 70, first, last))
        specs["role"] = ('<div class="body" style="position:absolute;left:%dpx;top:%dpx;font-size:58px;font-weight:600;'
                         'color:#F2AE86;line-height:1;white-space:nowrap">%s</div>' % (px + 92, py + 420, role))
    return specs


def animate_lt(layers, order, total=6.0, wipe=("bar", "panel"), out_at=None):
    n = int(total * FPS)
    out_at = out_at or n - 6
    for f in range(n):
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        exit_p = EXIT(prog(f, out_at, 240))
        for k, name in enumerate(order):
            L = layers[name]
            if name in wipe:
                p = RISE(prog(f, 0, 400))
                place(im, L, clip_w=p if p > 0 else 0.001, alpha=(1 - exit_p) if p > 0 else 0, dy=32 * exit_p)
            elif name in ("rule", "slab"):
                p = RISE(prog(f, 2, 400))
                place(im, L, dy=32 * (1 - p) + 32 * exit_p, alpha=p * (1 - exit_p))
            else:
                start = 4 + k * 1.5  # 60ms stagger
                p = RISE(prog(f, start, 700))
                place(im, L, dy=32 * (1 - p) + 32 * exit_p, alpha=p * (1 - exit_p))
        yield im


def full_still(layers, order):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for n in order:
        place(im, layers[n])
    return im


# ---------- shared clips ----------

def shared():
    d = os.path.join(VOUT, "_shared")
    print("shared")
    # Classic lower third, sample and plate.
    L = render_layers({"ltc_" + k: v for k, v in lt_classic_specs().items()})
    L = {k[4:]: v for k, v in L.items()}
    encode(animate_lt(L, ["bar", "rule", "name", "role"]), os.path.join(d, "motion", "LowerThird_Classic_4K25.mov"))
    still(full_still(L, ["bar", "rule", "name", "role"]), os.path.join(d, "stills", "LowerThird_Classic_4K.png"))
    P = {k: L[k] for k in ("bar", "rule")}
    encode(animate_lt(P, ["bar", "rule"]), os.path.join(d, "motion", "LowerThird_Classic_Plate_4K25.mov"))
    still(full_still(P, ["bar", "rule"]), os.path.join(d, "stills", "LowerThird_Classic_Plate_4K.png"))

    # Stickers: Climb Orange tag tilted -4 degrees, White Montserrat Black (large text), spring pop.
    for word in [C.html(st.text) for st in words().all("sticker")]:
        key = word.replace(" ", "")
        S = render_layers({"st_" + key: '<div class="disp black" style="position:absolute;left:360px;top:300px;'
                           'transform:rotate(-4deg);transform-origin:left top;background:#E8712A;color:#fff;font-size:96px;'
                           'padding:26px 48px 22px;border-radius:14px;box-shadow:0 18px 60px rgba(232,113,42,.45)">%s</div>'
                           % word})
        layer = S["st_" + key]
        origin = (layer.x + layer.im.width / 2, layer.y + layer.im.height / 2)

        def frames(layer=layer, origin=origin):
            n = 3 * FPS
            for f in range(n):
                im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                p = prog(f, 0, 400)
                s = 0.6 + 0.4 * SPRING(p)
                out = EXIT(prog(f, n - 4, 160))
                place(im, layer, scale=s, alpha=min(1, p * 3) * (1 - out), origin=origin)
                yield im
        encode(frames(), os.path.join(d, "motion", "Sticker_%s_4K25.mov" % key))
        still(full_still({"s": layer}, ["s"]), os.path.join(d, "stills", "Sticker_%s_4K.png" % key))

    # Slab wipe: a Climb Orange slab with a Dark Brown slab behind it, cut at the chevron angle. Cut under it at frame 12.
    def wipe_frames(w=W, h=H):
        n = 25
        run = h / M.CHEVRON_SLOPE
        for f in range(n):
            im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            from PIL import ImageDraw
            dr = ImageDraw.Draw(im)
            for lag, colour in ((2.5, (30, 15, 5, 255)), (0, (232, 113, 42, 255))):
                p_in = RISE(prog(f - lag, 0, 440))
                p_out = EXIT(prog(f - lag, 12, 440))
                lead = -run + (w + run) * p_in
                tail = -run + (w + 2 * run) * p_out
                if lead <= tail:
                    continue
                pts = [(tail, h), (tail + run, 0), (lead + run, 0), (lead, h)]
                dr.polygon(pts, fill=colour)
            yield im
    encode(wipe_frames(), os.path.join(d, "motion", "Transition_SlabWipe_4K25.mov"))
    encode(wipe_frames(2160, 3840), os.path.join(d, "motion", "Transition_SlabWipe_Vertical_4K25.mov"), w=2160, h=3840)

    # Background loops (8 s, seamless): stage light glow drifting on a sine; for titles and holding screens.
    for orient, (w, h) in (("16x9", (W, H)), ("9x16", (2160, 3840))):
        base = render_ground("loopbase_" + orient, art.svg(w, h, M.contours(w, h, seed=5, rings=12, dark=True, marker=True,
                             cx=0.88, cy=0.92) + M.grain(w, h, seed=3, opacity=0.05)), w, h)
        glow = render_layers({"loopglow_" + orient: art.svg(w, h, M.stage_light(w, h, seed=4, beams=3, uid="lg"))}, w, h)
        g = glow["loopglow_" + orient]

        def loop(base=base, g=g, w=w, h=h):
            n = 8 * FPS
            for f in range(n):
                t = f / n * 2 * math.pi
                im = base.copy()
                place(im, g, dx=math.sin(t) * w * 0.02, dy=0, alpha=0.82 + 0.18 * math.sin(t * 2))
                yield im
        encode(loop(), os.path.join(d, "motion", "Background_StageLight_Loop_%s_4K25.mp4" % orient), alpha=False, w=w, h=h)
        still(base, os.path.join(d, "stills", "Background_Contours_%s_4K.png" % orient))

    # Safe areas and caption reference.
    sa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    from PIL import ImageDraw
    dr = ImageDraw.Draw(sa)
    for inset, colour in ((0.05, (232, 113, 42, 255)), (0.10, (242, 174, 134, 200))):
        dr.rectangle([W * inset, H * inset, W * (1 - inset), H * (1 - inset)], outline=colour, width=6)
    still(sa, os.path.join(d, "stills", "Guide_SafeAreas_16x9_4K.png"))
    cap = render_layers({"caption": '<div class="body" style="position:absolute;left:50%%;transform:translateX(-50%%);'
                         'bottom:%dpx;background:rgba(30,15,5,.7);color:#fff;font-weight:600;font-size:84px;line-height:1.3;'
                         'padding:18px 36px;text-align:center;max-width:2900px">%s</div>'
                         % (H - SAFE_BOTTOM + 40, C.html(words().one("captions.guide").text))})
    still(full_still(cap, ["caption"]), os.path.join(d, "stills", "Guide_Captions_16x9_4K.png"))


# ---------- brand clips ----------

def bug(b):
    """Reversed monogram at 60% opacity, top right, 160px on a 4K frame (guidelines/video.md)."""
    d = os.path.join(VOUT, b)
    bug = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    mono = Image.open(B.logo(b, "icon-monogram-on-ground", 512)).convert("RGBA").resize((160, 160), Image.LANCZOS)
    mono.putalpha(mono.getchannel("A").point(lambda v: int(v * 0.6)))
    bug.alpha_composite(mono, (W - 192 - 160, 108))
    still(bug, os.path.join(d, "stills", "%s_Bug_4K.png" % b))


def per_brand(b):
    info = B.BRANDS[b]
    d = os.path.join(VOUT, b)
    print(b)
    # Pill lower third with the edition mark.
    L = render_layers({"%s_ltp_%s" % (b, k): v for k, v in lt_pill_specs(b).items()})
    L = {k.split("_ltp_")[1]: v for k, v in L.items()}
    order = ["panel", "slab", "mark", "pill", "name", "role"]
    encode(animate_lt(L, order, total=6.0), os.path.join(d, "motion", "%s_LowerThird_Festival_4K25.mov" % b))
    still(full_still(L, order), os.path.join(d, "stills", "%s_LowerThird_Festival_4K.png" % b))
    P = {k: L[k] for k in ("panel", "slab", "mark")}
    encode(animate_lt(P, ["panel", "slab", "mark"]), os.path.join(d, "motion", "%s_LowerThird_Festival_Plate_4K25.mov" % b))
    still(full_still(P, ["panel", "slab", "mark"]), os.path.join(d, "stills", "%s_LowerThird_Festival_Plate_4K.png" % b))

    bug(b)

    # End card and logo sting, 16:9 and 9:16: lockup rises, line and URL follow with the 60ms stagger, hold 5 s.
    for orient, (w, h) in (("16x9", (W, H)), ("9x16", (2160, 3840))):
        ground = render_ground("%s_endbg_%s" % (b, orient), art.svg(w, h,
                               M.stage_light(w, h, seed=12, beams=4, uid="e") +
                               art.glow(w * 0.5, h * 0.5, w * 0.45, h * 0.35, opacity=0.18, uid="e2") +
                               M.peak(w, h, x0=0.0, base=0.95, summit=(0.5, 0.78), seed=5, colour="#E8712A", opacity=0.45) +
                               M.grain(w, h, seed=7, opacity=0.05)), w, h)
        lw = int(w * (0.5 if orient == "16x9" else 0.78))
        lk = B.logo(b, "tagline-lockup-reversed", 2048)
        ly = int(h * (0.3 if orient == "16x9" else 0.36))
        line = info["edition"] or C.html(words(b).one("end-card.line").text)
        fs = int(w * (0.026 if orient == "16x9" else 0.045))
        Ls = render_layers({
            "%s_end_logo_%s" % (b, orient): '<img src="file://%s" style="position:absolute;left:%dpx;top:%dpx;width:%dpx">'
                                            % (lk, (w - lw) // 2, ly, lw),
            "%s_end_line_%s" % (b, orient): '<div class="disp" style="position:absolute;left:0;width:%dpx;text-align:center;'
                                            'top:%dpx;font-size:%dpx">%s</div>' % (w, int(h * (0.62 if orient == "16x9" else 0.58)), fs, line),
            "%s_end_url_%s" % (b, orient): '<div class="disp" style="position:absolute;left:50%%;transform:translateX(-50%%);'
                                           'top:%dpx;font-size:%dpx;background:#E8712A;color:#fff;padding:%dpx %dpx;'
                                           'border-radius:%dpx;box-shadow:0 20px 80px rgba(232,113,42,.5)">%s</div>'
                                           % (int(h * (0.72 if orient == "16x9" else 0.66)), int(fs * 0.8), fs // 2, fs, fs, info["url"]),
        }, w, h)
        seq = [Ls["%s_end_%s_%s" % (b, k, orient)] for k in ("logo", "line", "url")]

        def sting(ground=ground, seq=seq):
            n = 8 * FPS
            for f in range(n):
                im = ground.copy()
                for k, L in enumerate(seq):
                    p = RISE(prog(f, 6 + k * 1.5 if k else 0, 700))
                    place(im, L, dy=96 * (1 - p), alpha=p)
                yield im
        encode(sting(), os.path.join(d, "motion", "%s_EndCard_Sting_%s_4K25.mp4" % (b, orient)), alpha=False, w=w, h=h)
        last = ground.copy()
        for L in seq:
            place(last, L)
        still(last.convert("RGB"), os.path.join(d, "stills", "%s_EndCard_%s_4K.png" % (b, orient)))

    # Title card sample (opaque): headline lines rise in one at a time over the loop ground.
    titles = [C.html(t.text) for t in words(b).all("title-card.line")]
    ground = Image.open(os.path.join(TMP, "loopbase_16x9.png")).convert("RGBA")
    TL = render_layers({"%s_title_%d" % (b, i): '<div class="disp black" style="position:absolute;left:%dpx;top:%dpx;'
                        'font-size:260px">%s</div>' % (SAFE_X + 60, 700 + i * 270, t) for i, t in enumerate(titles)})
    TL["rule"] = render_layers({"%s_title_rule" % b: '<div style="position:absolute;left:%dpx;top:600px;width:256px;height:24px;'
                                'border-radius:12px;background:#E8712A"></div>' % (SAFE_X + 64)})["%s_title_rule" % b]
    lines = [TL["rule"]] + [TL["%s_title_%d" % (b, i)] for i in range(len(titles))]

    def title_frames():
        n = 5 * FPS
        for f in range(n):
            im = ground.copy()
            for k, L in enumerate(lines):
                p = RISE(prog(f, 3 + k * 4, 700))
                place(im, L, dy=96 * (1 - p), alpha=p)
            yield im
    encode(title_frames(), os.path.join(d, "motion", "%s_TitleCard_4K25.mp4" % b), alpha=False)
    last = ground.copy()
    for L in lines:
        place(last, L)
    still(last.convert("RGB"), os.path.join(d, "stills", "%s_TitleCard_4K.png" % b))


def main():
    args = sys.argv[1:]
    if not args or "shared" in args:
        shared()
    for b in [a for a in args if a in B.BRANDS] or (list(B.BRANDS) if not args else []):
        per_brand(b)


if __name__ == "__main__":
    main()
