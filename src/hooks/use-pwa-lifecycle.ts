import { useEffect, useState } from "react";
import { isIOS, isStandalone, type InstallPromptEvent } from "@/lib/pwa";

export function usePwaLifecycle() {
  const [prompt, setPrompt] = useState<InstallPromptEvent | null>(null);
  const [installed, setInstalled] = useState(false);
  const [ios, setIos] = useState(false);
  const [online, setOnline] = useState(true);
  const [ready, setReady] = useState(false);
  const [busy, setBusy] = useState(false);
  const [installError, setInstallError] = useState(false);

  useEffect(() => {
    const media = window.matchMedia("(display-mode: standalone)");
    const sync = () => {
      const nav = navigator as Navigator & { standalone?: boolean };
      setInstalled(isStandalone(media.matches, nav.standalone === true));
      setOnline(navigator.onLine);
    };
    const beforeInstall = (event: Event) => {
      event.preventDefault();
      setPrompt(event as InstallPromptEvent);
      setInstallError(false);
    };
    const onInstalled = () => { setInstalled(true); setPrompt(null); };
    setIos(isIOS(navigator.userAgent, navigator.platform, navigator.maxTouchPoints));
    sync();
    setReady(true);
    window.addEventListener("beforeinstallprompt", beforeInstall);
    window.addEventListener("appinstalled", onInstalled);
    window.addEventListener("online", sync);
    window.addEventListener("offline", sync);
    window.addEventListener("pageshow", sync);
    document.addEventListener("visibilitychange", sync);
    media.addEventListener("change", sync);
    return () => {
      window.removeEventListener("beforeinstallprompt", beforeInstall);
      window.removeEventListener("appinstalled", onInstalled);
      window.removeEventListener("online", sync);
      window.removeEventListener("offline", sync);
      window.removeEventListener("pageshow", sync);
      document.removeEventListener("visibilitychange", sync);
      media.removeEventListener("change", sync);
    };
  }, []);

  const install = async () => {
    if (!prompt || busy) return;
    setBusy(true);
    setInstallError(false);
    try {
      await prompt.prompt();
      await prompt.userChoice;
    } catch {
      setInstallError(true);
    } finally {
      setPrompt(null);
      setBusy(false);
    }
  };
  return { ready, installed, ios, online, canPrompt: Boolean(prompt), busy, installError, install };
}