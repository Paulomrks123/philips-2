import { createFileRoute } from "@tanstack/react-router";
import { useState, type ReactNode } from "react";
import {
  ChevronUp, ChevronDown, ChevronLeft, ChevronRight, Star, Power, Plus, Minus,
  Undo2, MoreHorizontal, Menu as MenuIcon, Settings, VolumeX, X, Delete, Check, AlertTriangle,
} from "lucide-react";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Philips Remote — Protótipo 26PFL3404" },
      { name: "description", content: "Protótipo visual do controle remoto Philips 26PFL3404. Sem transmissão infravermelha." },
      { property: "og:title", content: "Philips Remote — Protótipo 26PFL3404" },
      { property: "og:description", content: "Protótipo visual do controle remoto Philips 26PFL3404." },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary" },
    ],
  }),
  component: Index,
});

function Round({ children, label, size = "md", tone = "default", onClick }: {
  children: ReactNode; label: string; size?: "md" | "lg"; tone?: "default" | "power" | "star"; onClick: () => void;
}) {
  const s = size === "lg" ? "h-24 w-24" : "h-16 w-16";
  const t = tone === "power" ? "text-destructive" : tone === "star" ? "text-primary" : "text-foreground/80";
  return (
    <button aria-label={label} onClick={onClick} className={`remote-btn ${s} ${t}`}>
      {children}
    </button>
  );
}

function Rocker({ label, onUp, onDown, up, down }: { label: string; onUp: () => void; onDown: () => void; up: ReactNode; down: ReactNode }) {
  return (
    <div className="flex flex-col items-center gap-2 text-foreground/90">
      <button aria-label={`${label} +`} onClick={onUp} className="remote-ghost">{up}</button>
      <span className="h-px w-6 bg-foreground/50" />
      <span className="text-lg tracking-[0.2em]">{label}</span>
      <span className="h-px w-6 bg-foreground/50" />
      <button aria-label={`${label} -`} onClick={onDown} className="remote-ghost">{down}</button>
    </div>
  );
}

function Index() {
  const [last, setLast] = useState<string | null>(null);
  const [pad, setPad] = useState(false);
  const [more, setMore] = useState(false);
  const [digits, setDigits] = useState("");
  const press = (c: string) => {
    if (typeof navigator !== "undefined" && "vibrate" in navigator) navigator.vibrate?.(15);
    setLast(c);
  };

  return (
    <div className="mx-auto flex min-h-screen max-w-md flex-col bg-background">
      <header className="bg-[image:var(--gradient-header)] px-4 pb-2 pt-4 text-primary-foreground">
        <div className="flex items-center justify-between">
          <MenuIcon className="h-6 w-6" />
          <h1 className="text-xl font-semibold">Philips TV 26PFL3404</h1>
          <Settings className="h-5 w-5" />
        </div>
        <div className="mt-2 flex items-center justify-center gap-1 rounded-md bg-background/20 px-2 py-1 text-xs">
          <AlertTriangle className="h-3.5 w-3.5" /> Protótipo visual — navegador não emite infravermelho
        </div>
      </header>

      <main className="relative flex flex-1 flex-col px-6 py-6">
        <div className="grid grid-cols-3 items-start">
          <div className="pt-4"><Rocker label="CH" onUp={() => press("CHANNEL_UP")} onDown={() => press("CHANNEL_DOWN")} up={<ChevronUp />} down={<ChevronDown />} /></div>
          <div className="flex justify-center"><Round size="lg" tone="star" label="Favoritos" onClick={() => press("FAVORITES")}><Star className="h-10 w-10 fill-current" /></Round></div>
          <div className="flex justify-end pt-24"><Round tone="power" label="Power" onClick={() => press("POWER")}><Power className="h-8 w-8" /></Round></div>
        </div>

        <div className="mt-6 grid grid-cols-[1fr_auto] items-center gap-4">
          <div className="dpad mx-auto">
            {([
              ["UP", "top-0 left-1/2 -translate-x-1/2", <ChevronUp key="u" />],
              ["DOWN", "bottom-0 left-1/2 -translate-x-1/2", <ChevronDown key="d" />],
              ["LEFT", "left-0 top-1/2 -translate-y-1/2", <ChevronLeft key="l" />],
              ["RIGHT", "right-0 top-1/2 -translate-y-1/2", <ChevronRight key="r" />],
            ] as const).map(([c, pos, icon]) => (
              <button key={c} aria-label={c} onClick={() => press(c)} className={`dpad-dir absolute ${pos}`}>{icon}</button>
            ))}
            <button aria-label="OK" onClick={() => press("OK")} className="dpad-ok">OK</button>
          </div>
          <div className="flex flex-col items-center gap-4">
            <Rocker label="VOL" onUp={() => press("VOLUME_UP")} onDown={() => press("VOLUME_DOWN")} up={<Plus />} down={<Minus />} />
            <button aria-label="Mute" onClick={() => press("MUTE")} className="remote-ghost"><VolumeX /></button>
          </div>
        </div>

        <div className="mt-8 flex justify-center gap-12">
          <Round label="Menu" onClick={() => press("MENU")}><span className="text-lg">Menu</span></Round>
          <Round label="Voltar" onClick={() => press("BACK")}><Undo2 /></Round>
        </div>
        <div className="mt-6 flex justify-between">
          <Round label="Teclado numérico" onClick={() => setPad(true)}><span className="text-lg">123</span></Round>
          <Round label="Sair" onClick={() => press("EXIT")}><span className="text-lg">Sair</span></Round>
          <Round label="Mais opções" onClick={() => setMore(true)}><MoreHorizontal /></Round>
        </div>

        <p aria-live="polite" className="mt-6 text-center text-xs text-muted-foreground">
          {last ? `Comando ${last} — não transmitido (sem IR neste ambiente)` : "Toque em um botão"}
        </p>
      </main>

      {(pad || more) && (
        <div className="fixed inset-0 z-50 flex items-end justify-center bg-background/70" onClick={() => { setPad(false); setMore(false); }}>
          <div className="sheet w-full max-w-md" onClick={(e) => e.stopPropagation()}>
            <div className="mb-4 flex items-center justify-between">
              <span className="text-lg font-semibold">{pad ? (digits || "Canal") : "Funções"}</span>
              <button aria-label="Fechar" onClick={() => { setPad(false); setMore(false); }} className="remote-ghost"><X /></button>
            </div>
            {pad ? (
              <div className="grid grid-cols-3 gap-3">
                {["1","2","3","4","5","6","7","8","9"].map((d) => (
                  <button key={d} onClick={() => { setDigits((v) => (v + d).slice(0, 3)); press(`NUM_${d}`); }} className="key">{d}</button>
                ))}
                <button aria-label="Apagar" onClick={() => setDigits((v) => v.slice(0, -1))} className="key"><Delete /></button>
                <button onClick={() => { setDigits((v) => (v + "0").slice(0, 3)); press("NUM_0"); }} className="key">0</button>
                <button aria-label="Confirmar" onClick={() => { press(`OK (${digits})`); setDigits(""); setPad(false); }} className="key text-primary"><Check /></button>
              </div>
            ) : (
              <div className="grid grid-cols-3 gap-3">
                {["SOURCE","TV","AV","HDMI","INFO","GUIDE","IMAGEM","SOM","SLEEP"].map((c) => (
                  <button key={c} onClick={() => press(c)} className="key text-sm">{c}</button>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
