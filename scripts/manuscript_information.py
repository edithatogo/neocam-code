# ruff: ignore[implicit-namespace-package] -- repository scripts are a namespace package
"""Scenario value of contract clarification and an informative registry signal (AUD)."""

import csv
import hashlib
import json
from importlib.metadata import version
from pathlib import Path

import numpy as np
from voiage.methods.basic import evpi

ROOT = Path(__file__).resolve().parents[1]
FISCAL = ROOT / "verification/mixed-policy-fiscal"
cash = FISCAL / "chhhs-cash.csv"
effects = FISCAL / "chhhs-estimate-sensitivity.csv"
with cash.open() as stream:
    rows = list(csv.DictReader(stream))
with effects.open() as stream:
    estimates = list(csv.DictReader(stream))
policies = list(dict.fromkeys(row["policy"] for row in rows))
billing = {}
for horizon in (3, 5):
    balances = np.array([
        [sum(float(r[key]) for r in rows if r["policy"] == p and int(r["year"]) <= horizon) for p in policies]
        for key in ("fixed_contract_no_care_cash", "variable_retrieval_no_care_cash")
    ])
    for quarters in (1, 2, 3):
        states = np.repeat(balances, [4 - quarters, quarters], axis=0)
        billing[f"{horizon}y_p{quarters * 25}"] = evpi(states)
# Equal prior on attenuated and null. Binary registry signal has symmetric accuracy.
means = np.array([
    [
        next(
            float(r["mean"])
            for r in estimates
            if r["policy"] == p and r["effect_mode"] == mode and r["perspective"] == "district"
        )
        for p in policies
    ]
    for mode in ("attenuated", "null")
])
registry = {}
for accuracy in (0.5, 0.7, 0.9, 1.0):
    posterior = accuracy * means + (1 - accuracy) * means[::-1]
    value = evpi(posterior)
    if not np.isclose(value, posterior.max(axis=1).mean() - means.mean(axis=0).max()):
        msg = "Registry signal valuation failed independent reconstruction"
        raise ValueError(msg)
    registry[str(accuracy)] = value
paths = [Path(__file__).resolve(), cash, effects]
hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
result = {"inputs_and_script": hashes, "voiage": version("voiage"), "billing": billing, "registry": registry}
revision = hashlib.sha256(json.dumps(result, sort_keys=True).encode()).hexdigest()[:12]
out = ROOT / "verification/manuscript-information"
out.mkdir(exist_ok=True)
(out / f"{revision}.json").write_text(json.dumps(result, indent=2) + "\n")
