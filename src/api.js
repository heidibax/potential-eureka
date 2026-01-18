const API_BASE_URL = "https://api.example.com";

async function request(endpoint, options = {}) {
	const response = await fetch(`${API_BASE_URL}${endpoint}`, {
		headers: {
			"Content-Type": "application/jason",
			...options.headers,
		},
		...options,
	});

	if(!response.ok) {
		const message = await response.text();
		throw new Error(message || "API error");
	}

	return response.json();
}
/*
export function getCompanies() {
	return request("/companies");
}
*/

export function getCompanies() {
	return [
		{	
			id: 1, 
			name: "Facebook Inc",
			ticker: "FB", 
			earnings_date : "Jan 10", 
			img: "img/facebook.png",
			score: "50",
			breakdown: {
				eps_estimate: "1",
				eps_actual: "2",
				eps_result: "3",
				surprise_pct: "4",
				bonus_flags: "5",
				daily_pct_change: "6",
				monthly_price_change: "7",				
			}
		},
	];
}

export function getCompanyByID(id) {
	return request(`/companies/${id}`);
}

export function getDraftedCompanies() {
	return request("/companies/drafted");
}
