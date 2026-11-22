import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState, type ReactNode } from "react";
import { Button } from "@/components/ui/button";
import appIcon from "@/assets/remote-192.png.asset.json";
import {
  ChevronUp, ChevronDown, ChevronLeft, ChevronRight, Star, Power, Plus, Minus,
  Undo2, MoreHorizontal, VolumeX, X, Delete, Check, AlertTriangle, Wifi,
} from "lucide-react";

declare global {
  interface Window {
    PhilipsIR?: {
      getStatus: () => string;
      send: (command: string) => string;
      connectNetwork: (ip: string) => string;
    };
  }
}

type IrStatus = { available: boolean; profileConfigured: boolean; supports36kHz?: boolean; networkConnected?: boolean; carrierRangesHz?: number[][]; message: string };

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Philips Remote — 50PUG6654/78" },
      { name: "description", content: "Controle remoto para Philips 50PUG6654/78." },
      { property: "og:title", content: "Philips Remote — 50PUG6654/78" },
      { property: "og:description", content: "Controle remoto para Philips 50PUG6654/78." },
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
  const [irStatus, setIrStatus] = useState<IrStatus | null>(null);
  const [tvIp, setTvIp] = useState("");
  const [syncStatus, setSyncStatus] = useState<string | null>(null);

  useEffect(() => {
    const readStatus = () => {
      if (!window.PhilipsIR) return;
      try { setIrStatus(JSON.parse(window.PhilipsIR.getStatus()) as IrStatus); }
      catch { setIrStatus({ available: false, profileConfigured: false, message: "Não foi possível consultar o módulo IR." }); }
    };
    readStatus();
  }, []);

  const syncTv = () => {
    if (!window.PhilipsIR) {
      setSyncStatus("A sincronização Wi-Fi exige a versão Android instalada, não o navegador.");
      return;
    }
    try {
      const response = JSON.parse(window.PhilipsIR.connectNetwork(tvIp)) as { ok: boolean; message: string };
      setSyncStatus(response.message);
      if (response.ok) {
        setIrStatus((previous) => previous ? { ...previous, networkConnected: true, message: "TV conectada pela rede Wi-Fi." } : previous);
      }
    } catch {
      setSyncStatus("Não foi possível iniciar a sincronização. Confira o IP da TV.");
    }
  };

  const press = (c: string) => {
    if (typeof navigator !== "undefined" && "vibrate" in navigator) navigator.vibrate?.(15);
    if (!window.PhilipsIR) {
      setLast(`${c}: abra a versão Android nativa para acessar o infravermelho; navegador/PWA não transmite IR.`);
      return;
    }
    try {
      const response = JSON.parse(window.PhilipsIR.send(c)) as { ok: boolean; message: string };
      setLast(`${c}: ${response.message}`);
    } catch {
      setLast(`${c}: erro ao comunicar com o módulo infravermelho.`);
    }
  };

  return (
    <div className="remote-app mx-auto flex max-w-md flex-col bg-background">
      <header className="remote-header bg-[image:var(--gradient-header)] px-4 pb-2 text-primary-foreground">
        <div className="flex items-center justify-center gap-2">
          <img src={appIcon.url} width={32} height={32} alt="" className="size-8 shrink-0 rounded-md" />
          <h1 className="text-lg font-semibold">Philips TV 50PUG6654/78</h1>
        </div>
        <div className="mt-2 flex items-center justify-center gap-1 rounded-md bg-background/20 px-2 py-1 text-center text-xs">
          <AlertTriangle className="h-3.5 w-3.5 shrink-0" /> {irStatus ? irStatus.message : "Modo web: sem acesso direto ao infravermelho"}
        </div>
        <div className="mt-3 flex gap-2">
          <input
            aria-label="Endereço IP da TV"
            value={tvIp}
            onChange={(event) => setTvIp(event.target.value)}
            placeholder="IP da TV (ex.: 192.168.1.50)"
            inputMode="decimal"
            className="min-w-0 flex-1 rounded-lg border border-primary-foreground/30 bg-background/15 px-3 py-2 text-sm text-primary-foreground placeholder:text-primary-foreground/65 outline-none focus:ring-2 focus:ring-primary-foreground/50"
          />
          <Button variant="secondary" onClick={syncTv} className="shrink-0 gap-2">
            <Wifi className="h-4 w-4" /> Sincronizar
          </Button>
        </div>
        {syncStatus && <p role="status" className="mt-2 text-center text-xs text-primary-foreground">{syncStatus}</p>}
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
          {last ?? (irStatus?.available ? "Emissor IR detectado" : "Nenhum comando transmitido") }
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
