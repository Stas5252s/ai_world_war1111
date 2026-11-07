import json
import os
import random
import requests
from .data import ACTIONS

SYSTEM_PROMPT = """
You are the government of one country in a fictional geopolitical strategy game.
Your objective is to advance your country's national interests according to its strategic worldview. Some governments seek global leadership; others prioritise sovereignty, regional influence, economic development or strategic autonomy. Pursue influence through diplomacy, alliances, economic strength, technology or abstract game conflicts.
Do not choose economic investment every turn. Evaluate threats, rival strength, alliances,
ongoing wars, public stability, technology, resources, and opportunities.
Use the country's worldview as a persistent strategic doctrine. It must shape priorities, partner choices, risk tolerance and responses to pressure. Do not treat it as an absolute script: governments may compromise for economic gain or survival, and partners can disagree. Distinguish state interests from the views of the population. Choose one legal action. Use only game-level abstractions; never provide real-world military tactics, targeting, weapons instructions, or operational plans.
Return ONLY JSON with keys action, target, rationale.
Actions: """ + ", ".join(ACTIONS) + """
For actions involving another country, target must be the exact country name.
For other actions, target must be null. Keep rationale to one concise sentence.
"""

def _json(raw):
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
    a, b = raw.find("{"), raw.rfind("}")
    if a < 0 or b <= a:
        raise ValueError("No JSON object returned")
    return json.loads(raw[a:b + 1])

def _fallback(country, state):
    c = state["countries"][country]
    worldview = c.get("worldview", {})
    preferred = set(worldview.get("preferred_partners", []))
    competitors = set(worldview.get("competitors", []))

    def strategic_score(name):
        score = state["relations"][country].get(name, 0)
        if name in preferred:
            score += 18
        if name in competitors:
            score -= 18
        return score

    wars = state.get("wars", {})
    alliances = state.get("alliances", {})
    active_wars = [w for w in wars.values() if w.get("status") == "active"
                   and country in w.get("participants", [])]
    enemies = []
    for w in active_wars:
        enemies.extend([n for n in w["participants"] if n != country])
    enemies = list(dict.fromkeys(enemies))

    # Countries under pressure prioritize survival and peace.
    if active_wars:
        if c["stability"] < 30 or c["military"] < 20:
            enemy = enemies[0]
            return {"action": "peace", "target": enemy,
                    "rationale": "Seeking a negotiated end to an increasingly costly war."}
        if c["military"] < 45 and c["resources"] > 25:
            return {"action": "mobilize", "target": None,
                    "rationale": "Improving abstract readiness during an ongoing war."}
        return {"action": "continue_war", "target": enemies[0],
                "rationale": "Maintaining pressure in the ongoing strategic contest."}

    # Weak finances and low production push governments toward economic reform.
    if c.get("budget_balance", 0) < 0 and c.get("debt", 0) > c.get("gdp", 0) * 700:
        return {"action": "invest_economy", "target": None,
                "rationale": "Trying to restore productive capacity and improve the public finances."}
    if c.get("production", 50) < 38 and state["turn"] % 3 == 0:
        return {"action": "invest_economy", "target": None,
                "rationale": "Investing to reverse falling industrial and productive output."}

    # Respond to pending ultimatums.
    pending_from = [u["issuer"] for u in state.get("ultimatums", [])
                    if u.get("target") == country and u.get("status") == "pending"]
    if pending_from:
        issuer = pending_from[0]
        action = "accept_ultimatum" if state["relations"][country].get(issuer, 0) > -45 else "reject_ultimatum"
        return {"action": action, "target": issuer,
                "rationale": "Responding to a pending diplomatic ultimatum."}

    # Build alliances when isolated or threatened.
    my_allies = alliances.get(country, [])
    ranked = sorted(
        (n for n in state["countries"] if n != country and n not in my_allies),
        key=strategic_score,
        reverse=True
    )
    if ranked and len(my_allies) < 2 and state["relations"][country].get(ranked[0], 0) > 18:
        return {"action": "form_alliance", "target": ranked[0],
                "rationale": "Building a coalition to increase diplomatic and strategic influence."}

    # Found and expand diplomatic blocs.
    membership = [b for b in state.get("blocs", {}).values() if country in b.get("members", [])]
    if not membership and state["turn"] % 9 == 0:
        return {"action": "create_bloc", "target": None,
                "rationale": "Creating a diplomatic bloc for long-term cooperation."}
    if membership and state["turn"] % 6 == 0:
        existing = [m for b in state.get("blocs", {}).values() for m in b.get("members", [])]
        invitees = [n for n in ranked if n not in existing]
        if invitees:
            return {"action": "invite_to_bloc", "target": invitees[0],
                    "rationale": "Expanding the country's diplomatic bloc."}

    # Guarantee a friendly, weaker state's independence.
    guaranteed = {(g.get("guarantor"), g.get("protected")) for g in state.get("guarantees", [])}
    if ranked and state["turn"] % 8 == 0:
        candidate = next((n for n in ranked
                          if (country, n) not in guaranteed
                          and state["relations"][country].get(n, 0) > 12
                          and c["military"] >= state["countries"][n]["military"]), None)
        if candidate:
            return {"action": "guarantee_independence", "target": candidate,
                    "rationale": "Offering a security guarantee to a friendly state."}

    # Break a weak alliance if relations collapse.
    bad_allies = [n for n in my_allies if state["relations"][country].get(n, 0) < -15]
    if bad_allies:
        return {"action": "break_alliance", "target": bad_allies[0],
                "rationale": "Leaving an alliance that no longer serves national interests."}

    # Opportunistic abstract war against a rival, with restraint against much stronger foes.
    rivals = sorted(
        (n for n in state["countries"] if n != country
         and n not in my_allies
         and not any(w.get("status") == "active" and country in w.get("participants", [])
                     and n in w.get("participants", []) for w in wars.values())),
        key=strategic_score
    )
    if rivals and state["turn"] >= 3:
        target = rivals[0]
        other = state["countries"][target]
        own_power = c["military"] * .55 + c["tech"] * .25 + c["stability"] * .20
        other_power = other["military"] * .55 + other["tech"] * .25 + other["stability"] * .20
        if (state["relations"][country].get(target, 0) < -20
                and own_power >= other_power * .60
                and c["stability"] > 32):
            return {"action": "declare_war", "target": target,
                    "rationale": "A long-running rivalry has escalated into an abstract strategic conflict."}

    # Diplomatic actions and development are still useful, but not the only strategy.
    if ranked and state["relations"][country].get(ranked[0], 0) < 5:
        return {"action": "diplomacy", "target": ranked[0],
                "rationale": "Improving relations to avoid isolation and create future options."}
    if c["stability"] < 43:
        return {"action": "social_program", "target": None,
                "rationale": "Restoring domestic stability before pursuing external ambitions."}
    if c["tech"] < 72 and state["turn"] % 4 == 0:
        return {"action": "research", "target": None,
                "rationale": "Strengthening long-term national capabilities."}
    if c["military"] < 62 and state["turn"] % 3 == 0:
        return {"action": "mobilize", "target": None,
                "rationale": "Maintaining credible abstract defensive readiness."}
    if ranked and state["turn"] % 4 == 0:
        return {"action": "trade", "target": ranked[0],
                "rationale": "Expanding economic influence through trade."}
    return {"action": "invest_economy", "target": None,
            "rationale": "Strengthening the economic base needed for long-term influence."}

def choose_action(country, state, provider="Fallback", model=None):
    if provider == "Fallback":
        return _fallback(country, state), "Fallback"

    c = state["countries"][country]
    prompt = {
        "country": country,
        "profile": c,
        "worldview": c.get("worldview", {}),
        "economic_state": {k: c.get(k) for k in ("gdp", "budget", "budget_balance", "treasury", "debt", "production", "trade", "resources", "resource_stock", "inflation", "unemployment")},
        "turn": state["turn"],
        "relations": state["relations"][country],
        "alliances": state.get("alliances", {}).get(country, []),        "foreign_influence_on_us": sorted(
            state.get("influence", {}).get(country, {}).items(),
            key=lambda item: item[1], reverse=True
        )[:5],
        "our_influence_abroad": sorted(
            [(target, scores.get(country, 0)) for target, scores in state.get("influence", {}).items() if target != country],
            key=lambda item: item[1], reverse=True
        )[:5],
        "active_wars": [
            {k: w.get(k) for k in ("id", "participants", "progress", "status", "attacker", "defender")}
            for w in state.get("wars", {}).values()
            if w.get("status") == "active" and country in w.get("participants", [])
        ],
        "recent_events": state.get("events", [])[-12:],
        "goal": "Pursue national interests according to the country worldview. Great powers may seek influence, middle powers may balance rivals, and smaller states may prioritise sovereignty, trade and security. Do not assume every country wants conquest.",
        "decision_guidance": "Use worldview priorities, red lines, preferred partners, competitors and current influence levels as meaningful context. Expand soft power through diplomacy, trade, alliances and guarantees when useful. Notice when a rival is gaining influence nearby. Do not automatically attack competitors; prefer diplomacy, trade, alliances, deterrence or sanctions when these better serve national interests."
    }
    try:
        if provider == "Ollama":
            base = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
            chosen = model or os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
            r = requests.post(
                base + "/api/chat",
                json={"model": chosen, "stream": False, "format": "json",
                      "messages": [{"role": "system", "content": SYSTEM_PROMPT},
                                   {"role": "user", "content": json.dumps(prompt)}]},
                timeout=120
            )
            r.raise_for_status()
            raw = r.json()["message"]["content"]
        else:
            base = os.getenv("CLOUD_BASE_URL", "https://api.openai.com/v1").rstrip("/")
            key = os.getenv("CLOUD_API_KEY", "")
            chosen = model or os.getenv("CLOUD_MODEL", "gpt-4.1-mini")
            if not key:
                raise RuntimeError("CLOUD_API_KEY is missing")
            r = requests.post(
                base + "/chat/completions",
                headers={"Authorization": "Bearer " + key},
                json={"model": chosen, "temperature": 0.8,
                      "response_format": {"type": "json_object"},
                      "messages": [{"role": "system", "content": SYSTEM_PROMPT},
                                   {"role": "user", "content": json.dumps(prompt)}]},
                timeout=120
            )
            r.raise_for_status()
            raw = r.json()["choices"][0]["message"]["content"]

        d = _json(raw)
        if d.get("action") not in ACTIONS:
            raise ValueError("Unknown action")
        target = d.get("target")
        if target not in state["countries"] or target == country:
            target = None
        needs_target = d["action"] in {
            "diplomacy", "trade", "sanction", "conflict", "declare_war",
            "form_alliance", "break_alliance", "guarantee_independence",
            "revoke_guarantee", "ultimatum", "accept_ultimatum",
            "reject_ultimatum", "sever_relations", "invite_to_bloc",
            "peace", "continue_war"
        }
        if needs_target and target is None:
            return _fallback(country, state), "Fallback"
        return {
            "action": d["action"],
            "target": target,
            "rationale": str(d.get("rationale", ""))[:240]
        }, provider
    except Exception as e:
        d = _fallback(country, state)
        d["rationale"] = f"Fallback used ({type(e).__name__}); " + d["rationale"]
        return d, "Fallback"
