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
		{ id: 1, name: "Facebook", industry : "Techno", img: "img/Facebook.jpg" },
		{ id: 2, name: "ESSO", industry : "Energy", img: "img/ESSO.jpg" }
	];
}

export function getCompanyByID(id) {
	return request(`/companies/${id}`);
}
