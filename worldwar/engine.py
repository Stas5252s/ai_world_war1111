import copy
import random
from .data import COUNTRIES
from .agents import choose_action

def _record_history(state):
    """Store a compact yearly snapshot for historical charts."""
    countries = {}
    for name, country in state.get("countries", {}).items():
        countries[name] = {
            key: country.get(key, 0)
            for key in ("gdp", "population", "stability", "tech", "military", "production")
        }
    active_wars = sum(
        1 for war in state.get("wars", {}).values()
        if war.get("status") == "active"
    )
    state.setdefault("history", []).append({
        "turn": state.get("turn", 0),
        "countries": countries,
        "world_gdp": sum(country.get("gdp", 0) for country in state.get("countries", {}).values()),
        "world_population": sum(country.get("population", 0) for country in state.get("countries", {}).values()),
        "active_wars": active_wars,
        "sovereign_states": len(_independent_countries(state)),
    })
    # Keep the latest 500 years to prevent saves from growing without limit.
    state["history"] = state["history"][-500:]


def _update_influence(s):
    """Update soft-power scores from diplomacy, trade, security ties and economic weight."""
    countries = s.get("countries", {})
    independent = set(_independent_countries(s))
    influence = s.setdefault("influence", {})
    trade_pairs = {frozenset(deal.get("countries", [])) for deal in s.get("trade_agreements", []) if len(deal.get("countries", [])) == 2}
    guarantee_pairs = {(item.get("guarantor"), item.get("protected")) for item in s.get("guarantees", [])}
    sanctioned = {(item.get("issuer"), item.get("target")) for item in s.get("sanctions", [])}
    at_war = set()
    for war in s.get("wars", {}).values():
        if war.get("status") == "active":
            members = war.get("participants", [])
            for a in members:
                for b in members:
                    if a != b: at_war.add(frozenset((a, b)))
    bloc_memberships = {}
    for bloc in _normalise_blocs(s).values():
        members = bloc.get("members", [])
        for member in members:
            bloc_memberships.setdefault(member, set()).update(n for n in members if n != member)
    relations = s.get("relations", {})
    for target in countries:
        scores = influence.setdefault(target, {})
        for actor in list(scores):
            if actor not in countries or actor == target or actor not in independent: scores.pop(actor, None)
        if target not in independent: continue
        for actor in independent:
            if actor == target: continue
            relation = relations.get(target, {}).get(actor, 0)
            current = float(scores.get(actor, max(0.0, (relation + 20) * 0.18)))
            economic_weight = min(0.35, max(0.0, countries[actor].get("gdp", 0)) ** 0.25 * 0.08)
            change = (relation - 20) / 45 + economic_weight - 0.35
            pair = frozenset((actor, target))
            if pair in trade_pairs: change += 1.2
            if actor in s.get("alliances", {}).get(target, []): change += 1.6
            if actor in bloc_memberships.get(target, set()): change += 0.9
            if (actor, target) in guarantee_pairs: change += 0.8
            if (actor, target) in sanctioned: change -= 1.5
            if pair in at_war: change -= 3.0
            scores[actor] = round(clamp(current + change, 0, 100), 2)
    s["influence"] = influence

def new_world(seed=7):
    random.seed(seed)
    countries = copy.deepcopy(COUNTRIES)
    names = list(countries)
    relations = {
        a: {b: (0 if a == b else random.randint(-20, 25)) for b in names}
        for a in names
    }
    # Seed a restrained diplomatic landscape from each country's
    # strategic worldview. These are starting tendencies, not permanent blocs.
    for a, profile in countries.items():
        worldview = profile.get("worldview", {})
        for b in worldview.get("preferred_partners", []):
            if b in relations and b != a and a not in countries.get(b, {}).get("worldview", {}).get("competitors", []):
                relations[a][b] = max(relations[a][b], 24)
                relations[b][a] = max(relations[b][a], 18)
        for b in worldview.get("competitors", []):
            if b in relations and b != a:
                relations[a][b] = min(relations[a][b], -34)
                relations[b][a] = min(relations[b][a], -28)

    # Persistent rivalries start with elevated tension, but can still improve.
    rivalries = [
        ("China", "India"), ("United States", "China"),
        ("Russia", "United States"), ("Iran", "Saudi Arabia"),
        ("India", "Pakistan"), ("Japan", "China"),
        ("North Korea", "South Korea"), ("Israel", "Iran"),
        ("Ukraine", "Russia")
    ]
    for a, b in rivalries:
        if a in relations and b in relations:
            relations[a][b] = relations[b][a] = -48
    organizations = {
        "UN": {"name": "United Nations", "type": "diplomatic", "description": "A global forum for diplomacy, sovereignty and peaceful dispute resolution.", "members": [n for n in names], "founded": 0},
        "NATO": {"name": "NATO", "type": "defense", "description": "A collective-defence organization. Members support one another if attacked in the simulation.", "members": [n for n in ["United States", "Canada", "United Kingdom", "France", "Germany", "Italy", "Poland", "Turkey", "Norway", "Denmark", "Netherlands", "Belgium", "Spain", "Portugal", "Greece", "Czechia", "Hungary", "Romania", "Bulgaria", "Slovakia", "Slovenia", "Croatia", "Estonia", "Latvia", "Lithuania", "Albania", "Montenegro", "North Macedonia", "Finland", "Sweden"] if n in countries], "founded": 0},
        "EU": {"name": "European Union", "type": "economic", "description": "Economic integration, shared markets and coordinated policy.", "members": [n for n in ["Germany", "France", "Italy", "Poland", "Spain", "Netherlands", "Belgium", "Sweden", "Finland", "Denmark", "Ireland", "Austria", "Portugal", "Greece", "Czechia", "Hungary", "Romania", "Bulgaria", "Slovakia", "Slovenia", "Croatia", "Estonia", "Latvia", "Lithuania", "Luxembourg", "Cyprus", "Malta"] if n in countries], "founded": 0},
        "BRICS": {"name": "BRICS", "type": "economic", "description": "A forum for economic cooperation among major emerging economies.", "members": [n for n in ["Brazil", "Russia", "India", "China", "South Africa", "Egypt", "Ethiopia", "Indonesia", "Iran", "United Arab Emirates"] if n in countries], "founded": 0},
        "ASEAN": {"name": "ASEAN", "type": "economic", "description": "Southeast Asian regional cooperation and economic integration.", "members": [n for n in ["Indonesia", "Malaysia", "Singapore", "Thailand", "Vietnam", "Philippines", "Cambodia", "Laos", "Myanmar", "Brunei"] if n in countries], "founded": 0},
        "AU": {"name": "African Union", "type": "diplomatic", "description": "Continental cooperation, diplomacy and regional stability.", "members": [n for n in names if countries[n].get("iso") in {"DZA","AGO","BEN","BWA","BFA","BDI","CPV","CMR","CAF","TCD","COM","COG","COD","CIV","DJI","EGY","GNQ","ERI","SWZ","ETH","GAB","GMB","GHA","GIN","GNB","KEN","LSO","LBR","LBY","MDG","MWI","MLI","MRT","MUS","MAR","MOZ","NAM","NER","NGA","RWA","STP","SEN","SYC","SLE","SOM","ZAF","SSD","SDN","TZA","TGO","TUN","UGA","ZMB","ZWE"}], "founded": 0},
        "G7": {"name": "Group of Seven", "type": "economic", "description": "A forum for advanced industrial economies to coordinate economic policy.", "members": [n for n in ["United States", "Canada", "United Kingdom", "France", "Germany", "Italy", "Japan"] if n in countries], "founded": 0},
        "OPEC": {"name": "OPEC", "type": "energy", "description": "Coordination among major oil-exporting countries.", "members": [n for n in ["Saudi Arabia", "Iran", "Iraq", "Kuwait", "United Arab Emirates", "Venezuela", "Nigeria", "Algeria", "Libya", "Angola", "Congo", "Gabon", "Equatorial Guinea"] if n in countries], "founded": 0}
    }
    state = {
        "turn": 0, "countries": countries, "relations": relations,
        "alliances": {n: [] for n in names},
        "wars": {}, "next_war_id": 1,
        "influence": {target: {actor: max(0.0, (relations[target][actor] + 20) * 0.18) for actor in names if actor != target} for target in names},
        "guarantees": [], "trade_agreements": [], "sanctions": [], "blocs": {},
        "next_bloc_id": 1, "ultimatums": [], "organizations": organizations,
        "sovereignty": {n: n for n in names},
        "events": [{"turn": 0, "kind": "world",
                    "text": "The simulation begins. Every government seeks global influence."}],
        "history": []
    }
    _record_history(state)
    return state

def _normalize_organizations(s):
    organizations = s.setdefault("organizations", {})
    if not isinstance(organizations, dict):
        organizations = {}
        s["organizations"] = organizations
    for org_id, org in organizations.items():
        if not isinstance(org, dict):
            organizations[org_id] = {"name": str(org_id), "type": "diplomatic", "description": "", "members": []}
            org = organizations[org_id]
        members = org.get("members", [])
        if not isinstance(members, (list, tuple, set)):
            members = []
        org["members"] = list(dict.fromkeys(n for n in members if n in s.get("countries", {})))
        org.setdefault("name", str(org_id))
        org.setdefault("type", "diplomatic")
        org.setdefault("description", "")
    return organizations


def _organization_membership(s, country, organization, action):
    organizations = _normalize_organizations(s)
    if country not in s.get("countries", {}) or organization not in organizations:
        return
    org = organizations[organization]
    members = org["members"]
    if action == "join":
        if country in members:
            _event(s, "organization", f"{country} is already a member of {org['name']}.")
            return
        members.append(country)
        _event(s, "organization", f"{country} joined {org['name']}.")
    elif action == "leave":
        if country not in members:
            return
        members.remove(country)
        _event(s, "organization", f"{country} left {org['name']}.")


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


def _normalise_blocs(s):
    """Repair legacy or malformed bloc records without losing valid members."""
    raw = s.get("blocs", {})
    if not isinstance(raw, dict):
        raw = {}
    cleaned = {}
    for key, value in raw.items():
        if isinstance(value, dict):
            bloc = dict(value)
            members = bloc.get("members", [])
            if isinstance(members, str):
                members = [members]
            elif not isinstance(members, (list, tuple, set)):
                members = []
            bloc["members"] = list(dict.fromkeys(
                name for name in members if isinstance(name, str) and name in s.get("countries", {})
            ))
            bloc.setdefault("id", str(key))
            bloc.setdefault("name", f"International Bloc {key}")
            bloc.setdefault("leader", bloc["members"][0] if bloc["members"] else "")
            if bloc["leader"] and bloc["leader"] not in bloc["members"]:
                bloc["members"].insert(0, bloc["leader"])
            cleaned[str(key)] = bloc
        elif isinstance(value, (list, tuple, set)):
            members = list(dict.fromkeys(
                name for name in value if isinstance(name, str) and name in s.get("countries", {})
            ))
            if members:
                cleaned[str(key)] = {
                    "id": str(key), "name": f"International Bloc {key}",
                    "leader": members[0], "members": members
                }
    s["blocs"] = cleaned
    return cleaned


def _create_bloc(s, founder):
    blocs = _normalise_blocs(s)
    for bloc in blocs.values():
        if founder in bloc["members"]:
            _event(s, "diplomacy", f"{founder} already belongs to {bloc['name']}.")
            return
    bid = str(s.get("next_bloc_id", 1))
    s["next_bloc_id"] = int(bid) + 1
    name = f"International Bloc {bid}"
    blocs[bid] = {"id": bid, "name": name, "leader": founder, "members": [founder]}
    _event(s, "diplomacy", f"{founder} founded {name}.")


def _invite_to_bloc(s, founder, target):
    blocs = _normalise_blocs(s)
    if founder not in s.get("countries", {}) or target not in s.get("countries", {}):
        return
    if founder == target:
        return

    # A country can belong to only one diplomatic bloc.
    for existing in blocs.values():
        if target in existing["members"]:
            _event(s, "diplomacy", f"{target} already belongs to {existing['name']}.")
            return

    bloc = next((b for b in blocs.values() if b.get("leader") == founder), None)
    if bloc is None:
        _create_bloc(s, founder)
        blocs = _normalise_blocs(s)
        bloc = next((b for b in blocs.values() if b.get("leader") == founder), None)
    if bloc is None:
        return

    members = bloc.get("members")
    if not isinstance(members, list):
        members = []
        bloc["members"] = members
    if target not in members:
        members.append(target)

    s.setdefault("relations", {}).setdefault(founder, {})
    s.setdefault("relations", {}).setdefault(target, {})
    s["relations"][founder][target] = clamp(s["relations"][founder].get(target, 0) + 10, -100, 100)
    s["relations"][target][founder] = clamp(s["relations"][target].get(founder, 0) + 10, -100, 100)
    _event(s, "diplomacy", f"{target} joined {bloc['name']} led by {founder}.")

def _sever_relations(s, a, b):
    s["relations"][a][b] = -100
    s["relations"][b][a] = -100
    _break_alliance(s, a, b)
    s["trade_agreements"] = [x for x in s.get("trade_agreements", []) if set(x.get("countries", [])) != {a, b}]
    s["sanctions"] = [x for x in s.get("sanctions", []) if not ({x.get("issuer"), x.get("target")} == {a, b})]
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
    _event(s, "economy", f"War #{wid} is disrupting trade and production while raising military expenditure for both sides.")


    for guarantee in s.get("guarantees", []):
        if guarantee.get("protected") == defender:
            guarantor = guarantee.get("guarantor")
            if guarantor in independent and guarantor not in s["wars"][wid]["participants"] and not _active_war_between(s, guarantor, attacker):
                s["wars"][wid]["side_b"].append(guarantor)
                s["wars"][wid]["participants"].append(guarantor)
                _event(s, "diplomacy", f"{guarantor} honored its guarantee to {defender} and joined war #{wid}.")

    # Members of collective-defence organizations support an attacked member.
    organizations = _normalize_organizations(s)
    for org in organizations.values():
        if org.get("type") != "defense" or defender not in org.get("members", []):
            continue
        for member in org["members"]:
            if member not in (attacker, defender) and member in independent and member not in s["wars"][wid]["participants"] and not _active_war_between(s, member, attacker):
                s["wars"][wid]["side_b"].append(member)
                s["wars"][wid]["participants"].append(member)
                _event(s, "organization", f"{member} joined {defender}'s side in war #{wid} under {org['name']} collective defence.")

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
        c = s["countries"][n]
        c["stability"] = clamp(c["stability"] + 2)
        c["gdp"] = round(c["gdp"] * 1.01, 6)
        c["production"] = clamp(c.get("production", 50) - 1)
        c["debt"] = c.get("debt", 0) + c["gdp"] * 2
    for n in loser_side:
        c = s["countries"][n]
        c["stability"] = clamp(c["stability"] - 4)
        c["gdp"] = round(max(.00001, c["gdp"] * .97), 6)
        c["production"] = clamp(c.get("production", 50) - 4)
        c["debt"] = c.get("debt", 0) + c["gdp"] * 10
        c["unemployment"] = min(45, c.get("unemployment", 7) + 1.5)
        c["inflation"] = min(35, c.get("inflation", 3) + 1.2)
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
    _event(s, "economy", f"War #{w['id']} left the defeated side with damaged production, higher debt and unemployment. Recovery will take multiple turns.")
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
        c["production"] = clamp(c.get("production", 50) + 2.0)
        c["treasury"] = max(0, c.get("treasury", 0) - c["gdp"] * 5)
        c["stability"] = clamp(c["stability"] + .3)
        msg, kind = f"{country} invested in infrastructure and productive capacity.", "economy"
    elif action == "research":
        c["tech"] = clamp(c["tech"] + 2)
        c["production"] = clamp(c.get("production", 50) + .5)
        c["treasury"] = max(0, c.get("treasury", 0) - c["gdp"] * 3)
        msg, kind = f"{country} funded research and development.", "technology"
    elif action == "social_program":
        c["stability"] = clamp(c["stability"] + 4)
        c["treasury"] = max(0, c.get("treasury", 0) - c["gdp"] * 4)
        msg, kind = f"{country} funded public services and social support.", "politics"
    elif action == "mobilize":
        c["military"] = clamp(c["military"] + 5)
        c["military_spending"] = min(.15, c.get("military_spending", .035) + .008)
        c["treasury"] = max(0, c.get("treasury", 0) - c["gdp"] * 10)
        msg, kind = f"{country} increased readiness and military spending.", "military"

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
            c["trade"] = c.get("trade", 0) * 1.04
            cs[target]["trade"] = cs[target].get("trade", 0) * 1.04
            msg, kind = f"{country} and {target} signed a continuing trade agreement.", "economy"
        elif action == "sanction":
            rel[country][target] = clamp(rel[country][target] - 12, -100, 100)
            cs[target]["trade"] = cs[target].get("trade", 0) * .94
            cs[target]["production"] = clamp(cs[target].get("production", 50) - .4)
            c["trade"] = c.get("trade", 0) * .99
            if not any(x.get("issuer") == country and x.get("target") == target for x in s.setdefault("sanctions", [])):
                s["sanctions"].append({"issuer": country, "target": target, "since": s["turn"]})
            msg, kind = f"{country} imposed continuing economic sanctions on {target}.", "economy"
        else:
            rel[country][target] = clamp(rel[country][target] + 18, -100, 100)
            rel[target][country] = clamp(rel[target][country] + 12, -100, 100)
            s["sanctions"] = [x for x in s.get("sanctions", []) if not (x.get("issuer") == country and x.get("target") == target)]
            msg, kind = f"{country} proposed de-escalation to {target} and lifted its sanctions.", "diplomacy"
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

def _economy_step(s):
    """Advance one year. GDP is USD trillions; fiscal/trade flows are USD billions."""
    active_wars = {}
    for war in s.get("wars", {}).values():
        if war.get("status") == "active":
            for name in war.get("participants", []):
                active_wars[name] = active_wars.get(name, 0) + 1

    trade_partners = {name: set() for name in s["countries"]}
    sanctioned_targets = {}
    for sanction in s.get("sanctions", []):
        target = sanction.get("target")
        if target in s["countries"]:
            sanctioned_targets[target] = sanctioned_targets.get(target, 0) + 1
    for org in _normalize_organizations(s).values():
        if org.get("type") in ("economic", "energy"):
            members = [n for n in org.get("members", []) if n in trade_partners]
            for i, a in enumerate(members):
                for b in members[i + 1:]:
                    trade_partners[a].add(b)
                    trade_partners[b].add(a)
    for agreement in s.get("trade_agreements", []):
        pair = agreement.get("countries", [])
        if len(pair) == 2 and all(n in trade_partners for n in pair):
            trade_partners[pair[0]].add(pair[1])
            trade_partners[pair[1]].add(pair[0])

    independent = set(_independent_countries(s))
    for name, c in s["countries"].items():
        gdp = max(0.00001, float(c.get("gdp", 0.01)))
        c.setdefault("production", 45.0)
        c.setdefault("budget", gdp * 210)
        c.setdefault("budget_balance", 0.0)
        c.setdefault("treasury", gdp * 80)
        c.setdefault("debt", gdp * 350)
        c.setdefault("trade", gdp * 350)
        c.setdefault("trade_balance", 0.0)
        c.setdefault("resource_stock", 60.0)
        c.setdefault("inflation", 3.0)
        c.setdefault("unemployment", 7.0)
        c.setdefault("military_spending", 0.035)

        war_count = active_wars.get(name, 0)
        war_cost = min(0.035, war_count * 0.018)
        trade_bonus = min(0.012, len(trade_partners[name]) * 0.0015)
        sanction_penalty = min(0.018, sanctioned_targets.get(name, 0) * 0.006)
        resource_factor = (c["resource_stock"] - 50) / 10000
        debt_ratio = c["debt"] / max(gdp * 1000, 1)
        political_factor = (c["stability"] - 50) / 10000
        technology_factor = (c["tech"] - 50) / 8000
        production_factor = (c["production"] - 50) / 9000
        growth = 0.006 + political_factor + technology_factor + production_factor + resource_factor + trade_bonus - war_cost - sanction_penalty - max(0, debt_ratio - 0.8) * 0.004
        if name not in independent:
            growth -= 0.002
        growth = max(-0.06, min(0.045, growth))
        c["gdp"] = round(max(0.00001, gdp * (1 + growth)), 6)

        production_change = (c["tech"] - 50) * 0.006 + (c["resources"] - 50) * 0.003
        production_change += trade_bonus * 80 - (1.25 * war_count)
        if c["resource_stock"] < 15:
            production_change -= 0.8
        c["production"] = round(clamp(c["production"] + production_change, 1, 100), 2)
        c["resource_stock"] = round(clamp(
            c["resource_stock"] + (c["resources"] - 50) * 0.012
            - c["production"] * 0.005 - war_count * 0.15, 0, 100
        ), 2)

        population_growth = 0.008 + (c["stability"] - 50) / 12000 - war_count * 0.003
        c["population"] = round(max(0.001, c["population"] * (1 + max(-0.015, min(0.025, population_growth)))), 3)
        c["tech"] = clamp(c["tech"] + 0.08 + c["production"] / 2000)
        c["stability"] = clamp(c["stability"] + (0.08 if growth > 0 else -0.12) - war_count * 0.25)

        gdp_billions = c["gdp"] * 1000
        tax_rate = 0.16 + c["tech"] / 1000
        revenue = gdp_billions * tax_rate
        military_rate = c.get("military_spending", 0.035) + war_cost
        military_expense = gdp_billions * military_rate
        public_expense = gdp_billions * (0.145 + max(0, 55 - c["stability"]) / 2000)
        interest = c["debt"] * 0.035
        balance = revenue - military_expense - public_expense - interest
        c["budget"] = round(revenue, 2)
        c["budget_balance"] = round(balance, 2)
        c["treasury"] = round(max(0, c["treasury"] + balance), 2)
        if balance < 0:
            c["debt"] = round(c["debt"] + abs(balance), 2)
        else:
            repayment = min(c["debt"], balance * 0.35)
            c["debt"] = round(max(0, c["debt"] - repayment), 2)
            c["treasury"] = round(max(0, c["treasury"] - repayment), 2)

        openness = 0.22 + c["tech"] / 250 + len(trade_partners[name]) * 0.012
        sanction_factor = max(0.55, 1 - sanctioned_targets.get(name, 0) * 0.12)
        c["trade"] = round(gdp_billions * openness * (1 - min(0.25, war_count * 0.08)) * sanction_factor, 2)
        c["trade_balance"] = round(c["trade"] * ((c["resources"] - 50) / 250), 2)
        c["inflation"] = round(max(0.2, min(35, c["inflation"] + war_count * 0.7 + max(0, -balance / max(gdp_billions, 1) * 100) * 0.08 - 0.08)), 2)
        c["unemployment"] = round(max(1, min(45, c["unemployment"] + war_count * 0.45 - max(0, growth) * 18 - (c["production"] - 50) * 0.006)), 2)



def advance_turn(state, providers=None):
    state.setdefault("alliances", {n: [] for n in state["countries"]})
    state.setdefault("wars", {})
    state.setdefault("guarantees", [])
    state.setdefault("trade_agreements", [])
    state.setdefault("sanctions", [])
    state.setdefault("blocs", {})
    _normalise_blocs(state)
    state.setdefault("ultimatums", [])
    _ensure_sovereignty(state)
    if not state.get("history"):
        _record_history(state)
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
    _economy_step(state)
    _update_influence(state)
    _record_history(state)
    return state

def player_intervention(state, country, action, target=None):
    _ensure_sovereignty(state)
    apply_action(state, country, action, target, "Player intervention.")
    _event(state, "player", f"PLAYER INTERVENTION: ordered {country} to {action.replace('_', ' ')}.")
    return state
