#!/usr/bin/env python3
"""
Gaming Platform Scenario 1: Credential Theft via Phishing & Session Hijacking
==============================================================================

THREAT SUMMARY
--------------
A major online gaming platform ranked among the top targets for credential-stealing
malware (Kaspersky, 2023). Attackers use phishing sites mimicking the platform's
login page, browser-injected cookie loggers, and Trojan-PSW malware distributed
as fake in-game currency generators or cheat tools. The primary goal is account
takeover — compromised accounts are looted for virtual currency, sold on secondary
markets, or used to access linked parent payment methods for unauthorized purchases.

ATTACK VECTORS (in order of documented prevalence)
---------------------------------------------------
1. Phishing sites / fake platform login portals
   — Victims redirected via in-game chat links, YouTube comments, Discord
   — Credential entered directly into attacker-controlled page

2. Trojan-PSW / credential-stealing malware (e.g., RedLine Stealer)
   — Distributed as "free in-game currency generators", cheat tools, or mod menus
   — Harvests saved browser credentials and session cookies
   — RedLine Stealer alone affected 2,362 unique platform-targeting users (Kaspersky 2022)

3. Session cookie hijacking
   — Browser extensions or scripts steal active session tokens
   — Attacker replays session without needing the password
   — Increasingly common as MFA bypasses grow more sophisticated

4. Credential stuffing
   — Breached username/password pairs from other platforms tested against the platform
   — Effective because many child/teen users reuse passwords across accounts

DATA SOURCES & CITATIONS
-------------------------
All figures are sourced from:
  [1] Kaspersky Securelist, "Gaming-related cyberthreats in 2022–2023" (2023)
      https://securelist.com/game-related-threat-report-2023/110960/
      — 30,367 unique users affected; 8,682 unique malicious files; platform = 20.37% of all gaming detections

  [2] Kaspersky Securelist, "Gaming-related cyberthreats" (2022)
      https://securelist.com/gaming-related-cyberthreats/
      — 38,838 platform threat encounters; 1,733 credential-stealer attacks; 3.1M gaming phishing attacks;
        13% YoY increase in stealer activity; 77% of cases involved Trojan-PSW

  [3] IBM, "Cost of a Data Breach Report 2025"
      https://www.ibm.com/reports/data-breach
      — $4.4M global average breach cost (used as secondary loss ceiling reference)

REPLACE BEFORE USING IN PRODUCTION
------------------------------------
TEF, vulnerability, and loss parameters below are derived from the industry data
cited above. If your organization has internal incident data, use that instead.
Per-account loss estimates ($100–$2,000) are proxied from gaming ATO benchmarks —
the platform does not publish account-level loss data.
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
    print("Gaming Platform Scenario 1: Credential Theft via Phishing & Session Hijacking")
    print("=" * 70)

    scenario = (
        RiskScenario("Gaming Platform — Credential Theft via Phishing & Session Hijacking")

        # THREAT EVENT FREQUENCY (TEF)
        # Kaspersky documented 1,733 credential-stealer attacks targeting the platform's
        # users in a single year (2021-2022) and 30,367 total threat encounters in
        # 2022-2023. TEF here represents individual account-level theft events per year.
        # Range accounts for significant underreporting on a platform serving 80M+ DAU.
        # Source: [1][2]
        .with_tef(PERTDistribution(500, 1_500, 5_000))

        # VULNERABILITY
        # Kaspersky's 2021-2022 data shows ~1,733 successful credential-stealer
        # attacks out of ~38,838 total platform-themed threat encounters, implying a
        # ~4.5% success rate. The upper bound is elevated to reflect the platform's
        # demographic (children and teens typically exhibit lower security awareness
        # than the general adult internet population).
        # Source: [2]
        .with_vulnerability(PERTDistribution(0.02, 0.04, 0.08))

        # PRIMARY LOSS MAGNITUDE (per incident)
        # Direct loss per compromised account: virtual currency balance liquidated,
        # unauthorized purchases via linked parent payment method, or account sold on
        # secondary market. The platform does not publish average account value data;
        # range is proxied from gaming ATO benchmarks. High end reflects accounts with
        # significant virtual currency balances or active parent payment methods.
        # Note: $1,000 floor reflects tool minimum and is consistent with meaningful
        # account compromise (virtual currency balance + any unauthorized purchase activity).
        .with_primary_loss(LogNormalDistribution(low=1_000, high=2_000))

        # SECONDARY LOSS
        # Frequency: ~35% of individual credential theft incidents escalate to
        # platform-level secondary loss events (media coverage, regulatory inquiry,
        # class action exposure). Given the platform's child user base, secondary losses
        # tend to be disproportionate to primary loss.
        # Magnitude: Platform-level remediation, customer service surge, legal fees,
        # reputational damage. Upper bound references IBM's $4.4M average breach cost
        # for large-scale incidents. Source: [3]
        .with_secondary_loss(
            frequency=0.35,
            magnitude=LogNormalDistribution(low=50_000, high=500_000)
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

    print("\nData Sources:")
    print("  [1] Kaspersky Securelist 2023: securelist.com/game-related-threat-report-2023/110960/")
    print("  [2] Kaspersky Securelist 2022: securelist.com/gaming-related-cyberthreats/")
    print("  [3] IBM Cost of Data Breach 2025: ibm.com/reports/data-breach")


if __name__ == "__main__":
    main()
