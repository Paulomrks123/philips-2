import { describe, expect, it } from "vitest";
import { isIOS, isStandalone } from "@/lib/pwa";

describe("PWA installation platform rules", () => {
  it("uses iOS guidance for iPhone Safari", () => {
    expect(isIOS("Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X)", "iPhone", 5)).toBe(true);
  });
  it("uses iOS guidance for iPad Safari in desktop mode", () => {
    expect(isIOS("Mozilla/5.0 Macintosh", "MacIntel", 5)).toBe(true);
  });
  it("does not use iOS guidance for Android Chrome", () => {
    expect(isIOS("Mozilla/5.0 (Linux; Android 15) Chrome/130", "Linux armv8l", 5)).toBe(false);
  });
  it("recognizes installed Android standalone mode", () => {
    expect(isStandalone(true, false)).toBe(true);
  });
  it("recognizes installed iOS standalone mode", () => {
    expect(isStandalone(false, true)).toBe(true);
  });
  it("keeps installation available in a normal browser tab", () => {
    expect(isStandalone(false, false)).toBe(false);
  });
});