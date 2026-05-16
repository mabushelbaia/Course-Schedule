import type { UploadResponse, CalendarResponse } from "./types";

const BASE = "/api";

export async function uploadFile(file: File): Promise<UploadResponse> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${BASE}/upload`, { method: "POST", body: form });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Upload failed");
  }
  return res.json();
}

export async function liveFetch(username: string, password: string): Promise<UploadResponse> {
  const form = new FormData();
  form.append("username", username);
  form.append("password", password);
  const res = await fetch(`${BASE}/live`, { method: "POST", body: form });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Fetch failed");
  }
  return res.json();
}

export async function fetchCalendar(): Promise<CalendarResponse> {
  const res = await fetch(`${BASE}/calendar`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Calendar fetch failed");
  }
  return res.json();
}
