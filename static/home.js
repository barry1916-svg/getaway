function renderCountryCard(c) {
    const flag = FLAGS[c.country] || "🌍";
    const bestLine = c.count > 0
        ? `Best: ${c.best_city}, ${c.best_temp}° · ${c.best_good_days} sunny day${c.best_good_days !== 1 ? "s" : ""}`
        : "No destinations meet the criteria right now";
    return `<a class="country-card" href="/country/${encodeURIComponent(c.country)}">
        <div class="country-flag">${flag}</div>
        <div class="country-name">${c.country}</div>
        <div class="country-meta">${c.count} destination${c.count !== 1 ? "s" : ""}</div>
        <div class="country-best">${bestLine}</div>
    </a>`;
}

function renderOriginPanelCard(p) {
    const bestLine = p.count > 0
        ? `Best: ${p.best_city}, ${p.best_temp}° · ${p.best_good_days} sunny day${p.best_good_days !== 1 ? "s" : ""}`
        : "No destinations meet the criteria right now";
    return `<a class="country-card" href="/origin/${encodeURIComponent(p.key)}">
        <div class="country-flag">${p.icon}</div>
        <div class="country-name">${p.label}</div>
        <div class="country-meta">${p.count} destination${p.count !== 1 ? "s" : ""}</div>
        <div class="country-best">${bestLine}</div>
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
        grid.innerHTML = data.countries.map(renderCountryCard).join("") + data.origin_panels.map(renderOriginPanelCard).join("");

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
