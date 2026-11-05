"""Synthetic game-balance values, not live national statistics."""
COUNTRIES = {
 "India":{"iso":"IND","population":1450,"gdp":4.0,"stability":68,"tech":61,"military":70,"resources":58,"style":"growth-focused, pragmatic"},
 "China":{"iso":"CHN","population":1410,"gdp":18.0,"stability":72,"tech":82,"military":88,"resources":70,"style":"industrial, strategic, long-term"},
 "United States":{"iso":"USA","population":345,"gdp":28.0,"stability":70,"tech":94,"military":96,"resources":82,"style":"innovation-led, alliance-oriented"},
 "Indonesia":{"iso":"IDN","population":283,"gdp":1.4,"stability":67,"tech":54,"military":48,"resources":76,"style":"trade-focused, cautious"},
 "Pakistan":{"iso":"PAK","population":250,"gdp":0.37,"stability":52,"tech":48,"military":62,"resources":42,"style":"security-conscious"},
 "Nigeria":{"iso":"NGA","population":232,"gdp":0.25,"stability":49,"tech":43,"military":42,"resources":74,"style":"resource-rich, development-focused"},
 "Brazil":{"iso":"BRA","population":212,"gdp":2.2,"stability":66,"tech":59,"military":51,"resources":86,"style":"agricultural, diplomatic"},
 "Bangladesh":{"iso":"BGD","population":174,"gdp":0.45,"stability":58,"tech":47,"military":34,"resources":36,"style":"export-led, stability-focused"},
 "Russia":{"iso":"RUS","population":144,"gdp":2.0,"stability":60,"tech":72,"military":84,"resources":91,"style":"resource-focused, security-driven"},
 "Ethiopia":{"iso":"ETH","population":132,"gdp":0.16,"stability":51,"tech":39,"military":38,"resources":55,"style":"development-focused, regional"}}
ACTIONS=["invest_economy","research","social_program","diplomacy","trade","mobilize","deescalate","sanction","conflict"]
ACTION_LABELS={"invest_economy":"Invest in economy","research":"Fund research","social_program":"Launch social programme","diplomacy":"Improve relations","trade":"Propose trade agreement","mobilize":"Increase readiness","deescalate":"De-escalate tensions","sanction":"Apply economic pressure","conflict":"Initiate abstract conflict"}
