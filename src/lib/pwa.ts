export interface InstallPromptEvent extends Event {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: "accepted" | "dismissed" }>;
}

export function isIOS(userAgent: string, platform: string, touchPoints: number) {
  return /iPad|iPhone|iPod/i.test(userAgent) || (platform === "MacIntel" && touchPoints > 1);
}

export function isStandalone(displayMode: boolean, iosStandalone: boolean) {
  return displayMode || iosStandalone;
}