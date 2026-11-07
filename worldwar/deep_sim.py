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
        priorities = " ".join(country.get("worldview", {}).get("priorities", [])).lower()
        if not profile.get("primary_goal"):
            if any(word in priorities for word in ("technology", "innovation", "research", "digital")):
                profile["primary_goal"] = "innovation"
            elif any(word in priorities for word in ("security", "deterrence", "defence", "defense", "sovereignty", "regime")):
                profile["primary_goal"] = "security"
            elif any(word in priorities for word in ("influence", "leadership", "diplomacy", "regional", "alliances")):
                profile["primary_goal"] = "influence"
            else:
                profile["primary_goal"] = "prosperity"
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



def _negotiation_step(state):
    """Resolve persistent diplomatic proposals instead of treating all diplomacy as instant."""
    turn = state.get("turn", 0)
    proposals = state.setdefault("negotiations", [])
    relations = state.get("relations", {})
    countries = state.get("countries", {})
    memory = state.get("state_memory", {})
    agreements = {
        tuple(sorted(item.get("countries", [])))
        for item in state.get("trade_agreements", [])
        if len(item.get("countries", [])) == 2
    }
    # Resolve proposals that have been pending since an earlier turn.
    for proposal in proposals:
        if proposal.get("status") != "pending":
            continue
        a, b = proposal.get("from"), proposal.get("to")
        if a not in countries or b not in countries:
            proposal["status"] = "cancelled"
            continue
        relation = float(relations.get(b, {}).get(a, 0))
        grievance = float(memory.get(b, {}).get(a, {}).get("grievance", 0))
        trust = float(memory.get(b, {}).get(a, {}).get("trust", 0))
        score = relation + trust * 0.25 - grievance * 0.35
        if score >= 42:
            proposal["status"] = "accepted"
            proposal["resolved_turn"] = turn
            if proposal.get("type") == "trade_agreement":
                pair = tuple(sorted((a, b)))
                if pair not in agreements:
                    state.setdefault("trade_agreements", []).append({"countries": [a, b], "turn": turn, "source": "negotiation"})
                    agreements.add(pair)
                relations[a][b] = _clamp(relations[a][b] + 3, -100, 100)
                relations[b][a] = _clamp(relations[b][a] + 3, -100, 100)
                _event(state, "negotiation", f"{a} and {b} accepted a negotiated trade agreement after diplomatic talks.")
            else:
                relations[a][b] = _clamp(relations[a][b] + 2, -100, 100)
                relations[b][a] = _clamp(relations[b][a] + 2, -100, 100)
                _event(state, "negotiation", f"{a} and {b} completed a diplomatic summit and agreed to maintain dialogue.")
        elif turn >= int(proposal.get("expires", turn + 1)):
            proposal["status"] = "rejected"
            proposal["resolved_turn"] = turn
            _event(state, "negotiation", f"{b} rejected a diplomatic proposal from {a}; relations cooled slightly.")
            relations[a][b] = _clamp(relations[a][b] - 1, -100, 100)
    # Every third turn, governments with a constructive relationship can open talks.
    if turn % 3 == 0 and len([p for p in proposals if p.get("status") == "pending"]) < 5:
        independent = [n for n in countries if state.get("sovereignty", {}).get(n, n) == n]
        candidates = []
        for i, a in enumerate(independent):
            for b in independent[i + 1:]:
                pair = tuple(sorted((a, b)))
                if pair in agreements:
                    continue
                if any(p.get("status") == "pending" and {p.get("from"), p.get("to")} == {a, b} for p in proposals):
                    continue
                if any(w.get("status") == "active" and a in w.get("participants", []) and b in w.get("participants", []) for w in state.get("wars", {}).values()):
                    continue
                score = (float(relations.get(a, {}).get(b, 0)) + float(relations.get(b, {}).get(a, 0))) / 2
                if score >= 48:
                    candidates.append((score + random.random() * 8, a, b))
        candidates.sort(reverse=True)
        for _, a, b in candidates[:2]:
            kind = "trade_agreement"
            proposals.append({
                "id": len(proposals) + 1, "from": a, "to": b,
                "type": kind, "created_turn": turn,
                "expires": turn + 2, "status": "pending"
            })
            _event(state, "negotiation", f"{a} opened diplomatic negotiations with {b} on a trade agreement.")
    state["negotiations"] = proposals[-150:]


def _information_environment_step(state):
    """Model abstract foreign information pressure and domestic resilience."""
    influence = state.get("influence", {})
    resilience = state.setdefault("information_resilience", {})
    politics = state.get("politics", {})
    for name, country in state.get("countries", {}).items():
        record = resilience.setdefault(name, {"resilience": 45.0, "external_pressure": 0.0})
        external = sum(float(value) for actor, value in influence.get(name, {}).items() if actor != name)
        external = min(100.0, external / 8.0)
        record["external_pressure"] = round(external, 1)
        tech = float(country.get("tech", 40))
        stability = float(country.get("stability", 50))
        record["resilience"] = round(_clamp(record.get("resilience", 45) + (tech - 50) * 0.002 + (stability - 50) * 0.001, 5, 95), 1)
        pressure = max(0.0, external - record["resilience"])
        government = politics.get(name, {})
        if pressure > 35 and government:
            government["approval"] = round(_clamp(government.get("approval", 50) - min(0.18, pressure * 0.002), 5, 95), 1)
        record["pressure_gap"] = round(pressure, 1)


def _covert_pressure_step(state):
    """Resolve occasional abstract influence contests; no operational detail is modelled."""
    turn = state.get("turn", 0)
    if turn % 4 != 0:
        return
    countries = state.get("countries", {})
    influence = state.get("influence", {})
    relations = state.get("relations", {})
    resilience = state.get("information_resilience", {})
    operations = state.setdefault("covert_operations", [])
    candidates = []
    for target, actors in influence.items():
        if target not in countries:
            continue
        for actor, score in actors.items():
            if actor not in countries or actor == target or float(score) < 32:
                continue
            relation = float(relations.get(actor, {}).get(target, 0))
            if relation < -12:
                candidates.append((float(score) + abs(relation) * 0.25, actor, target))
    candidates.sort(reverse=True)
    for _, actor, target in candidates[:2]:
        target_resilience = float(resilience.get(target, {}).get("resilience", 45))
        tech_edge = float(countries[actor].get("tech", 40)) - float(countries[target].get("tech", 40))
        chance = _clamp(38 + float(influence[target].get(actor, 0)) * 0.35 + tech_edge * 0.18 - target_resilience * 0.28, 5, 75)
        success = random.random() * 100 < chance
        entry = {"turn": turn, "actor": actor, "target": target, "success": success, "chance": round(chance, 1)}
        operations.append(entry)
        if success:
            countries[target]["stability"] = _clamp(countries[target].get("stability", 50) - 0.7, 0, 100)
            relations[target][actor] = _clamp(relations[target][actor] - 2, -100, 100)
            _event(state, "covert_influence", f"An abstract foreign influence operation by {actor} unsettled public confidence in {target}.",
                   "The simulation resolves covert pressure probabilistically using influence, technology and resilience.")
        else:
            relations[target][actor] = _clamp(relations[target][actor] - 0.5, -100, 100)
            _event(state, "covert_influence", f"{target} detected and contained an attempted foreign influence operation attributed to {actor}.")
    state["covert_operations"] = operations[-120:]


def _self_determination_step(state):
    """Occupied territories can regain sovereignty after sustained legitimacy collapse."""
    ownership = state.setdefault("sovereignty", {})
    countries = state.get("countries", {})
    movements = state.setdefault("autonomy_movements", {})
    for territory, controller in list(ownership.items()):
        if territory == controller or territory not in countries or controller not in countries:
            continue
        stability = float(countries[territory].get("stability", 50))
        record = movements.setdefault(territory, {"pressure": 0.0, "since": state.get("turn", 0)})
        if stability < 28:
            record["pressure"] = _clamp(record.get("pressure", 0) + (28 - stability) * 0.12, 0, 100)
        else:
            record["pressure"] = _clamp(record.get("pressure", 0) - 1.5, 0, 100)
        if record["pressure"] >= 35 and state.get("turn", 0) - int(record.get("last_attempt", -20)) >= 6:
            record["last_attempt"] = state.get("turn", 0)
            if random.random() < min(0.8, 0.25 + record["pressure"] / 150):
                ownership[territory] = territory
                countries[territory]["stability"] = _clamp(stability + 5, 0, 100)
                relations = state.get("relations", {})
                relations.setdefault(territory, {})[controller] = _clamp(relations.get(territory, {}).get(controller, 0) - 12, -100, 100)
                relations.setdefault(controller, {})[territory] = _clamp(relations.get(controller, {}).get(territory, 0) - 8, -100, 100)
                _event(state, "independence", f"{territory} restored its sovereignty after a prolonged legitimacy crisis under {controller}'s control.",
                       "The abstract self-determination system responds to sustained low stability in an occupied territory.")
                movements.pop(territory, None)
    state["autonomy_movements"] = movements

def advance_deep_systems(state):
    initialize_deep_systems(state)
    _update_state_memory(state)
    _review_strategies(state)
    _supply_chain_step(state)
    _demographic_step(state)
    _finance_step(state)
    _research_step(state)
    _corporate_step(state)
    _negotiation_step(state)
    _information_environment_step(state)
    _covert_pressure_step(state)
    _self_determination_step(state)
    _global_crisis_step(state)
    return state
