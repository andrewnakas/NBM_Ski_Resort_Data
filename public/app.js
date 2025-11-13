// Main application logic
let currentResort = null;
let forecastData = null;

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    initializeResortSelector();
    loadForecastData();
});

// Populate resort selector dropdown
function initializeResortSelector() {
    const select = document.getElementById('resort-select');
    select.innerHTML = '<option value="">Select a ski resort...</option>';

    skiResorts.forEach((resort, index) => {
        const option = document.createElement('option');
        option.value = index;
        option.textContent = `${resort.name} (${resort.state})`;
        select.appendChild(option);
    });

    select.addEventListener('change', (e) => {
        if (e.target.value !== '') {
            currentResort = skiResorts[e.target.value];
            updateResortInfo();
            renderCharts();
        }
    });

    // Select first resort by default
    if (skiResorts.length > 0) {
        select.value = 0;
        currentResort = skiResorts[0];
        updateResortInfo();
    }
}

// Update resort information display
function updateResortInfo() {
    if (!currentResort) return;

    document.getElementById('resort-elevation').textContent =
        `Elevation: ${currentResort.elevation}m`;
    document.getElementById('resort-coords').textContent =
        `Coordinates: ${currentResort.lat.toFixed(4)}°N, ${Math.abs(currentResort.lon).toFixed(4)}°W`;
}

// Load forecast data (from generated JSON or use sample data)
async function loadForecastData() {
    try {
        const response = await fetch('data/forecast.json');
        if (response.ok) {
            forecastData = await response.json();
            updateLastUpdateTime();
            renderCharts();
        } else {
            // Use sample data if no real data available
            forecastData = generateSampleData();
            updateLastUpdateTime();
            renderCharts();
        }
    } catch (error) {
        console.log('Using sample data');
        forecastData = generateSampleData();
        updateLastUpdateTime();
        renderCharts();
    }
}

// Update last update timestamp
function updateLastUpdateTime() {
    const lastUpdate = document.getElementById('last-update');
    const now = new Date();
    lastUpdate.textContent = now.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        timeZoneName: 'short'
    });
}

// Generate sample forecast data
function generateSampleData() {
    const hours = 72; // 3-day forecast
    const timestamps = [];
    const now = new Date();

    for (let i = 0; i < hours; i++) {
        const time = new Date(now.getTime() + i * 3600000);
        timestamps.push(time.toISOString());
    }

    return {
        timestamps: timestamps,
        hourlySnow: {
            p10: Array.from({length: hours}, () => Math.random() * 2),
            p50: Array.from({length: hours}, () => Math.random() * 8),
            p90: Array.from({length: hours}, () => Math.random() * 15 + 5),
            p95: Array.from({length: hours}, () => Math.random() * 20 + 10)
        },
        totalSnow: {
            p10: [],
            p50: [],
            p90: [],
            p95: []
        },
        hourlyPrecip: {
            p10: Array.from({length: hours}, () => Math.random() * 3),
            p50: Array.from({length: hours}, () => Math.random() * 10),
            p90: Array.from({length: hours}, () => Math.random() * 18 + 5),
            p95: Array.from({length: hours}, () => Math.random() * 25 + 10)
        },
        snowLevel: {
            p10: Array.from({length: hours}, () => 1500 + Math.random() * 500),
            p50: Array.from({length: hours}, () => 2000 + Math.random() * 500),
            p90: Array.from({length: hours}, () => 2500 + Math.random() * 500),
            p95: Array.from({length: hours}, () => 2800 + Math.random() * 500)
        },
        cumulativePrecip: {
            p10: [],
            p50: [],
            p90: [],
            p95: []
        }
    };
}

// Calculate cumulative values
function calculateCumulative(hourlyData) {
    let sum = 0;
    return hourlyData.map(val => {
        sum += val;
        return sum;
    });
}

// Render all charts
function renderCharts() {
    if (!forecastData || !currentResort) return;

    // Calculate cumulative data
    forecastData.totalSnow = {
        p10: calculateCumulative(forecastData.hourlySnow.p10),
        p50: calculateCumulative(forecastData.hourlySnow.p50),
        p90: calculateCumulative(forecastData.hourlySnow.p90),
        p95: calculateCumulative(forecastData.hourlySnow.p95)
    };

    forecastData.cumulativePrecip = {
        p10: calculateCumulative(forecastData.hourlyPrecip.p10),
        p50: calculateCumulative(forecastData.hourlyPrecip.p50),
        p90: calculateCumulative(forecastData.hourlyPrecip.p90),
        p95: calculateCumulative(forecastData.hourlyPrecip.p95)
    };

    renderHourlySnowChart();
    renderTotalSnowChart();
    renderHourlyPrecipChart();
    renderSnowLevelChart();
    renderCumulativePrecipChart();
}

// Common chart layout
function getChartLayout(title, yaxis) {
    return {
        title: {
            text: '',
            font: { size: 14 }
        },
        xaxis: {
            title: 'Time',
            type: 'date',
            tickformat: '%b %d %H:%M'
        },
        yaxis: {
            title: yaxis,
            rangemode: 'tozero'
        },
        hovermode: 'x unified',
        showlegend: true,
        legend: {
            orientation: 'h',
            y: -0.2
        },
        margin: {
            l: 60,
            r: 30,
            t: 30,
            b: 80
        }
    };
}

// Create probability trace
function createTrace(x, y, name, color, fill = false) {
    return {
        x: x,
        y: y,
        name: name,
        type: 'scatter',
        mode: 'lines',
        line: {
            color: color,
            width: 2
        },
        fill: fill ? 'tonexty' : 'none',
        fillcolor: fill ? color.replace('rgb', 'rgba').replace(')', ', 0.1)') : undefined
    };
}

// Chart 1: Hourly Snow Accumulation
function renderHourlySnowChart() {
    const traces = [
        createTrace(forecastData.timestamps, forecastData.hourlySnow.p10, '10th percentile', 'rgb(0, 100, 200)'),
        createTrace(forecastData.timestamps, forecastData.hourlySnow.p50, '50th percentile (Median)', 'rgb(0, 150, 50)', true),
        createTrace(forecastData.timestamps, forecastData.hourlySnow.p90, '90th percentile', 'rgb(255, 140, 0)', true),
        createTrace(forecastData.timestamps, forecastData.hourlySnow.p95, '95th percentile', 'rgb(200, 0, 0)', true)
    ];

    const layout = getChartLayout('Hourly Snow Accumulation', 'Snow (mm/hr)');
    Plotly.newPlot('hourly-snow-chart', traces, layout, {responsive: true});
}

// Chart 2: Running Total Snow
function renderTotalSnowChart() {
    const traces = [
        createTrace(forecastData.timestamps, forecastData.totalSnow.p10, '10th percentile', 'rgb(0, 100, 200)'),
        createTrace(forecastData.timestamps, forecastData.totalSnow.p50, '50th percentile (Median)', 'rgb(0, 150, 50)', true),
        createTrace(forecastData.timestamps, forecastData.totalSnow.p90, '90th percentile', 'rgb(255, 140, 0)', true),
        createTrace(forecastData.timestamps, forecastData.totalSnow.p95, '95th percentile', 'rgb(200, 0, 0)', true)
    ];

    const layout = getChartLayout('Running Total Snow', 'Cumulative Snow (mm)');
    Plotly.newPlot('total-snow-chart', traces, layout, {responsive: true});
}

// Chart 3: Hourly Precipitation
function renderHourlyPrecipChart() {
    const traces = [
        createTrace(forecastData.timestamps, forecastData.hourlyPrecip.p10, '10th percentile', 'rgb(0, 100, 200)'),
        createTrace(forecastData.timestamps, forecastData.hourlyPrecip.p50, '50th percentile (Median)', 'rgb(0, 150, 50)', true),
        createTrace(forecastData.timestamps, forecastData.hourlyPrecip.p90, '90th percentile', 'rgb(255, 140, 0)', true),
        createTrace(forecastData.timestamps, forecastData.hourlyPrecip.p95, '95th percentile', 'rgb(200, 0, 0)', true)
    ];

    const layout = getChartLayout('Hourly Precipitation', 'Precipitation (mm/hr)');
    Plotly.newPlot('hourly-precip-chart', traces, layout, {responsive: true});
}

// Chart 4: Snow Level Forecast
function renderSnowLevelChart() {
    const traces = [
        createTrace(forecastData.timestamps, forecastData.snowLevel.p10, '10th percentile', 'rgb(0, 100, 200)'),
        createTrace(forecastData.timestamps, forecastData.snowLevel.p50, '50th percentile (Median)', 'rgb(0, 150, 50)', true),
        createTrace(forecastData.timestamps, forecastData.snowLevel.p90, '90th percentile', 'rgb(255, 140, 0)', true),
        createTrace(forecastData.timestamps, forecastData.snowLevel.p95, '95th percentile', 'rgb(200, 0, 0)', true)
    ];

    // Add resort elevation line
    if (currentResort) {
        traces.push({
            x: forecastData.timestamps,
            y: Array(forecastData.timestamps.length).fill(currentResort.elevation),
            name: 'Resort Base Elevation',
            type: 'scatter',
            mode: 'lines',
            line: {
                color: 'rgb(128, 0, 128)',
                width: 3,
                dash: 'dash'
            }
        });
    }

    const layout = getChartLayout('Snow Level Forecast', 'Elevation (meters ASL)');
    layout.yaxis.rangemode = 'normal';
    Plotly.newPlot('snow-level-chart', traces, layout, {responsive: true});
}

// Chart 5: Cumulative Precipitation
function renderCumulativePrecipChart() {
    const traces = [
        createTrace(forecastData.timestamps, forecastData.cumulativePrecip.p10, '10th percentile', 'rgb(0, 100, 200)'),
        createTrace(forecastData.timestamps, forecastData.cumulativePrecip.p50, '50th percentile (Median)', 'rgb(0, 150, 50)', true),
        createTrace(forecastData.timestamps, forecastData.cumulativePrecip.p90, '90th percentile', 'rgb(255, 140, 0)', true),
        createTrace(forecastData.timestamps, forecastData.cumulativePrecip.p95, '95th percentile', 'rgb(200, 0, 0)', true)
    ];

    const layout = getChartLayout('Cumulative Precipitation', 'Total Precipitation (mm)');
    Plotly.newPlot('cumulative-precip-chart', traces, layout, {responsive: true});
}

// Auto-refresh data every hour
setInterval(loadForecastData, 3600000);
