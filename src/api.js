const API_BASE_URL = ""; // use same origin to avoid CORS mismatches between 127.0.0.1 and localhost

async function request(endpoint, options = {}) {
	const response = await fetch(`${API_BASE_URL}${endpoint}`, {
		headers: {
			"Content-Type": "application/json",
			...options.headers,
		},
		...options,
	});

	if (!response.ok) {
		const message = await response.text();
		throw new Error(message || "API error");
	}

	return response.json();
}

const MOCK_COMPANIES = [
	{ id: 1, name: "Meta Platforms", ticker: "META", img: "https://via.placeholder.com/64" },
	{ id: 2, name: "Apple", ticker: "AAPL", img: "https://via.placeholder.com/64" },
	{ id: 3, name: "Microsoft", ticker: "MSFT", img: "https://via.placeholder.com/64" },
	{ id: 4, name: "Amazon", ticker: "AMZN", img: "https://via.placeholder.com/64" },
	{ id: 5, name: "NVIDIA", ticker: "NVDA", img: "https://via.placeholder.com/64" },
];

export async function getCompanies() {
	try {
		const stocks = await request("/api/stocks");
		// Map API response into the shape the UI expects
		return stocks.map((stock, index) => ({
			id: index + 1,
			name: stock.ticker,
			ticker: stock.ticker,
			price: stock.price,
			img: "https://via.placeholder.com/64",
		}));
	} catch (err) {
		console.error("getCompanies fallback to mock data", err);
		return MOCK_COMPANIES;
	}
}

export function getCompanyByID(id) {
	return request(`/companies/${id}`);
}

export function getDraftedCompanies() {
	return request("/companies/drafted");
}
