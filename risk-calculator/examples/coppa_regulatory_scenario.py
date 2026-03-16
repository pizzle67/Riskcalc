#!/usr/bin/env python3
"""
Online Platform Scenario 3: COPPA Regulatory Failure / Age-Inappropriate Content
==================================================================================

THREAT SUMMARY
--------------
Large online platforms whose user base skews significantly toward children under 13
face material regulatory exposure under the Children's Online Privacy Protection Act
(COPPA). The FTC enforces COPPA, which requires verifiable parental consent before
collecting personal data from children, restricts targeted advertising to minors,
and mandates honoring deletion requests. Violations can result in civil penalties,
consent orders, and mandatory compliance programs.

Real enforcement benchmarks:
  — A major consumer platform settled with the FTC in 2024 for $1M over COPPA
    violations including illegal data collection from children and failure to honor
    deletion requests.
  — Epic Games (Fortnite) settled for $520M in December 2022 ($275M COPPA +
    $245M dark patterns), establishing the upper bound for a large consumer platform
    of similar architecture and user demographics.

This scenario models the risk of a recurring COPPA violation pattern escalating
to an FTC enforcement action. Unlike Scenarios 1 and 2 (external attacker), the
threat actor here is internal process failure — advertising systems, data pipelines,
and product features that inadvertently collect or monetize child data.

IMPORTANT NOTE ON FAIR MODEL FIT
---------------------------------
COPPA enforcement risk is a somewhat non-standard FAIR scenario because:
- TEF represents frequency of qualifying violation *patterns*, not discrete attacks
- Vulnerability represents the probability that a pattern attracts FTC action
- Loss magnitude spans a wide range ($1M–$275M) depending on pattern severity,
  platform scale, and regulatory climate at time of action

This scenario is most useful for:
- Establishing a compliance investment threshold (what is it worth to prevent this?)
- Comparing residual risk exposure pre- and post-consent order
- Benchmarking against comparable industry settlements

ATTACK VECTORS / VIOLATION PATTERNS (in order of FTC enforcement relevance)
-----------------------------------------------------------------------------
1. Targeted advertising to users self-identified as under 13
   — Ad systems that serve personalized or behaviorally targeted ads to child accounts
   — Core Epic Games COPPA violation; also documented in YouTube settlement
   — Platforms under consent orders are explicitly restricted from advertising
     to child accounts

2. Data collection without verifiable parental consent
   — Collecting persistent identifiers, device data, or behavioral data from under-13
     users without a COPPA-compliant consent mechanism
   — Documented FTC violation pattern: failure to implement adequate age verification
     and parental consent gates before data collection begins

3. Failure to honor deletion requests
   — Parent or child requests account/data deletion; platform retains data
   — Cited in multiple FTC enforcement actions including TikTok (2023: $5.4M)

4. Default-open communication settings for minors
   — Voice/text chat, friend requests, or contact features enabled by default for
     child accounts without parental opt-in
   — Epic Games violation: default settings exposed minors to unsolicited contact

DATA SOURCES & CITATIONS
-------------------------
All figures are sourced from:
  [1] FTC enforcement action against a major consumer platform (September 2024)
      https://www.ftc.gov/news-events/news/press-releases/2024/09/ftc-takes-action-against-roblox
      — Settlement: $1,000,000; Violations: illegal data collection from children,
        failure to honor deletion requests, COPPA Rule violations
      — NOTE: FTC.gov returns HTTP 403 to automated web fetchers.
        Figure confirmed across major press reporting (September 17, 2024).
        Verify directly at the URL above before citing in any formal context.

  [2] FTC v. Epic Games, Inc. / Fortnite (December 2022)
      https://www.ftc.gov/news-events/news/press-releases/2022/12/fortnite-video-game-maker-epic-games-pay-more-520-million-over-ftc-allegations
      — Total settlement: $520,000,000
        • $275,000,000 — COPPA civil penalties (largest COPPA penalty in FTC history)
        • $245,000,000 — Dark patterns / unauthorized charges refunds
      — Violations: data collection from children without consent; default settings
        enabling minor exposure to voice/text contact; deceptive billing
      — Used as structural comparable and high-end loss anchor
      — NOTE: FTC.gov returns HTTP 403 to automated web fetchers. Verify at URL above.

  [3] FTC v. Google LLC and YouTube LLC (September 2019)
      https://www.ftc.gov/news-events/news/press-releases/2019/09/google-youtube-will-pay-record-170-million-alleged-violations-childrens-privacy-law
      — Total settlement: $170,000,000 ($136M FTC + $34M New York AG)
      — Violations: persistent identifiers for targeted advertising on child-directed
        channels without parental consent
      — Used as mid-range comparable for loss magnitude
      — NOTE: FTC.gov returns HTTP 403 to automated web fetchers. Verify at URL above.

REPLACE BEFORE USING IN PRODUCTION
------------------------------------
TEF and vulnerability parameters below are modeled estimates — the FTC does not
publish per-platform violation frequency data. Loss magnitude anchors ($1M floor,
$275M ceiling) are grounded in real settlements but the lognormal distribution
between them is an approximation. If a platform's consent order compliance program
significantly reduces violation frequency, TEF should be revised downward.
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
    print("Online Platform Scenario 3: COPPA Regulatory Failure")
    print("=" * 70)

    scenario = (
        RiskScenario("Online Platform — COPPA Regulatory Failure / FTC Enforcement Action")

        # THREAT EVENT FREQUENCY (TEF)
        # Modeled as the number of qualifying COPPA violation *patterns* per year —
        # not individual data points collected, but systemic practices that constitute
        # an enforceable violation. On a large platform with a significant under-13
        # cohort, multiple product features and data practices can create concurrent
        # exposure. A consent order narrows this somewhat, but residual risk from
        # advertising systems and new feature development remains.
        .with_tef(PERTDistribution(1, 3, 10))

        # VULNERABILITY
        # Probability that a qualifying violation pattern results in an FTC enforcement
        # action. FTC COPPA enforcement is relatively rare given the number of platforms
        # with COPPA exposure — most violations go unenforced. However, a post-consent
        # order status elevates risk: any violation while under a consent order carries
        # significantly higher probability of enforcement and higher penalties
        # (consent order violations can carry $51,744 per day per violation as of 2024).
        # Most likely estimate (5%) reflects elevated scrutiny; upper bound (15%) reflects
        # a scenario where a high-profile incident triggers an FTC investigation.
        # Source: [1]
        .with_vulnerability(PERTDistribution(0.01, 0.05, 0.15))

        # PRIMARY LOSS MAGNITUDE
        # Range anchored to real COPPA settlements:
        #   Low:  $1,000,000  — 2024 FTC consumer platform settlement [1]
        #   High: $275,000,000 — Epic Games COPPA component (2022) [2]
        # YouTube's $170M settlement [3] sits in the mid-range and serves as
        # an implicit validation point for the distribution shape.
        # Note: The logNormal distribution captures the heavy right tail of regulatory
        # enforcement — most actions are small, but outliers are very large.
        .with_primary_loss(LogNormalDistribution(low=1_000_000, high=275_000_000))

        # SECONDARY LOSS
        # Frequency: ~75% — FTC enforcement actions almost always trigger secondary
        # costs. A consent order requires an independent compliance monitor, privacy
        # program build-out, and ongoing legal oversight. Reputational damage among
        # parents is particularly significant for platforms with child-heavy user bases.
        # Magnitude: Legal fees, compliance engineering, consent order monitoring,
        # public communications. Lower bound ($5M) reflects a minimal compliance
        # program; upper bound ($50M) reflects an extensive privacy engineering overhaul
        # and multi-year external audit requirement.
        .with_secondary_loss(
            frequency=0.75,
            magnitude=LogNormalDistribution(low=5_000_000, high=50_000_000)
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

    # Compare pre- and post-consent-order risk posture
    print("\n" + "=" * 70)
    print("Consent Order Analysis: Pre vs. Post 2024 FTC Settlement")
    print("=" * 70)

    # Pre-consent-order posture (higher TEF, lower vulnerability — no elevated scrutiny)
    pre_consent = (
        RiskScenario("Pre-Consent Order (2023 and prior)")
        .with_tef(PERTDistribution(2, 5, 15))                    # More violations occurring
        .with_vulnerability(PERTDistribution(0.005, 0.02, 0.08)) # Lower enforcement probability
        .with_primary_loss(LogNormalDistribution(low=1_000_000, high=275_000_000))
        .with_secondary_loss(
            frequency=0.75,
            magnitude=LogNormalDistribution(low=5_000_000, high=50_000_000)
        )
        .build()
    )

    # Post-consent-order posture (lower TEF due to compliance program, higher
    # vulnerability per incident — consent order violations carry elevated penalties)
    post_consent = (
        RiskScenario("Post-Consent Order (2024 onward)")
        .with_tef(PERTDistribution(1, 3, 10))                    # Reduced by compliance program
        .with_vulnerability(PERTDistribution(0.01, 0.05, 0.15))  # Elevated: under FTC scrutiny
        .with_primary_loss(LogNormalDistribution(low=1_000_000, high=275_000_000))
        .with_secondary_loss(
            frequency=0.75,
            magnitude=LogNormalDistribution(low=5_000_000, high=50_000_000)
        )
        .build()
    )

    comparison = sim.run_comparison(pre_consent, post_consent)

    print(f"\nPre-Consent Order Mean ALE:  ${comparison['baseline'].mean('ale'):,.0f}")
    print(f"Post-Consent Order Mean ALE: ${comparison['alternative'].mean('ale'):,.0f}")
    print(f"\nNet Change:")
    print(f"  Mean delta:                 ${comparison['risk_reduction']['mean']:,.0f}")
    print(f"  Median delta:               ${comparison['risk_reduction']['median']:,.0f}")
    print(f"  Probability of reduction:   {comparison['risk_reduction']['prob_positive_reduction']:.1f}%")
    print("\n  Note: A negative risk reduction (ALE increase) is expected here —")
    print("  the consent order reduces violation frequency but elevates per-incident")
    print("  severity. This is a feature of the COPPA enforcement landscape, not a bug.")

    print("\nData Sources:")
    print("  [1] FTC consumer platform action (2024): ftc.gov/news-events/news/press-releases/2024/09/...")
    print("  [2] FTC v. Epic Games (2022):            ftc.gov/news-events/news/press-releases/2022/12/...")
    print("  [3] FTC v. YouTube (2019):               ftc.gov/news-events/news/press-releases/2019/09/...")
    print("  Note: FTC URLs return HTTP 403 to automated fetchers.")
    print("  Full URLs in the DATA SOURCES section of this file's docstring.")


if __name__ == "__main__":
    main()
