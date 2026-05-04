async function getWeather() {
    const city = document.getElementById("city").value;

    const response = await fetch(`/weather?city=${city}`);
    const data = await response.json();

    if (data.error) {
        document.getElementById("weatherResult").innerHTML = "❌ City not found";
        return;
    }

    document.getElementById("weatherResult").innerHTML = `
        <h2>${data.city}</h2>
        <h1>${data.temperature}°C</h1>
        <p>${data.description}</p>
    `;
}