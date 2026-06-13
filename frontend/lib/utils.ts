import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatTime(isoString: string): string {
  try {
    const date = new Date(isoString);
    return date.toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit", hour12: true, timeZone: "Asia/Kolkata" });
  } catch { return isoString; }
}

export function getPriorityColor(priority: string): string {
  switch (priority) {
    case "critical": return "text-red-400 border-red-500/40 bg-red-500/10";
    case "high": return "text-orange-400 border-orange-500/40 bg-orange-500/10";
    case "normal": return "text-blue-400 border-blue-500/30 bg-blue-500/10";
    default: return "text-gray-400 border-gray-500/30 bg-gray-500/10";
  }
}

export function getConfidenceColor(confidence: number): string {
  if (confidence >= 0.9) return "text-emerald-400";
  if (confidence >= 0.7) return "text-blue-400";
  if (confidence >= 0.5) return "text-yellow-400";
  return "text-gray-400";
}
