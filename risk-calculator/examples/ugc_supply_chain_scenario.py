#!/usr/bin/env python3
"""
Gaming Platform Scenario 2: Malicious UGC / Developer Supply Chain Abuse
=========================================================================

THREAT SUMMARY
--------------
A major gaming platform hosts approximately 40 million user-created experiences
(games). The platform's open developer model — anyone can publish a game — creates
a supply chain risk: a threat actor can publish a malicious experience that harvests
player credentials, redirects children to phishing sites, or delivers malware,
using the platform's own trust model as cover. Unlike direct phishing (Scenario 1),
the attack surface here is the developer ecosystem, not the end user.

This scenario models the risk from malicious games that reach a meaningful player
count before detection and takedown — the period of exposure where player accounts
are at risk.

ATTACK VECTORS (in order of documented prevalence)
---------------------------------------------------
1. Newly registered malicious developer accounts
   — Attacker creates a free developer account and publishes a game with embedded
     credential harvesters, clickjacking to external phishing pages, or social
     engineering prompts (e.g., "enter your password to claim free in-game currency")
   — Low barrier to entry; the platform's trust lends legitimacy to the game UI

2. Compromised legitimate developer accounts
   — Existing developer with established player base is phished or credential-stuffed
   — Attacker injects malicious content into an already-popular experience
   — High impact: existing player trust accelerates exposure before detection
   — Analogous to a software supply chain attack (malicious update to trusted package)

3. Malicious scripts in collaborative development (model theft / script injection)
   — Platform developer tools allow free-model assets; attackers publish malicious
     free models containing hidden scripts that execute when a developer includes
     them in their game
   — Developer unknowingly ships the attacker's script to their own player base

4. UGC item fraud (avatar marketplace abuse)
   — Fraudulent avatar items or catalog entries used to redirect players or harvest
     session data; exploits the virtual goods economy as a delivery mechanism

DATA SOURCES & CITATIONS
-------------------------
All figures are sourced from:
  [1] Kaspersky Securelist, "Gaming-related cyberthreats in 2022–2023" (2023)
      https://securelist.com/game-related-threat-report-2023/110960/
      — 8,682 unique malicious files targeting platform users; 20.37% of all gaming detections;
        platform ranked #2 most-targeted game overall

  [2] Kaspersky Securelist, "Gaming-related cyberthreats" (2022)
      https://securelist.com/gaming-related-cyberthreats/
      — 1,186 mobile users exposed to platform-delivered malicious files;
        612 unique malicious mobile files; supply chain delivery vector documented

  [3] Platform Safety Tools Page (2025)
      — "Thousands of trained professionals" in 24/7 moderation;
        100+ safety enhancements in 2025; automated detection + human review layer confirmed
      — Note: granular takedown counts are not published; see platform EU DSA
        Transparency Reports (downloadable PDF) for detailed moderation statistics

REPLACE BEFORE USING IN PRODUCTION
------------------------------------
TEF is modeled as malicious game *campaigns* (not individual files) that achieve
meaningful player exposure. Vulnerability represents the fraction that reach a
player threshold before takedown. These are estimated from the Kaspersky malicious
file counts and the platform's described moderation architecture; internal data from
the platform's trust & safety team or the EU DSA transparency report would improve precision.
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
    print("Gaming Platform Scenario 2: Malicious UGC / Developer Supply Chain Abuse")
    print("=" * 70)

    scenario = (
        RiskScenario("Gaming Platform — Malicious UGC / Developer Supply Chain Abuse")

        # THREAT EVENT FREQUENCY (TEF)
        # Modeled as the number of malicious game campaigns published per year that
        # are capable of reaching meaningful player exposure. Kaspersky documented
        # 8,682 unique malicious files targeting the platform in one year [1], but most
        # of these are external (phishing lures, fake downloads). In-platform
        # malicious campaigns are a subset. Range is conservative to reflect that
        # large-scale campaigns are rarer than individual phishing attempts.
        # Source: [1][2]
        .with_tef(PERTDistribution(50, 150, 500))

        # VULNERABILITY
        # Fraction of malicious game campaigns that achieve exposure (reach players)
        # before detection and takedown. The platform employs automated detection and
        # thousands of human moderators [3], meaning most low-sophistication attempts
        # are caught quickly. Higher vulnerability applies to compromised legitimate
        # developer accounts (attack hides behind an established trust profile) and
        # to malicious free-model scripts (which may persist undetected in games
        # built by unwitting developers).
        # Source: [3]
        .with_vulnerability(PERTDistribution(0.05, 0.15, 0.30))

        # PRIMARY LOSS MAGNITUDE (per successful campaign)
        # When a malicious experience reaches players before takedown, primary loss
        # includes: virtual currency stolen from affected accounts, unauthorized
        # purchases via exposed payment methods, and cost to the platform of account
        # remediation. Range reflects scale: a small campaign might affect dozens of
        # accounts (~$10K impact), while a large campaign exploiting a popular
        # experience could affect thousands (~$500K).
        .with_primary_loss(LogNormalDistribution(low=10_000, high=500_000))

        # SECONDARY LOSS
        # Frequency: ~25% of successful UGC supply chain incidents escalate to
        # secondary losses — not every compromised game generates media coverage or
        # regulatory inquiry, but high-profile incidents involving child victims do.
        # Magnitude: Incident response, developer ecosystem communications, potential
        # FTC/regulatory scrutiny, reputational impact. Upper bound reflects a
        # worst-case scenario where a popular experience with millions of plays is
        # compromised and the incident receives significant press attention.
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
    # more campaigns caught before any player exposure
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
    print("  [3] Platform Safety Tools 2025: (see platform's official safety documentation)")


if __name__ == "__main__":
    main()
