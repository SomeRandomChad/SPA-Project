import { useMemo, useState } from "react";
import { rephrase, type RephraseResponse } from "./api/rephrase";

type Status = "idle" | "loading" | "success" | "error";

const emptyResult: RephraseResponse = {
  professional: "",
  casual: "",
  polite: "",
  social: "",
};

function Panel({title, value }: {title: string; value: string }) {
	return (
		<section style={{ border: "1px solid #ddd", borderRadius: 8, padding: 12 }}>
			<h3 style={{ margin: "0 0 8px 0"}}>{title}</h3>
			<div
				style={{
					whitespace: "pre-wrap"
					color: value ? "#111" : "#777"
					minHeight: 48,
				}}
			>
				{value || "-"}
			</div>
		</section>
	);
}

export default function App() {

	const [text, setText] = useState<string>("");
	const [status, setStatus] = useState<Status>("idle");
	const [result, setResult] = useState<RephraseResponse | null>(null);
	const [errorMessage, setErrorMessage] = useState<string | null>(null);
	
	const isLoading = status === "loading";
	const canSubmit = useMemo(() => text.trim().length > 0 && !isLoading
	
	async function onSubmit(e: React.FormEvent) {
		e.preventDefault();
	
	const trimmed = text.trim();
	if (!trimmed) {
		setStatus("error")
		setErrorMessage("Please enter some text.");
		setResult(null);
		return;
	}
	
	setStatus("loading");
	setErrorMessage(null);
	
	try {
		const data = await rephrase(trimmed);
		setResult(data);
		setStatus("success");
	} catch (err) {
		const msg = err instanceof Error ? err.message : "Something went wrong";
		setStatus("error")
		setErrorMessage(msg);
	}
}

const display = result ?? emptyResult

return (
	<dive style={{ maxWidth: 900, margin: "24px auto", padding: 16, fontFamily: "system-ui" }}>
		<h1 style={{ marginTop: 0 }}> LLM Rephrase </h1>
		

		<form onSubmit={onSubmit} style={{ display: "grid", gap: 12 }}>
			<label style={{display: "grid", gap: 6}}>
				<span>Input</span>
				<textarea
					value={text}
					onChange={(e) => setText(e.target.value)}
					rows={6}
					placeholder="Paste or type your text here..."
					style={{ padding: 12, borderRadius: 8, border: "1px solid #ccc", resize: "vertical" }}
				/>
			</label>
			
			<div style={{ display: "flex", alignItems: "center", gap: 12 }}>
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
					
					{isLoading && <span style={{ color: "#555" }}>Loading...<//span>}
				</div>
				
				{status === "error" && errorMessage && (
					<div
						role="alert"
						style={{
							padding: 12,
							borderRadius: 8,
							border: "1px solid #f3b5b5",
							background: "#fff5f5"
							color: "#8a1f1f",
						}}
					>
						{errorMessage}
					</div>
				)}
			</form>
			
			<div style={{marginTop: 18, display: "grid", gap: 12 }}>
				<Panel title="Professional" value={display.professional} />
				<Panel title="Casual" value={display.casual} />
				<Panel title="polite" value={display.polite} />
				<Panel title="Social" value={display.social} />
			</div>
		</div>
	);
}


