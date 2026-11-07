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


def explain_question(state, question):
    question = (question or "").strip()
    if len(question) < 4:
        return {"title": "Ask a more specific question", "summary": "For example: Why did Germany's economy fall? Or why are China and India hostile?", "evidence": [], "confidence": "—"}

    countries = state.get("countries", {})
    names = _country_mentions(question, countries)
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
