import { useState } from "react";
import { Download, Share, PlusSquare, WifiOff } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { usePwaLifecycle } from "@/hooks/use-pwa-lifecycle";
import appIcon from "@/assets/remote-192.png.asset.json";

export function PwaLifecycle() {
  const { ready, installed, ios, online, canPrompt, busy, installError, install } = usePwaLifecycle();
  const [open, setOpen] = useState(false);
  if (!ready) return null;

  return (
    <>
      {!online && <p role="status" className="flex items-center justify-center gap-2 bg-muted px-3 py-2 text-xs text-muted-foreground"><WifiOff className="size-4" />Sem conexão. Reabrir o app exige internet.</p>}
      {!installed && (
        <div className="install-strip">
          <img src={appIcon.url} alt="" width={36} height={36} className="size-9 rounded-md" />
          <div className="min-w-0 flex-1"><p className="text-sm font-medium">Philips Remote</p><p className="text-xs text-muted-foreground">Na tela inicial do seu celular</p></div>
          <Button size="sm" disabled={busy} onClick={() => canPrompt ? void install() : setOpen(true)}><Download />{busy ? "Aguarde" : "Instalar"}</Button>
        </div>
      )}
      {installError && <p role="alert" className="px-4 py-2 text-center text-xs text-muted-foreground">Não foi possível abrir a instalação. Tente pelo menu do navegador.</p>}
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="max-h-[85dvh] w-[calc(100%-2rem)] max-w-sm overflow-y-auto rounded-lg">
          <DialogHeader>
            <img src={appIcon.url} alt="Ícone Philips Remote" width={64} height={64} className="mb-2 size-16 self-center rounded-lg" />
            <DialogTitle className="tracking-normal">Instalar Philips Remote</DialogTitle>
            <DialogDescription>Adicione o controle à tela inicial.</DialogDescription>
          </DialogHeader>
          {ios ? (
            <ol className="space-y-4 text-sm">
              <li>1. Abra este site publicado no <strong>Safari</strong>.</li>
              <li className="flex items-center gap-2">2. Toque em <Share className="size-5 shrink-0 text-primary" aria-hidden="true" /><strong>Compartilhar</strong>.</li>
              <li className="flex items-center gap-2">3. Escolha <PlusSquare className="size-5 shrink-0 text-primary" aria-hidden="true" /><strong>Adicionar à Tela de Início</strong>.</li>
              <li>4. Ative “Abrir como App”, se aparecer, e toque em <strong>Adicionar</strong>.</li>
            </ol>
          ) : (
            <ol className="space-y-4 text-sm">
              <li>1. Abra este site publicado no <strong>Chrome</strong> (Android) ou no navegador do seu dispositivo.</li>
              <li>2. Abra o menu do navegador e escolha <strong>Instalar aplicativo</strong> ou <strong>Adicionar à tela inicial</strong>.</li>
              <li>3. Confirme em <strong>Instalar</strong> ou <strong>Adicionar</strong>.</li>
            </ol>
          )}
          <p className="text-xs text-muted-foreground">A opção depende do navegador. A instalação não habilita infravermelho nem modo offline.</p>
          <Button variant="secondary" onClick={() => setOpen(false)}>Entendi</Button>
        </DialogContent>
      </Dialog>
    </>
  );
}