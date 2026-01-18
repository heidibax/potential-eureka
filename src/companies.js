export function renderCompanies(container, companies) {
	container.innerHTML = "";
	
	companies.forEach(company => {
		const card = document.createElement("div");
		card.className = "company-card";
	
		const name = document.createElement("h2");
		name.textContent = company.name || company.ticker;

		const earningsDate = document.createElement("p");
		earningsDate.textContent = `Earnings: ${company.earnings_date || 'N/A'}`;
		
		const img = document.createElement("img");
		img.src = company.img;
		img.width = 200;
		img.className = "company-img";
		img.alt = company.name || company.ticker;
		img.onerror = function() {
			this.src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200"><rect fill="%23ccc"/><text x="50%25" y="50%25" text-anchor="middle" dy=".3em" fill="%23999">${company.ticker}</text></svg>';
		};
		
		//make drop-down
		const scoreBtn = document.createElement("button");
		scoreBtn.className = "score-btn";
		scoreBtn.textContent = `Score: ${company.score || 0}`;

		const details = document.createElement("div");
		details.className = "score-details";
		details.style.display = "none";
	
		details.innerHTML = `
			<p><strong>EPS Result:</strong> ${company.breakdown.eps_result || 'N/A'}</p>
			<p><strong>EPS Points:</strong> ${company.breakdown.eps || 0}</p>
			<p><strong>Daily Change Points:</strong> ${company.breakdown['daily percent change'] || 0}</p>
			<p><strong>Monthly Change Points:</strong> ${company.breakdown['monthly percent change'] || 0}</p>
			<p><strong>Bonus Points:</strong> ${company.breakdown.bonus || 0}</p>
			<p><strong>Tags:</strong> ${company.breakdown.tags || 'None'}</p>
		`;
	
		scoreBtn.addEventListener("click", () => {
			const isOpen = details.style.display === "block";
			details.style.display = isOpen ? "none" : "block";
		});

		card.append(name, earningsDate, img, scoreBtn, details);
		container.appendChild(card);
	});
}

	
