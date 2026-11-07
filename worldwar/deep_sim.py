"""Deep simulation layer: strategic plans, state memory, supply chains,
demographics, finance, technology portfolios, corporations and global shocks.

All values are fictional game abstractions. This module is deliberately
self-contained so old saves can be upgraded lazily and safely.
"""
import random


def _clamp(value, low=0.0, high=100.0):
    return max(low, min(high, float(value)))


def _event(state, kind, text, rationale=""):
    state.setdefault("events", []).append({
        "turn": state.get("turn", 0), "kind": kind,
        "text": text, "rationale": rationale
    })
    state["events"] = state["events"][-600:]


def initialize_deep_systems(state):
    countries = state.get("countries", {})
    plans = state.setdefault("strategic_plans", {})
    memory = state.setdefault("state_memory", {})
    demographics = state.setdefault("demographics", {})
    finance = state.setdefault("financial_system", {})
    research = state.setdefault("research_programs", {})
    corporations = state.setdefault("corporate_presence", {})
    for name, country in countries.items():
        profile = state.setdefault("ai_profiles", {}).setdefault(name, {})
        goal = profile.get("primary_goal", "prosperity")
        plans.setdefault(name, {
            "goal": goal, "horizon": 12, "started": state.get("turn", 0),
            "progress": 0.0, "milestones": [], "last_review": state.get("turn", 0)
        })
        memory.setdefault(name, {})
        pop = max(0.001, float(country.get("population", 1)))
        demographics.setdefault(name, {
            "working_age": 63.0, "urbanization": 55.0,
            "net_migration": 0.0, "dependency_ratio": 0.58,
            "population_base": pop
        })
        finance.setdefault(name, {
            "credit_rating": 70.0, "risk": 20.0,
            "default_cooldown": 0, "last_debt_ratio": 0.0
        })
        research.setdefault(name, {
            "points": 0.0, "branches": {
                "AI and computing": 0.0, "Energy": 0.0,
                "Medicine": 0.0, "Advanced industry": 0.0
            }, "unlocked": []
        })
        corporations.setdefault(name, {
            "capital": max(0.1, float(country.get("gdp", 0.01)) * 8),
            "jobs_index": 50.0, "foreign_investment": 0.0
        })
    state.setdefault("deep_systems", {}).setdefault("last_event_index", 0)
    return state


def _update_state_memory(state):
    events = state.get("events", [])
    deep = state.setdefault("deep_systems", {})
    last_turn = int(deep.get("last_memory_turn", state.get("turn", 0) - 1))
    memory = state.setdefault("state_memory", {})
    countries = state.get("countries", {})
    for event in events:
        if int(event.get("turn", 0)) <= last_turn:
            continue
        text = str(event.get("text", ""))
        involved = [name for name in countries if name in text]
        if len(involved) < 2:
            continue
        kind = str(event.get("kind", "world")).lower()
        for i, first in enumerate(involved):
            for second in involved[i + 1:]:
                record = memory.setdefault(first, {}).setdefault(second, {
                    "trust": 0.0, "grievance": 0.0, "cooperation": 0.0,
                    "last_event": "", "last_turn": 0, "events": 0
                })
                if any(word in kind for word in ("betray", "war", "sanction", "ultimatum")):
                    record["trust"] = _clamp(record["trust"] - 5, -100, 100)
                    record["grievance"] = _clamp(record["grievance"] + 7, 0, 100)
                elif any(word in kind for word in ("alliance", "trade", "diplomacy", "guarantee", "peace")):
                    record["trust"] = _clamp(record["trust"] + 3, -100, 100)
                    record["cooperation"] = _clamp(record["cooperation"] + 4, 0, 100)
                record["last_event"] = text[:180]
                record["last_turn"] = event.get("turn", state.get("turn", 0))
                record["events"] += 1
                reverse = memory.setdefault(second, {}).setdefault(first, {
                    "trust": 0.0, "grievance": 0.0, "cooperation": 0.0,
                    "last_event": "", "last_turn": 0, "events": 0
                })
                reverse.update(record)
    deep["last_memory_turn"] = state.get("turn", 0)
    # Old saves and long simulations should not accumulate unbounded memory.
    for name in list(memory):
        partners = memory[name]
        if len(partners) > 80:
            keep = sorted(partners.items(), key=lambda item: item[1].get("last_turn", 0), reverse=True)[:80]
            memory[name] = dict(keep)


def _review_strategies(state):
    plans = state.setdefault("strategic_plans", {})
    for name, country in state.get("countries", {}).items():
        plan = plans.setdefault(name, {"goal": "prosperity", "horizon": 12, "progress": 0, "milestones": []})
        if state.get("turn", 0) - int(plan.get("last_review", 0)) < 5:
            continue
        stability = float(country.get("stability", 50))
        debt = float(country.get("debt", 0))
        gdp = max(0.001, float(country.get("gdp", 0.01)))
        tech = float(country.get("tech", 40))
        military = float(country.get("military", 40))
        if stability < 32:
            goal = "security"
        elif debt / (gdp * 1000) > 1.25:
            goal = "prosperity"
        elif tech < 55 and country.get("production", 0) > 35:
            goal = "innovation"
        elif military > 75 and stability > 55:
            goal = "influence"
        else:
            goal = state.get("ai_profiles", {}).get(name, {}).get("primary_goal", "prosperity")
        if goal != plan.get("goal"):
            old = plan.get("goal", "prosperity")
            plan["goal"] = goal
            plan["progress"] = 0.0
            plan["started"] = state.get("turn", 0)
            _event(state, "strategy", f"{name} revised its long-term national strategy from {old} to {goal}.",
                   "The government reassessed domestic conditions, fiscal pressure and national capabilities.")
        plan["last_review"] = state.get("turn", 0)
        plan["progress"] = round(_clamp(plan.get("progress", 0) + 2.5, 0, 100), 1)
        if plan["progress"] >= 100:
            plan["milestones"] = (plan.get("milestones", []) + [state.get("turn", 0)])[-12:]
            plan["progress"] = 0.0
            _event(state, "strategy", f"{name} completed a strategic development cycle focused on {plan['goal']}.")


def _supply_chain_step(state):
    countries = state.get("countries", {})
    agreements = [x.get("countries", []) for x in state.get("trade_agreements", [])]
    sanctions = {(x.get("issuer"), x.get("target")) for x in state.get("sanctions", [])}
    supply = state.setdefault("supply_chains", {})
    for name, country in countries.items():
        partners = set()
        for pair in agreements:
            if len(pair) == 2 and name in pair:
                partners.update(n for n in pair if n != name)
        for org in state.get("organizations", {}).values():
            if org.get("type") in ("economic", "energy") and name in org.get("members", []):
                partners.update(n for n in org.get("members", []) if n != name)
        stock = float(country.get("resource_stock", 50))
        resource_endowment = float(country.get("resources", 50))
        import_need = _clamp(58 - resource_endowment + max(0, 45 - stock) * 0.7, 0, 100)
        partner_coverage = min(45, len(partners) * 7.5)
        exposure = _clamp(import_need - partner_coverage, 0, 100)
        blocked = sum(1 for issuer, target in sanctions if target == name or issuer in partners)
        risk = _clamp(exposure * 0.58 + max(0, 30 - stock) * 0.7 + blocked * 5, 0, 100)
        supply[name] = {
            "import_dependency": round(import_need, 1),
            "partner_coverage": round(partner_coverage, 1),
            "disruption_risk": round(risk, 1),
            "partners": sorted(partners)
        }
        if risk > 72:
            country["production"] = round(_clamp(country.get("production", 50) - 0.22, 1, 100), 2)
            country["inflation"] = round(min(35, country.get("inflation", 3) + 0.12), 2)
        elif risk < 28:
            country["production"] = round(_clamp(country.get("production", 50) + 0.08, 1, 100), 2)


def _demographic_step(state):
    countries = state.get("countries", {})
    demographics = state.setdefault("demographics", {})
    ownership = state.get("sovereignty", {})
    independent = {n for n in countries if ownership.get(n, n) == n}
    for name, country in countries.items():
        record = demographics.setdefault(name, {
            "working_age": 63.0, "urbanization": 55.0, "net_migration": 0.0,
            "dependency_ratio": 0.58, "population_base": country.get("population", 1)
        })
        stability = float(country.get("stability", 50))
        unemployment = float(country.get("unemployment", 7))
        growth = float(country.get("gdp_growth", 0))
        urban = float(record.get("urbanization", 55))
        working = float(record.get("working_age", 63))
        migration = (stability - 50) * 0.012 + (8 - unemployment) * 0.018 + growth * 0.12
        migration = max(-1.5, min(1.5, migration))
        if name not in independent:
            migration = min(0, migration)
        record["net_migration"] = round(migration, 3)
        record["urbanization"] = round(_clamp(urban + max(0.02, country.get("tech", 40) / 3000), 10, 98), 2)
        record["working_age"] = round(_clamp(working + (0.015 if country.get("tech", 40) > 65 else -0.025), 48, 72), 2)
        record["dependency_ratio"] = round(_clamp(1.05 - record["working_age"] / 100, 0.25, 0.8), 3)
        if abs(migration) > 0.25:
            country["population"] = round(max(0.001, country.get("population", 1) * (1 + migration / 100)), 3)


def _finance_step(state):
    countries = state.get("countries", {})
    records = state.setdefault("financial_system", {})
    for name, country in countries.items():
        record = records.setdefault(name, {"credit_rating": 70, "risk": 20, "default_cooldown": 0})
        gdp_bn = max(1.0, float(country.get("gdp", 0.01)) * 1000)
        ratio = float(country.get("debt", 0)) / gdp_bn
        treasury_months = float(country.get("treasury", 0)) / max(1.0, gdp_bn / 12)
        risk = _clamp((ratio - 0.55) * 38 + max(0, 3 - treasury_months) * 7 + max(0, country.get("inflation", 3) - 8) * 1.1, 0, 100)
        rating = _clamp(96 - risk * 0.72 - max(0, 45 - country.get("stability", 50)) * 0.35, 5, 99)
        record["risk"] = round(risk, 1)
        record["credit_rating"] = round(rating, 1)
        record["last_debt_ratio"] = round(ratio, 3)
        if record.get("default_cooldown", 0) > 0:
            record["default_cooldown"] -= 1
        if ratio > 1.65 and treasury_months < 1.2 and record.get("default_cooldown", 0) == 0:
            country["debt"] = round(country.get("debt", 0) * 0.82, 2)
            country["gdp"] = round(max(0.00001, country.get("gdp", 0.01) * 0.94), 6)
            country["stability"] = _clamp(country.get("stability", 50) - 9, 0, 100)
            country["inflation"] = round(min(35, country.get("inflation", 3) + 5), 2)
            record["default_cooldown"] = 8
            _event(state, "default", f"Sovereign debt crisis in {name}: the government restructured its debt after losing market confidence.",
                   "Debt exceeded sustainable levels while available treasury reserves fell critically low.")


def _research_step(state):
    countries = state.get("countries", {})
    programs = state.setdefault("research_programs", {})
    for name, country in countries.items():
        program = programs.setdefault(name, {"points": 0.0, "branches": {}, "unlocked": []})
        branches = program.setdefault("branches", {
            "AI and computing": 0.0, "Energy": 0.0, "Medicine": 0.0, "Advanced industry": 0.0
        })
        budget = max(0.0, float(country.get("gdp", 0.01)) * 1000)
        base = 0.12 + float(country.get("tech", 40)) / 180 + float(country.get("production", 45)) / 250
        if state.get("ai_profiles", {}).get(name, {}).get("primary_goal") == "innovation":
            base *= 1.2
        program["points"] = round(program.get("points", 0) + base, 2)
        weights = {
            "AI and computing": max(1, country.get("tech", 40)),
            "Energy": max(1, country.get("resources", 50)),
            "Medicine": max(1, country.get("population", 1) / 10),
            "Advanced industry": max(1, country.get("production", 45))
        }
        total = sum(weights.values())
        for branch, weight in weights.items():
            branches[branch] = round(branches.get(branch, 0) + base * weight / total, 2)
        thresholds = [("AI and computing", 18), ("Energy", 20), ("Medicine", 22), ("Advanced industry", 24)]
        for branch, threshold in thresholds:
            milestone = f"{branch} breakthrough"
            if branches.get(branch, 0) >= threshold and milestone not in program.setdefault("unlocked", []):
                program["unlocked"].append(milestone)
                country["tech"] = _clamp(country.get("tech", 40) + 1.2)
                country["production"] = round(_clamp(country.get("production", 45) + 0.8), 2)
                _event(state, "research", f"{name} achieved a {branch.lower()} breakthrough. Research capacity and productivity improved.")


def _corporate_step(state):
    countries = state.get("countries", {})
    presence = state.setdefault("corporate_presence", {})
    trade_pairs = [x.get("countries", []) for x in state.get("trade_agreements", [])]
    for name, country in countries.items():
        record = presence.setdefault(name, {"capital": max(0.1, country.get("gdp", 0.01) * 8), "jobs_index": 50, "foreign_investment": 0})
        partners = sum(1 for pair in trade_pairs if len(pair) == 2 and name in pair)
        openness = max(0.1, country.get("tech", 40) / 100) * max(0.1, country.get("stability", 50) / 100)
        inflow = max(0.0, country.get("gdp", 0.01) * (0.0008 + partners * 0.0003) * openness)
        record["foreign_investment"] = round(inflow * 1000, 2)
        record["capital"] = round(max(0.1, record.get("capital", 0.1) * 0.995 + inflow * 1000), 2)
        record["jobs_index"] = round(_clamp(record.get("jobs_index", 50) + (openness - 0.5) * 0.18 - country.get("unemployment", 7) * 0.004), 2)
        country["production"] = round(_clamp(country.get("production", 45) + min(0.08, inflow * 0.02), 1, 100), 2)


def _global_crisis_step(state):
    deep = state.setdefault("deep_systems", {})
    last = int(deep.get("last_global_crisis", -20))
    if state.get("turn", 0) - last < 5:
        return
    countries = state.get("countries", {})
    if not countries or random.random() > 0.045:
        return
    kind = random.choice(["financial", "climate", "health", "food", "energy"])
    exposed = sorted(countries, key=lambda n: (
        countries[n].get("stability", 50) + countries[n].get("resources", 50)
        + countries[n].get("tech", 40)
    ))[:max(5, min(18, len(countries) // 8))]
    for name in exposed:
        country = countries[name]
        if kind == "financial":
            country["gdp"] = round(max(0.00001, country.get("gdp", 0.01) * 0.985), 6)
            country["unemployment"] = round(min(45, country.get("unemployment", 7) + 0.8), 2)
        elif kind == "climate":
            country["resources"] = _clamp(country.get("resources", 50) - 2.5, 0, 100)
            country["stability"] = _clamp(country.get("stability", 50) - 0.8, 0, 100)
        elif kind == "health":
            country["population"] = round(max(0.001, country.get("population", 1) * 0.998), 3)
            country["stability"] = _clamp(country.get("stability", 50) - 1.2, 0, 100)
        elif kind == "food":
            country["inflation"] = round(min(35, country.get("inflation", 3) + 1.2), 2)
            country["resources"] = _clamp(country.get("resources", 50) - 1.8, 0, 100)
        else:
            country["inflation"] = round(min(35, country.get("inflation", 3) + 1.5), 2)
            country["production"] = round(_clamp(country.get("production", 45) - 1.2, 1, 100), 2)
    deep["last_global_crisis"] = state.get("turn", 0)
    label = {"financial": "global financial", "climate": "climate", "health": "public-health", "food": "food-security", "energy": "energy"}[kind]
    _event(state, "global_crisis", f"A global {label} crisis spread across vulnerable economies, disrupting growth and domestic stability.",
           "Countries with weaker resilience, resources or technology experienced the largest simulated effects.")


def advance_deep_systems(state):
    initialize_deep_systems(state)
    _update_state_memory(state)
    _review_strategies(state)
    _supply_chain_step(state)
    _demographic_step(state)
    _finance_step(state)
    _research_step(state)
    _corporate_step(state)
    _global_crisis_step(state)
    return state
