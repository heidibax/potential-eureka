export function renderCompanies(container, companies) {
	container.innerHTML = "";
	
	companies.forEach(company => {
		const card = document.createElement("div");
		card.className = "company-card";
	
		const name = document.createElement("h2");
		name.textContent = company.name;

		const industry = document.createElement("p");
		industry.textContent = company.industry;
		
		const img = document.createElement("img");
		img.src = company.img;
		img.width = 200;
		
		card.append(name, industry, img)
		
	
		
		container.appendChild(card);
	});
}

	
