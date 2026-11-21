import { createFileRoute } from "@tanstack/react-router";
import { useState, type ReactNode } from "react";
import { Button } from "@/components/ui/button";
import appIcon from "@/assets/remote-192.png.asset.json";
import {
  ChevronUp, ChevronDown, ChevronLeft, ChevronRight, Star, Power, Plus, Minus,
  Undo2, MoreHorizontal, VolumeX, X, Delete, Check, AlertTriangle,
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
  const s = size === "lg" ? "remote-large" : "remote-medium";
  const t = tone === "power" ? "text-destructive" : tone === "star" ? "text-primary" : "text-foreground/80";
  return (
    <Button variant="remote" size="remote" aria-label={label} onClick={onClick} className={`remote-btn ${s} ${t}`}>
      {children}
    </Button>
  );
}

function Rocker({ label, onUp, onDown, up, down }: { label: string; onUp: () => void; onDown: () => void; up: ReactNode; down: ReactNode }) {
  return (
    <div className="flex flex-col items-center gap-2 text-foreground/90">
      <Button variant="remote" size="remote" aria-label={`${label} +`} onClick={onUp} className="remote-ghost">{up}</Button>
      <span className="h-px w-6 bg-foreground/50" />
      <span className="text-base">{label}</span>
      <span className="h-px w-6 bg-foreground/50" />
      <Button variant="remote" size="remote" aria-label={`${label} -`} onClick={onDown} className="remote-ghost">{down}</Button>
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
    <div className="remote-app mx-auto flex max-w-md flex-col bg-background">
      <header className="remote-header bg-[image:var(--gradient-header)] px-4 pb-2 text-primary-foreground">
        <div className="flex items-center justify-center gap-2">
          <img src={appIcon.url} width={32} height={32} alt="" className="size-8 shrink-0 rounded-md" />
          <h1 className="text-lg font-semibold">Philips TV 26PFL3404</h1>
        </div>
        <div className="mt-2 flex items-center justify-center gap-1 rounded-md bg-background/20 px-2 py-1 text-center text-xs">
          <AlertTriangle className="h-3.5 w-3.5 shrink-0" /> Protótipo visual — sem transmissão infravermelha
        </div>
      </header>

      <main className="remote-main relative flex flex-1 flex-col">
        <div className="remote-top grid grid-cols-3 items-start">
          <div><Rocker label="CH" onUp={() => press("CHANNEL_UP")} onDown={() => press("CHANNEL_DOWN")} up={<ChevronUp />} down={<ChevronDown />} /></div>
          <div className="flex justify-center"><Round size="lg" tone="star" label="Favoritos" onClick={() => press("FAVORITES")}><Star className="h-10 w-10 fill-current" /></Round></div>
          <div className="remote-power flex justify-end"><Round tone="power" label="Power" onClick={() => press("POWER")}><Power className="h-8 w-8" /></Round></div>
        </div>

        <div className="remote-navigation grid grid-cols-[minmax(0,1fr)_auto] items-center gap-4">
          <div className="dpad mx-auto">
            {([
              ["UP", "top-0 left-1/2 -translate-x-1/2", <ChevronUp key="u" />],
              ["DOWN", "bottom-0 left-1/2 -translate-x-1/2", <ChevronDown key="d" />],
              ["LEFT", "left-0 top-1/2 -translate-y-1/2", <ChevronLeft key="l" />],
              ["RIGHT", "right-0 top-1/2 -translate-y-1/2", <ChevronRight key="r" />],
            ] as const).map(([c, pos, icon]) => (
              <Button variant="remote" size="remote" key={c} aria-label={c} onClick={() => press(c)} className={`dpad-dir absolute ${pos}`}>{icon}</Button>
            ))}
            <Button variant="remote" size="remote" aria-label="OK" onClick={() => press("OK")} className="dpad-ok">OK</Button>
          </div>
          <div className="flex flex-col items-center gap-2">
            <Rocker label="VOL" onUp={() => press("VOLUME_UP")} onDown={() => press("VOLUME_DOWN")} up={<Plus />} down={<Minus />} />
            <Button variant="remote" size="remote" aria-label="Mute" onClick={() => press("MUTE")} className="remote-ghost"><VolumeX /></Button>
          </div>
        </div>

        <div className="remote-menu flex justify-center gap-12">
          <Round label="Menu" onClick={() => press("MENU")}><span className="text-lg">Menu</span></Round>
          <Round label="Voltar" onClick={() => press("BACK")}><Undo2 /></Round>
        </div>
        <div className="remote-bottom flex justify-between">
          <Round label="Teclado numérico" onClick={() => setPad(true)}><span className="text-lg">123</span></Round>
          <Round label="Sair" onClick={() => press("EXIT")}><span className="text-lg">Sair</span></Round>
          <Round label="Mais opções" onClick={() => setMore(true)}><MoreHorizontal /></Round>
        </div>

        <p aria-live="polite" className="remote-feedback text-center text-xs text-muted-foreground">
          {last ? `Comando ${last} — não transmitido (sem IR neste ambiente)` : "Nenhum comando transmitido"}
        </p>
      </main>

      {(pad || more) && (
        <div className="fixed inset-0 z-50 flex items-end justify-center bg-background/70" onClick={() => { setPad(false); setMore(false); }}>
          <div className="sheet w-full max-w-md" onClick={(e) => e.stopPropagation()}>
            <div className="mb-4 flex items-center justify-between">
              <span className="text-lg font-semibold">{pad ? (digits || "Canal") : "Funções"}</span>
              <Button variant="remote" size="remote" aria-label="Fechar" onClick={() => { setPad(false); setMore(false); }} className="remote-ghost"><X /></Button>
            </div>
            {pad ? (
              <div className="grid grid-cols-3 gap-3">
                {["1","2","3","4","5","6","7","8","9"].map((d) => (
                  <Button variant="remote" size="remote" key={d} onClick={() => { setDigits((v) => (v + d).slice(0, 3)); press(`NUM_${d}`); }} className="key">{d}</Button>
                ))}
                <Button variant="remote" size="remote" aria-label="Apagar" onClick={() => setDigits((v) => v.slice(0, -1))} className="key"><Delete /></Button>
                <Button variant="remote" size="remote" onClick={() => { setDigits((v) => (v + "0").slice(0, 3)); press("NUM_0"); }} className="key">0</Button>
                <Button variant="remote" size="remote" aria-label="Confirmar" onClick={() => { press(`OK (${digits})`); setDigits(""); setPad(false); }} className="key text-primary"><Check /></Button>
              </div>
            ) : (
              <div className="grid grid-cols-3 gap-3">
                {["SOURCE","TV","AV","HDMI","INFO","GUIDE","IMAGEM","SOM","SLEEP"].map((c) => (
                  <Button variant="remote" size="remote" key={c} onClick={() => press(c)} className="key text-sm">{c}</Button>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
