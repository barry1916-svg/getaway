const FLAGS = {
    "Spain": "🇪🇸", "Portugal": "🇵🇹", "Italy": "🇮🇹", "Greece": "🇬🇷",
    "Croatia": "🇭🇷", "Cyprus": "🇨🇾", "France": "🇫🇷", "Netherlands": "🇳🇱",
    "Belgium": "🇧🇪", "Switzerland": "🇨🇭", "Austria": "🇦🇹", "Hungary": "🇭🇺",
    "Czech Republic": "🇨🇿", "Poland": "🇵🇱", "Sweden": "🇸🇪", "Denmark": "🇩🇰",
    "Norway": "🇳🇴", "Finland": "🇫🇮", "Latvia": "🇱🇻", "Estonia": "🇪🇪",
    "Lithuania": "🇱🇹", "Bulgaria": "🇧🇬", "Romania": "🇷🇴", "Turkey": "🇹🇷",
    "Montenegro": "🇲🇪", "Slovenia": "🇸🇮", "Malta": "🇲🇹",
    "Slovakia": "🇸🇰",
};

function formatDate(dateStr) {
    const d = new Date(dateStr + "T12:00:00");
    return d.toLocaleDateString("en-GB", { day: "numeric", month: "short" });
}

function getDayShort(dateStr) {
    const d = new Date(dateStr + "T12:00:00");
    return d.toLocaleDateString("en-GB", { weekday: "short" }).slice(0, 3);
}

function renderCard(dest) {
    const flag = FLAGS[dest.country] || "🌍";
    const depart = formatDate(dest.depart_date);
    const ret = formatDate(dest.return_date);

    const forecastHTML = dest.forecast.slice(0, 7).map(day => {
        const temp = day.temp !== null ? Math.round(day.temp) + "°" : "—";
        const label = getDayShort(day.date);
        return `<div class="forecast-day${day.is_good ? " sunny" : ""}">
            <div class="day-icon">${day.icon}</div>
            <div class="day-temp">${temp}</div>
            <div class="day-label">${label}</div>
        </div>`;
    }).join("");

    const routesHTML = dest.routes.map(r =>
        `<a class="route-tag" href="${r.url}" target="_blank" rel="noopener noreferrer"><span class="airline">${r.airline}</span><span>from ${r.airport}</span></a>`
    ).join("");

    const sunnyText = `${dest.good_days_count} sunny day${dest.good_days_count !== 1 ? "s" : ""}`;

    const bookHTML = `
        <div class="book-links">
            <a class="book-link skyscanner" href="${dest.skyscanner_url}" target="_blank" rel="noopener noreferrer">✈ Flights</a>
            <a class="book-link airbnb"     href="${dest.airbnb_url}"     target="_blank" rel="noopener noreferrer">🏠 Stays</a>
            <a class="book-link booking"    href="${dest.booking_url}"    target="_blank" rel="noopener noreferrer">🏨 Hotels</a>
        </div>`;

    return `<div class="card">
        <div class="card-header">
            <div class="city-info">
                <div class="flag">${flag}</div>
                <div class="city-name">${dest.city}</div>
                <div class="country-name">${dest.country}</div>
            </div>
            <div class="temp-badge">
                <div class="temp-value">${dest.best_temp}°</div>
                <div class="temp-label">max °C</div>
            </div>
        </div>
        <div class="card-body">
            <div class="sunny-badge">☀️ ${sunnyText}</div>
            <div class="dates">✈️ <strong>${depart}</strong>&nbsp;—&nbsp;<strong>${ret}</strong></div>
            <div class="forecast-strip">${forecastHTML}</div>
            <div class="routes">${routesHTML}</div>
            ${bookHTML}
        </div>
    </div>`;
}
