# ONE source of truth: the form (served at /fields) and TOKENS.txt both come from this list.
MODULES = {"regcomply": "RegComply (GRC & audit)", "aml": "AML monitoring", "kyc": "Customer verification",
           "regwatch": "RegWatch (intelligence)", "learn": "Compliance learning", "fraud": "Fraud detection"}
# Slide numbers (1-based, as in the template) that may be dropped for a shorter proposal
DROPPABLE_SLIDES = {13: "Integration & assurance", 16: "Governance", 17: "Value & outcomes", 18: "Commercials"}

def _f(key, label, group, it):
    return {"key": key, "label": label, "group": group, **(it[2] if len(it) > 2 else {})}
def G(group, items):
    return [_f(it[0], it[1], group, it) for it in items]
def rep(n, prefix, group, items):
    return [_f(f"{prefix}{i}_{it[0]}", f"{it[1]} {i}", group, it) for i in range(1, n + 1) for it in items]

A = {"area": 1}
FIELDS = (
 G("Cover", [("client_name", "Client name", {"req": 1}), ("headline", "Outcome headline", {"req": 1}), ("outcome_line", "One-sentence outcome", A)]) +
 G("Document control", [("client_code", "Client code (e.g. ZEN)", {"req": 1}), ("recipient_name", "Recipient name"), ("recipient_title", "Recipient title"),
    ("author_name", "Prepared by (name)"), ("author_title", "Prepared by (title)"), ("status", "Draft / Final", {"def": "Draft"})]) +
 G("Executive summary", [("exec_context", "Context", A), ("exec_recommendation", "Recommendation", A), ("exec_outcome", "Outcome", A)]) +
 G("At a glance", [(f"stat{i}_{k}", f"Stat {i} {k}") for i in (1, 2, 3) for k in ("value", "label")]) +
 G("Understanding", [("stand_intro", "Where they stand", A), ("market_position", "Market position", A), ("growth_agenda", "Growth agenda", A),
    ("governance_strength", "Governance strength", A), ("our_perspective", "Our perspective", A)]) +
 rep(4, "prio", "Client priorities", [("body", "Priority", A), ("impl", "Business implication")]) +
 rep(4, "reg", "Regulatory context", [("date", "Date (Qx YYYY)"), ("regulator", "Regulator"), ("req", "Requirement", A)]) +
 rep(4, "map", "Priority mapping", [("priority", "Client priority"), ("response", "Our response", A), ("outcome", "Outcome", A)]) +
 rep(5, "scope", "Scope: in scope", [("in", "Item")]) + rep(4, "resp", "Scope: client responsibilities", [("item", "Item")]) +
 G("Assurance", [("client_systems", "Client systems to integrate"), ("roles_in_scope", "Roles in scope"),
    ("hosting", "Hosting & data protection (security-approved)", A)]) +
 G("Implementation", [("go_live_weeks", "Weeks to go-live", {"def": "12"})]) + rep(4, "phase", "Implementation phases", [("weeks", "Weeks (e.g. 1–2)")]) +
 G("Governance", [("steer_client", "Client sponsor"), ("steer_rt", "RegTech365 sponsor"), ("gov_owner", "Project owner"), ("gov_compliance", "Compliance lead"),
    ("gov_tech", "Technology lead"), ("gov_eng", "Engagement lead"), ("gov_consultant", "Solution consultant"), ("gov_impl", "Implementation lead")]) +
 rep(4, "kpi", "Outcome measures", [("base", "Baseline"), ("target", "Target")]) +
 G("Business case", [("biz_case", "Business case (₦m, only if provable)"), ("biz_basis", "Basis of calculation", A)]) +
 rep(3, "price", "Commercials: modules", [("module", "Module"), ("basis", "Licensing basis"), ("y1", "Year 1 (₦)"), ("y2", "Year 2+ (₦)")]) +
 G("Commercials: totals & terms", [("price_impl", "Implementation (₦, one-off)"), ("price_total_y1", "Total Year 1 (₦)"), ("price_total_y2", "Total Year 2+ (₦)"),
    ("payment", "Payment terms", {"def": "Annually in advance"}), ("term", "Term", {"def": "3-year agreement"})]) +
 rep(3, "proof", "Why RegTech365: proof points", [("point", "Verified proof point", A)]) +
 rep(4, "next", "Next steps", [("date", "Date")]) + rep(4, "assume", "Key assumptions", [("item", "Assumption")]) +
 G("Contact", [("contact_name", "Account lead name"), ("contact_title", "Account lead title"), ("share_with", "Share generated deck with (email)")])
)
if __name__ == "__main__":  # python schema.py > ../TOKENS.txt
    print("Automatic tokens: {{issue_date}} {{valid_until}} {{doc_ref}}")
    print("Module tiles: set Alt text to " + " | ".join(f"module:{k}" for k in MODULES) + "\n")
    for f in FIELDS: print("{{%s}}\t%s  [%s]" % (f["key"], f["label"], f["group"]))
