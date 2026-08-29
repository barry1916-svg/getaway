function renderCountryCard(c) {
    const flag = FLAGS[c.country] || "🌍";
    return `<a class="country-card" href="/country/${encodeURIComponent(c.country)}">
        <div class="country-flag">${flag}</div>
        <div class="country-name">${c.country}</div>
        <div class="country-meta">${c.count} destination${c.count !== 1 ? "s" : ""}</div>
        <div class="country-best">Best: ${c.best_city}, ${c.best_temp}° · ${c.best_good_days} sunny day${c.best_good_days !== 1 ? "s" : ""}</div>
    </a>`;
}

async function loadCountries(force = false) {
    const url = force ? "/api/countries?refresh=1" : "/api/countries";
    try {
        const res = await fetch(url);
        if (!res.ok) throw new Error("API error " + res.status);
        const data = await res.json();

        document.getElementById("loading").style.display = "none";
        document.getElementById("last-updated").textContent = "Updated " + data.updated_at;
        document.getElementById("error").style.display = "none";

        const grid = document.getElementById("country-grid");
        grid.style.display = "grid";
        grid.innerHTML = data.countries.map(renderCountryCard).join("");

        // Schedule silent auto-refresh in 1 hour
        setTimeout(() => loadCountries(false), 60 * 60 * 1000);

    } catch (e) {
        document.getElementById("loading").style.display = "none";
        document.getElementById("error").style.display = "block";
        document.getElementById("last-updated").textContent = "Failed to load";
    }
}

async function manualRefresh() {
    const btn = document.getElementById("refresh-btn");
    btn.disabled = true;
    document.getElementById("last-updated").textContent = "Refreshing…";
    await loadCountries(true);
    btn.disabled = false;
}

loadCountries();
