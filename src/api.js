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
			name: "Facebook", 
			earnings_date : "Jan 10", 
			img: "img/Facebook.jpg",
			score: "50",
			breakdown: {
				eps: "1",
				revenue: "2",
				guidance_score: "3",
				bonus_score: "4",
				tags: "5",				
			}
		},
		{ 	id: 2, 
			name: "ESSO", 
			earnings_date : "Feb 5", 
			img: "img/ESSO.jpg",
			score: "30",
			breakdown: {
				eps: "1",
				revenue: "2",
				guidance_score: "3",
				bonus_score: "4",
				tags: "5",
			}
		 }
	];
}

export function getCompanyByID(id) {
	return request(`/companies/${id}`);
}
