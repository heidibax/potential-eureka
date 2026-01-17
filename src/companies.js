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
		
		//make drop-down
		const scoreBtn = document.createElement("button");
		scoreBtn.className = "score-btn";
		scoreBtn.textContent = `Score: ${company.score}`;

		const details = document.createElement("div");
		details.className = "score-details";
		details.style.display = "none";
	
		details.innerHTML = `
			<p>EPS: ${company.breakdown.eps}</p>
			<p>Revenue: ${company.breakdown.revenue}</p>
			<p>Guidance: ${company.breakdown.guidance_score}</p>
			<p>Bonus: ${company.breakdown.bonus_score}</p>
			<p>Tags: ${company.breakdown.tags}</p>
		`;
	
		scoreBtn.addEventListener("click", () => {
			const isOpen = details.style.display === "block";
			details.style.display = isOpen ? "none" : "block";
		});

		card.append(name, industry, img, scoreBtn, details)
		container.appendChild(card);
	});
}

	
