import { Request, Response } from "express";
import { rephraseService, ValidationError } from "../services/rephrase.service";

export async function rephraseRoute(req: Request, res: Response) {

try {
    // Basic input validation (optional but recommended)
    const text = req.body?.text;
    if (typeof text !== "string" || !text.trim()) {
      return res
        .status(400)
        .json({ error: "Field 'text' is required and must be a non-empty string." });
    }

    const result = await rephraseService({ text });
    return res.status(200).json(result);
  } catch (err) {
    // Service-level validation error
    if (err instanceof ValidationError) {
      return res.status(400).json({ error: err.message });
    }

    // Generic runtime error
    if (err instanceof Error) {
      console.error("Unhandled error in /rephrase:", err);
      return res.status(500).json({ error: "Internal server error", details: err.message });
    }

    // Truly unknown
    console.error("Unhandled non-Error in /rephrase:", err);
    return res.status(500).json({ error: "Internal server error" });
  }
}