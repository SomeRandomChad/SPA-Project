import React, { useMemo, useRef, useState } from "react";
import { rephrase, type RephraseResponse } from "./api/rephrase";

type Status = "idle" | "loading" | "success" | "error";


const emptyResult: RephraseResponse = {
  professional: "",
  casual: "",
  polite: "",
  social: "",
};

function Panel({ title, value }: { title: string; value: string }) {
  return (
    <section style={{ border: "1px solid #ddd", borderRadius: 8, padding: 12 }}>
      <h3 style={{ margin: "0 0 8px 0" }}>{title}</h3>
      <div
        style={{
          whiteSpace: "pre-wrap",
          color: value ? "#111" : "#777",
          minHeight: 48,
        }}
      >
        {value || "—"}
      </div>
    </section>
  );
}

function isAbortError(err: unknown): boolean {
  return (
    typeof err === "object" &&
    err !== null &&
    "name" in err &&
    (err as any).name === "AbortError"
  );
}

export default function App() {
  const [text, setText] = useState<string>("");
  const [status, setStatus] = useState<Status>("idle");
  const [result, setResult] = useState<RephraseResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const abortRef = useRef<AbortController | null>(null);

  const isLoading = status === "loading";
  const canSubmit = useMemo(
    () => text.trim().length > 0 && !isLoading,
    [text, isLoading]
  );

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();

    const trimmed = text.trim();
    if (!trimmed) {
      setStatus("error");
      setErrorMessage("Please enter some text.");
      setResult(null);
      return;
    }

    abortRef.current?.abort();

    const controller = new AbortController();
    abortRef.current = controller;

    setStatus("loading");
    setErrorMessage(null);

    try {
      const data = await rephrase(trimmed, controller.signal);
      if (controller.signal.aborted) return;

      setResult(data);
      setStatus("success");
    } catch (err) {
      if (isAbortError(err)){
        setStatus("idle");
        setErrorMessage(null);
        return
      }

      const msg = err instanceof Error ? err.message : "Something went wrong";
      setResult(null);
      setStatus("error");
      setErrorMessage(msg);
    } finally {
      if (abortRef.current === controller) {
        abortRef.current = null;
      }
    }
  }

  function onCancel() {
    abortRef.current?.abort();
    abortRef.current = null;
    setStatus("idle");
    setErrorMessage(null);
  }

  const display = result ?? emptyResult;

  return (
    <div style={{ maxWidth: 900, margin: "24px auto", padding: 16, fontFamily: "system-ui" }}>
      <h1 style={{ marginTop: 0 }}>LLM Rephrase</h1>

      <form onSubmit={onSubmit} style={{ display: "grid", gap: 12 }}>
        <label style={{ display: "grid", gap: 6 }}>
          <span>Input</span>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            rows={6}
            placeholder="Paste or type your text here..."
            style={{ padding: 12, borderRadius: 8, border: "1px solid #ccc", resize: "vertical" }}
          />
        </label>

    <div style={{ display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap" }}>
      <button
        type="submit"
        disabled={!canSubmit}
        style={{
          padding: "10px 14px",
          borderRadius: 8,
          border: "1px solid #111",
          background: canSubmit ? "#111" : "#666",
          color: "#fff",
          cursor: canSubmit ? "pointer" : "not-allowed",
        }}
      >
        {isLoading ? "Rephrasing..." : "Rephrase"}
      </button>

      {isLoading && (
        <button
          type="button"
          onClick={onCancel}
          style={{
            padding: "10px 14px",
            borderRadius: 8,
            border: "1px solid #999",
            background: "#fff",
            color: "#111",
            cursor: "pointer",
          }}
        >
          Cancel
        </button>
      )}

      {isLoading && <span style={{ color: "#555" }}>Loading...</span>}
    </div>

        {status === "error" && errorMessage && (
          <div
            role="alert"
            style={{
              padding: 12,
              borderRadius: 8,
              border: "1px solid #f3b5b5",
              background: "#fff5f5",
              color: "#8a1f1f",
            }}
          >
            {errorMessage}
          </div>
        )}
      </form>

      <div style={{ marginTop: 18, display: "grid", gap: 12 }}>
        <Panel title="Professional" value={display.professional} />
        <Panel title="Casual" value={display.casual} />
        <Panel title="Polite" value={display.polite} />
        <Panel title="Social media" value={display.social} />
      </div>
    </div>
  );
}
