export function renderCompanies(container, companies) {
	container.innerHTML = "";
	
	companies.forEach(company => {
		const card = document.createElement("div");
		card.className = "company-card";
	
		const name = document.createElement("h2");
		name.textContent = company.name;

		const industry = document.createElement("p");
		industry.textContent = company.industry;

		card.append(name, industry)
		container.appendChild(card);
	});
}

	
