// Open FAIR Monte Carlo Calculator - Frontend JavaScript

let histogramChart = null;
let exceedanceChart = null;

// Format currency
function formatCurrency(value) {
    if (value >= 1000000000) {
        return '$' + (value / 1000000000).toFixed(2) + 'B';
    } else if (value >= 1000000) {
        return '$' + (value / 1000000).toFixed(2) + 'M';
    } else if (value >= 1000) {
        return '$' + (value / 1000).toFixed(1) + 'K';
    } else {
        return '$' + value.toFixed(0);
    }
}

// Format number with commas
function formatNumber(value, decimals = 2) {
    return value.toLocaleString('en-US', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    });
}

// Toggle distribution input fields
function toggleDistribution(prefix) {
    const type = document.getElementById(`${prefix}-type`).value;

    // Hide all distribution inputs for this prefix
    const allInputs = document.querySelectorAll(`[id^="${prefix}-"][class="distribution-inputs"]`);
    allInputs.forEach(el => el.style.display = 'none');

    // Show the selected distribution inputs
    const selectedInput = document.getElementById(`${prefix}-${type}`);
    if (selectedInput) {
        selectedInput.style.display = 'block';
    }
}

// Collect form data
function collectFormData() {
    const data = {
        name: document.getElementById('scenario-name').value,
        iterations: parseInt(document.getElementById('iterations').value),
        tef: {},
        vulnerability: {},
        loss: {}
    };

    // TEF
    const tefType = document.getElementById('tef-type').value;
    if (tefType === 'pert') {
        data.tef = {
            type: 'pert',
            min: parseFloat(document.getElementById('tef-min').value),
            likely: parseFloat(document.getElementById('tef-likely').value),
            max: parseFloat(document.getElementById('tef-max').value)
        };
    } else {
        data.tef = {
            type: 'constant',
            value: parseFloat(document.getElementById('tef-value').value)
        };
    }

    // Vulnerability
    const vulnType = document.getElementById('vuln-type').value;
    if (vulnType === 'pert') {
        data.vulnerability = {
            type: 'pert',
            min: parseFloat(document.getElementById('vuln-min').value),
            likely: parseFloat(document.getElementById('vuln-likely').value),
            max: parseFloat(document.getElementById('vuln-max').value)
        };
    } else {
        data.vulnerability = {
            type: 'constant',
            value: parseFloat(document.getElementById('vuln-value').value)
        };
    }

    // Loss
    const lossType = document.getElementById('loss-type').value;
    if (lossType === 'lognormal') {
        data.loss = {
            type: 'lognormal',
            low: parseFloat(document.getElementById('loss-low').value),
            high: parseFloat(document.getElementById('loss-high').value)
        };
    } else if (lossType === 'pert') {
        data.loss = {
            type: 'pert',
            min: parseFloat(document.getElementById('loss-min').value),
            likely: parseFloat(document.getElementById('loss-likely').value),
            max: parseFloat(document.getElementById('loss-max').value)
        };
    } else {
        data.loss = {
            type: 'constant',
            value: parseFloat(document.getElementById('loss-value').value)
        };
    }

    return data;
}

// Display results
function displayResults(data) {
    const resultsDiv = document.getElementById('results');
    resultsDiv.style.display = 'block';

    // Summary stats
    document.getElementById('result-mean').textContent = formatCurrency(data.summary.mean);
    document.getElementById('result-median').textContent = formatCurrency(data.summary.median);
    document.getElementById('result-var').textContent = formatCurrency(data.summary.var_95);
    document.getElementById('result-cvar').textContent = formatCurrency(data.summary.cvar_95);

    // Percentiles
    document.getElementById('result-p10').textContent = formatCurrency(data.summary.p10);
    document.getElementById('result-p25').textContent = formatCurrency(data.summary.p25);
    document.getElementById('result-p75').textContent = formatCurrency(data.summary.p75);
    document.getElementById('result-p90').textContent = formatCurrency(data.summary.p90);
    document.getElementById('result-p95').textContent = formatCurrency(data.summary.p95);

    // Components
    document.getElementById('result-lef').textContent = formatNumber(data.lef.mean) + ' events/year';
    document.getElementById('result-lm').textContent = formatCurrency(data.lm.mean);
    document.getElementById('result-min').textContent = formatCurrency(data.summary.min);
    document.getElementById('result-max').textContent = formatCurrency(data.summary.max);
    document.getElementById('result-std').textContent = formatCurrency(data.summary.std);

    // Update charts
    updateHistogramChart(data.histogram);
    updateExceedanceChart(data.exceedance);

    // Scroll to results
    resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Create/update histogram chart
function updateHistogramChart(histogramData) {
    const ctx = document.getElementById('histogram-chart').getContext('2d');

    // Calculate bin centers for x-axis labels
    const binCenters = [];
    for (let i = 0; i < histogramData.bins.length - 1; i++) {
        binCenters.push((histogramData.bins[i] + histogramData.bins[i + 1]) / 2);
    }

    if (histogramChart) {
        histogramChart.destroy();
    }

    histogramChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: binCenters.map(v => formatCurrency(v)),
            datasets: [{
                label: 'Frequency',
                data: histogramData.counts,
                backgroundColor: 'rgba(37, 99, 235, 0.6)',
                borderColor: 'rgba(37, 99, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        title: function(context) {
                            const idx = context[0].dataIndex;
                            const low = histogramData.bins[idx];
                            const high = histogramData.bins[idx + 1];
                            return formatCurrency(low) + ' - ' + formatCurrency(high);
                        }
                    }
                }
            },
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Annual Loss ($)'
                    },
                    ticks: {
                        maxTicksLimit: 8,
                        maxRotation: 45
                    }
                },
                y: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Frequency'
                    }
                }
            }
        }
    });
}

// Create/update exceedance curve chart
function updateExceedanceChart(exceedanceData) {
    const ctx = document.getElementById('exceedance-chart').getContext('2d');

    if (exceedanceChart) {
        exceedanceChart.destroy();
    }

    exceedanceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: exceedanceData.values.map(v => formatCurrency(v)),
            datasets: [{
                label: 'Probability of Exceedance',
                data: exceedanceData.probabilities,
                borderColor: 'rgba(37, 99, 235, 1)',
                backgroundColor: 'rgba(37, 99, 235, 0.1)',
                fill: true,
                tension: 0.4,
                pointRadius: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.parsed.y.toFixed(1) + '% chance of exceeding this loss';
                        }
                    }
                }
            },
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Loss Amount ($)'
                    },
                    ticks: {
                        maxTicksLimit: 8,
                        maxRotation: 45
                    }
                },
                y: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Probability (%)'
                    },
                    min: 0,
                    max: 100
                }
            }
        }
    });
}

// Run simulation
async function runSimulation(event) {
    event.preventDefault();

    const btn = document.getElementById('run-btn');
    btn.disabled = true;
    btn.textContent = 'Running Simulation...';
    btn.classList.add('loading');

    try {
        const formData = collectFormData();

        const response = await fetch('/api/simulate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        const data = await response.json();

        if (data.success) {
            displayResults(data);
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        alert('Error running simulation: ' + error.message);
    } finally {
        btn.disabled = false;
        btn.textContent = 'Run Simulation';
        btn.classList.remove('loading');
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    // Set up form submission
    document.getElementById('risk-form').addEventListener('submit', runSimulation);

    // Initialize distribution toggles
    toggleDistribution('tef');
    toggleDistribution('vuln');
    toggleDistribution('loss');
});
