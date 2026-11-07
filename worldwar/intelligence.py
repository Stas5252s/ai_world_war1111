"""Explain questions about the current simulated world using its actual state and event log."""

def _country_mentions(question, countries):
    q = question.casefold()
    aliases = {
        "China": ["китай", "китая", "китаем"],
        "India": ["индия", "индии", "индию"],
        "Germany": ["германия", "германии", "германию"],
        "United States": ["сша", "соединенные штаты", "америка", "америки"],
        "Russia": ["россия", "россии", "россию"],
        "Ukraine": ["украина", "украины", "украину"],
        "France": ["франция", "франции", "францию"],
        "United Kingdom": ["британия", "великобритания", "англия"],
        "Japan": ["япония", "японии", "японию"],
        "Iran": ["иран", "ирана", "ираном"],
        "Israel": ["израиль", "израиля", "израилем"],
        "Turkey": ["турция", "турции", "турцию"],
        "Poland": ["польша", "польши", "польшу"],
        "South Korea": ["южная корея", "южной кореи"],
        "North Korea": ["северная корея", "северной кореи"]
    }
    found = [name for name in countries if name.casefold() in q]
    for name, variants in aliases.items():
        if name in countries and any(alias in q for alias in variants) and name not in found:
            found.append(name)
    return found



def _control_question(state, question, countries):
    """Explain how one country gained control of another using recorded ownership changes."""
    q = question.casefold()
    trigger_terms = (
        "контроллер", "контролировать", "под контрол", "контролем",
        "захватил", "захватила", "захватило", "взял под контроль",
        "стала контролировать", "стал контролировать", "annexed", "control of"
    )
    if not any(term in q for term in trigger_terms):
        return None

    aliases = {
        "China": ["китай", "китая", "китаем"],
        "India": ["индия", "индии", "индию"],
        "Germany": ["германия", "германии", "германию"],
        "United States": ["сша", "соединенные штаты", "америка", "америки", "соединенных штатов"],
        "Russia": ["россия", "россии", "россию"],
        "Ukraine": ["украина", "украины", "украину", "украиной"],
        "France": ["франция", "франции", "францию"],
        "United Kingdom": ["британия", "великобритания", "англия"],
        "Japan": ["япония", "японии", "японию"],
        "Iran": ["иран", "ирана", "ираном"],
        "Israel": ["израиль", "израиля", "израилем"],
        "Turkey": ["турция", "турции", "турцию"],
        "Poland": ["польша", "польши", "польшу"],
        "South Korea": ["южная корея", "южной кореи"],
        "North Korea": ["северная корея", "северной кореи"]
    }

    mentions = []
    for name in countries:
        variants = [name] + aliases.get(name, [])
        positions = [q.find(v.casefold()) for v in variants if v and q.find(v.casefold()) >= 0]
        if positions:
            mentions.append((min(positions), name))
    mentions.sort()
    if len(mentions) < 2:
        return None

    first, second = mentions[0][1], mentions[1][1]
    # "How X became controller of Y" vs "How Y came under X's control".
    territory_first_phrases = ("под контролем", "оказалась под контролем", "оказался под контролем", "захватил")
    if any(p in q for p in territory_first_phrases):
        territory, controller = first, second
    else:
        controller, territory = first, second

    ownership = state.get("sovereignty", {})
    current_owner = ownership.get(territory, territory)
    wars = state.get("wars", {})
    events = state.get("events", [])
    causes, evidence = [], []

    if current_owner == controller:
        causes.append(f"CURRENT STATUS: {controller} currently controls {territory}.")
    else:
        causes.append(f"CURRENT STATUS: {territory} is currently controlled by {current_owner}, not {controller}.")

    transfer_records = []
    related_wars = []
    for war in wars.values():
        changes = [x for x in war.get("territory_changes", []) if x.get("territory") == territory]
        for change in changes:
            transfer_records.append((change.get("turn", 0), change, war))
            if change.get("to") == controller or change.get("from") == controller:
                if war not in related_wars:
                    related_wars.append(war)
        annexed = territory in war.get("annexed_territories", [])
        if annexed and war.get("annexing_country") == controller:
            if war not in related_wars:
                related_wars.append(war)
            transfer_records.append((war.get("ended", 0), {
                "turn": war.get("ended", "?"), "territory": territory,
                "from": "independent state", "to": controller, "type": "annexation"
            }, war))

    for turn, change, war in sorted(transfer_records, key=lambda item: item[0]):
        wid = war.get("id", "?")
        evidence.append(
            f"TURN {turn} | WAR #{wid}: {territory} changed from "
            f"{change.get('from', 'unknown')} to {change.get('to', 'unknown')}."
        )

    for war in sorted(related_wars, key=lambda w: w.get("started", 0)):
        wid = war.get("id", "?")
        winner = war.get("winner")
        if winner:
            winning_side = war.get("side_a", []) if winner == "side_a" else war.get("side_b", [])
            causes.append(
                f"WAR #{wid}: began on turn {war.get('started', '?')}, ended on turn "
                f"{war.get('ended', '?')}. Winner: {', '.join(winning_side)}. "
                f"Reason: {war.get('end_reason', 'not recorded')}. "
                f"Final score: {war.get('final_score', 'not recorded')}."
            )
        else:
            causes.append(
                f"WAR #{wid}: started on turn {war.get('started', '?')} and is "
                f"{war.get('status', 'unknown')}. Participants: "
                f"{', '.join(war.get('participants', []))}."
            )

    for event in sorted(events, key=lambda e: e.get("turn", 0)):
        line = event.get("text", "")
        low = line.casefold()
        if territory.casefold() in low and (
            controller.casefold() in low or "control" in low or "annex" in low or "captured" in low
        ):
            evidence.append(f"TURN {event.get('turn', '?')} | {event.get('kind', 'event')}: {line}")

    if not transfer_records and not evidence:
        causes.append(
            f"HISTORY NOT FOUND: the save records who controls {territory} now, "
            f"but contains no recorded transfer showing how {controller} gained it. "
            "The game cannot honestly reconstruct a cause from the available data."
        )
    elif transfer_records:
        causes.append(
            "MECHANISM: territory changed hands during the recorded war. In this simulation, "
            "front-line changes require a sustained war-score advantage; the strongest military "
            "country on the winning side is selected as the new controller. Annexation can also "
            "transfer the defeated state's territory when the war ends."
        )

    return {
        "title": f"How {controller} gained control of {territory}",
        "summary": "This is a chronological investigation of the territory's ownership changes. "
                   "Recorded events are shown separately from the simulation's rules.",
        "causes": causes[:14],
        "evidence": evidence[:30],
        "confidence": "Recorded transfer found" if transfer_records else "No transfer history recorded"
    }

def explain_question(state, question):
    question = (question or "").strip()
    if len(question) < 4:
        return {"title": "Ask a more specific question", "summary": "For example: Why did Germany's economy fall? Or why are China and India hostile?", "evidence": [], "confidence": "—"}

    countries = state.get("countries", {})
    names = _country_mentions(question, countries)
    control_report = _control_question(state, question, countries)
    if control_report:
        return control_report
    events = state.get("events", [])
    relations = state.get("relations", {})
    wars = state.get("wars", {})
    evidence = []
    causes = []
    title = "World intelligence report"

    if len(names) >= 2:
        a, b = names[:2]
        title = f"{a} ↔ {b}"
        score = relations.get(a, {}).get(b, 0)
        reverse = relations.get(b, {}).get(a, score)
        causes.append(f"Diplomatic relations: {score:.0f}/100 from {a}'s side and {reverse:.0f}/100 from {b}'s side.")
        if b in state.get("alliances", {}).get(a, []):
            causes.append("They currently have a mutual alliance.")
        else:
            causes.append("They do not currently have a mutual bilateral alliance.")
        shared_wars = [w for w in wars.values() if w.get("status") == "active" and a in w.get("participants", []) and b in w.get("participants", [])]
        for war in shared_wars:
            causes.append(f"They are both participants in active war {war.get('id', '?')} (progress {war.get('progress', 0)}).")
        for org_name, org in state.get("organizations", {}).items():
            members = org.get("members", [])
            if a in members and b in members:
                causes.append(f"Both belong to {org.get('name', org_name)}.")
            elif (a in members) != (b in members):
                causes.append(f"Membership differs: {org.get('name', org_name)} includes {a if a in members else b}, but not both.")
        relevant = [e for e in events if a.casefold() in e.get("text", "").casefold() and b.casefold() in e.get("text", "").casefold()]
    elif len(names) == 1:
        a = names[0]
        country = countries[a]
        title = f"Situation report: {a}"
        causes.extend([
            f"GDP: {country.get('gdp', 0):.4f} trillion USD.",
            f"Stability: {country.get('stability', 0):.1f}/100; technology: {country.get('tech', 0):.1f}/100; military: {country.get('military', 0):.1f}/100.",
            f"Inflation: {country.get('inflation', 0):.1f}%; unemployment: {country.get('unemployment', 0):.1f}%; production: {country.get('production', 0):.1f}/100."
        ])
        politics = state.get("politics", {}).get(a, {})
        if politics:
            causes.append(f"Government: {politics.get('government', 'unknown')} ({politics.get('ideology', 'unknown')}); approval {politics.get('approval', 0):.1f}%; next election: turn {politics.get('election_due', '?')}.")
        active = [w for w in wars.values() if w.get("status") == "active" and a in w.get("participants", [])]
        for war in active:
            opponents = [n for n in war.get("participants", []) if n != a]
            causes.append(f"Active war {war.get('id', '?')} against/alongside: {', '.join(opponents) or 'other participants'}; progress {war.get('progress', 0)}.")
        allies = state.get("alliances", {}).get(a, [])
        if allies:
            causes.append("Current allies: " + ", ".join(allies[:10]) + ".")
        sanctions = [s for s in state.get("sanctions", []) if s.get("target") == a or s.get("issuer") == a]
        if sanctions:
            causes.append(f"Sanctions involving this country: {len(sanctions)}.")
        relevant = [e for e in events if a.casefold() in e.get("text", "").casefold()]
    else:
        q = question.casefold()
        relevant = []
        keywords = {
            "war": ("war", "conflict", "invasion", "peace", "battle"),
            "econom": ("econom", "gdp", "inflation", "debt", "trade", "recession"),
            "protest": ("protest", "riot", "government", "election", "coup"),
            "alliance": ("alliance", "bloc", "organization", "nato", "eu", "brics"),
            "influence": ("influence", "power", "strongest", "dominant")
        }
        matches = [key for key, terms in keywords.items() if any(term in q for term in terms)]
        relevant = [e for e in events if any(term in e.get("text", "").casefold() for key in matches for term in keywords[key])]
        if "war" in matches:
            for war in wars.values():
                if war.get("status") == "active":
                    causes.append(f"Active war {war.get('id', '?')}: {', '.join(war.get('participants', [])[:12])}; progress {war.get('progress', 0)}.")
        if "influence" in matches:
            ranking = sorted(((name, sum(scores.values())) for name, scores in state.get("influence", {}).items()), key=lambda x: x[1], reverse=True)
            if ranking:
                causes.append("Highest aggregate influence scores: " + "; ".join(f"{n} ({v:.1f})" for n, v in ranking[:5]) + ".")
        if "alliance" in matches:
            pairs = []
            for name, allies in state.get("alliances", {}).items():
                for other in allies:
                    if name < other:
                        pairs.append(f"{name}–{other}")
            causes.append("Mutual alliances: " + (", ".join(pairs[:15]) if pairs else "none currently recorded") + ".")

    relevant = sorted(relevant, key=lambda e: e.get("turn", 0), reverse=True)
    for event in relevant[:8]:
        evidence.append(f"Turn {event.get('turn', '?')} · {event.get('kind', 'event')}: {event.get('text', '')}")
        if event.get("rationale"):
            evidence.append("AI rationale: " + event["rationale"])

    if not causes and not evidence:
        summary = "I couldn't identify enough relevant facts in the current simulation. Mention a country, two countries, an active war, or a specific economic/political issue."
    else:
        summary = "This explanation is based on the current simulation state, not outside-world assumptions. The facts below show what is happening; the event log provides the recorded history behind it."
    return {
        "title": title,
        "summary": summary,
        "causes": causes[:12],
        "evidence": evidence,
        "confidence": "Based on recorded simulation data" if causes or evidence else "Insufficient data"
    }
