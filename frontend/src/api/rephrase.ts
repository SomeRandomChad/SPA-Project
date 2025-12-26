export type RephraseResponse = {
  professional: string;
  casual: string;
  polite: string;
  social: string;
};

function isRephraseResponse(x: unknown): x is RephraseResponse {
  if (!x || typeof x !== "object") return false;
  const o = x as Record<string, unknown>;
  return (
    typeof o.professional === "string" &&
    typeof o.casual === "string" &&
    typeof o.polite === "string" &&
    typeof o.social === "string"
  );
}

export async function rephrase(
  text: string, signal?: AbortSignal
): Promise<RephraseResponse> {
  const resp = await fetch("/rephrase", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
    signal,
  });

  if (!resp.ok) {
    let msg = `Request failed (${resp.status})`;
    try {
      const body = (await resp.json()) as any;
      if (body?.message && typeof body.message === "string") msg = body.message;
      if (body?.error && typeof body.error === "string") msg = body.error;
    } catch {
      // ignore JSON parse errors
    }
    throw new Error(msg);
  }

  const data: unknown = await resp.json();

  if (!isRephraseResponse(data)) {
    throw new Error("Invalid response shape from server");
  }

  return data;
}
