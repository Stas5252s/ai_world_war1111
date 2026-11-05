
"""Synthetic game-balance values, not live national statistics."""

COUNTRIES = {
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

ACTIONS = [
    "invest_economy",
    "research",
    "social_program",
    "diplomacy",
    "trade",
    "mobilize",
    "deescalate",
    "sanction",
    "conflict"
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
    "conflict": "Initiate abstract conflict"
}
