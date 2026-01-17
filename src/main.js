import { getCompanies } from "./api.js";
import { renderCompanies } from ".companies.js";

document.addEventListener("DOMContentLoaded, async () => {
	const container = document.getElementById("companies");

	try {
		const companies = await getCompanies();
		renderCompanies(container, companies);
	} catch (err) {
		container.textContent = "Failed to load companies";
		console.error(err);
	}
});



