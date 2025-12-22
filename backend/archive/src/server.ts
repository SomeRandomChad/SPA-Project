import express from "express";
import { rephraseRoute } from "./routes/rephrase.route";

const app = express();

// middleware to parse JSON bodies
app.use(express.json());

// Routes
app.post("/rephrase", rephraseRoute);

// start the server
const PORT = Number(process.env.PORT) || 3000;
app.listen(PORT, () => {
	console.log(`API listening on port ${PORT}`);
});