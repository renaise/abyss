#!/usr/bin/env python3
"""ABYSS demo cut: a simple ffmpeg/PIL edit that adds the slow Z roll (the Z roll is applied here in compositing).
Run from anywhere: python3 tools/film.py  (~1 min). Needs Pillow, NumPy and ffmpeg/ffprobe on PATH.
Inputs (relative to the repo root): examples/abyss_spin_netsuke.mp4 (falls back to examples/abyss_tumble.mp4),
examples/abyss_tumble.mp4, examples/specimen_hippo.png, inputs/netsuke.png, inputs/hippo.png.
Scratch files go to build/ (git-ignored). Output: examples/abyss_demo.mp4 (overwritten).
Font: Inter variable font; set ABYSS_FONT to its .ttf path if it is not at the default location below."""
import os, subprocess, math, wave, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1920, 1080, 30
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); OUT = ROOT + '/examples'; BLD = ROOT + '/build'
os.makedirs(BLD, exist_ok=True)
INTER = os.environ.get('ABYSS_FONT', '/usr/share/fonts/truetype/google/Inter/Inter-VariableFont_opsz,wght.ttf')
def font(sz, wght):
    f = ImageFont.truetype(INTER, sz)
    try: f.set_variation_by_axes([14 if sz < 32 else 32, wght])
    except Exception: pass
    return f

CLIP = OUT + '/abyss_spin_netsuke.mp4'
if not os.path.exists(CLIP): CLIP = OUT + '/abyss_tumble.mp4'
o = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height,r_frame_rate', '-of', 'csv=p=0', CLIP],
                   capture_output=True, text=True).stdout.strip().split(',')
cw, ch = int(o[0]), int(o[1]); n_, d_ = o[2].split('/'); cfps = float(n_) / float(d_)
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', CLIP, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
FR = np.frombuffer(raw, np.uint8).reshape(-1, ch, cw, 3); CDUR = len(FR) / cfps
HIP = Image.open(OUT + '/specimen_hippo.png').convert('RGB')
P_NET = Image.open(ROOT + '/inputs/netsuke.png').convert('RGB')
P_HIP = Image.open(ROOT + '/inputs/hippo.png').convert('RGB')

# timeline (s)
S = [('photo', 0.0, 1.2, P_NET), ('net', 1.2, 6.2, 0.0), ('photo', 6.2, 7.0, P_HIP), ('hip', 7.0, 11.0, None),
     ('net', 11.0, 12.8, 2.6), ('title', 12.8, 15.0, None)]
TOTAL = S[-1][2]; NF = int(round(TOTAL * FPS)); CUTS = [s[1] for s in S[1:]]
ROLL = 24.0  # deg/s

yy, xx = np.mgrid[0:H, 0:W]
r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
VIG = np.clip((1.25 - r) / 0.45, 0, 1)[..., None].astype(np.float32)   # soft falloff to pure black
SHARP = ImageFilter.UnsharpMask(radius=1.6, percent=55, threshold=2)

def cover(im, z):
    s = max(W / im.width, H / im.height) * z
    im2 = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x, y = (im2.width - W) // 2, (im2.height - H) // 2
    return im2.crop((x, y, x + W, y + H))

def place(im, scale, ang):
    im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS).filter(SHARP)
    im = im.rotate(ang, resample=Image.BICUBIC, expand=True, fillcolor=(0, 0, 0))
    c = Image.new('RGB', (W, H)); c.paste(im, ((W - im.width) // 2, (H - im.height) // 2))
    a = np.asarray(c, np.float32)
    a = np.clip((a - 6) * (255 / 249), 0, 255) * VIG     # crush the clip's near-black to pure black
    return Image.fromarray(a.astype(np.uint8))

def frame(f):
    t = f / FPS
    for kind, t0, t1, arg in S:
        if t0 <= t < t1: break
    lt, u = t - t0, (t - t0) / (t1 - t0)
    if kind == 'photo':
        return cover(arg, 1.0 + 0.06 * u)
    if kind == 'net':
        # light speed ramp: slow-fast-slow mapping over the segment
        span = min(CDUR - arg, (t1 - t0) * 0.95)
        src = arg + span * (u - 0.12 * math.sin(2 * math.pi * u) / (2 * math.pi) * 2)
        fr = Image.fromarray(FR[min(int(src * cfps), len(FR) - 1)])
        base = 1.62 if t0 < 5 else 1.72
        return place(fr, base * (1 + 0.05 * u), ROLL * (t - 1.2))
    if kind == 'hip':
        s = 960 / HIP.height * (1 + 0.06 * u) * (1 + 0.02 * math.sin(2 * math.pi * 0.5 * lt))
        return place(HIP, s, -ROLL * lt)
    # title
    img = Image.new('RGB', (W, H)); d = ImageDraw.Draw(img)
    a = min(1, max(0, (lt - 0.25) / 0.6)) * min(1, (t1 - t) / 0.4 + 0.0001)
    a = max(0, min(1, a))
    c1 = tuple(int(v * a) for v in (240, 238, 234)); c2 = tuple(int(v * a) for v in (150, 148, 144))
    d.text((W // 2, H // 2 - 14), 'A B Y S S', font=font(64, 300), fill=c1, anchor='mm')
    d.text((W // 2, H // 2 + 46), 'built in ComfyUI  ·  open weights', font=font(20, 400), fill=c2, anchor='mm')
    return img

def audio():
    sr = 48000; n = int(TOTAL * sr); t = np.arange(n) / sr
    a = 0.09 * (np.sin(2 * np.pi * 38 * t) + 0.5 * np.sin(2 * np.pi * 57 * t + np.sin(2 * np.pi * 0.1 * t)))
    a *= (0.75 + 0.25 * np.sin(2 * np.pi * 0.12 * t)) * np.clip(t / 0.8, 0, 1) * np.clip((TOTAL - t) / 1.5, 0, 1)
    rng = np.random.default_rng(3)
    for i, c in enumerate(CUTS):
        tt = np.arange(int(1.4 * sr)) / sr
        g = 0.75 if i in (0, 2) else (0.45 if c != S[-1][1] else 0.6)
        fq = 34 + 60 * np.exp(-tt * 9)
        hit = np.sin(2 * np.pi * np.cumsum(fq) / sr) * np.exp(-tt * 3.2)
        nz = np.convolve(rng.normal(0, 1, len(tt)), np.ones(200) / 200, 'same') * np.exp(-tt * 12) * 0.6
        s = g * (hit + nz); i0 = int(c * sr); j = min(n, i0 + len(s)); a[i0:j] += s[:j - i0]
    st = np.clip(np.stack([a, a], 1), -1, 1)
    with wave.open(BLD + '/film_synth.wav', 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes((st * 32767).astype(np.int16).tobytes())

if __name__ == '__main__':
    audio()
    vid = BLD + '/film_noaudio.mp4'
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p', vid], stdin=subprocess.PIPE)
    for f in range(NF): p.stdin.write(frame(f).tobytes())
    p.stdin.close(); p.wait()
    d1, d2, d3 = 1200, 7000, 11000
    fc = (f'[1:a]aresample=48000,atrim=0:5,afade=t=out:st=4.6:d=0.4,adelay={d1}|{d1}[x];'
          f'[2:a]aresample=48000,volume=0.8,atrim=0:4,afade=t=out:st=3.6:d=0.4,adelay={d2}|{d2}[y];'
          f'[1:a]aresample=48000,atrim=2.6:4.4,asetpts=PTS-STARTPTS,afade=t=out:st=1.4:d=0.4,adelay={d3}|{d3}[z];'
          f'[3:a][x][y][z]amix=inputs=4:normalize=0:duration=first,alimiter=limit=0.9[a]')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', vid, '-i', CLIP, '-i', OUT + '/abyss_tumble.mp4', '-i', BLD + '/film_synth.wav',
                    '-filter_complex', fc, '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
                    '-t', f'{TOTAL:.3f}', '-movflags', '+faststart', OUT + '/abyss_demo.mp4'], check=True)
    print('done', TOTAL, NF, CLIP)
