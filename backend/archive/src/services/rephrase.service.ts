export type RephraseRequest = {
  text: string;
};

export type RephraseResponse = {
  professional: string;
  casual: string;
  polite: string;
  social: string;
};

export class ValidationError extends Error {
  constructor(message: string) {
  super(message);
  this.name = "ValidationError";
  Object.setPrototypeOf(this, ValidationError.prototype);
	}
 }
 
 function validateInput(input: RephraseRequest): string {
	const text = input?.text;
	
	if(typeof text !== "string"){
		throw new ValidationError(`"text" must be a string`);
	}
	
	const trimmed = text.trim()
	if (trimmed.length === 0) {
		throw new ValidationError(`"text" must not be empty`);
	}
	
	const MAX_LEN = 5000;
	if (trimmed.length > MAX_LEN) {
		throw new ValidationError(`"text" must be <= ${MAX_LEN} characters`);
	}

  return trimmed;
  }
  
  export async function rephraseService(input: RephraseRequest): Promise<RephraseResponse> {
	const text = validateInput(input);
	
	return{
		professional: text,
		casual: text,
		polite: text,
		social: text,
	};
}