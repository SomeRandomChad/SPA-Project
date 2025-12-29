// frontend/src/api/rephraseStream.ts
import type { RephraseResponse } from "./rephrase";

export type StreamEvent =
  | { type: "partial"; style: keyof RephraseResponse; delta: string }
  | { type: "final"; data: RephraseResponse }
  | { type: "error"; error: { code: string; message: string; details?: any[] } };

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

/**
 * Parse SSE text frames and emit events.
 * Works with POST /rephrase/stream (SSE over fetch).
 */
export async function* rephraseStream(
  text: string,
  signal?: AbortSignal
): AsyncGenerator<StreamEvent, void, void> {
  const resp = await fetch("http://127.0.0.1:3000/rephrase/stream", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
    signal,
  });

  // For SSE, many servers still respond 200 even on logical errors.
  // We handle both non-200 and event:error.
  if (!resp.ok) {
    let msg = `Request failed (${resp.status})`;
    try {
      const body = (await resp.json()) as any;
      if (body?.message && typeof body.message === "string") msg = body.message;
      if (body?.detail && typeof body.detail === "string") msg = body.detail;
    } catch {
      // ignore
    }
    yield { type: "error", error: { code: "HTTP_ERROR", message: msg } };
    return;
  }

  if (!resp.body) {
    yield { type: "error", error: { code: "STREAM_ERROR", message: "No response body." } };
    return;
  }

  const reader = resp.body.getReader();
  const decoder = new TextDecoder("utf-8");

  let buffer = "";

  // SSE frames are separated by a blank line (LF or CRLF).
  const emitFrames = async function* (chunkText: string): AsyncGenerator<string> {
    buffer += chunkText; 
    // Find either "\n\n" or "\r\n\r\n"
    while (true) {
      const lfIdx = buffer.indexOf("\n\n");
      const crlfIdx = buffer.indexOf("\r\n\r\n");

      let idx = -1;
      let delimLen = 0;

      if (crlfIdx !== -1 && (lfIdx === -1 || crlfIdx < lfIdx)) {
        idx = crlfIdx;
        delimLen = 4;
      } else if (lfIdx !== -1) {
        idx = lfIdx;
        delimLen = 2;
      } else {
        break;
      }

      const frame = buffer.slice(0, idx);
      buffer = buffer.slice(idx + delimLen);
      if (frame.trim()) yield frame;
    }
  };

  try {
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      const chunkText = decoder.decode(value, { stream: true });

      for await (const frame of emitFrames(chunkText)) {
        // Parse a single SSE frame
        // Example:
        // event: partial
        // data: {"style":"professional","delta":"Hi"}
        let eventType = "message";
        let dataLine = "";

        for (const line of frame.split("\n")) {
          if (line.startsWith("event:")) {
            eventType = line.slice("event:".length).trim();
          } else if (line.startsWith("data:")) {
            // data may appear multiple times; we concatenate
            const part = line.slice("data:".length).trimStart();
            dataLine = dataLine ? dataLine + "\n" + part : part;
          }
        }

        // Ignore frames with no data
        if (!dataLine) continue;

        let data: any;
        try {
          data = JSON.parse(dataLine);
        } catch {
          yield {
            type: "error",
            error: { code: "STREAM_PARSE_ERROR", message: "Invalid JSON in SSE data." },
          };
          continue;
        }

        if (eventType === "partial") {
          const style = data?.style;
          const delta = data?.delta;
          const okStyle =
            style === "professional" || style === "casual" || style === "polite" || style === "social";
          if (okStyle && typeof delta === "string") {
            yield { type: "partial", style, delta };
          } else {
            yield {
              type: "error",
              error: { code: "STREAM_PARSE_ERROR", message: "Invalid partial event shape." },
            };
          }
        } else if (eventType === "final") {
          if (isRephraseResponse(data)) {
            yield { type: "final", data };
            return;
          }
          yield {
            type: "error",
            error: { code: "STREAM_PARSE_ERROR", message: "Invalid final response shape." },
          };
        } else if (eventType === "error") {
          // Expect your Error shape
          const code = typeof data?.code === "string" ? data.code : "STREAM_ERROR";
          const message = typeof data?.message === "string" ? data.message : "Stream error";
          const details = Array.isArray(data?.details) ? data.details : [];
          yield { type: "error", error: { code, message, details } };
          return;
        }
      }
    }

    // If stream ended without final, surface it
    yield {
      type: "error",
      error: { code: "STREAM_ENDED", message: "Stream ended before final response." },
    };
  } finally {
    try {
      reader.releaseLock();
    } catch {
      // ignore
    }
  }
}
