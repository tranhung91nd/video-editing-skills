import React from "react";
import {
  AbsoluteFill,
  Audio,
  Composition,
  Img,
  OffthreadVideo,
  Sequence,
  interpolate,
  registerRoot,
  spring,
  staticFile,
  useCurrentFrame,
} from "remotion";
import { loadFont } from "@remotion/google-fonts/Roboto";
import TL from "./timeline.json";
import PLAN from "./plan.json";
import { DIMS } from "./dims";

const { fontFamily: ROBOTO } = loadFont("normal", { weights: ["500", "700", "900"], subsets: ["vietnamese", "latin"] });

const FPS = 30;
const W = 1080;
const H = 1920;
const YELLOW = "#FEC529";
const ORANGE = "#F89B1D";
const NAVY = "#1A2B48";
const XF = 6;

type Word = { w: string; start: number; end: number };
type Sent = { id: string; display: string; start: number; end: number; words: Word[] };
type Shot = { v: string; t: number; at: number; fx?: number; z?: number };
const SENTS = TL as Sent[];
type Brand = { badge: string; branch: string; phone: string; address: string; priceLead: string; price: string; dates: [string, string, boolean?][]; logo?: string };
const P = PLAN as unknown as { total: number; shots: Shot[]; tags: { text: string; from: number; to: number }[]; cards: Record<string, [number, number]>; brand: Brand };
const B = P.brand;
const LOGO = B.logo ?? "logo.png";
const TOTAL = P.total;
const sec = (s: number) => Math.round(s * FPS);

// ---------- footage ----------
const ShotView: React.FC<{ s: Shot; dur: number }> = ({ s, dur }) => {
  const f = useCurrentFrame();
  const [sw, sh] = DIMS[s.v];
  const prog = Math.min(1, f / Math.max(1, dur * FPS));
  const scale = Math.max(H / sh, W / sw) * (s.z ?? 1) * (1.0 + 0.06 * prog);
  const dW = sw * scale, dH = sh * scale;
  const left = Math.min(0, Math.max(W - dW, W / 2 - (s.fx ?? 0.5) * dW));
  return (
    <AbsoluteFill style={{ overflow: "hidden" }}>
      <OffthreadVideo src={staticFile(`v/${s.v}.mp4`)} startFrom={sec(s.t)} muted
        style={{ position: "absolute", width: dW, height: dH, left, top: (H - dH) / 2, maxWidth: "none" }} />
    </AbsoluteFill>
  );
};

const Fade: React.FC<{ frames: number; children: React.ReactNode }> = ({ frames, children }) => {
  const f = useCurrentFrame();
  const o = frames ? interpolate(f, [0, frames], [0, 1], { extrapolateRight: "clamp" }) : 1;
  return <AbsoluteFill style={{ opacity: o }}>{children}</AbsoluteFill>;
};

const Footage: React.FC = () => (
  <>
    {P.shots.map((s, i) => {
      const end = i + 1 < P.shots.length ? P.shots[i + 1].at : TOTAL;
      const from = sec(s.at);
      const len = sec(end) - from + (i + 1 < P.shots.length ? XF : 0);
      return (
        <Sequence key={i} from={from} durationInFrames={len} layout="none">
          <Fade frames={i ? XF : 0}><ShotView s={s} dur={len / FPS} /></Fade>
        </Sequence>
      );
    })}
  </>
);

// ---------- brand ----------
const Logo: React.FC = () => (
  <div style={{ position: "absolute", left: 48, top: 96, display: "flex", alignItems: "stretch", borderRadius: 18, overflow: "hidden", boxShadow: "0 6px 24px rgba(0,0,0,0.35)" }}>
    <div style={{ background: "white", padding: "12px 20px", display: "flex", alignItems: "center" }}>
      <Img src={staticFile(LOGO)} style={{ height: 70 }} />
    </div>
    <div style={{ background: NAVY, color: YELLOW, fontFamily: ROBOTO, fontWeight: 900, fontSize: 34, letterSpacing: 2, padding: "0 24px", display: "flex", alignItems: "center" }}>
      {B.badge}
    </div>
  </div>
);

const pop = (f: number, len: number, d = 15) => {
  const a = spring({ frame: f, fps: FPS, config: { damping: d, mass: 0.7 } });
  const o = interpolate(f, [len - 7, len], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return { a, o };
};

// Place name, a yellow tab under the logo.
const Tag: React.FC<{ text: string; len: number }> = ({ text, len }) => {
  const f = useCurrentFrame();
  const { a, o } = pop(f, len);
  return (
    <div style={{ position: "absolute", left: 48, top: 252, opacity: o, transform: `translateX(${(1 - a) * -60}px)` }}>
      <div style={{ display: "flex", alignItems: "center", gap: 14, background: YELLOW, color: NAVY, fontFamily: ROBOTO, fontWeight: 900, fontSize: 46, padding: "14px 28px", borderRadius: 14, boxShadow: "0 6px 20px rgba(0,0,0,0.35)" }}>
        <svg width="36" height="36" viewBox="0 0 24 24"><path fill={NAVY} d="M12 2a7 7 0 0 0-7 7c0 5.2 7 13 7 13s7-7.8 7-13a7 7 0 0 0-7-7zm0 9.5A2.5 2.5 0 1 1 12 6a2.5 2.5 0 0 1 0 5.5z" /></svg>
        {text}
      </div>
    </div>
  );
};

// One-line subtitle in a navy box; <word> is drawn yellow.
const Sub: React.FC<{ text: string; len: number }> = ({ text, len }) => {
  const f = useCurrentFrame();
  const { a, o } = pop(f, len, 18);
  const parts = text.split(/(<[^>]+>)/).filter(Boolean);
  return (
    <div style={{ position: "absolute", left: 0, width: W, top: 1340, display: "flex", justifyContent: "center", opacity: a * o }}>
      <div style={{ background: "rgba(26,43,72,0.86)", borderRadius: 16, padding: "18px 30px", fontFamily: ROBOTO, fontWeight: 700, fontSize: 54, color: "white", whiteSpace: "nowrap", transform: `translateY(${(1 - a) * 20}px)`, borderBottom: `5px solid ${YELLOW}` }}>
        {parts.map((p, i) => p.startsWith("<") ? <span key={i} style={{ color: YELLOW }}>{p.slice(1, -1)}</span> : <span key={i}>{p}</span>)}
      </div>
    </div>
  );
};

const Price: React.FC<{ len: number }> = ({ len }) => {
  const f = useCurrentFrame();
  const { a, o } = pop(f, len, 12);
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", opacity: o }}>
      <div style={{ transform: `scale(${0.7 + 0.3 * a})`, display: "flex", flexDirection: "column", alignItems: "center", gap: 18 }}>
        <div style={{ fontFamily: ROBOTO, fontWeight: 700, fontSize: 52, color: "white", textShadow: "0 3px 14px rgba(0,0,0,0.6)" }}>{B.priceLead}</div>
        <div style={{ background: YELLOW, color: NAVY, fontFamily: ROBOTO, fontWeight: 900, fontSize: 132, padding: "8px 44px", borderRadius: 24, boxShadow: "0 14px 40px rgba(0,0,0,0.45)" }}>{B.price}</div>
      </div>
    </AbsoluteFill>
  );
};

const Schedule: React.FC<{ len: number }> = ({ len }) => {
  const f = useCurrentFrame();
  const { a, o } = pop(f, len);
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", opacity: o }}>
      <div style={{ width: 900, background: "rgba(26,43,72,0.92)", borderRadius: 28, padding: "36px 44px", transform: `translateY(${(1 - a) * 60}px)`, boxShadow: "0 18px 50px rgba(0,0,0,0.5)", border: `4px solid ${YELLOW}` }}>
        <div style={{ fontFamily: ROBOTO, fontWeight: 900, fontSize: 54, color: YELLOW, textAlign: "center", marginBottom: 22 }}>LỊCH KHỞI HÀNH</div>
        {B.dates.map(([d, p, hot], i) => {
          const r = spring({ frame: f - 6 - i * 4, fps: FPS, config: { damping: 18 } });
          return (
            <div key={i} style={{ display: "flex", justifyContent: "space-between", fontFamily: ROBOTO, fontWeight: 700, fontSize: 42, color: "white", padding: "14px 4px", borderTop: i ? "2px solid rgba(255,255,255,0.15)" : undefined, opacity: r, transform: `translateX(${(1 - r) * 40}px)` }}>
              <span>{d}</span><span style={{ color: hot ? ORANGE : YELLOW }}>{p}</span>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

const End: React.FC<{ len: number }> = ({ len }) => {
  const f = useCurrentFrame();
  const a = spring({ frame: f, fps: FPS, config: { damping: 15 } });
  const c = spring({ frame: f - 8, fps: FPS, config: { damping: 12 } });
  const d = spring({ frame: f - 16, fps: FPS, config: { damping: 16 } });
  const pulse = 1 + 0.03 * Math.sin((f / FPS) * Math.PI * 1.6) * Math.min(1, Math.max(0, (f - 30) / 20));
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", gap: 40 }}>
      <div style={{ background: "white", borderRadius: 28, padding: "26px 44px", opacity: a, transform: `scale(${0.85 + 0.15 * a})`, display: "flex", flexDirection: "column", alignItems: "center" }}>
        <Img src={staticFile(LOGO)} style={{ height: 160 }} />
        <div style={{ fontFamily: ROBOTO, fontWeight: 900, fontSize: 46, color: NAVY, letterSpacing: 4, marginTop: 6 }}>{B.branch}</div>
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: 22, background: YELLOW, borderRadius: 999, padding: "24px 54px", opacity: c, transform: `scale(${(0.8 + 0.2 * c) * pulse})`, boxShadow: "0 16px 44px rgba(0,0,0,0.5)" }}>
        <svg width="66" height="66" viewBox="0 0 24 24"><path fill={NAVY} d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.25 11.4 11.4 0 0 0 3.6.57 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.25.2 2.45.57 3.57a1 1 0 0 1-.25 1z" /></svg>
        <div style={{ fontFamily: ROBOTO, fontWeight: 900, fontSize: 84, color: NAVY, whiteSpace: "nowrap" }}>{B.phone}</div>
      </div>
      <div style={{ opacity: d, transform: `translateY(${(1 - d) * 20}px)`, fontFamily: ROBOTO, fontWeight: 700, fontSize: 44, color: "white", textAlign: "center", lineHeight: 1.35, textShadow: "0 3px 12px rgba(0,0,0,0.7)" }}>
        📍 {B.address}
      </div>
    </AbsoluteFill>
  );
};

// ---------- timeline ----------
const card = (k: string) => P.cards[k];
const subsHidden = (t: number) => Object.entries(P.cards).some(([k, [a, b]]) => k !== "schedule" && t >= a && t < b);

const DURATION = sec(TOTAL);
const MUSIC: number[] = (() => {
  const talk = SENTS.map((x) => [x.start - 0.25, x.end + 0.3]);
  const out: number[] = [];
  let level = 0.45;
  for (let fr = 0; fr < DURATION; fr++) {
    const t = fr / FPS;
    const target = talk.some(([a, c]) => t >= a && t <= c) ? 0.13 : 0.45;
    level += (target - level) * 0.1;
    out.push(level * Math.max(0, Math.min(1, t / 0.5, (TOTAL - t) / 2)));
  }
  return out;
})();

const Main: React.FC = () => {
  const [pa, pb] = card("price");
  const [sa, sb] = card("schedule");
  const [ea] = card("end");
  return (
    <AbsoluteFill style={{ background: "black" }}>
      <Footage />
      <AbsoluteFill style={{ background: "linear-gradient(rgba(0,0,0,0.35) 0%, rgba(0,0,0,0) 22%, rgba(0,0,0,0) 62%, rgba(0,0,0,0.4) 100%)" }} />
      <Sequence from={sec(pa)} durationInFrames={sec(pb) - sec(pa)}><AbsoluteFill style={{ background: "rgba(0,0,0,0.35)" }} /><Price len={sec(pb) - sec(pa)} /></Sequence>
      <Sequence from={sec(sa)} durationInFrames={sec(sb) - sec(sa)}><AbsoluteFill style={{ background: "rgba(0,0,0,0.3)" }} /><Schedule len={sec(sb) - sec(sa)} /></Sequence>
      <Sequence from={sec(ea)}><AbsoluteFill style={{ background: "rgba(10,18,32,0.55)" }} /><End len={DURATION - sec(ea)} /></Sequence>
      {sec(ea) > 0 && <Sequence durationInFrames={sec(ea)}><Logo /></Sequence>}
      {P.tags.map((t, i) => (
        <Sequence key={i} from={sec(t.from)} durationInFrames={sec(t.to) - sec(t.from)}><Tag text={t.text} len={sec(t.to) - sec(t.from)} /></Sequence>
      ))}
      {SENTS.filter((s) => !subsHidden((s.start + s.end) / 2)).map((s, i, arr) => {
        const next = arr[i + 1];
        const to = Math.min(s.end + 0.45, next ? next.start : TOTAL);
        const len = sec(to) - sec(s.start - 0.05);
        return <Sequence key={s.id} from={sec(s.start - 0.05)} durationInFrames={len}><Sub text={s.display} len={len} /></Sequence>;
      })}
      <Audio src={staticFile("narration.wav")} />
      <Audio src={staticFile("music.wav")} volume={(f) => MUSIC[Math.min(f, MUSIC.length - 1)]} />
    </AbsoluteFill>
  );
};

const Root: React.FC = () => <Composition id="Main" component={Main} durationInFrames={DURATION} fps={FPS} width={W} height={H} />;
registerRoot(Root);
