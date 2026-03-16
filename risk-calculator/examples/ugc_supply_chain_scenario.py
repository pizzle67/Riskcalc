#!/usr/bin/env python3
"""
Online Platform Scenario 2: Malicious UGC / Developer Supply Chain Abuse
=========================================================================

THREAT SUMMARY
--------------
Large online platforms that host user-generated content (UGC) face a distinct
supply chain risk: a threat actor can publish malicious content that harvests
user credentials, redirects users to phishing sites, or delivers malware — using
the platform's own trust model as cover. Unlike direct phishing (Scenario 1),
the attack surface here is the content creation ecosystem, not the end user.

This scenario models the risk from malicious content submissions that reach a
meaningful user count before detection and takedown — the window of exposure
where user accounts are at risk.

ATTACK VECTORS (in order of documented prevalence)
---------------------------------------------------
1. Newly registered malicious accounts
   — Attacker creates a free account and publishes content with embedded
     credential harvesters, clickjacking to external phishing pages, or social
     engineering prompts (e.g., "enter your password to claim free platform credits")
   — Low barrier to entry; the platform's trust lends legitimacy to the content

2. Compromised legitimate creator accounts
   — Existing creator with an established audience is phished or credential-stuffed
   — Attacker injects malicious content into an already-popular submission
   — High impact: existing audience trust accelerates exposure before detection
   — Analogous to a software supply chain attack (malicious update to trusted package)

3. Malicious assets in collaborative creation workflows
   — Platform ecosystems often include shared/open asset libraries; attackers publish
     malicious assets containing hidden payloads that execute when another creator
     incorporates them into their own content
   — Creator unknowingly distributes the attacker's payload to their own audience

4. Virtual goods / marketplace abuse
   — Fraudulent digital items or catalog entries used to redirect users or harvest
     session data; exploits the virtual goods economy as a delivery mechanism

DATA SOURCES & CITATIONS
-------------------------
All figures are sourced from:
  [1] Kaspersky Securelist, "Gaming-related cyberthreats in 2022–2023" (2023)
      https://securelist.com/game-related-threat-report-2023/110960/
      — 8,682 unique malicious files identified across tracked platforms;
        UGC-heavy platforms ranked among the most-targeted in the industry

  [2] Kaspersky Securelist, "Gaming-related cyberthreats" (2022)
      https://securelist.com/gaming-related-cyberthreats/
      — 1,186 mobile users exposed to platform-delivered malicious files;
        612 unique malicious mobile files; supply chain delivery vector documented

  [3] Platform trust & safety industry benchmarks (2025)
      — Large platforms typically deploy "thousands of trained professionals"
        in 24/7 moderation alongside automated detection systems;
        see platform EU DSA Transparency Reports for detailed moderation statistics

REPLACE BEFORE USING IN PRODUCTION
------------------------------------
TEF is modeled as malicious content *campaigns* (not individual files) that achieve
meaningful user exposure. Vulnerability represents the fraction that reach a user
threshold before takedown. These estimates are derived from industry threat
intelligence; internal data from your platform's trust & safety team or regulatory
transparency reports would improve precision.
"""

from fair_monte_carlo import (
    FAIRModel,
    RiskScenario,
    MonteCarloSimulation,
    PERTDistribution,
    LogNormalDistribution,
    RiskReport,
)


def main():
    print("=" * 70)
    print("Online Platform Scenario 2: Malicious UGC / Developer Supply Chain Abuse")
    print("=" * 70)

    scenario = (
        RiskScenario("Online Platform — Malicious UGC / Developer Supply Chain Abuse")

        # THREAT EVENT FREQUENCY (TEF)
        # Modeled as the number of malicious content campaigns published per year
        # capable of reaching meaningful user exposure. Industry data documents
        # 8,682 unique malicious files across tracked platforms in one year [1],
        # but most are external (phishing lures, fake downloads). In-platform
        # malicious campaigns are a subset. Range is conservative to reflect that
        # large-scale campaigns are rarer than individual phishing attempts.
        # Source: [1][2]
        .with_tef(PERTDistribution(50, 150, 500))

        # VULNERABILITY
        # Fraction of malicious content campaigns that achieve user exposure before
        # detection and takedown. Large platforms employ automated detection and
        # significant human moderation capacity [3], catching most low-sophistication
        # attempts quickly. Higher vulnerability applies to compromised legitimate
        # creator accounts (attack hides behind an established trust profile) and
        # to malicious shared assets (which may persist undetected in content built
        # by unwitting creators).
        # Source: [3]
        .with_vulnerability(PERTDistribution(0.05, 0.15, 0.30))

        # PRIMARY LOSS MAGNITUDE (per successful campaign)
        # When malicious content reaches users before takedown, primary loss includes:
        # digital assets stolen from affected accounts, unauthorized purchases via
        # exposed payment methods, and platform cost of account remediation.
        # Range reflects scale: a small campaign might affect dozens of accounts
        # (~$10K impact), while a large campaign exploiting a popular content creator
        # could affect thousands (~$500K).
        .with_primary_loss(LogNormalDistribution(low=10_000, high=500_000))

        # SECONDARY LOSS
        # Frequency: ~25% of successful UGC supply chain incidents escalate to
        # secondary losses — not every compromised content submission generates media
        # coverage or regulatory inquiry, but high-profile incidents involving younger
        # users do.
        # Magnitude: Incident response, creator ecosystem communications, potential
        # regulatory scrutiny, reputational impact. Upper bound reflects a worst-case
        # scenario where a high-traffic content submission is compromised and receives
        # significant press attention.
        .with_secondary_loss(
            frequency=0.25,
            magnitude=LogNormalDistribution(low=100_000, high=2_000_000)
        )
        .build()
    )

    sim = MonteCarloSimulation(iterations=10_000, seed=42)
    results = sim.run(scenario)

    report = RiskReport(results)
    report.print_summary()

    print("\nKey Risk Statistics:")
    print(f"  Mean ALE:   ${results.mean('ale'):,.0f}")
    print(f"  Median ALE: ${results.median('ale'):,.0f}")
    print(f"  95% VaR:    ${results.var(0.95):,.0f}")
    print(f"  95% CVaR:   ${results.cvar(0.95):,.0f}")

    # Compare the impact of tightening platform-side detection (lower vulnerability)
    print("\n" + "=" * 70)
    print("Control Analysis: Impact of Improved Automated Detection")
    print("=" * 70)

    # Baseline: current moderation posture (as above)
    baseline = (
        RiskScenario("Baseline — Current Moderation")
        .with_tef(PERTDistribution(50, 150, 500))
        .with_vulnerability(PERTDistribution(0.05, 0.15, 0.30))
        .with_primary_loss(LogNormalDistribution(low=10_000, high=500_000))
        .with_secondary_loss(
            frequency=0.25,
            magnitude=LogNormalDistribution(low=100_000, high=2_000_000)
        )
        .build()
    )

    # Improved: enhanced ML-based detection at upload reduces vulnerability —
    # more campaigns caught before any user exposure
    improved = (
        RiskScenario("Improved — Enhanced Upload-Time Detection")
        .with_tef(PERTDistribution(50, 150, 500))          # Same attack frequency
        .with_vulnerability(PERTDistribution(0.01, 0.05, 0.10))  # Significantly lower success rate
        .with_primary_loss(LogNormalDistribution(low=10_000, high=500_000))
        .with_secondary_loss(
            frequency=0.25,
            magnitude=LogNormalDistribution(low=100_000, high=2_000_000)
        )
        .build()
    )

    comparison = sim.run_comparison(baseline, improved)

    print(f"\nBaseline Mean ALE:  ${comparison['baseline'].mean('ale'):,.0f}")
    print(f"Improved Mean ALE:  ${comparison['alternative'].mean('ale'):,.0f}")
    print(f"\nRisk Reduction:")
    print(f"  Mean:                       ${comparison['risk_reduction']['mean']:,.0f}")
    print(f"  Median:                     ${comparison['risk_reduction']['median']:,.0f}")
    print(f"  Probability of reduction:   {comparison['risk_reduction']['prob_positive_reduction']:.1f}%")

    print("\nData Sources:")
    print("  [1] Kaspersky Securelist 2023: securelist.com/game-related-threat-report-2023/110960/")
    print("  [2] Kaspersky Securelist 2022: securelist.com/gaming-related-cyberthreats/")
    print("  [3] Platform trust & safety benchmarks (see EU DSA transparency reports)")


if __name__ == "__main__":
    main()
