import React, { useEffect, useState } from "react";
import {
  AbsoluteFill,
  Audio,
  Composition,
  Img,
  OffthreadVideo,
  Sequence,
  continueRender,
  delayRender,
  interpolate,
  registerRoot,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
// Local OFL fonts: the same Anton / Montserrat families as the Hanta source.
const ANTON = { family: "Hanta Anton", weight: 400, style: "normal" } as const;
const M6 = { family: "Hanta Montserrat", weight: 600, style: "normal" } as const;
const M7 = { family: "Hanta Montserrat", weight: 700, style: "normal" } as const;
const M8 = { family: "Hanta Montserrat", weight: 800, style: "normal" } as const;
const MI5 = { family: "Hanta Montserrat", weight: 500, style: "italic" } as const;
const MI6 = { family: "Hanta Montserrat", weight: 600, style: "italic" } as const;
type F = { family: string; weight: number; style: "normal" | "italic" };
let fontPromise: Promise<void> | undefined;
const W = 1080;
const MAXW = 860; // bề rộng tối đa của từ khoá
const STRETCH = 1.245; // từ khoá Anton bị kéo giãn ngang
const GRAD = "linear-gradient(90deg,#FEDA3C 0%,#FCE56C 15%,#F9EA8B 30%,#F8ED96 50%,#F9EA8B 70%,#FCE56C 85%,#FEDA3C 100%)";
const PALE = "#F7ED92";
const GLOW = "#FF8C00";
const GOLD = "#F4E1A1";
const OFFWHITE = "#F8F8F0";
const PAPER = "#EEEADB";
const CLAMP = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const SHADOW = "0 2px 10px rgba(0,0,0,.55)";

type Cut = { start: number; end: number };
type MediaRef = { src: string; start?: number; label?: string; wide?: boolean; focus?: string };
type Item = any;
type Plan = {
  video: string;
  fps?: number;
  cuts: Cut[];
  zoom?: number;
  captions?: Item[];
  inserts?: Item[];
  music?: string;
  musicVolume?: number;
  sfx?: boolean;
  shade?: "soft" | "full";
};

// Mốc trong edit.json tính theo thời gian của video gốc; hàm này đổi sang thời gian sau khi cắt.
const toOut = (cuts: Cut[], t: number) => {
  let acc = 0;
  for (const c of cuts) {
    if (t < c.start) return acc;
    if (t <= c.end) return acc + (t - c.start);
    acc += c.end - c.start;
  }
  return acc;
};

const up = (s: string) => s.normalize("NFC").toLocaleUpperCase("vi");
const fade = (f: number, dur: number, a = 5, b = 5) =>
  Math.min(interpolate(f, [0, a], [0, 1], CLAMP), interpolate(f, [dur - b, dur], [1, 0], CLAMP));

// ---------- Đo chữ (chỉ gọi sau khi font đã tải xong) ----------
let g2d: CanvasRenderingContext2D | null = null;
const ctx = () => (g2d ??= document.createElement("canvas").getContext("2d")!);
const fstr = (f: F, size: number) => `${f.style} ${f.weight} ${size}px "${f.family}"`;
const metCache: Record<string, { asc: number; desc: number; cap: number }> = {};
const met = (f: F) => {
  const k = fstr(f, 1);
  if (!metCache[k]) {
    const c = ctx();
    c.font = fstr(f, 1000);
    const m = c.measureText("H");
    metCache[k] = { asc: m.fontBoundingBoxAscent / 1000, desc: m.fontBoundingBoxDescent / 1000, cap: m.actualBoundingBoxAscent / 1000 };
  }
  return metCache[k];
};
const tw = (text: string, f: F, size: number) => {
  const c = ctx();
  c.font = fstr(f, size);
  return c.measureText(text).width;
};

// Một dòng chữ đặt theo đường chân chữ (baseline) y, canh giữa trong vùng [left, left+width].
const Line: React.FC<{
  f: F;
  size: number;
  y: number;
  color?: string;
  left?: number;
  width?: number;
  align?: "center" | "left" | "right";
  style?: React.CSSProperties;
  children: React.ReactNode;
}> = ({ f, size, y, color = "#fff", left = 0, width = W, align = "center", style, children }) => {
  const m = met(f);
  const lh = (m.asc + m.desc) * size;
  return (
    <div
      style={{
        position: "absolute",
        left,
        width,
        top: y - m.asc * size,
        height: lh,
        lineHeight: `${lh}px`,
        textAlign: align,
        whiteSpace: "nowrap",
        fontFamily: `"${f.family}"`,
        fontWeight: f.weight,
        fontStyle: f.style,
        fontSize: size,
        color,
        ...style,
      }}
    >
      {children}
    </div>
  );
};

const GradText: React.FC<{ children: React.ReactNode; style?: React.CSSProperties }> = ({ children, style }) => (
  <span style={{ position: "relative", background: GRAD, WebkitBackgroundClip: "text", backgroundClip: "text", color: "transparent", ...style }}>
    {children}
  </span>
);

// ---------- Đốm sao lấp lánh quanh từ khoá lúc xuất hiện ----------
// [x theo bề rộng chữ, y theo chiều cao chữ hoa (0 = đỉnh), cỡ px, trễ khung hình]
const STARS: number[][] = [
  [-0.03, -0.12, 34, 2],
  [0.99, -0.2, 42, 3],
  [0.1, 0.34, 24, 4],
  [0.5, 0.46, 28, 5],
  [1.03, 0.64, 32, 6],
  [0.64, -0.24, 28, 7],
  [0.3, 1.06, 22, 8],
];
const STAR = "M0-1C.1-.1.1-.1 1 0C.1.1.1.1 0 1C-.1.1-.1.1-1 0C-.1-.1-.1-.1 0-1Z";
const Sparkles: React.FC<{ f: number; sx: number; capTop: number; capH: number }> = ({ f, sx, capTop, capH }) => (
  <>
    {STARS.map(([x, y, size, d], i) => {
      const p = (f - d) / 10;
      if (p <= 0 || p >= 1) return null;
      const s = Math.sin(Math.PI * p);
      return (
        <svg
          key={i}
          viewBox="-1 -1 2 2"
          style={{ position: "absolute", left: `${x * 100}%`, top: capTop + y * capH, width: size, height: size, marginLeft: -size / 2, marginTop: -size / 2, overflow: "visible", transform: `scale(${s / sx},${s}) rotate(${(p - 0.5) * 40}deg)`, filter: "drop-shadow(0 0 6px rgba(255,238,160,.95))" }}
        >
          <path d={STAR} fill="#fff" />
        </svg>
      );
    })}
  </>
);

// ---------- Từ khoá vàng: Anton kéo giãn, màu chuyển, quầng sáng cam, bật vọt rồi co về ----------
// inkTop: toạ độ đỉnh phần mực (kể cả dấu). Mẫu neo từ khoá theo đỉnh mực nên chữ không dấu nằm cao hơn chữ có dấu.
const kwGeom = (text: string, size: number, inkTop: number, fill = false) => {
  let fs = size;
  // fill: giãn hết bề rộng (tên thương hiệu, nhãn dưới cửa sổ nổi), tối đa 1,9 lần như mẫu.
  let sx = fill ? Math.min(1.9, (MAXW + 8) / tw(text, ANTON, fs)) : Math.min(STRETCH, MAXW / tw(text, ANTON, fs));
  if (!fill && sx < 0.92) {
    fs = (size * sx) / 0.92;
    sx = 0.92;
  }
  const c = ctx();
  c.font = fstr(ANTON, fs);
  const mt = c.measureText(text);
  const base = inkTop + mt.actualBoundingBoxAscent;
  return { fs, sx, base, inkBottom: base + mt.actualBoundingBoxDescent };
};
type Geom = ReturnType<typeof kwGeom>;

const Keyword: React.FC<{ text: string; g: Geom; f: number; sparkle?: boolean; glow?: boolean }> = ({ text, g, f, sparkle = true, glow = true }) => {
  if (f < 0) return null;
  const m = met(ANTON);
  const { fs, sx, base: y } = g;
  const pop = interpolate(f, [0, 5, 6, 17], [0.83, 1.12, 1.134, 1], CLAMP);
  const blur = interpolate(f, [0, 3], [10, 0], CLAMP);
  const flash = interpolate(f, [1, 5, 16], [0, 1, 0], CLAMP);
  const lh = (m.asc + m.desc) * fs;
  return (
    <div style={{ position: "absolute", left: 0, width: W, top: y - m.asc * fs, height: lh, lineHeight: `${lh}px`, textAlign: "center", whiteSpace: "nowrap", fontFamily: `"${ANTON.family}"`, fontSize: fs, opacity: interpolate(f, [0, 3], [0, 1], CLAMP) }}>
      <span style={{ display: "inline-block", position: "relative", transform: `scale(${sx * pop},${pop})`, transformOrigin: `50% ${(m.asc - m.cap / 2) * fs}px` }}>
        {glow && <span style={{ position: "absolute", inset: 0, color: GLOW, filter: `blur(${15 + 9 * flash}px)`, opacity: 0.69 + 0.1 * flash }}>{text}</span>}
        {glow && <span style={{ position: "absolute", inset: 0, color: "#000", filter: "blur(6px)", opacity: 0.6 }}>{text}</span>}
        {glow && flash > 0 && <span style={{ position: "absolute", inset: 0, color: "#FFE58A", filter: "blur(4px)", opacity: 0.3 * flash }}>{text}</span>}
        <GradText style={{ filter: blur > 0 ? `blur(${blur}px)` : undefined }}>{text}</GradText>
        {sparkle && <Sparkles f={f} sx={sx} capTop={(m.asc - m.cap) * fs} capH={m.cap * fs} />}
      </span>
    </div>
  );
};

const Small: React.FC<{ text: string; y: number; size?: number; opacity?: number; upper?: boolean }> = ({ text, y, size = 57, opacity = 1, upper }) => {
  const t = upper ? up(text) : text;
  const fs = Math.min(size, (940 / tw(t, MI6, size)) * size);
  return (
    <Line f={MI6} size={fs} y={y} style={{ opacity, textShadow: SHADOW, letterSpacing: upper ? "0.02em" : undefined }}>
      {t}
    </Line>
  );
};

const Hero: React.FC<{ c: Item; dur: number; pip: boolean }> = ({ c, dur, pip }) => {
  const f = useCurrentFrame();
  const out = interpolate(f, [dur - 4, dur], [1, 0], CLAMP);
  const text = c.raw ? c.main : up(c.main);
  // Dưới cửa sổ nổi, từ khoá thành nhãn giãn hết bề rộng.
  if (pip) {
    return (
      <AbsoluteFill style={{ opacity: out }}>
        <Keyword text={text} g={kwGeom(text, 86, 1473, true)} f={f} sparkle={false} />
      </AbsoluteFill>
    );
  }
  const bottoms: string[] = [].concat(c.bottom ?? []);
  const list = bottoms.length > 1; // kiểu phủ định: từ khoá nhỏ phía trên, các dòng liệt kê bên dưới
  const big = c.size === "lg" || c.size === "xl";
  const size = c.size === "xl" ? 170 : c.size === "lg" ? 136 : c.size === "sm" || list ? 102 : 112;
  const g = kwGeom(text, size, list ? 1054.5 : big ? 1117.5 : 1129.5);
  const topY = big ? 1082 : 1094;
  // Dòng dưới cách đáy mực của từ khoá ít nhất 20px (chữ có dấu nặng đẩy dòng dưới xuống).
  const botY = Math.max(big ? 1326 : 1314, g.inkBottom + 20 + 0.7 * 55.5);
  const inOp = (a: number) => interpolate(f, [a, a + 3], [0, 1], CLAMP);
  return (
    <AbsoluteFill style={{ opacity: out }}>
      {c.number != null && (
        <Line f={ANTON} size={660} y={1533} color="rgba(255,255,255,.325)" style={{ transform: "scaleX(1.22)", opacity: inOp(0) }}>
          {c.number}
        </Line>
      )}
      {c.top && !list && <Small text={c.top} y={topY} size={58} opacity={inOp(0)} />}
      <Keyword text={text} g={g} f={f - 1} />
      {list
        ? bottoms.map((b, i) => <Small key={i} text={b} y={i ? 1334 + (i - 1) * 81 : 1253} size={i ? 58 : 73} opacity={inOp(8 + i * 14)} />)
        : bottoms.map((b, i) => <Small key={i} text={b} y={botY} size={55.5} opacity={inOp(4)} />)}
    </AbsoluteFill>
  );
};

// ---------- Phụ đề hai dòng gõ từng ký tự có con trỏ ----------
const RATE = 0.77; // ký tự mỗi khung hình ở 30 fps
const TypeLine: React.FC<{ text: string; typed: number; y: number; color: string }> = ({ text, typed, y, color }) => {
  const chars = Array.from(text);
  return (
    <Line f={M7} size={48.6} y={y} color={color} style={{ textShadow: SHADOW }}>
      <span>{chars.slice(0, typed).join("")}</span>
      {typed > 0 && typed < chars.length && (
        <span style={{ display: "inline-block", width: 0, height: 0, position: "relative" }}>
          <span style={{ position: "absolute", left: 4, bottom: "-0.16em", width: 3, height: "0.98em", background: color }} />
        </span>
      )}
      <span style={{ opacity: 0 }}>{chars.slice(typed).join("")}</span>
    </Line>
  );
};

const Sub: React.FC<{ c: Item; dur: number; pip: boolean }> = ({ c, dur, pip }) => {
  const f = useCurrentFrame();
  const l1 = (c.line1 ?? "").normalize("NFC");
  const l2 = (c.line2 ?? "").normalize("NFC");
  const n1 = Array.from(l1).length;
  const n2 = Array.from(l2).length;
  const typed1 = Math.min(n1, Math.floor(f * RATE) + 1);
  const typed2 = Math.max(0, Math.min(n2, Math.floor((f - (n1 - 3) / RATE) * RATE) + 1));
  const shift = pip ? 318 : 0;
  return (
    <AbsoluteFill style={{ opacity: interpolate(f, [dur - 4, dur], [1, 0], CLAMP) }}>
      <TypeLine text={l1} typed={typed1} y={(l2 ? 1173.5 : 1207) + shift} color="#fff" />
      {l2 && <TypeLine text={l2} typed={typed2} y={1239.5 + shift} color={PALE} />}
    </AbsoluteFill>
  );
};

const Cta: React.FC<{ c: Item; dur: number }> = ({ c, dur }) => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ opacity: fade(f, dur, 1, 1) }}>
      {c.top && <Small text={c.top} y={1107} size={59} upper opacity={interpolate(f, [0, 3], [0, 1], CLAMP)} />}
      <Keyword text={up(c.main)} g={kwGeom(up(c.main), 112, 1129.5)} f={f - 1} />
      <svg width="398" height="220" viewBox="0 0 398 220" style={{ position: "absolute", left: 341, top: 1308, opacity: interpolate(f, [7, 9], [0, 1], CLAMP) }}>
        <polyline points="36,20 199,166 362,20" fill="none" stroke="#FE5130" strokeWidth="54" strokeMiterlimit="10" />
      </svg>
    </AbsoluteFill>
  );
};

// Tên sản phẩm/chương trình: các dòng giãn đều hết bề rộng, thanh vàng nhạt phía dưới.
const Brand: React.FC<{ c: Item; dur: number }> = ({ c, dur }) => {
  const f = useCurrentFrame();
  const lines: string[] = [].concat(c.lines).map(up);
  const first = 1084.5 - (lines.length - 2) * 139.5;
  const geoms: Geom[] = [];
  let last = first - 25.5;
  let inkBottom = -1e9;
  for (const l of lines) {
    const g = kwGeom(l, 133, Math.max(last + 25.5, inkBottom + 16), true);
    geoms.push(g);
    last = g.base;
    inkBottom = g.inkBottom;
  }
  const bar = interpolate(f, [8, 14], [0, 1], CLAMP);
  return (
    <AbsoluteFill style={{ opacity: interpolate(f, [dur - 4, dur], [1, 0], CLAMP) }}>
      {c.top && <Small text={c.top} y={first - 49} size={59} opacity={interpolate(f, [0, 3], [0, 1], CLAMP)} />}
      {lines.map((l, i) => (
        <Keyword key={i} text={l} g={geoms[i]} f={f - 1 - i * 3} sparkle={i === 0} />
      ))}
      {c.bar && (
        <div style={{ position: "absolute", left: 96, top: Math.max(last + 27, inkBottom + 16), width: 888, height: 72, background: PALE, transform: `scaleX(${bar})`, overflow: "hidden" }}>
          <Line f={MI6} size={48} y={52} color="#111" width={888} style={{ letterSpacing: "0.07em", opacity: interpolate(f, [12, 16], [0, 1], CLAMP) }}>
            {c.bar}
          </Line>
        </div>
      )}
    </AbsoluteFill>
  );
};

// ---------- Tư liệu chèn ----------
const Media: React.FC<{ m: MediaRef; style?: React.CSSProperties }> = ({ m, style }) => {
  const { fps } = useVideoConfig();
  const s: React.CSSProperties = { width: "100%", height: "100%", objectFit: "cover", objectPosition: m.focus, display: "block", ...style };
  return /\.(mp4|mov|m4v|webm)$/i.test(m.src) ? (
    <OffthreadVideo src={staticFile(m.src)} muted startFrom={Math.round((m.start ?? 0) * fps)} style={s} />
  ) : (
    <Img src={staticFile(m.src)} style={s} />
  );
};
const asMedia = (m: any): MediaRef => (typeof m === "string" ? { src: m } : m);

const Frame: React.FC<{ m: MediaRef; x: number; y: number; w: number; h: number; r?: number; delay?: number; border?: string; rotate?: number; shadow?: string }> = ({
  m,
  x,
  y,
  w,
  h,
  r = 24,
  delay = 0,
  border = "1.5px solid rgba(211,209,201,.8)",
  rotate = 0,
  shadow = "0 24px 60px rgba(0,0,0,.45)",
}) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({ frame: f - delay, fps, config: { damping: 16, stiffness: 160 } });
  return (
    <div style={{ position: "absolute", left: x, top: y, width: w, height: h, borderRadius: r, overflow: "hidden", border, boxShadow: shadow, opacity: s, transform: `translateY(${(1 - s) * 40}px) rotate(${rotate}deg)` }}>
      <Media m={m} />
    </div>
  );
};

// ---------- Thẻ tối toàn màn hình ----------
const DARK_BG =
  "radial-gradient(90% 55% at 100% 64%, rgba(74,58,34,.5), rgba(74,58,34,0) 70%), radial-gradient(80% 45% at 0% 0%, rgba(30,32,50,.75), rgba(30,32,50,0) 70%), #0C0E12";
const titleSize = (lines: string[]) => {
  const longest = Math.max(...lines.map((l) => tw(l, ANTON, 100)));
  return Math.max(92, Math.min(145, (480 / longest) * 100));
};

const Card: React.FC<{ c: Item; dur: number; rel: (t: number) => number }> = ({ c, dur, rel }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const title: string[] = [].concat(c.title).map(up);
  const size = titleSize(title);
  const cap = 0.859 * size;
  // Dấu tiếng Việt cao/thấp hơn chữ hoa: xếp dòng theo phần mực thật để các dòng và nhãn phía trên không dính nhau.
  const ink = title.map((t) => {
    const k = ctx();
    k.font = fstr(ANTON, size);
    const mt = k.measureText(t);
    return { a: mt.actualBoundingBoxAscent, d: mt.actualBoundingBoxDescent };
  });
  const bases: number[] = [];
  title.forEach((_, i) => {
    bases.push(i === 0 ? Math.max((title.length > 1 ? 342 : 365) + cap, 324 + ink[0].a) : Math.max(bases[i - 1] + 1.156 * size, bases[i - 1] + ink[i - 1].d + 0.11 * size + ink[i].a));
  });
  const lastBase = bases[bases.length - 1];
  const items: Item[] = c.items ?? [];
  const step = Math.min(24, (dur * 0.6) / Math.max(1, items.length));
  const at = (it: Item, i: number) => (it.at != null ? rel(it.at) : 12 + i * step);
  const app = (it: Item, i: number) => spring({ frame: f - at(it, i), fps, config: { damping: 15, stiffness: 170 } });
  const rise = (s: number): React.CSSProperties => ({ opacity: s, transform: `translateY(${(1 - s) * 36}px)` });
  const layout = c.layout ?? "rows";
  const media = c.media ? asMedia(c.media) : null;
  const top0 = lastBase + 95;
  const no = (i: number) => String(i + 1).padStart(2, "0");
  return (
    <AbsoluteFill style={{ background: DARK_BG, opacity: fade(f, dur, 6, 6), overflow: "hidden" }}>
      {c.ghost && (
        <Line f={ANTON} size={216} y={300} color="#1B1D23">
          {up(c.ghost)}
        </Line>
      )}
      {(c.tag || c.ghost) && <div style={{ position: "absolute", left: 85, top: 291, width: 85, height: 3, background: "rgba(243,225,161,.6)" }} />}
      {c.tag && (
        <Line f={M6} size={23} y={303} color="#B6B8BD" align="right" width={W - 87} style={{ letterSpacing: "0.03em" }}>
          {up(c.tag)}
        </Line>
      )}
      {c.top && (
        <Line f={MI5} size={38} y={bases[0] - Math.max(cap + 62, ink[0].a + 36)} style={{ letterSpacing: "0.02em" }}>
          {up(c.top)}
        </Line>
      )}
      <div style={{ transform: `translateY(${interpolate(f, [0, 10], [36, 0], CLAMP)}px)` }}>
        {title.map((t, i) => (
          <Line key={i} f={ANTON} size={size} y={bases[i]} color={title.length > 1 && i === title.length - 1 ? GOLD : OFFWHITE}>
            {t}
          </Line>
        ))}
      </div>

      {layout === "rows" && !media && items.length <= 4 &&
        items.map((it, i) => {
          const y = top0 + 16 + i * 273;
          return (
            <div key={i} style={{ position: "absolute", left: 107, top: y, width: 866, height: 228, borderRadius: 20, background: "#1D201F", border: "1.5px solid rgba(160,158,128,.55)", ...rise(app(it, i)) }}>
              <Line f={ANTON} size={72} y={it.note ? 140 : 152} left={55} width={130} align="left">
                <GradText>{no(i)}</GradText>
              </Line>
              <Line f={ANTON} size={85} y={it.note ? 122 : 150} left={120} width={746}>
                <GradText>{up(it.label)}</GradText>
              </Line>
              {it.note && (
                <Line f={MI5} size={33} y={188} left={120} width={746}>
                  {it.note}
                </Line>
              )}
            </div>
          );
        })}

      {/* Hàng kẻ mảnh: dùng khi có ảnh phía trên, hoặc khi có từ 5 mục (ô viền không đủ chỗ). */}
      {layout === "rows" && (media || items.length > 4) && (
        <>
          {media && <Frame m={media} x={96} y={top0} w={888} h={498} r={26} delay={6} />}
          {items.map((it, i) => {
            const y0 = top0 + (media ? 498 + 132 : 112);
            const pitch = Math.min(168, (1760 - y0) / Math.max(1, items.length - 1));
            const fs = Math.min(75, pitch * 0.45);
            const y = y0 + i * pitch;
            return (
              <div key={i} style={rise(app(it, i))}>
                <Line f={M7} size={30} y={y - 0.29 * fs} color="#EBDFAB" left={125} width={90} align="left">
                  {no(i)}
                </Line>
                <Line f={ANTON} size={fs} y={y} color="#FEFBF5" left={68}>
                  {up(it.label)}
                </Line>
                <div style={{ position: "absolute", left: 100, top: y + pitch * 0.31, width: 881, height: 1.5, background: "rgba(255,235,190,.2)" }} />
              </div>
            );
          })}
        </>
      )}

      {layout === "paper" && (
        <>
          {media && <Frame m={media} x={334} y={top0 - 28} w={617} h={789} r={24} delay={5} rotate={2.5} />}
          <div style={{ position: "absolute", left: 80, top: top0 + 178, width: 465, height: 125 + items.length * 171, borderRadius: 22, background: PAPER, boxShadow: "0 30px 70px rgba(0,0,0,.55)", transform: `rotate(-3deg) translateY(${interpolate(f, [4, 14], [50, 0], CLAMP)}px)`, opacity: interpolate(f, [4, 10], [0, 1], CLAMP) }}>
            {c.listTitle && (
              <Line f={M7} size={24} y={78} color="#6B6455" width={465} style={{ letterSpacing: "0.04em" }}>
                {up(c.listTitle)}
              </Line>
            )}
            {items.map((it, i) => (
              <div key={i} style={{ position: "absolute", left: 0, top: 100 + i * 171, width: 465, height: 171, opacity: app(it, i) }}>
                <Line f={ANTON} size={48} y={62} color="#A8873A" left={46} width={100} align="left">
                  {no(i)}
                </Line>
                <Line f={M8} size={34} y={110} color="#2B2B2B" left={96} width={360} align="left">
                  {up(it.label)}
                </Line>
                {i < items.length - 1 && <div style={{ position: "absolute", left: 50, right: 50, bottom: 14, height: 1.5, background: "rgba(0,0,0,.14)" }} />}
              </div>
            ))}
          </div>
        </>
      )}

      {layout === "stack" &&
        items.slice(0, 3).map((it, i) => {
          const pos = [
            { x: 110, y: top0 + 60, r: -7 },
            { x: 225, y: top0 + 190, r: 5 },
            { x: 180, y: top0 + 560, r: 0 },
          ][i];
          const s = app(it, i);
          const lines: string[] = [].concat(it.lines ?? it.note ?? []);
          return (
            <div key={i} style={{ position: "absolute", left: pos.x, top: pos.y, width: 690, height: 372, borderRadius: 20, background: PAPER, boxShadow: "0 26px 60px rgba(0,0,0,.5)", opacity: s, transform: `translateY(${(1 - s) * 60}px) rotate(${pos.r}deg)` }}>
              <div style={{ position: "absolute", left: 30, top: 30, padding: "0 16px", height: 36, lineHeight: "36px", borderRadius: 7, background: "#222", color: "#fff", fontFamily: `"${M7.family}"`, fontWeight: 700, fontSize: 18 }}>{it.tag ?? no(i)}</div>
              <Line f={M8} size={40} y={132} color="#26241F" left={42} width={620} align="left">
                {up(it.label)}
              </Line>
              {lines.map((l, k) => (
                <Line key={k} f={M6} size={29} y={204 + k * 50} color="#4A473F" left={42} width={620} align="left">
                  {l}
                </Line>
              ))}
              <div style={{ position: "absolute", left: 40, right: 40, bottom: 38, height: 1.5, background: "rgba(0,0,0,.2)" }} />
            </div>
          );
        })}

      {layout === "steps" &&
        items.slice(0, 3).map((it, i) => {
          const leftImg = i % 2 === 0;
          const y = top0 + 20 + i * 345;
          const tx = leftImg ? 540 : 40;
          return (
            <div key={i} style={rise(app(it, i))}>
              {it.media && <Frame m={asMedia(it.media)} x={leftImg ? 75 : 575} y={y} w={430} h={300} r={18} />}
              <Line f={ANTON} size={75} y={y + 82} color={GOLD} left={tx} width={500}>
                {no(i)}
              </Line>
              <Line f={M7} size={39} y={y + 168} left={tx} width={500} style={{ letterSpacing: "0.02em" }}>
                {up(it.label)}
              </Line>
              {it.note && (
                <Line f={M6} size={26} y={y + 228} color="#9C9C9C" left={tx} width={500}>
                  {it.note}
                </Line>
              )}
            </div>
          );
        })}

      {(c.lines ?? []).map((l: string, i: number, arr: string[]) => (
        <Line key={i} f={M7} size={36} y={1700 - (arr.length - 1 - i) * 80} color={i === arr.length - 1 ? GOLD : "#fff"} style={{ letterSpacing: "0.03em", opacity: interpolate(f, [16 + i * 8, 22 + i * 8], [0, 1], CLAMP) }}>
          {up(l)}
        </Line>
      ))}
      {c.footer && (
        <Line f={ANTON} size={84} y={1620} color={GOLD} style={{ opacity: interpolate(f, [dur * 0.55, dur * 0.55 + 6], [0, 1], CLAMP) }}>
          {up(c.footer)}
        </Line>
      )}
    </AbsoluteFill>
  );
};

// ---------- Thẻ so sánh trước/sau ----------
const Compare: React.FC<{ c: Item; dur: number; rel: (t: number) => number }> = ({ c, dur, rel }) => {
  const f = useCurrentFrame();
  const pills: Item[] = c.pills ?? [];
  const pill = [...pills].reverse().find((p) => f >= rel(p.t));
  const pf = pill ? f - rel(pill.t) : 0;
  const cream = !!c.title; // có tiêu đề: nền kem, nhãn chữ trơn; không tiêu đề: nền xám sáng, nhãn trong ô đen
  const L = cream ? { x: 120, y: 741, w: 279, h: 495 } : { x: 39, y: 712, w: 321, h: 567 };
  const R = cream ? { x: 450, y: 467, w: 507, h: 902 } : { x: 411, y: 262, w: 618, h: 1098 };
  const frame = (m: MediaRef, b: typeof L, delay: number) => (
    <Frame m={m} x={b.x} y={b.y} w={b.w} h={b.h} r={cream ? 18 : 22} delay={delay} border={cream ? "2px solid rgba(231,225,206,.95)" : "none"} shadow="0 22px 50px rgba(0,0,0,.28)" />
  );
  const label = (m: MediaRef, b: typeof L, delay: number, big: boolean) =>
    m.label &&
    (cream ? (
      <Line f={M7} size={big ? 40 : 27} y={b.y - (big ? 46 : 49)} color="#1E1C19" left={b.x} width={b.w} style={{ opacity: interpolate(f, [delay, delay + 5], [0, 1], CLAMP) }}>
        {up(m.label)}
      </Line>
    ) : (
      <div style={{ position: "absolute", left: b.x + b.w / 2 - 125, top: b.y - 33, width: 250, height: 52, borderRadius: 10, background: "#0A0A0A", opacity: interpolate(f, [delay, delay + 5], [0, 1], CLAMP) }}>
        <Line f={M8} size={28} y={36} width={250}>
          {up(m.label)}
        </Line>
      </div>
    ));
  return (
    <AbsoluteFill style={{ background: cream ? "#EEEBE8" : "linear-gradient(#DADADA,#F1F1F1 50%,#D6D6D6)", opacity: fade(f, dur, 6, 6) }}>
      {c.title && (
        <Line f={M7} size={44} y={260} color="#1E1C19" style={{ letterSpacing: "0.02em" }}>
          {up(c.title)}
        </Line>
      )}
      {frame(asMedia(c.left), L, 4)}
      {frame(asMedia(c.right), R, 11)}
      {label(asMedia(c.left), L, 6, false)}
      {label(asMedia(c.right), R, 13, true)}
      {pill && !cream && (
        <div style={{ position: "absolute", left: 80, top: 1436, width: 921, height: 269, borderRadius: 26, background: "#131313", opacity: interpolate(pf, [0, 4], [0, 1], CLAMP) }}>
          {pill.top && (
            <Line f={MI5} size={38} y={84} width={921}>
              {pill.top}
            </Line>
          )}
          <Line f={ANTON} size={Math.min(85, (800 / tw(up(pill.main), ANTON, 100)) * 100)} y={pill.top ? 232 : 170} width={921}>
            <GradText>{up(pill.main)}</GradText>
          </Line>
        </div>
      )}
      {c.footer && (
        <Line f={M6} size={29} y={1482} color="#53514D" style={{ letterSpacing: "0.03em", opacity: interpolate(f, [16, 22], [0, 1], CLAMP) }}>
          {up(c.footer)}
        </Line>
      )}
    </AbsoluteFill>
  );
};

// ---------- Thẻ bằng chứng ----------
const Proof: React.FC<{ c: Item; dur: number }> = ({ c, dur }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const media: MediaRef[] = (c.media ?? []).map(asMedia);
  const s = spring({ frame: f - 16, fps, config: { damping: 12, stiffness: 180 } });
  const boxes =
    media.length > 1
      ? [
          { x: 129, y: 477, w: 364, h: 786 },
          { x: 588, y: 477, w: 364, h: 786 },
        ]
      : media[0]?.wide
        ? [{ x: 100, y: 610, w: 880, h: 520 }]
        : [{ x: 318, y: 477, w: 444, h: 786 }];
  return (
    <AbsoluteFill style={{ background: "#06080E", opacity: fade(f, dur, 6, 6) }}>
      {c.name && (
        <Line f={M7} size={42} y={292} style={{ letterSpacing: "0.02em", opacity: interpolate(f, [0, 8], [0, 1], CLAMP) }}>
          {up(c.name)}
        </Line>
      )}
      {media.map((m, i) => (
        <React.Fragment key={i}>
          {m.label && (
            <Line f={M7} size={26} y={boxes[i].y - 42} color="#EDE9B2" left={boxes[i].x} width={boxes[i].w} style={{ opacity: interpolate(f, [4 + i * 6, 10 + i * 6], [0, 1], CLAMP) }}>
              {up(m.label)}
            </Line>
          )}
          <Frame m={m} {...boxes[i]} r={20} delay={4 + i * 6} border="2px solid rgba(255,255,255,.9)" />
        </React.Fragment>
      ))}
      <Line f={M8} size={Math.min(92, (860 / tw(up(c.stat), M8, 100)) * 100)} y={1414} color="#ECE7A0" style={{ opacity: s, transform: `scale(${0.8 + 0.2 * s})` }}>
        {up(c.stat)}
      </Line>
      {c.note && (
        <Line f={M7} size={43} y={1515} style={{ opacity: interpolate(f, [22, 28], [0, 1], CLAMP) }}>
          {up(c.note)}
        </Line>
      )}
    </AbsoluteFill>
  );
};

const Broll: React.FC<{ c: Item; dur: number; joinPrev: boolean; joinNext: boolean }> = ({ c, dur, joinPrev, joinNext }) => {
  const f = useCurrentFrame();
  // Cảnh chèn nối tiếp nhau thì cắt thẳng, không mờ dần (tránh lộ người nói giữa hai cảnh).
  const op = Math.min(joinPrev ? 1 : interpolate(f, [0, 4], [0, 1], CLAMP), joinNext ? 1 : interpolate(f, [dur - 4, dur], [1, 0], CLAMP));
  return (
    <AbsoluteFill style={{ opacity: op, overflow: "hidden" }}>
      <Media m={c} style={{ transform: `scale(${interpolate(f, [0, dur], [1, 1.07])})` }} />
    </AbsoluteFill>
  );
};

// pos "top": đặt ở khoảng trống phía trên đầu người nói; mặc định nằm ở nửa dưới như mẫu.
const PIP_BOX = { top: { left: 108, top: 100, width: 864, height: 486 }, bottom: { left: 180, top: 1050, width: 720, height: 405 } };
const Pip: React.FC<{ c: Item; dur: number; joinPrev: boolean; joinNext: boolean }> = ({ c, dur, joinPrev, joinNext }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = joinPrev ? 1 : spring({ frame: f, fps, config: { damping: 15, stiffness: 170 } });
  return (
    <AbsoluteFill style={{ opacity: joinNext ? 1 : interpolate(f, [dur - 5, dur], [1, 0], CLAMP) }}>
      <div style={{ position: "absolute", ...PIP_BOX[c.pos === "top" ? "top" : "bottom"], borderRadius: 15, overflow: "hidden", border: "1.5px solid rgba(255,255,255,.7)", boxShadow: "0 0 40px rgba(255,255,255,.12), 0 30px 70px rgba(0,0,0,.6)", opacity: s, transform: `scale(${0.88 + 0.12 * s})` }}>
        <Media m={c} />
      </div>
    </AbsoluteFill>
  );
};

const useFonts = () => {
 const [ready,setReady]=useState(false);
 const [handle]=useState(()=>delayRender("Bundled Anton and Montserrat"));
 useEffect(()=>{
  fontPromise ??= Promise.all([
   new FontFace(ANTON.family,`url(${staticFile("fonts/Anton.ttf")})`,{weight:"400"}),
   new FontFace(M6.family,`url(${staticFile("fonts/Montserrat.ttf")})`,{weight:"100 900"}),
   new FontFace(M6.family,`url(${staticFile("fonts/Montserrat-Italic.ttf")})`,{weight:"100 900",style:"italic"})
  ].map(async f=>{document.fonts.add(await f.load());})).then(()=>undefined);
  fontPromise.then(()=>{setReady(true);continueRender(handle);}).catch(e=>{throw e;});
 },[handle]);
 return ready;
};

const Main: React.FC<Plan> = (p) => {
  const { fps } = useVideoConfig();
  const ready = useFonts();
  const fr = (t: number) => Math.round(toOut(p.cuts, t) * fps);
  const span = (it: Item) => {
    const from = fr(it.t);
    return { from, dur: Math.max(2, fr(it.end) - from) };
  };
  const inserts = p.inserts ?? [];
  const captions = p.captions ?? [];
  const of = (type: string) => inserts.filter((i) => i.type === type);
  const pips = of("pip");
  const full = inserts.filter((i) => ["card", "compare", "proof"].includes(i.type));
  let acc = 0;
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      {p.cuts.map((c, i) => {
        const from = Math.round(acc * fps);
        acc += c.end - c.start;
        const dur = Math.round(acc * fps) - from;
        return (
          <Sequence key={i} from={from} durationInFrames={dur}>
            <OffthreadVideo
              src={staticFile(p.video)}
              startFrom={Math.round(c.start * fps)}
              style={{ width: "100%", height: "100%", objectFit: "cover", transform: `scale(${i % 2 ? p.zoom ?? 1.08 : 1})`, transformOrigin: "50% 35%" }}
            />
          </Sequence>
        );
      })}
      {of("broll").map((c, i) => {
        const s = span(c);
        return (
          <Sequence key={i} from={s.from} durationInFrames={s.dur}>
            <Broll
              c={c}
              dur={s.dur}
              joinPrev={of("broll").some((q) => q !== c && Math.abs(q.end - c.t) < 0.08)}
              joinNext={of("broll").some((q) => q !== c && Math.abs(q.t - c.end) < 0.08)}
            />
          </Sequence>
        );
      })}
      {/* shade "full": đen hẳn phía dưới như mẫu. Mặc định "soft": chỉ làm tối dải sau chữ, phần dưới video vẫn thấy. */}
      <AbsoluteFill
        style={{
          background:
            p.shade === "full"
              ? "linear-gradient(to bottom, rgba(0,0,0,0) 45%, rgba(0,0,0,.33) 56%, rgba(0,0,0,.55) 62.5%, rgba(0,0,0,.82) 70%, #000 79%)"
              : "linear-gradient(to bottom, rgba(0,0,0,0) 43%, rgba(0,0,0,.42) 54%, rgba(0,0,0,.62) 61%, rgba(0,0,0,.62) 69%, rgba(0,0,0,.42) 80%, rgba(0,0,0,.3) 100%)",
        }}
      />
      {ready && (
        <>
          {pips.map((c, i) => {
            const s = span(c);
            return (
              <Sequence key={i} from={s.from} durationInFrames={s.dur}>
                <Pip
                  c={c}
                  dur={s.dur}
                  joinPrev={pips.some((q) => q !== c && q.pos === c.pos && Math.abs(q.end - c.t) < 0.08)}
                  joinNext={pips.some((q) => q !== c && q.pos === c.pos && Math.abs(q.t - c.end) < 0.08)}
                />
              </Sequence>
            );
          })}
          {captions.map((c, i) => {
            const s = span(c);
            const pip = pips.some((q) => q.pos !== "top" && c.t >= q.t - 0.05 && c.t < q.end);
            return (
              <Sequence key={i} from={s.from} durationInFrames={s.dur}>
                {c.type === "hero" ? <Hero c={c} dur={s.dur} pip={pip} /> : c.type === "cta" ? <Cta c={c} dur={s.dur} /> : c.type === "brand" ? <Brand c={c} dur={s.dur} /> : <Sub c={c} dur={s.dur} pip={pip} />}
                {p.sfx && c.type !== "sub" && <Audio src={staticFile("sfx/pop.wav")} volume={0.5} />}
              </Sequence>
            );
          })}
          {full.map((c, i) => {
            const s = span(c);
            const rel = (t: number) => fr(t) - s.from;
            return (
              <Sequence key={i} from={s.from} durationInFrames={s.dur}>
                {c.type === "card" ? <Card c={c} dur={s.dur} rel={rel} /> : c.type === "compare" ? <Compare c={c} dur={s.dur} rel={rel} /> : <Proof c={c} dur={s.dur} />}
                {p.sfx && <Audio src={staticFile("sfx/whoosh.wav")} volume={0.45} />}
              </Sequence>
            );
          })}
        </>
      )}
      {p.music && <Audio src={staticFile(p.music)} loop volume={p.musicVolume ?? 0.08} />}
    </AbsoluteFill>
  );
};

const Root: React.FC = () => (
  <Composition
    id="Main"
    component={Main as any}
    width={1080}
    height={1920}
    fps={30}
    durationInFrames={30}
    defaultProps={{ video: "raw.mp4", cuts: [{ start: 0, end: 1 }] } as any}
    calculateMetadata={({ props }: any) => {
      const fps = props.fps ?? 30;
      const total = props.cuts.reduce((a: number, c: Cut) => a + c.end - c.start, 0);
      return { fps, durationInFrames: Math.max(1, Math.round(total * fps)) };
    }}
  />
);

registerRoot(Root);
