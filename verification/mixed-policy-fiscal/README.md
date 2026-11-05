# Retrieval payer sensitivity

From the repository root, run the following with the frozen Python 3.15.1 environment. It reproduces retrieval-payers.csv. Currency is modelled annual AUD relative to telephone, using the deterministic reference parameters for each retained activity scenario. Positive values are avoided marginal retrieval resources assigned to the named payer, conditional on its liability varying with those resources. The retained parameter audit identifies the CHHHS retrieval share as an assumption. A fixed contract could yield zero in-year expenditure change even with a positive resource offset.

The default assigns all retrievals in the selected portfolio to CHHHS, including retrievals from other origins in wider portfolios. Alternatives assign all to a separate retrieval funder, all to the receiving organisation, or half each to CHHHS and the retrieval funder. These are mutually exclusive accounting roles within each scenario. The receiving organisation's identity is unknown. The split illustrates linear sensitivity, without estimating a contract rate. Each row partitions one component of the health-system result. Do not add the allocation to that result.

```python
import csv
import math
from pathlib import Path

from scripts.analyse_refinements import (
    ROOT, ActivitySpec, eligibility_catalogue, evaluate_policies,
    load_configuration, load_refinements, policy_catalogue, portfolio,
)

config = load_configuration(ROOT)
activity_rows = load_refinements(ROOT / "config/refinements.json")["activity_scenarios"]
with Path("outputs/v13-refinements/policy_deterministic.csv").open() as f:
    retained = {(r["portfolio"], r["activity_id"], r["policy"]): float(r["net_saving"])
                for r in csv.DictReader(f)}
shares = {
    "chhhs_default": (1, 0, 0),
    "retrieval_funder": (0, 1, 0),
    "destination": (0, 0, 1),
    "shared": (0.5, 0.5, 0),
}
rows = []
seen = set()
for network in config.portfolios:
    sites = portfolio(network)
    for a in activity_rows:
        arms = evaluate_policies(
            sites, policy_catalogue(sites), eligibility_catalogue(sites, allow_hypothetical=True),
            config.parameters, config.pathways, config.owned_assets,
            activity=ActivitySpec(a["activity_basis"], a["contacts_per_episode"]),
        )
        for policy, arm in arms.items():
            key = network, a["id"], policy
            seen.add(key)
            assert math.isclose(arm["net_saving"][0], retained[key], abs_tol=1e-7)
            offset = float(arm["transport_resource_benefit"][0])
            assert math.isclose(offset, arms["telephone"]["transport_resource_cost"][0]
                                - arm["transport_resource_cost"][0], abs_tol=1e-7)
            for scenario, weights in shares.items():
                amounts = [offset * w for w in weights]
                assert math.isclose(sum(amounts), offset, abs_tol=1e-7)
                rows.append((*key, scenario, offset, *amounts))
assert seen == set(retained)
with Path("verification/mixed-policy-fiscal/retrieval-payers.csv").open("w", newline="") as f:
    writer = csv.writer(f, lineterminator="\n")
    writer.writerow(["portfolio", "activity_id", "policy", "payer_scenario",
                     "system_retrieval_offset", "chhhs", "retrieval_funder", "destination"])
    writer.writerows(rows)
```
