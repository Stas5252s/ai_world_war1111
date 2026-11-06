import copy
import random
from .data import COUNTRIES
from .agents import choose_action

def new_world(seed=7):
    random.seed(seed)
    countries = copy.deepcopy(COUNTRIES)
    names = list(countries)
    relations = {
        a: {b: (0 if a == b else random.randint(-20, 25)) for b in names}
        for a in names
    }
    # Seed a few geopolitical rivalries so the world does not begin as a room
    # full of perfectly polite economists.
    rivalries = [
        ("China", "India"), ("United States", "China"),
        ("Russia", "United States"), ("Iran", "Saudi Arabia")
    ]
    for a, b in rivalries:
        if a in relations and b in relations:
            relations[a][b] = relations[b][a] = -45
    return {
        "turn": 0, "countries": countries, "relations": relations,
        "alliances": {n: [] for n in names},
        "wars": {}, "next_war_id": 1,
        "guarantees": [], "trade_agreements": [], "blocs": {},
        "next_bloc_id": 1, "ultimatums": [],
        "sovereignty": {n: n for n in names},
        "events": [{"turn": 0, "kind": "world",
                    "text": "The simulation begins. Every government seeks global influence."}],
        "history": []
    }

def _ensure_sovereignty(s):
    """Keep old saved sessions compatible with the territorial-control system."""
    ownership = s.setdefault("sovereignty", {})
    for name in s["countries"]:
        ownership.setdefault(name, name)
    return ownership

def _independent_countries(s):
    ownership = _ensure_sovereignty(s)
    return [name for name in s["countries"] if ownership.get(name, name) == name]

def _event(s, kind, text, rationale=""):
    s["events"].append({
        "turn": s["turn"], "kind": kind, "text": text,
        "rationale": rationale
    })
    s["events"] = s["events"][-400:]

def clamp(v, lo=0, hi=100):
    return max(lo, min(hi, v))

def _allied(s, a, b):
    return b in s.get("alliances", {}).get(a, [])

def _active_war_between(s, a, b):
    return any(
        w.get("status") == "active"
        and a in w.get("participants", [])
        and b in w.get("participants", [])
        for w in s.get("wars", {}).values()
    )

def _form_alliance(s, a, b):
    independent = _independent_countries(s)
    if b not in independent or a not in independent or a == b:
        return
    if _active_war_between(s, a, b):
        _event(s, "diplomacy", f"{a} could not form an alliance with {b} while they are at war.")
        return
    s.setdefault("alliances", {}).setdefault(a, [])
    s.setdefault("alliances", {}).setdefault(b, [])
    if b not in s["alliances"][a]:
        s["alliances"][a].append(b)
    if a not in s["alliances"][b]:
        s["alliances"][b].append(a)
    s["relations"][a][b] = clamp(s["relations"][a][b] + 18, -100, 100)
    s["relations"][b][a] = clamp(s["relations"][b][a] + 18, -100, 100)
    _event(s, "alliance", f"{a} and {b} formed a mutual alliance.")

def _break_alliance(s, a, b):
    if b in s.get("alliances", {}).get(a, []):
        s["alliances"][a].remove(b)
        s["alliances"][b].remove(a)
        s["relations"][a][b] = clamp(s["relations"][a][b] - 20, -100, 100)
        s["relations"][b][a] = clamp(s["relations"][b][a] - 10, -100, 100)
        _event(s, "betrayal", f"{a} withdrew from its alliance with {b}.")


def _create_bloc(s, founder):
    for bloc in s.setdefault("blocs", {}).values():
        if founder in bloc.get("members", []):
            _event(s, "diplomacy", f"{founder} already belongs to {bloc['name']}.")
            return
    bid = str(s.get("next_bloc_id", 1))
    s["next_bloc_id"] = int(bid) + 1
    name = f"International Bloc {bid}"
    s["blocs"][bid] = {"id": bid, "name": name, "leader": founder, "members": [founder]}
    _event(s, "diplomacy", f"{founder} founded {name}.")

def _invite_to_bloc(s, founder, target):
    blocs = s.setdefault("blocs", {})
    bloc = next((b for b in blocs.values() if b.get("leader") == founder), None)
    if bloc is None:
        _create_bloc(s, founder)
        bloc = next((b for b in blocs.values() if b.get("leader") == founder), None)
    if any(target in b.get("members", []) for b in blocs.values()):
        _event(s, "diplomacy", f"{target} already belongs to a bloc.")
        return
    bloc["members"].append(target)
    s["relations"][founder][target] = clamp(s["relations"][founder][target] + 10, -100, 100)
    s["relations"][target][founder] = clamp(s["relations"][target][founder] + 10, -100, 100)
    _event(s, "diplomacy", f"{target} joined {bloc['name']} led by {founder}.")

def _sever_relations(s, a, b):
    s["relations"][a][b] = -100
    s["relations"][b][a] = -100
    _break_alliance(s, a, b)
    s["trade_agreements"] = [x for x in s.get("trade_agreements", []) if set(x.get("countries", [])) != {a, b}]
    s["guarantees"] = [x for x in s.get("guarantees", []) if not ((x.get("guarantor") == a and x.get("protected") == b) or (x.get("guarantor") == b and x.get("protected") == a))]
    _event(s, "diplomacy", f"{a} severed diplomatic relations with {b}.")

def _start_war(s, attacker, defender):
    independent = _independent_countries(s)
    if defender not in independent or attacker not in independent or attacker == defender:
        return
    if _active_war_between(s, attacker, defender):
        return
    if _allied(s, attacker, defender):
        _break_alliance(s, attacker, defender)
        _event(s, "betrayal", f"{attacker} broke its alliance with {defender} before declaring war.")
    wid = str(s.get("next_war_id", 1))
    s["next_war_id"] = int(wid) + 1
    s.setdefault("wars", {})[wid] = {
        "id": wid, "attacker": attacker, "defender": defender,
        "side_a": [attacker], "side_b": [defender],
        "participants": [attacker, defender],
        "progress": 50.0, "status": "active", "started": s["turn"],
        "score": 0.0, "last_update": s["turn"]
    }
    s["relations"][attacker][defender] = clamp(s["relations"][attacker][defender] - 35, -100, 100)
    s["relations"][defender][attacker] = clamp(s["relations"][defender][attacker] - 35, -100, 100)
    _event(s, "war", f"War #{wid} began: {attacker} vs {defender}.")


    for guarantee in s.get("guarantees", []):
        if guarantee.get("protected") == defender:
            guarantor = guarantee.get("guarantor")
            if guarantor in independent and guarantor not in s["wars"][wid]["participants"] and not _active_war_between(s, guarantor, attacker):
                s["wars"][wid]["side_b"].append(guarantor)
                s["wars"][wid]["participants"].append(guarantor)
                _event(s, "diplomacy", f"{guarantor} honored its guarantee to {defender} and joined war #{wid}.")

    # Mutual-defense allies join automatically, unless already fighting on the other side.
    for ally in list(s.get("alliances", {}).get(defender, [])):
        if ally not in (attacker, defender) and not _active_war_between(s, ally, attacker):
            s["wars"][wid]["side_b"].append(ally)
            s["wars"][wid]["participants"].append(ally)
            _event(s, "war", f"{ally} joined {defender}'s side in war #{wid}.")
    for ally in list(s.get("alliances", {}).get(attacker, [])):
        if ally not in (attacker, defender) and not _active_war_between(s, ally, defender):
            s["wars"][wid]["side_a"].append(ally)
            s["wars"][wid]["participants"].append(ally)
            _event(s, "war", f"{ally} joined {attacker}'s side in war #{wid}.")

def _finish_war(s, w, winner, reason, annex=False):
    w["status"] = "ended"
    w["winner"] = winner
    w["ended"] = s["turn"]
    loser_side = w["side_b"] if winner == "side_a" else w["side_a"]
    winner_side = w["side_a"] if winner == "side_a" else w["side_b"]
    ownership = _ensure_sovereignty(s)
    for n in winner_side:
        s["countries"][n]["stability"] = clamp(s["countries"][n]["stability"] + 2)
        s["countries"][n]["gdp"] = round(s["countries"][n]["gdp"] * 1.01, 3)
    for n in loser_side:
        s["countries"][n]["stability"] = clamp(s["countries"][n]["stability"] - 4)
        s["countries"][n]["gdp"] = round(max(.05, s["countries"][n]["gdp"] * .97), 3)
    captured = []
    if annex and winner_side:
        annexer = w.get("attacker") if w.get("attacker") in winner_side else winner_side[0]
        for defeated in loser_side:
            if defeated in s["countries"] and ownership.get(defeated, defeated) == defeated:
                ownership[defeated] = annexer
                captured.append(defeated)
                for territory, controller in list(ownership.items()):
                    if controller == defeated:
                        ownership[territory] = annexer
                _event(s, "territory", f"{annexer} annexed {defeated}. Its territory is now under {annexer}'s control.")
                for ally in list(s.get("alliances", {}).get(defeated, [])):
                    if defeated in s.get("alliances", {}).get(ally, []):
                        s["alliances"][ally].remove(defeated)
                s.get("alliances", {}).pop(defeated, None)
        w["annexed_territories"] = captured
        w["annexing_country"] = annexer if captured else None
    names = ", ".join(winner_side)
    result = f" Territories annexed: {', '.join(captured)}." if captured else ""
    _event(s, "peace", f"War #{w['id']} ended. Winning side: {names}. {reason}{result}")

def _progress_wars(s):
    for w in list(s.get("wars", {}).values()):
        if w.get("status") != "active":
            continue
        def power(side):
            total = 0
            for n in side:
                c = s["countries"][n]
                total += c["military"] * .55 + c["tech"] * .25 + c["stability"] * .20
            return max(1, total)
        a, b = power(w["side_a"]), power(w["side_b"])
        swing = (a - b) / max(a + b, 1) * 18 + random.uniform(-5, 5)
        w["score"] = clamp(w.get("score", 0) + swing, -100, 100)
        w["progress"] = round(50 + w["score"] / 2, 1)
        w["last_update"] = s["turn"]

        # A sustained advantage moves the fictional front line during the war.
        # Ownership can change in either direction as the balance of the conflict shifts.
        ownership = _ensure_sovereignty(s)
        last_shift = int(w.get("last_territory_change", w.get("started", 0)))
        if abs(w["score"]) >= 18 and s["turn"] - last_shift >= 2:
            winning_side = w["side_a"] if w["score"] > 0 else w["side_b"]
            losing_side = w["side_b"] if w["score"] > 0 else w["side_a"]
            enemy_territories = [
                territory for territory, controller in ownership.items()
                if controller in losing_side
            ]
            if enemy_territories and winning_side:
                territory = random.choice(enemy_territories)
                controller = max(
                    winning_side,
                    key=lambda name: s["countries"][name]["military"]
                )
                previous_controller = ownership[territory]
                ownership[territory] = controller
                w["last_territory_change"] = s["turn"]
                change = {
                    "turn": s["turn"], "territory": territory,
                    "from": previous_controller, "to": controller
                }
                w.setdefault("territory_changes", []).append(change)
                w["territory_changes"] = w["territory_changes"][-30:]
                _event(
                    s, "territory",
                    f"{territory} changed control: {controller} captured it from {previous_controller} as the front line shifted."
                )

        for n in w["participants"]:
            c = s["countries"][n]
            c["military"] = clamp(c["military"] - random.uniform(.2, 1.0))
            c["stability"] = clamp(c["stability"] - random.uniform(.1, .7))
            c["gdp"] = round(max(.05, c["gdp"] * random.uniform(.992, .998)), 3)
        def side_condition(side):
            if not side:
                return 0
            return sum((s["countries"][n]["stability"] * .45 +
                        s["countries"][n]["military"] * .55) for n in side) / len(side)
        a_condition, b_condition = side_condition(w["side_a"]), side_condition(w["side_b"])
        if a_condition < 25 and b_condition > a_condition * 1.35:
            _finish_war(s, w, "side_b", "The opposing side capitulated after its game stability and readiness collapsed.", annex=True)
        elif b_condition < 25 and a_condition > b_condition * 1.35:
            _finish_war(s, w, "side_a", "The opposing side capitulated after its game stability and readiness collapsed.", annex=True)
        elif w["progress"] >= 100:
            _finish_war(s, w, "side_a", "The strategic contest reached a decisive outcome.", annex=True)
        elif w["progress"] <= 0:
            _finish_war(s, w, "side_b", "The strategic contest reached a decisive outcome.", annex=True)
        elif s["turn"] - w["started"] >= 12:
            winner = "side_a" if w["score"] >= 0 else "side_b"
            _finish_war(s, w, winner, "The parties accepted an armistice after a prolonged conflict.")

def apply_action(s, country, action, target=None, rationale=""):
    cs, rel = s["countries"], s["relations"]
    independent = _independent_countries(s)
    if country not in independent:
        _event(s, "politics", f"{country} cannot issue independent decisions because its territory is controlled by {s['sovereignty'].get(country, country)}.")
        return
    c = cs[country]
    valid = target in independent and target != country

    if action == "invest_economy":
        c["gdp"] = round(c["gdp"] * 1.012 + .015, 3)
        c["stability"] = clamp(c["stability"] + .3)
        msg, kind = f"{country} invested in economic development.", "economy"
    elif action == "research":
        c["tech"] = clamp(c["tech"] + 2)
        c["gdp"] = round(c["gdp"] * 1.003, 3)
        msg, kind = f"{country} funded a research programme.", "technology"
    elif action == "social_program":
        c["stability"] = clamp(c["stability"] + 4)
        c["gdp"] = round(max(.05, c["gdp"] * .997), 3)
        msg, kind = f"{country} launched a public support programme.", "politics"
    elif action == "mobilize":
        c["military"] = clamp(c["military"] + 5)
        c["gdp"] = round(max(.05, c["gdp"] * .997), 3)
        msg, kind = f"{country} increased abstract readiness.", "military"

    elif action == "create_bloc":
        _create_bloc(s, country)
        return
    elif action == "invite_to_bloc" and valid:
        _invite_to_bloc(s, country, target)
        return
    elif action == "guarantee_independence" and valid:
        if not any(x.get("guarantor") == country and x.get("protected") == target for x in s.setdefault("guarantees", [])):
            s["guarantees"].append({"guarantor": country, "protected": target, "since": s["turn"]})
            _event(s, "diplomacy", f"{country} guaranteed the independence of {target}.")
        return
    elif action == "revoke_guarantee" and valid:
        s["guarantees"] = [x for x in s.setdefault("guarantees", []) if not (x.get("guarantor") == country and x.get("protected") == target)]
        _event(s, "diplomacy", f"{country} revoked its guarantee to {target}.")
        return
    elif action == "ultimatum" and valid:
        s.setdefault("ultimatums", []).append({"issuer": country, "target": target, "issued": s["turn"], "expires": s["turn"] + 2, "status": "pending"})
        rel[country][target] = clamp(rel[country][target] - 12, -100, 100)
        _event(s, "diplomacy", f"{country} issued an ultimatum to {target}.")
        return
    elif action in ("accept_ultimatum", "reject_ultimatum") and valid:
        pending = next((u for u in reversed(s.setdefault("ultimatums", [])) if u.get("issuer") == target and u.get("target") == country and u.get("status") == "pending"), None)
        if pending:
            pending["status"] = "accepted" if action == "accept_ultimatum" else "rejected"
            delta = 12 if action == "accept_ultimatum" else -18
            rel[country][target] = clamp(rel[country][target] + delta, -100, 100)
            _event(s, "diplomacy", f"{country} {pending['status']} the ultimatum from {target}.")
        return
    elif action == "sever_relations" and valid:
        _sever_relations(s, country, target)
        return
    elif action in ("diplomacy", "trade", "sanction", "deescalate") and valid:
        if action == "diplomacy":
            rel[country][target] = clamp(rel[country][target] + 12, -100, 100)
            rel[target][country] = clamp(rel[target][country] + 7, -100, 100)
            msg, kind = f"{country} opened diplomatic talks with {target}.", "diplomacy"
        elif action == "trade":
            rel[country][target] = clamp(rel[country][target] + 8, -100, 100)
            rel[target][country] = clamp(rel[target][country] + 8, -100, 100)
            pair = sorted([country, target])
            if not any(sorted(x.get("countries", [])) == pair for x in s.setdefault("trade_agreements", [])):
                s["trade_agreements"].append({"countries": pair, "signed": s["turn"]})
            c["gdp"] = round(c["gdp"] * 1.008, 3)
            cs[target]["gdp"] = round(cs[target]["gdp"] * 1.006, 3)
            msg, kind = f"{country} and {target} signed a continuing trade agreement.", "economy"
        elif action == "sanction":
            rel[country][target] = clamp(rel[country][target] - 12, -100, 100)
            cs[target]["gdp"] = round(max(.05, cs[target]["gdp"] * .992), 3)
            c["gdp"] = round(max(.05, c["gdp"] * .998), 3)
            msg, kind = f"{country} imposed economic restrictions on {target}.", "economy"
        else:
            rel[country][target] = clamp(rel[country][target] + 18, -100, 100)
            rel[target][country] = clamp(rel[target][country] + 12, -100, 100)
            msg, kind = f"{country} proposed de-escalation to {target}.", "diplomacy"
    elif action == "form_alliance" and valid:
        _form_alliance(s, country, target)
        return
    elif action == "break_alliance" and valid:
        _break_alliance(s, country, target)
        return
    elif action in ("declare_war", "conflict") and valid:
        _start_war(s, country, target)
        return
    elif action == "peace" and valid:
        for w in s.get("wars", {}).values():
            if w.get("status") == "active" and country in w["participants"] and target in w["participants"]:
                side = "side_a" if country in w["side_a"] else "side_b"
                _finish_war(s, w, side, "A negotiated settlement ended the war.")
                return
        _event(s, "diplomacy", f"{country} sought peace with {target}, but no matching war was active.")
        return
    elif action == "continue_war":
        return
    else:
        c["gdp"] = round(c["gdp"] * 1.004, 3)
        msg, kind = f"{country} maintained its current policy.", "world"

    _event(s, kind, msg, rationale)

def _passive(s):
    for agreement in s.get("trade_agreements", []):
        a, b = agreement.get("countries", [None, None])
        if a in s["countries"] and b in s["countries"]:
            s["countries"][a]["gdp"] = round(s["countries"][a]["gdp"] * 1.0015, 3)
            s["countries"][b]["gdp"] = round(s["countries"][b]["gdp"] * 1.0015, 3)
    independent = set(_independent_countries(s))
    for name, c in s["countries"].items():
        if name not in independent:
            continue
        c["gdp"] = round(max(.05, c["gdp"] * (1 + (c["tech"] - 50) / 10000)), 3)
        c["stability"] = clamp(c["stability"] + (.12 if c["gdp"] > 1 else -.04)
                               - max(0, 50 - c["stability"]) * .006)
        c["population"] = round(c["population"] * (1 + .0008 + (c["stability"] - 50) / 100000), 2)
        c["resources"] = clamp(c["resources"] - .05 + (.10 if c["gdp"] < 1 else 0))
        c["tech"] = clamp(c["tech"] + .05)

def advance_turn(state, providers=None):
    state.setdefault("alliances", {n: [] for n in state["countries"]})
    state.setdefault("wars", {})
    state.setdefault("guarantees", [])
    state.setdefault("trade_agreements", [])
    state.setdefault("blocs", {})
    state.setdefault("ultimatums", [])
    _ensure_sovereignty(state)
    state["turn"] += 1
    for ultimatum in state.setdefault("ultimatums", []):
        if ultimatum.get("status") == "pending" and state["turn"] >= ultimatum.get("expires", 0):
            ultimatum["status"] = "expired"
            issuer, target = ultimatum["issuer"], ultimatum["target"]
            state["relations"][issuer][target] = clamp(state["relations"][issuer][target] - 12, -100, 100)
            state["relations"][target][issuer] = clamp(state["relations"][target][issuer] - 12, -100, 100)
            _event(state, "diplomacy", f"{target} ignored the ultimatum from {issuer}; relations deteriorated.")
    snap = copy.deepcopy(state)
    decisions = []
    providers = providers or {}
    for name in _independent_countries(snap):
        cfg = providers.get(name, {})
        d, p = choose_action(name, snap, cfg.get("provider", "Fallback"), cfg.get("model"))
        decisions.append((name, d, p))
    for name, d, p in decisions:
        apply_action(state, name, d["action"], d.get("target"), d.get("rationale", ""))
        if state["events"]:
            state["events"][-1]["text"] += f" [AI: {p}]"
    _progress_wars(state)
    _passive(state)
    state["history"].append({
        "turn": state["turn"],
        "countries": copy.deepcopy(state["countries"]),
        "wars": copy.deepcopy(state["wars"]),
        "sovereignty": copy.deepcopy(state["sovereignty"])
    })
    return state

def player_intervention(state, country, action, target=None):
    _ensure_sovereignty(state)
    apply_action(state, country, action, target, "Player intervention.")
    _event(state, "player", f"PLAYER INTERVENTION: ordered {country} to {action.replace('_', ' ')}.")
    return state
