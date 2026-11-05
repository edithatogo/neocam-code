# CHHHS perspective scenario reproduction

Run the Python block from the repository root in the frozen 3.15.1 environment. Values are annual AUD savings relative to telephone. Reference portfolio CHHHS, activity contacts_1, deterministic inputs. Each scenario overrides only its named assumptions. Site values cover origin activity. District includes those sites. Perspectives overlap.

```python
import csv
import itertools
from pathlib import Path
from math import isclose
from scripts.analyse_refinements import (ROOT, ActivitySpec, load_configuration, portfolio,
    policy_catalogue, eligibility_catalogue, evaluate_policies)
from src.deployment import DeploymentPolicy

out = Path("verification/mixed-policy-fiscal")
cfg = load_configuration(ROOT)
sites = portfolio("chhhs")
policies = policy_catalogue(sites)
def evaluate(group, choices):
    return evaluate_policies(group, choices, eligibility_catalogue(group, allow_hypothetical=True),
                             cfg.parameters, cfg.pathways, cfg.owned_assets, activity=ActivitySpec("contacts", 1))

def inputs(filename):
    with (ROOT / "outputs/v13-refinements" / filename).open() as f:
        return [r for r in csv.DictReader(f) if r["portfolio"] == "chhhs" and r["activity_id"] == "contacts_1"]

def write(name, rows):
    with (out / name).open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

def components(arms, key, hospital_fraction=None):
    a, phone = arms[key], arms["telephone"]
    def delta(field):
        difference = phone[field] - a[field]
        return float(difference[0]) if hospital_fraction is None else difference
    def cost(field):
        return -delta(field)
    hf = cfg.pathways.hospital_marginal_fraction if hospital_fraction is None else hospital_fraction
    origin = hf * sum(delta(f) for f in ("origin_benchmark_cost", "local_benchmark_cost", "pre_rescue_benchmark_cost"))
    receiver = hf * delta("receiving_benchmark_cost") + delta("rescue_extra_resource_cost")
    operating = cost("local_ready_cost") + cost("local_workflow_cost")
    return dict(origin=origin, receiver=receiver, retrieval=delta("transport_resource_cost"),
                capital=cost("capital_annualised"), operating=operating, hub=cost("hub_resource_cost"),
                benchmark=delta("hospital_benchmark_cost"), family=cost("family_cost_extension"))

arms = evaluate(sites, policies)
parts = {p.name: components(arms, p.name) for p in policies}
retained = {r["policy"]: float(r["net_saving"]) for r in inputs("policy_deterministic.csv")}
# The site bears local programme resources and enjoys origin care offsets. No shared hub or retrieval recharge.
site_rows = []
for site in sites:
    choices = [DeploymentPolicy(p.name, ((site.name, dict(p.assignments)[site.name]),), p.conditional) for p in policies]
    local = evaluate([site], choices)
    for p in policies:
        c = components(local, p.name)
        site_rows.append(dict(site=site.name, policy=p.name, site_net=c["origin"]-c["operating"]-c["capital"]))
write("chhhs-sites.csv", site_rows)

defaults = dict(retrieval=1, receiver=.5, capital=1, operating=1, hub=0, subsidy=.5, funding=0, pass_through=0)
cases = {
    "reference": {}, "retrieval_half": {"retrieval": .5}, "retrieval_external": {"retrieval": 0},
    "destination_external": {"receiver": 0}, "destination_district": {"receiver": 1},
    "capital_state_grant": {"capital": 0}, "operations_state_funded": {"operating": 0},
    "hub_district": {"hub": 1}, "no_travel_subsidy": {"subsidy": 0}, "full_travel_subsidy": {"subsidy": 1},
    "responsive_funding": {"funding": .405}, "responsive_passed_to_district": {"funding": .405, "pass_through": 1},
}
def ledger(c, s):
    site = c["origin"] - c["capital"]*s["capital"] - c["operating"]*s["operating"]
    commonwealth = c["benchmark"]*s["funding"]
    district = (site + c["retrieval"]*s["retrieval"] + c["receiver"]*s["receiver"]
                - c["hub"]*s["hub"] - commonwealth*s["pass_through"])
    health = c["origin"]+c["receiver"]+c["retrieval"]-c["capital"]-c["operating"]-c["hub"]
    subsidy = c["family"]*.4*s["subsidy"]
    return dict(origin_sites=site, district=district, state=health-commonwealth+subsidy,
                health_system=health, societal=health+c["family"], consumer=c["family"]-subsidy,
                commonwealth=commonwealth)
rows = []
for name, override in cases.items():
    for policy, c in parts.items():
        v = ledger(c, defaults | override)
        assert isclose(v["health_system"], retained[policy], abs_tol=1e-7)
        assert isclose(v["state"]+v["commonwealth"]+v["consumer"], v["societal"], abs_tol=1e-7)
        assert isclose(v["societal"], arms[policy]["net_with_family_extension"][0], abs_tol=1e-7)
        if name == "reference":
            assert isclose(v["origin_sites"],sum(r["site_net"] for r in site_rows if r["policy"]==policy),abs_tol=1e-7)
        rows.append(dict(scenario=name, policy=policy, **v))
write("chhhs-perspectives.csv", rows)

# Explore joint extremes; count ties as one winner set. Counts are not probabilities.
corners = []
fields = ["retrieval","receiver","capital","operating","hub","pass_through"]
for values in itertools.product((0,1), repeat=len(fields)):
    s = defaults | dict(zip(fields,values,strict=True)) | {"funding":.405}
    scores = {k:ledger(c,s)["district"] for k,c in parts.items()}
    best = max(scores.values())
    corners.append(dict(**s, preferred="|".join(k for k,v in scores.items() if abs(v-best)<1e-7), district_net=best))
write("chhhs-joint-sensitivity.csv", corners)

# Year-specific programme cash, as distinct from the annualised resource ledger.
cash = []
for r in inputs("policy_budget.csv"):
    c = parts[r["policy"]]
    programme = float(r["capital"])+float(r["cash_running"])-float(r["hub_cash_capacity"])
    cash.append(dict(policy=r["policy"], year=r["year"], fixed_contract_no_care_cash=-programme,
                     variable_retrieval_no_care_cash=c["retrieval"]-programme))
write("chhhs-cash.csv", cash)

# Paired uncertainty analysis at default financing, comparing all six conditional options.
import numpy as np
from scripts.analyse_refinements import sample_v7, load_refinements, optimal_probabilities

rankings = {(r["effect_mode"], r["policy"], r["perspective"]): r
            for r in inputs("policy_rankings.csv") if r["decision_set"] == "conditional_expansion"}
simulated = []
for mode in load_refinements(ROOT / "config/refinements.json")["effect_modes"]:
    x, e = sample_v7(cfg.parameters, cfg.pathways, n=cfg.draws, seed=cfg.seed, effect_mode=mode)
    sampled = evaluate_policies(sites, policies, eligibility_catalogue(sites, allow_hypothetical=True),
                                cfg.parameters, cfg.pathways, cfg.owned_assets, inputs=x,
                                structural_draws=e, activity=ActivitySpec("contacts", 1))
    by_policy = [ledger(components(sampled, p.name, e["hospital_fraction"]), defaults) for p in policies]
    for view in by_policy[0]:
        matrix = np.column_stack([v[view] for v in by_policy])
        probs = optimal_probabilities(matrix)
        for i, policy in enumerate(policies):
            values = matrix[:, i]
            mean = values.mean()
            if view in {"health_system", "societal"}:
                target = rankings[mode, policy.name, "societal_bounded" if view == "societal" else view]
                assert isclose(mean, float(target["expected_net_value"]), abs_tol=1e-7)
                assert isclose(probs[i], float(target["probability_optimal"]), abs_tol=1e-9)
            lo, hi = np.quantile(values, [.025,.975])
            simulated.append(dict(effect_mode=mode, perspective=view, policy=policy.name, mean=mean,
                                  p025=lo, p975=hi, probability_saving=(values>0).mean(),
                                  probability_optimal=probs[i]))
write("chhhs-estimate-sensitivity.csv", simulated)
```
