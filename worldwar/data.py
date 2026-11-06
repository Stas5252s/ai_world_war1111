
"""2024 World Bank population/GDP baselines plus synthetic game-balance indicators."""

_FEATURED_COUNTRIES = {
    "India": {
        "iso": "IND", "population": 1450, "gdp": 4.0,
        "stability": 68, "tech": 61, "military": 70, "resources": 58,
        "style": "growth-focused, pragmatic"
    },
    "China": {
        "iso": "CHN", "population": 1410, "gdp": 18.0,
        "stability": 72, "tech": 82, "military": 88, "resources": 70,
        "style": "industrial, strategic, long-term"
    },
    "United States": {
        "iso": "USA", "population": 345, "gdp": 28.0,
        "stability": 70, "tech": 94, "military": 96, "resources": 82,
        "style": "innovation-led, alliance-oriented"
    },
    "Indonesia": {
        "iso": "IDN", "population": 283, "gdp": 1.4,
        "stability": 67, "tech": 54, "military": 48, "resources": 76,
        "style": "trade-focused, cautious"
    },
    "Pakistan": {
        "iso": "PAK", "population": 250, "gdp": 0.37,
        "stability": 52, "tech": 48, "military": 62, "resources": 42,
        "style": "security-conscious"
    },
    "Nigeria": {
        "iso": "NGA", "population": 232, "gdp": 0.25,
        "stability": 49, "tech": 43, "military": 42, "resources": 74,
        "style": "resource-rich, development-focused"
    },
    "Brazil": {
        "iso": "BRA", "population": 212, "gdp": 2.2,
        "stability": 66, "tech": 59, "military": 51, "resources": 86,
        "style": "agricultural, diplomatic"
    },
    "Bangladesh": {
        "iso": "BGD", "population": 174, "gdp": 0.45,
        "stability": 58, "tech": 47, "military": 34, "resources": 36,
        "style": "export-led, stability-focused"
    },
    "Russia": {
        "iso": "RUS", "population": 144, "gdp": 2.0,
        "stability": 60, "tech": 72, "military": 84, "resources": 91,
        "style": "resource-focused, security-driven"
    },
    "Ethiopia": {
        "iso": "ETH", "population": 132, "gdp": 0.16,
        "stability": 51, "tech": 39, "military": 38, "resources": 55,
        "style": "development-focused, regional"
    },

    # Europe
    "Germany": {
        "iso": "DEU", "population": 84, "gdp": 4.5,
        "stability": 78, "tech": 88, "military": 65, "resources": 48,
        "style": "industrial, diplomatic, stability-focused"
    },
    "France": {
        "iso": "FRA", "population": 68, "gdp": 3.1,
        "stability": 69, "tech": 84, "military": 76, "resources": 55,
        "style": "strategic, diplomatic, independent"
    },
    "United Kingdom": {
        "iso": "GBR", "population": 69, "gdp": 3.4,
        "stability": 73, "tech": 87, "military": 79, "resources": 42,
        "style": "alliance-oriented, financial, pragmatic"
    },
    "Italy": {
        "iso": "ITA", "population": 59, "gdp": 2.3,
        "stability": 65, "tech": 77, "military": 62, "resources": 48,
        "style": "trade-focused, diplomatic"
    },
    "Poland": {
        "iso": "POL", "population": 38, "gdp": 0.85,
        "stability": 72, "tech": 70, "military": 67, "resources": 53,
        "style": "security-focused, alliance-oriented"
    },
    "North Korea": {
        "outlook": "Prioritise regime survival, sovereignty and deterrence against perceived external threats.",
        "priorities": ["regime security", "deterrence", "self-reliance", "strategic weapons programme", "economic survival"],
        "red_lines": ["direct threats to regime survival", "foreign-backed political change", "loss of deterrent capability"],
        "preferred_partners": ["China", "Russia"],
        "competitors": ["South Korea", "United States", "Japan"],
        "posture": "Highly security-focused, isolated and reliant on deterrence and selective external support."
    },
    "Turkey": {
        "iso": "TUR", "population": 86, "gdp": 1.3,
        "stability": 56, "tech": 66, "military": 73, "resources": 68,
        "style": "regional influence, strategic autonomy"
    },

    # Asia and Middle East
    "Japan": {
        "iso": "JPN", "population": 123, "gdp": 4.2,
        "stability": 80, "tech": 93, "military": 70, "resources": 30,
        "style": "technology-led, cautious, trade-oriented"
    },
    "South Korea": {
        "iso": "KOR", "population": 52, "gdp": 1.8,
        "stability": 74, "tech": 91, "military": 76, "resources": 32,
        "style": "technology-driven, security-conscious"
    },
    "Iran": {
        "iso": "IRN", "population": 92, "gdp": 0.4,
        "stability": 48, "tech": 61, "military": 69, "resources": 82,
        "style": "independent, resource-focused, security-driven"
    },
    "Saudi Arabia": {
        "iso": "SAU", "population": 35, "gdp": 1.1,
        "stability": 76, "tech": 67, "military": 72, "resources": 96,
        "style": "energy-focused, investment-oriented"
    },
    "Vietnam": {
        "iso": "VNM", "population": 101, "gdp": 0.47,
        "stability": 76, "tech": 59, "military": 57, "resources": 65,
        "style": "export-led, pragmatic, development-focused"
    },

    # Africa
    "Egypt": {
        "iso": "EGY", "population": 118, "gdp": 0.4,
        "stability": 54, "tech": 48, "military": 67, "resources": 60,
        "style": "regional influence, security-focused"
    },
    "South Africa": {
        "iso": "ZAF", "population": 64, "gdp": 0.4,
        "stability": 57, "tech": 63, "military": 46, "resources": 78,
        "style": "regional diplomacy, resource-focused"
    },

    # Americas
    "Mexico": {
        "iso": "MEX", "population": 132, "gdp": 1.8,
        "stability": 58, "tech": 64, "military": 48, "resources": 72,
        "style": "trade-oriented, regional development"
    },
    "Canada": {
        "iso": "CAN", "population": 42, "gdp": 2.2,
        "stability": 82, "tech": 83, "military": 58, "resources": 90,
        "style": "alliance-oriented, resource-rich, diplomatic"
    },
    "Argentina": {
        "iso": "ARG", "population": 46, "gdp": 0.63,
        "stability": 51, "tech": 62, "military": 43, "resources": 86,
        "style": "agricultural, reform-oriented"
    },

    # Oceania
    "Australia": {
        "iso": "AUS", "population": 27, "gdp": 1.8,
        "stability": 81, "tech": 84, "military": 65, "resources": 88,
        "style": "resource-rich, alliance-oriented"
    }
}



_WORLDVIEWS = {
    "United States": {
        "outlook": "Maintain a rules-based international order that preserves US leadership and freedom of navigation.",
        "priorities": [
            "alliances",
            "technology leadership",
            "financial influence",
            "open trade",
            "deterrence"
        ],
        "red_lines": [
            "major threats to treaty allies",
            "hostile domination of key regions"
        ],
        "preferred_partners": [
            "Canada",
            "United Kingdom",
            "Japan",
            "South Korea",
            "Australia",
            "Germany",
            "France",
            "Poland"
        ],
        "competitors": [
            "China",
            "Russia",
            "Iran"
        ],
        "posture": "Global leadership through alliances, institutions and innovation."
    },
    "China": {
        "outlook": "Build a more multipolar order, protect sovereignty and expand China's economic and diplomatic weight.",
        "priorities": [
            "industrial capacity",
            "trade corridors",
            "technology independence",
            "regional influence",
            "energy security"
        ],
        "red_lines": [
            "foreign-backed separatism",
            "containment near its borders"
        ],
        "preferred_partners": [
            "Russia",
            "Pakistan",
            "Iran"
        ],
        "competitors": [
            "United States",
            "India",
            "Japan"
        ],
        "posture": "Long-term economic statecraft, regional leverage and strategic patience."
    },
    "Russia": {
        "outlook": "Seek recognition as an independent great power and a security buffer in its near abroad.",
        "priorities": [
            "regime security",
            "strategic depth",
            "energy exports",
            "military deterrence",
            "great-power status"
        ],
        "red_lines": [
            "hostile military infrastructure near its borders",
            "loss of influence in its near abroad"
        ],
        "preferred_partners": [
            "China",
            "Belarus",
            "Iran"
        ],
        "competitors": [
            "United States",
            "United Kingdom",
            "Poland",
            "Ukraine"
        ],
        "posture": "Security-first and focused on preserving regional influence."
    },
    "India": {
        "outlook": "Preserve strategic autonomy while becoming a leading power in a multipolar world.",
        "priorities": [
            "economic growth",
            "technology",
            "border security",
            "Indian Ocean influence",
            "diplomatic independence"
        ],
        "red_lines": [
            "cross-border security threats",
            "strategic encirclement"
        ],
        "preferred_partners": [
            "United States",
            "France",
            "Japan",
            "Australia"
        ],
        "competitors": [
            "China",
            "Pakistan"
        ],
        "posture": "Multi-alignment, pragmatic partnerships and regional deterrence."
    },
    "United Kingdom": {
        "outlook": "Preserve an influential global role through alliances, finance, diplomacy and maritime security.",
        "priorities": [
            "NATO cohesion",
            "financial services",
            "open sea lanes",
            "technology",
            "European security"
        ],
        "red_lines": [
            "threats to close allies",
            "hostile domination of Europe"
        ],
        "preferred_partners": [
            "United States",
            "Canada",
            "Australia",
            "France",
            "Germany",
            "Poland",
            "Japan"
        ],
        "competitors": [
            "Russia",
            "China"
        ],
        "posture": "Alliance-centred global engagement."
    },
    "France": {
        "outlook": "Strengthen European sovereignty while retaining an independent global diplomatic and security role.",
        "priorities": [
            "European integration",
            "strategic autonomy",
            "defence industry",
            "diplomatic influence",
            "energy independence"
        ],
        "red_lines": [
            "collapse of European security",
            "loss of freedom of action"
        ],
        "preferred_partners": [
            "Germany",
            "Italy",
            "United Kingdom",
            "Poland",
            "United States"
        ],
        "competitors": [
            "Russia"
        ],
        "posture": "European leadership, diplomacy and selective independent action."
    },
    "Germany": {
        "outlook": "Protect European stability and prosperity through integration, trade and collective security.",
        "priorities": [
            "EU cohesion",
            "industrial competitiveness",
            "export markets",
            "energy security",
            "NATO cooperation"
        ],
        "red_lines": [
            "major instability in Europe",
            "threats to allied security"
        ],
        "preferred_partners": [
            "France",
            "Poland",
            "Netherlands",
            "United States",
            "United Kingdom"
        ],
        "competitors": [
            "Russia"
        ],
        "posture": "Economic interdependence, multilateral diplomacy and collective defence."
    },
    "Poland": {
        "outlook": "Strengthen the eastern flank of Europe and ensure no hostile power can dominate the region.",
        "priorities": [
            "territorial defence",
            "NATO",
            "EU influence",
            "regional infrastructure",
            "energy diversification"
        ],
        "red_lines": [
            "Russian coercion in Eastern Europe",
            "weakening of allied guarantees"
        ],
        "preferred_partners": [
            "United States",
            "United Kingdom",
            "Germany",
            "France",
            "Ukraine",
            "Lithuania"
        ],
        "competitors": [
            "Russia"
        ],
        "posture": "Hard security guarantees and close regional alliances."
    },
    "Japan": {
        "outlook": "Protect a stable Indo-Pacific order, secure trade routes and prevent coercive regional dominance.",
        "priorities": [
            "maritime security",
            "advanced technology",
            "trade",
            "energy imports",
            "US alliance"
        ],
        "red_lines": [
            "coercion around nearby sea lanes",
            "regional arms imbalance"
        ],
        "preferred_partners": [
            "United States",
            "Australia",
            "South Korea",
            "India",
            "United Kingdom"
        ],
        "competitors": [
            "China",
            "North Korea",
            "Russia"
        ],
        "posture": "Defensive security, economic diplomacy and close partnerships."
    },
    "South Korea": {
        "outlook": "Deter threats on the peninsula while maintaining export-led growth and regional stability.",
        "priorities": [
            "peninsula security",
            "technology exports",
            "US alliance",
            "energy security",
            "supply chains"
        ],
        "red_lines": [
            "direct threats from North Korea",
            "disruption of critical trade"
        ],
        "preferred_partners": [
            "United States",
            "Japan",
            "Australia"
        ],
        "competitors": [
            "North Korea"
        ],
        "posture": "Deterrence backed by trade and technology diplomacy."
    },
    "Turkey": {
        "outlook": "Act as an autonomous regional power and avoid dependence on any single great-power bloc.",
        "priorities": [
            "regional influence",
            "defence industry",
            "trade corridors",
            "energy transit",
            "diplomatic leverage"
        ],
        "red_lines": [
            "threats near its borders",
            "exclusion from regional decisions"
        ],
        "preferred_partners": [
            "Azerbaijan",
            "Qatar",
            "Pakistan"
        ],
        "competitors": [
            "Greece",
            "Syria"
        ],
        "posture": "Transactional diplomacy, strategic autonomy and regional balancing."
    },
    "Iran": {
        "outlook": "Preserve regime security, resist external pressure and maintain strategic depth in its neighbourhood.",
        "priorities": [
            "sanctions resistance",
            "regional networks",
            "deterrence",
            "energy exports",
            "strategic autonomy"
        ],
        "red_lines": [
            "direct threats to regime survival",
            "foreign military pressure"
        ],
        "preferred_partners": [
            "Russia",
            "China"
        ],
        "competitors": [
            "United States",
            "Israel",
            "Saudi Arabia"
        ],
        "posture": "Regional leverage and resistance to isolation."
    },
    "Saudi Arabia": {
        "outlook": "Protect energy infrastructure while becoming a diversified investment and diplomatic hub.",
        "priorities": [
            "energy markets",
            "economic diversification",
            "regime stability",
            "regional influence",
            "foreign investment"
        ],
        "red_lines": [
            "threats to energy infrastructure",
            "regional isolation"
        ],
        "preferred_partners": [
            "United States",
            "United Kingdom",
            "France",
            "United Arab Emirates",
            "Egypt"
        ],
        "competitors": [
            "Iran"
        ],
        "posture": "Pragmatic balancing, energy diplomacy and investment-led influence."
    },
    "Pakistan": {
        "outlook": "Prioritise national security and strategic balance in South Asia while maintaining external partnerships.",
        "priorities": [
            "border security",
            "strategic deterrence",
            "economic stability",
            "regional connectivity"
        ],
        "red_lines": [
            "major security pressure from India",
            "loss of strategic autonomy"
        ],
        "preferred_partners": [
            "China",
            "Saudi Arabia",
            "Turkey"
        ],
        "competitors": [
            "India"
        ],
        "posture": "Security-first balancing and selected partnerships."
    },
    "Ukraine": {
        "outlook": "Defend sovereignty and territorial integrity, secure durable guarantees and integrate with European institutions.",
        "priorities": [
            "sovereignty",
            "security guarantees",
            "European integration",
            "reconstruction",
            "defence resilience"
        ],
        "red_lines": [
            "territorial aggression",
            "forced loss of sovereignty",
            "abandonment by security partners"
        ],
        "preferred_partners": [
            "Poland",
            "United Kingdom",
            "United States",
            "France",
            "Germany",
            "Canada",
            "Lithuania"
        ],
        "competitors": [
            "Russia"
        ],
        "posture": "Defensive resilience, alliance-building and international legal legitimacy."
    },
    "Canada": {
        "outlook": "Support a stable rules-based order while protecting North American security and open trade.",
        "priorities": [
            "US partnership",
            "Arctic security",
            "critical minerals",
            "trade",
            "multilateral institutions"
        ],
        "red_lines": [
            "threats to North American sovereignty",
            "Arctic coercion"
        ],
        "preferred_partners": [
            "United States",
            "United Kingdom",
            "France",
            "Germany",
            "Australia",
            "Japan"
        ],
        "competitors": [
            "Russia"
        ],
        "posture": "Multilateral diplomacy, alliance cooperation and resource-based influence."
    },
    "Australia": {
        "outlook": "Maintain a secure Indo-Pacific balance and resilient trade links with regional partners.",
        "priorities": [
            "maritime security",
            "US alliance",
            "critical minerals",
            "regional partnerships",
            "trade diversification"
        ],
        "red_lines": [
            "coercive regional hegemony",
            "threats to sea lanes"
        ],
        "preferred_partners": [
            "United States",
            "Japan",
            "United Kingdom",
            "India",
            "South Korea"
        ],
        "competitors": [
            "China"
        ],
        "posture": "Alliance-backed deterrence and regional economic engagement."
    },
    "Brazil": {
        "outlook": "Increase the voice of the Global South and preserve freedom to cooperate across rival blocs.",
        "priorities": [
            "strategic autonomy",
            "agriculture",
            "industrial development",
            "regional leadership",
            "climate diplomacy"
        ],
        "red_lines": [
            "external domination of regional policy",
            "trade isolation"
        ],
        "preferred_partners": [
            "Argentina",
            "Mexico",
            "China",
            "India",
            "South Africa"
        ],
        "competitors": [],
        "posture": "Non-alignment, multilateralism and pragmatic economic partnerships."
    },
    "Indonesia": {
        "outlook": "Preserve ASEAN centrality and avoid being forced to choose between great-power camps.",
        "priorities": [
            "ASEAN cohesion",
            "maritime sovereignty",
            "trade",
            "industrial upgrading",
            "resource value chains"
        ],
        "red_lines": [
            "violation of maritime sovereignty",
            "regional bloc confrontation"
        ],
        "preferred_partners": [
            "Malaysia",
            "Singapore",
            "Japan",
            "Australia",
            "India"
        ],
        "competitors": [],
        "posture": "Non-alignment, regional consensus and pragmatic balancing."
    },
    "Israel": {
        "outlook": "Ensure national security and preserve diplomatic and technological partnerships.",
        "priorities": [
            "security",
            "technology",
            "deterrence",
            "trade",
            "international partnerships"
        ],
        "red_lines": [
            "direct existential threats",
            "cross-border attacks"
        ],
        "preferred_partners": [
            "United States",
            "Germany",
            "United Kingdom",
            "France"
        ],
        "competitors": [
            "Iran"
        ],
        "posture": "Security-first diplomacy and technology-driven influence."
    },
    "Egypt": {
        "outlook": "Preserve national stability and Egypt's central role in Arab and African regional affairs.",
        "priorities": [
            "water security",
            "Suez trade",
            "regional stability",
            "food security",
            "investment"
        ],
        "red_lines": [
            "threats to Nile water access",
            "instability on borders",
            "disruption of Suez traffic"
        ],
        "preferred_partners": [
            "Saudi Arabia",
            "United Arab Emirates",
            "France",
            "United States"
        ],
        "competitors": [
            "Ethiopia"
        ],
        "posture": "Regional balancing and protection of strategic trade routes."
    },
    "United Arab Emirates": {
        "outlook": "Build a secure, globally connected hub for finance, trade, logistics and technology.",
        "priorities": [
            "investment",
            "trade corridors",
            "energy",
            "technology",
            "regional security"
        ],
        "red_lines": [
            "threats to shipping",
            "regional instability"
        ],
        "preferred_partners": [
            "Saudi Arabia",
            "United States",
            "India",
            "France"
        ],
        "competitors": [
            "Iran"
        ],
        "posture": "Commercial diplomacy, investment and flexible partnerships."
    }
}

 
from .country_seed import COUNTRY_SEEDS

def _clamp(value, low=0, high=100):
    return max(low, min(high, value))

COUNTRIES = {}
for _name, _seed in COUNTRY_SEEDS.items():
    _pc = (_seed["gdp"] * 1_000_000_000_000) / max(1, _seed["population"] * 1_000_000)
    _income = max(0, min(1, (_pc - 900) / 65000))
    _code_score = sum(ord(ch) for ch in _seed["iso"])
    _featured = _FEATURED_COUNTRIES.get(_name, {})
    _profile = {
        "iso": _seed["iso"],
        "population": _seed["population"],
        "gdp": _seed["gdp"],
        "stability": round(42 + 38 * _income, 1),
        "tech": round(28 + 66 * _income, 1),
        "military": round(25 + 48 * _income + (_code_score % 17), 1),
        "resources": round(25 + (_code_score * 7 % 70), 1),
        "style": "balanced, national-development focused",
        "worldview": _WORLDVIEWS.get(_name, {"outlook": "Prioritise sovereignty, national development and independent diplomatic choices.", "priorities": ["economic development", "security", "trade", "diplomatic autonomy"], "red_lines": ["direct threats to sovereignty", "severe economic coercion"], "preferred_partners": [], "competitors": [], "posture": "Pragmatic and development-oriented"}),
        "capital": _seed["capital"],
        "lat": _seed["lat"],
        "lon": _seed["lon"],
        "production": round(30 + 60 * _income, 1),
        "budget": round(_seed["gdp"] * 1000 * 0.21, 2),
        "budget_balance": round(_seed["gdp"] * 1000 * 0.012, 2),
        "treasury": round(_seed["gdp"] * 1000 * 0.08, 2),
        "debt": round(_seed["gdp"] * 1000 * (0.25 + (1 - _income) * 0.25), 2),
        "trade": round(_seed["gdp"] * 1000 * (0.25 + _income * 0.35), 2),
        "trade_balance": 0.0,
        "resource_stock": round(45 + (_code_score * 11 % 55), 1),
        "inflation": round(2.0 + (1 - _income) * 5.0, 2),
        "unemployment": round(4.0 + (1 - _income) * 10.0, 2),
        "military_spending": 0.035
    }
    _profile.update({k: v for k, v in _featured.items()
                    if k not in ("population", "gdp", "iso")})
    _profile["iso"] = _seed["iso"]
    _profile["population"] = _seed["population"]
    _profile["gdp"] = _seed["gdp"]
    _profile["capital"] = _seed["capital"]
    _profile["lat"] = _seed["lat"]
    _profile["lon"] = _seed["lon"]
    COUNTRIES[_name] = _profile


ACTIONS = [
    "invest_economy", "research", "social_program", "diplomacy", "trade",
    "mobilize", "deescalate", "sanction", "conflict",
    "form_alliance", "break_alliance", "guarantee_independence", "revoke_guarantee", "ultimatum", "accept_ultimatum", "reject_ultimatum", "sever_relations", "create_bloc", "invite_to_bloc", "declare_war", "peace", "continue_war"
]

ACTION_LABELS = {
    "invest_economy": "Invest in economy",
    "research": "Fund research",
    "social_program": "Launch social programme",
    "diplomacy": "Improve relations",
    "trade": "Propose trade agreement",
    "mobilize": "Increase readiness",
    "deescalate": "De-escalate tensions",
    "sanction": "Apply economic pressure",
    "conflict": "Initiate abstract conflict",
    "form_alliance": "Form alliance",
    "break_alliance": "Break alliance",
    "guarantee_independence": "Guarantee independence",
    "revoke_guarantee": "Revoke guarantee",
    "ultimatum": "Issue ultimatum",
    "accept_ultimatum": "Accept ultimatum",
    "reject_ultimatum": "Reject ultimatum",
    "sever_relations": "Sever diplomatic relations",
    "create_bloc": "Create international bloc",
    "invite_to_bloc": "Invite country to bloc",
    "declare_war": "Declare war",
    "peace": "Negotiate peace",
    "continue_war": "Continue ongoing war"
}
