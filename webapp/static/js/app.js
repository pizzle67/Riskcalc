// Open FAIR Monte Carlo Calculator - Frontend JavaScript

let histogramChart = null;
let exceedanceChart = null;
let currentScenarioId = null;
let lastSimulationData = null;

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

// Format date for display
function formatDate(isoString) {
    if (!isoString) return 'Unknown';
    const date = new Date(isoString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

// Toggle distribution input fields
function toggleDistribution(prefix) {
    const typeSelect = document.getElementById(`${prefix}-type`);
    if (!typeSelect) return;

    const type = typeSelect.value;

    // Hide all distribution inputs for this prefix
    const allInputs = document.querySelectorAll(`[id^="${prefix}-"][class="distribution-inputs"]`);
    allInputs.forEach(el => el.style.display = 'none');

    // Show the selected distribution inputs
    const selectedInput = document.getElementById(`${prefix}-${type}`);
    if (selectedInput) {
        selectedInput.style.display = 'block';
    }
}

// Toggle LEF mode (direct vs derived)
function toggleLEFMode() {
    const mode = document.querySelector('input[name="lef-mode"]:checked').value;
    document.getElementById('lef-direct').style.display = mode === 'direct' ? 'block' : 'none';
    document.getElementById('lef-derived').style.display = mode === 'derived' ? 'block' : 'none';
}

// Toggle TEF mode (direct vs derived from CF+PoA)
function toggleTEFMode() {
    const mode = document.querySelector('input[name="tef-mode"]:checked').value;
    document.getElementById('tef-direct').style.display = mode === 'direct' ? 'block' : 'none';
    document.getElementById('tef-derived').style.display = mode === 'derived' ? 'block' : 'none';
}

// Toggle Vulnerability mode (direct vs derived from TCap+RS)
function toggleVulnMode() {
    const mode = document.querySelector('input[name="vuln-mode"]:checked').value;
    document.getElementById('vuln-direct').style.display = mode === 'direct' ? 'block' : 'none';
    document.getElementById('vuln-derived').style.display = mode === 'derived' ? 'block' : 'none';
}

// Toggle LM mode (direct vs derived)
function toggleLMMode() {
    const mode = document.querySelector('input[name="lm-mode"]:checked').value;
    document.getElementById('lm-direct').style.display = mode === 'direct' ? 'block' : 'none';
    document.getElementById('lm-derived').style.display = mode === 'derived' ? 'block' : 'none';
}

// Toggle analysis mode (ALE vs SLE)
function toggleAnalysisMode() {
    const mode = document.querySelector('input[name="analysis-mode"]:checked').value;
    const lefSection = document.querySelector('.taxonomy-section:first-of-type');
    const helpText = document.getElementById('analysis-mode-help');

    if (mode === 'sle') {
        lefSection.classList.add('section-disabled');
        helpText.textContent = 'SLE \u2014 loss distribution for a single event (LEF not used)';
    } else {
        lefSection.classList.remove('section-disabled');
        helpText.textContent = 'ALE = LEF \u00d7 LM \u2014 expected annual loss across all events';
    }
}

// Toggle secondary loss inputs
function toggleSecondaryLoss() {
    const include = document.getElementById('include-secondary').checked;
    document.getElementById('secondary-loss-inputs').style.display = include ? 'block' : 'none';
}

// Collect LEF configuration for saving
function collectLEFConfig() {
    const analysisMode = document.querySelector('input[name="analysis-mode"]:checked').value;
    const lefMode = document.querySelector('input[name="lef-mode"]:checked').value;
    const config = { analysisMode: analysisMode, mode: lefMode };

    if (lefMode === 'direct') {
        const lefType = document.getElementById('lef-type').value;
        config.type = lefType;
        if (lefType === 'triangular') {
            config.min = parseFloat(document.getElementById('lef-min').value);
            config.likely = parseFloat(document.getElementById('lef-likely').value);
            config.max = parseFloat(document.getElementById('lef-max').value);
        } else if (lefType === 'pert') {
            config.min = parseFloat(document.getElementById('lef-pert-min').value);
            config.likely = parseFloat(document.getElementById('lef-pert-likely').value);
            config.max = parseFloat(document.getElementById('lef-pert-max').value);
        } else {
            config.value = parseFloat(document.getElementById('lef-value').value);
        }
    } else {
        // TEF config
        const tefMode = document.querySelector('input[name="tef-mode"]:checked').value;
        config.tefMode = tefMode;
        if (tefMode === 'direct') {
            const tefType = document.getElementById('tef-type').value;
            config.tefType = tefType;
            if (tefType === 'triangular') {
                config.tefMin = parseFloat(document.getElementById('tef-min').value);
                config.tefLikely = parseFloat(document.getElementById('tef-likely').value);
                config.tefMax = parseFloat(document.getElementById('tef-max').value);
            } else if (tefType === 'pert') {
                config.tefMin = parseFloat(document.getElementById('tef-pert-min').value);
                config.tefLikely = parseFloat(document.getElementById('tef-pert-likely').value);
                config.tefMax = parseFloat(document.getElementById('tef-pert-max').value);
            } else {
                config.tefValue = parseFloat(document.getElementById('tef-value').value);
            }
        } else {
            config.cfMin = parseFloat(document.getElementById('cf-min').value);
            config.cfLikely = parseFloat(document.getElementById('cf-likely').value);
            config.cfMax = parseFloat(document.getElementById('cf-max').value);
            config.poaMin = parseFloat(document.getElementById('poa-min').value);
            config.poaLikely = parseFloat(document.getElementById('poa-likely').value);
            config.poaMax = parseFloat(document.getElementById('poa-max').value);
        }

        // Vulnerability config
        const vulnMode = document.querySelector('input[name="vuln-mode"]:checked').value;
        config.vulnMode = vulnMode;
        if (vulnMode === 'direct') {
            const vulnType = document.getElementById('vuln-type').value;
            config.vulnType = vulnType;
            if (vulnType === 'triangular') {
                config.vulnMin = parseFloat(document.getElementById('vuln-min').value);
                config.vulnLikely = parseFloat(document.getElementById('vuln-likely').value);
                config.vulnMax = parseFloat(document.getElementById('vuln-max').value);
            } else if (vulnType === 'pert') {
                config.vulnMin = parseFloat(document.getElementById('vuln-pert-min').value);
                config.vulnLikely = parseFloat(document.getElementById('vuln-pert-likely').value);
                config.vulnMax = parseFloat(document.getElementById('vuln-pert-max').value);
            } else {
                config.vulnValue = parseFloat(document.getElementById('vuln-value').value);
            }
        } else {
            config.tcapMin = parseFloat(document.getElementById('tcap-min').value);
            config.tcapLikely = parseFloat(document.getElementById('tcap-likely').value);
            config.tcapMax = parseFloat(document.getElementById('tcap-max').value);
            config.rsMin = parseFloat(document.getElementById('rs-min').value);
            config.rsLikely = parseFloat(document.getElementById('rs-likely').value);
            config.rsMax = parseFloat(document.getElementById('rs-max').value);
        }
    }

    return config;
}

// Collect LM configuration for saving
function collectLMConfig() {
    const lmMode = document.querySelector('input[name="lm-mode"]:checked').value;
    const config = { mode: lmMode };

    if (lmMode === 'direct') {
        const lossType = document.getElementById('loss-type').value;
        config.type = lossType;
        if (lossType === 'lognormal') {
            config.low = parseFloat(document.getElementById('loss-low').value);
            config.high = parseFloat(document.getElementById('loss-high').value);
        } else if (lossType === 'pert') {
            config.min = parseFloat(document.getElementById('loss-min').value);
            config.likely = parseFloat(document.getElementById('loss-likely').value);
            config.max = parseFloat(document.getElementById('loss-max').value);
        } else {
            config.value = parseFloat(document.getElementById('loss-value').value);
        }
    } else {
        const plType = document.getElementById('pl-type').value;
        config.plType = plType;
        if (plType === 'lognormal') {
            config.plLow = parseFloat(document.getElementById('pl-low').value);
            config.plHigh = parseFloat(document.getElementById('pl-high').value);
        } else if (plType === 'pert') {
            config.plMin = parseFloat(document.getElementById('pl-min').value);
            config.plLikely = parseFloat(document.getElementById('pl-likely').value);
            config.plMax = parseFloat(document.getElementById('pl-max').value);
        } else {
            config.plValue = parseFloat(document.getElementById('pl-value').value);
        }

        config.includeSecondary = document.getElementById('include-secondary').checked;
        if (config.includeSecondary) {
            config.slefMin = parseFloat(document.getElementById('slef-min').value);
            config.slefLikely = parseFloat(document.getElementById('slef-likely').value);
            config.slefMax = parseFloat(document.getElementById('slef-max').value);
            config.slmLow = parseFloat(document.getElementById('slm-low').value);
            config.slmHigh = parseFloat(document.getElementById('slm-high').value);
        }
    }

    return config;
}

// Apply LEF configuration to form
function applyLEFConfig(config) {
    if (!config) return;

    // Set analysis mode if saved
    if (config.analysisMode) {
        const analysisModeRadio = document.querySelector(`input[name="analysis-mode"][value="${config.analysisMode}"]`);
        if (analysisModeRadio) {
            analysisModeRadio.checked = true;
            toggleAnalysisMode();
        }
    }

    // Set LEF mode
    const lefModeRadio = document.querySelector(`input[name="lef-mode"][value="${config.mode}"]`);
    if (lefModeRadio) {
        lefModeRadio.checked = true;
        toggleLEFMode();
    }

    if (config.mode === 'direct') {
        if (config.type) {
            document.getElementById('lef-type').value = config.type;
            toggleDistribution('lef');
        }
        if (config.type === 'triangular') {
            document.getElementById('lef-min').value = config.min || 1;
            document.getElementById('lef-likely').value = config.likely || 5;
            document.getElementById('lef-max').value = config.max || 15;
        } else if (config.type === 'pert') {
            document.getElementById('lef-pert-min').value = config.min || 1;
            document.getElementById('lef-pert-likely').value = config.likely || 5;
            document.getElementById('lef-pert-max').value = config.max || 15;
        } else {
            document.getElementById('lef-value').value = config.value || 5;
        }
    } else {
        // TEF
        const tefModeRadio = document.querySelector(`input[name="tef-mode"][value="${config.tefMode}"]`);
        if (tefModeRadio) {
            tefModeRadio.checked = true;
            toggleTEFMode();
        }

        if (config.tefMode === 'direct') {
            if (config.tefType) {
                document.getElementById('tef-type').value = config.tefType;
                toggleDistribution('tef');
            }
            if (config.tefType === 'triangular') {
                document.getElementById('tef-min').value = config.tefMin || 5;
                document.getElementById('tef-likely').value = config.tefLikely || 10;
                document.getElementById('tef-max').value = config.tefMax || 20;
            } else if (config.tefType === 'pert') {
                document.getElementById('tef-pert-min').value = config.tefMin || 5;
                document.getElementById('tef-pert-likely').value = config.tefLikely || 10;
                document.getElementById('tef-pert-max').value = config.tefMax || 20;
            } else {
                document.getElementById('tef-value').value = config.tefValue || 10;
            }
        } else {
            document.getElementById('cf-min').value = config.cfMin || 50;
            document.getElementById('cf-likely').value = config.cfLikely || 100;
            document.getElementById('cf-max').value = config.cfMax || 200;
            document.getElementById('poa-min').value = config.poaMin || 0.05;
            document.getElementById('poa-likely').value = config.poaLikely || 0.10;
            document.getElementById('poa-max').value = config.poaMax || 0.20;
        }

        // Vulnerability
        const vulnModeRadio = document.querySelector(`input[name="vuln-mode"][value="${config.vulnMode}"]`);
        if (vulnModeRadio) {
            vulnModeRadio.checked = true;
            toggleVulnMode();
        }

        if (config.vulnMode === 'direct') {
            if (config.vulnType) {
                document.getElementById('vuln-type').value = config.vulnType;
                toggleDistribution('vuln');
            }
            if (config.vulnType === 'triangular') {
                document.getElementById('vuln-min').value = config.vulnMin || 0.1;
                document.getElementById('vuln-likely').value = config.vulnLikely || 0.25;
                document.getElementById('vuln-max').value = config.vulnMax || 0.5;
            } else if (config.vulnType === 'pert') {
                document.getElementById('vuln-pert-min').value = config.vulnMin || 0.1;
                document.getElementById('vuln-pert-likely').value = config.vulnLikely || 0.25;
                document.getElementById('vuln-pert-max').value = config.vulnMax || 0.5;
            } else {
                document.getElementById('vuln-value').value = config.vulnValue || 0.25;
            }
        } else {
            document.getElementById('tcap-min').value = config.tcapMin || 15;
            document.getElementById('tcap-likely').value = config.tcapLikely || 55;
            document.getElementById('tcap-max').value = config.tcapMax || 65;
            document.getElementById('rs-min').value = config.rsMin || 10;
            document.getElementById('rs-likely').value = config.rsLikely || 50;
            document.getElementById('rs-max').value = config.rsMax || 60;
        }
    }
}

// Apply LM configuration to form
function applyLMConfig(config) {
    if (!config) return;

    // Set LM mode
    const lmModeRadio = document.querySelector(`input[name="lm-mode"][value="${config.mode}"]`);
    if (lmModeRadio) {
        lmModeRadio.checked = true;
        toggleLMMode();
    }

    if (config.mode === 'direct') {
        if (config.type) {
            document.getElementById('loss-type').value = config.type;
            toggleDistribution('loss');
        }
        if (config.type === 'lognormal') {
            document.getElementById('loss-low').value = config.low || 50000;
            document.getElementById('loss-high').value = config.high || 500000;
        } else if (config.type === 'pert') {
            document.getElementById('loss-min').value = config.min || 10000;
            document.getElementById('loss-likely').value = config.likely || 100000;
            document.getElementById('loss-max').value = config.max || 500000;
        } else {
            document.getElementById('loss-value').value = config.value || 100000;
        }
    } else {
        if (config.plType) {
            document.getElementById('pl-type').value = config.plType;
            toggleDistribution('pl');
        }
        if (config.plType === 'lognormal') {
            document.getElementById('pl-low').value = config.plLow || 25000;
            document.getElementById('pl-high').value = config.plHigh || 250000;
        } else if (config.plType === 'pert') {
            document.getElementById('pl-min').value = config.plMin || 10000;
            document.getElementById('pl-likely').value = config.plLikely || 75000;
            document.getElementById('pl-max').value = config.plMax || 300000;
        } else {
            document.getElementById('pl-value').value = config.plValue || 75000;
        }

        document.getElementById('include-secondary').checked = config.includeSecondary || false;
        toggleSecondaryLoss();

        if (config.includeSecondary) {
            document.getElementById('slef-min').value = config.slefMin || 0.1;
            document.getElementById('slef-likely').value = config.slefLikely || 0.3;
            document.getElementById('slef-max').value = config.slefMax || 0.6;
            document.getElementById('slm-low').value = config.slmLow || 50000;
            document.getElementById('slm-high').value = config.slmHigh || 500000;
        }
    }
}

// Collect form data
function collectFormData() {
    const data = {
        name: document.getElementById('scenario-name').value,
        iterations: parseInt(document.getElementById('iterations').value),
    };

    const analysisMode = document.querySelector('input[name="analysis-mode"]:checked').value;

    // Skip LEF collection for SLE mode
    if (analysisMode === 'sle') {
        // Only collect LM data — jump straight to Loss Magnitude section below
    } else {

    // LEF Mode
    const lefMode = document.querySelector('input[name="lef-mode"]:checked').value;

    if (lefMode === 'direct') {
        // Direct LEF input
        const lefType = document.getElementById('lef-type').value;
        if (lefType === 'triangular') {
            data.lef = {
                type: 'triangular',
                min: parseFloat(document.getElementById('lef-min').value),
                likely: parseFloat(document.getElementById('lef-likely').value),
                max: parseFloat(document.getElementById('lef-max').value)
            };
        } else if (lefType === 'pert') {
            data.lef = {
                type: 'pert',
                min: parseFloat(document.getElementById('lef-pert-min').value),
                likely: parseFloat(document.getElementById('lef-pert-likely').value),
                max: parseFloat(document.getElementById('lef-pert-max').value)
            };
        } else {
            data.lef = {
                type: 'constant',
                value: parseFloat(document.getElementById('lef-value').value)
            };
        }
    } else {
        // Derived LEF from TEF and Vulnerability

        // TEF
        const tefMode = document.querySelector('input[name="tef-mode"]:checked').value;
        if (tefMode === 'direct') {
            const tefType = document.getElementById('tef-type').value;
            if (tefType === 'triangular') {
                data.tef = {
                    type: 'triangular',
                    min: parseFloat(document.getElementById('tef-min').value),
                    likely: parseFloat(document.getElementById('tef-likely').value),
                    max: parseFloat(document.getElementById('tef-max').value)
                };
            } else if (tefType === 'pert') {
                data.tef = {
                    type: 'pert',
                    min: parseFloat(document.getElementById('tef-pert-min').value),
                    likely: parseFloat(document.getElementById('tef-pert-likely').value),
                    max: parseFloat(document.getElementById('tef-pert-max').value)
                };
            } else {
                data.tef = {
                    type: 'constant',
                    value: parseFloat(document.getElementById('tef-value').value)
                };
            }
        } else {
            // Derived TEF from CF and PoA
            data.contact_frequency = {
                type: 'triangular',
                min: parseFloat(document.getElementById('cf-min').value),
                likely: parseFloat(document.getElementById('cf-likely').value),
                max: parseFloat(document.getElementById('cf-max').value)
            };
            data.probability_of_action = {
                type: 'triangular',
                min: parseFloat(document.getElementById('poa-min').value),
                likely: parseFloat(document.getElementById('poa-likely').value),
                max: parseFloat(document.getElementById('poa-max').value)
            };
        }

        // Vulnerability
        const vulnMode = document.querySelector('input[name="vuln-mode"]:checked').value;
        if (vulnMode === 'direct') {
            const vulnType = document.getElementById('vuln-type').value;
            if (vulnType === 'triangular') {
                data.vulnerability = {
                    type: 'triangular',
                    min: parseFloat(document.getElementById('vuln-min').value),
                    likely: parseFloat(document.getElementById('vuln-likely').value),
                    max: parseFloat(document.getElementById('vuln-max').value)
                };
            } else if (vulnType === 'pert') {
                data.vulnerability = {
                    type: 'pert',
                    min: parseFloat(document.getElementById('vuln-pert-min').value),
                    likely: parseFloat(document.getElementById('vuln-pert-likely').value),
                    max: parseFloat(document.getElementById('vuln-pert-max').value)
                };
            } else {
                data.vulnerability = {
                    type: 'constant',
                    value: parseFloat(document.getElementById('vuln-value').value)
                };
            }
        } else {
            // Derived Vulnerability from TCap and RS (21x21 grid)
            data.threat_capability = {
                type: 'triangular',
                min: parseFloat(document.getElementById('tcap-min').value) / 100,
                likely: parseFloat(document.getElementById('tcap-likely').value) / 100,
                max: parseFloat(document.getElementById('tcap-max').value) / 100
            };
            data.resistance_strength = {
                type: 'triangular',
                min: parseFloat(document.getElementById('rs-min').value) / 100,
                likely: parseFloat(document.getElementById('rs-likely').value) / 100,
                max: parseFloat(document.getElementById('rs-max').value) / 100
            };
        }
    }

    } // end ALE-only LEF collection

    // Loss Magnitude Mode
    const lmMode = document.querySelector('input[name="lm-mode"]:checked').value;

    if (lmMode === 'direct') {
        // Direct LM input
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
    } else {
        // Derived LM from Primary + Secondary Loss
        const plType = document.getElementById('pl-type').value;
        if (plType === 'lognormal') {
            data.primary_loss = {
                type: 'lognormal',
                low: parseFloat(document.getElementById('pl-low').value),
                high: parseFloat(document.getElementById('pl-high').value)
            };
        } else if (plType === 'pert') {
            data.primary_loss = {
                type: 'pert',
                min: parseFloat(document.getElementById('pl-min').value),
                likely: parseFloat(document.getElementById('pl-likely').value),
                max: parseFloat(document.getElementById('pl-max').value)
            };
        } else {
            data.primary_loss = {
                type: 'constant',
                value: parseFloat(document.getElementById('pl-value').value)
            };
        }

        // Secondary loss (optional)
        if (document.getElementById('include-secondary').checked) {
            data.secondary_loss_frequency = {
                type: 'triangular',
                min: parseFloat(document.getElementById('slef-min').value),
                likely: parseFloat(document.getElementById('slef-likely').value),
                max: parseFloat(document.getElementById('slef-max').value)
            };
            data.secondary_loss_magnitude = {
                type: 'lognormal',
                low: parseFloat(document.getElementById('slm-low').value),
                high: parseFloat(document.getElementById('slm-high').value)
            };
        }
    }

    return data;
}

// Display results
function displayResults(data, analysisMode) {
    analysisMode = analysisMode || 'ale';
    const isSLE = analysisMode === 'sle';

    const resultsDiv = document.getElementById('results');
    resultsDiv.style.display = 'block';

    // Update labels based on analysis mode
    document.getElementById('results-title').textContent = isSLE ? 'Single Loss Event Results' : 'Results';
    document.getElementById('label-mean').textContent = isSLE ? 'Mean Single Loss' : 'Mean Annual Loss';
    document.getElementById('label-median').textContent = isSLE ? 'Median Single Loss' : 'Median Annual Loss';
    document.getElementById('label-min').textContent = isSLE ? 'Minimum Loss' : 'Minimum ALE';
    document.getElementById('label-max').textContent = isSLE ? 'Maximum Loss' : 'Maximum ALE';
    document.getElementById('histogram-title').textContent = isSLE ? 'Single Loss Distribution' : 'Loss Distribution';
    document.getElementById('exceedance-title').textContent = isSLE ? 'Single Loss Exceedance Curve' : 'Loss Exceedance Curve';

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

    // Components - show/hide LEF row based on mode
    const lefRow = document.getElementById('result-lef-row');
    if (isSLE) {
        lefRow.style.display = 'none';
        document.getElementById('result-lm').textContent = formatCurrency(data.summary.mean);
    } else {
        lefRow.style.display = '';
        document.getElementById('result-lef').textContent = formatNumber(data.lef.mean) + ' events/year';
        document.getElementById('result-lm').textContent = formatCurrency(data.lm.mean);
    }
    document.getElementById('result-min').textContent = formatCurrency(data.summary.min);
    document.getElementById('result-max').textContent = formatCurrency(data.summary.max);
    document.getElementById('result-std').textContent = formatCurrency(data.summary.std);

    // Show calculated vulnerability if derived from TCap/RS
    const vulnResultDiv = document.getElementById('vuln-result');
    if (data.calculated_vulnerability !== undefined) {
        vulnResultDiv.style.display = 'block';
        document.getElementById('calc-vuln').textContent = (data.calculated_vulnerability * 100).toFixed(1) + '%';
    } else {
        vulnResultDiv.style.display = 'none';
    }

    // Update charts
    const xLabel = isSLE ? 'Single Loss ($)' : 'Annual Loss ($)';
    updateHistogramChart(data.histogram, xLabel);
    updateExceedanceChart(data.exceedance, xLabel);

    // Show saved info if result was saved
    const savedInfoDiv = document.getElementById('result-saved-info');
    if (data.result_id) {
        savedInfoDiv.style.display = 'block';
    } else {
        savedInfoDiv.style.display = 'none';
    }

    // Scroll to results
    resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Create/update histogram chart
function updateHistogramChart(histogramData, xLabel) {
    xLabel = xLabel || 'Annual Loss ($)';
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
                        text: xLabel
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
function updateExceedanceChart(exceedanceData, xLabel) {
    xLabel = xLabel || 'Loss Amount ($)';
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
                        text: xLabel
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
        const analysisMode = document.querySelector('input[name="analysis-mode"]:checked').value;

        // Add save_result flag and scenario_id if saving
        if (document.getElementById('save-result-checkbox').checked && currentScenarioId) {
            formData.save_result = true;
            formData.scenario_id = currentScenarioId;
        }

        const endpoint = analysisMode === 'sle' ? '/api/simulate-sle' : '/api/simulate';

        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        const data = await response.json();

        if (data.success) {
            lastSimulationData = data;
            displayResults(data, analysisMode);
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

// ==================== Scenario Management Functions ====================

// Load all scenarios into dropdown
async function loadScenarios() {
    try {
        const response = await fetch('/api/scenarios');
        const data = await response.json();

        if (data.success) {
            const select = document.getElementById('scenario-select');
            // Clear existing options except the first one
            while (select.options.length > 1) {
                select.remove(1);
            }

            // Add scenarios
            data.scenarios.forEach(scenario => {
                const option = document.createElement('option');
                option.value = scenario.id;
                option.textContent = scenario.name;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error loading scenarios:', error);
    }
}

// Load a specific scenario
async function loadScenario(scenarioId) {
    if (!scenarioId) {
        resetForm();
        return;
    }

    try {
        const response = await fetch(`/api/scenarios/${scenarioId}`);
        const data = await response.json();

        if (data.success) {
            const scenario = data.scenario;

            // Set basic fields
            document.getElementById('scenario-name').value = scenario.name;
            document.getElementById('scenario-description').value = scenario.description || '';
            document.getElementById('iterations').value = scenario.iterations || 10000;

            // Apply configurations
            applyLEFConfig(scenario.lef_config);
            applyLMConfig(scenario.lm_config);

            // Update current scenario ID
            currentScenarioId = scenario.id;

            // Update UI state
            updateScenarioUI();
            showStatus('Scenario loaded successfully', 'success');
        } else {
            alert('Error loading scenario: ' + data.error);
        }
    } catch (error) {
        alert('Error loading scenario: ' + error.message);
    }
}

// Save current form as scenario
async function saveScenario(saveAsNew = false) {
    const name = document.getElementById('scenario-name').value.trim();
    if (!name) {
        alert('Please enter a scenario name');
        return;
    }

    const scenarioData = {
        name: name,
        description: document.getElementById('scenario-description').value.trim(),
        lef_config: collectLEFConfig(),
        lm_config: collectLMConfig(),
        iterations: parseInt(document.getElementById('iterations').value)
    };

    try {
        let response;
        if (currentScenarioId && !saveAsNew) {
            // Update existing scenario
            response = await fetch(`/api/scenarios/${currentScenarioId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(scenarioData)
            });
        } else {
            // Create new scenario
            response = await fetch('/api/scenarios', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(scenarioData)
            });
        }

        const data = await response.json();

        if (data.success) {
            currentScenarioId = data.scenario.id;
            await loadScenarios();
            document.getElementById('scenario-select').value = currentScenarioId;
            updateScenarioUI();
            showStatus('Scenario saved successfully', 'success');
        } else {
            alert('Error saving scenario: ' + data.error);
        }
    } catch (error) {
        alert('Error saving scenario: ' + error.message);
    }
}

// Delete current scenario
async function deleteScenario() {
    if (!currentScenarioId) return;

    if (!confirm('Are you sure you want to delete this scenario? This will also delete all associated simulation results.')) {
        return;
    }

    try {
        const response = await fetch(`/api/scenarios/${currentScenarioId}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (data.success) {
            currentScenarioId = null;
            await loadScenarios();
            resetForm();
            showStatus('Scenario deleted successfully', 'success');
        } else {
            alert('Error deleting scenario: ' + data.error);
        }
    } catch (error) {
        alert('Error deleting scenario: ' + error.message);
    }
}

// Reset form to default state
function resetForm() {
    currentScenarioId = null;
    document.getElementById('scenario-name').value = 'Risk Scenario';
    document.getElementById('scenario-description').value = '';
    document.getElementById('scenario-select').value = '';
    document.getElementById('iterations').value = '10000';
    document.getElementById('results').style.display = 'none';
    document.getElementById('history-panel').style.display = 'none';

    // Reset to defaults (could be more comprehensive)
    updateScenarioUI();
}

// Update UI based on current scenario state
function updateScenarioUI() {
    const loadBtn = document.getElementById('load-scenario-btn');
    const deleteBtn = document.getElementById('delete-scenario-btn');
    const saveResultCheckbox = document.getElementById('save-result-checkbox');

    loadBtn.disabled = !document.getElementById('scenario-select').value;
    deleteBtn.disabled = !currentScenarioId;
    saveResultCheckbox.disabled = !currentScenarioId;

    if (!currentScenarioId) {
        saveResultCheckbox.checked = false;
    }
}

// Show status message
function showStatus(message, type = 'info') {
    const statusDiv = document.getElementById('scenario-status');
    statusDiv.textContent = message;
    statusDiv.className = 'scenario-status ' + type;
    statusDiv.style.display = 'block';

    setTimeout(() => {
        statusDiv.style.display = 'none';
    }, 3000);
}

// ==================== History Functions ====================

// Load simulation history for current scenario
async function loadHistory() {
    if (!currentScenarioId) {
        alert('Please save or load a scenario first');
        return;
    }

    try {
        const response = await fetch(`/api/scenarios/${currentScenarioId}/results`);
        const data = await response.json();

        if (data.success) {
            displayHistory(data.results);
            document.getElementById('history-panel').style.display = 'block';
            document.getElementById('history-panel').scrollIntoView({ behavior: 'smooth' });
        } else {
            alert('Error loading history: ' + data.error);
        }
    } catch (error) {
        alert('Error loading history: ' + error.message);
    }
}

// Display history in the panel
function displayHistory(results) {
    const listDiv = document.getElementById('history-list');

    if (results.length === 0) {
        listDiv.innerHTML = '<p class="empty-state">No simulation history available</p>';
        return;
    }

    let html = '<table class="history-table"><thead><tr>';
    html += '<th>Date</th><th>Iterations</th><th>Mean ALE</th><th>95% VaR</th><th>Actions</th>';
    html += '</tr></thead><tbody>';

    results.forEach(result => {
        const stats = result.summary_stats || {};
        html += `<tr>
            <td>${formatDate(result.executed_at)}</td>
            <td>${result.iterations.toLocaleString()}</td>
            <td>${stats.mean ? formatCurrency(stats.mean) : '-'}</td>
            <td>${stats.var_95 ? formatCurrency(stats.var_95) : '-'}</td>
            <td>
                <button class="btn-small" onclick="viewResult(${result.id})">View</button>
                <button class="btn-small btn-danger" onclick="deleteResult(${result.id})">Delete</button>
            </td>
        </tr>`;
    });

    html += '</tbody></table>';
    listDiv.innerHTML = html;
}

// View a specific result
async function viewResult(resultId) {
    try {
        const response = await fetch(`/api/results/${resultId}`);
        const data = await response.json();

        if (data.success) {
            const result = data.result;
            // Format data similar to simulation response
            const displayData = {
                success: true,
                summary: result.summary_stats,
                histogram: result.histogram_data,
                exceedance: result.exceedance_data,
                lef: { mean: 0, median: 0 },  // Not stored in history
                lm: { mean: 0, median: 0 }    // Not stored in history
            };
            displayResults(displayData);
        } else {
            alert('Error viewing result: ' + data.error);
        }
    } catch (error) {
        alert('Error viewing result: ' + error.message);
    }
}

// Delete a result
async function deleteResult(resultId) {
    if (!confirm('Are you sure you want to delete this result?')) {
        return;
    }

    try {
        const response = await fetch(`/api/results/${resultId}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (data.success) {
            loadHistory();  // Refresh the list
        } else {
            alert('Error deleting result: ' + data.error);
        }
    } catch (error) {
        alert('Error deleting result: ' + error.message);
    }
}

// ==================== Initialize ====================

document.addEventListener('DOMContentLoaded', function() {
    // Set up form submission
    document.getElementById('risk-form').addEventListener('submit', runSimulation);

    // Initialize distribution toggles
    toggleDistribution('lef');
    toggleDistribution('tef');
    toggleDistribution('vuln');
    toggleDistribution('loss');
    toggleDistribution('pl');

    // Initialize mode toggles
    toggleAnalysisMode();
    toggleLEFMode();
    toggleTEFMode();
    toggleVulnMode();
    toggleLMMode();
    toggleSecondaryLoss();

    // Load scenarios
    loadScenarios();

    // Scenario management event listeners
    document.getElementById('scenario-select').addEventListener('change', function() {
        updateScenarioUI();
    });

    document.getElementById('load-scenario-btn').addEventListener('click', function() {
        const scenarioId = document.getElementById('scenario-select').value;
        if (scenarioId) {
            loadScenario(scenarioId);
        }
    });

    document.getElementById('save-scenario-btn').addEventListener('click', function() {
        saveScenario(false);
    });

    document.getElementById('save-as-btn').addEventListener('click', function() {
        saveScenario(true);
    });

    document.getElementById('delete-scenario-btn').addEventListener('click', deleteScenario);

    document.getElementById('view-history-link').addEventListener('click', function(e) {
        e.preventDefault();
        loadHistory();
    });

    document.getElementById('close-history-btn').addEventListener('click', function() {
        document.getElementById('history-panel').style.display = 'none';
    });

    // Initialize UI state
    updateScenarioUI();
});
