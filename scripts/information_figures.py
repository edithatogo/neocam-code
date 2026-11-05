# ruff: ignore[implicit-namespace-package] -- repository script
"""Draw portfolio assignments and the illustrative registry budget."""

import csv
import json
lazy from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
lazy from matplotlib.axes import Axes
lazy from matplotlib.figure import Figure

from scripts.information_geography import map_records

LABEL_LIMIT = 15
SOUTHEAST_WEST = 151
SOUTHEAST_NORTH = -26
CAPE_SOUTH = -16


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def _save(fig: Figure, out: Path, name: str) -> None:
    for ext in ("svg", "png"):
        fig.savefig(out / f"{name}.{ext}", dpi=300, metadata={"Date": None} if ext == "svg" else None)
    plt.close(fig)


def figures(root: Path, out: Path) -> None:
    """Write printable SVG and PNG figures."""
    plt.rcParams["svg.hashsalt"] = "neocam-information"
    coords = {
        r["site"]: (float(r["longitude"]), float(r["latitude"])) for r in _rows(root / "config/voi-facilities.csv")
    }
    assign = _rows(root / "outputs/v13-refinements/policy_assignments.csv")
    elig = {
        (r["portfolio"], r["site"], r["strategy"]): r["status"]
        for r in _rows(root / "outputs/v13-refinements/eligibility.csv")
    }
    fig, axes = plt.subplots(2, 2, figsize=(11, 10), layout="constrained")
    for ax, network in zip(axes.flat, ("pilot", "chhhs", "chhhs_tchhs", "spokes"), strict=True):
        selected = [
            r
            for r in assign
            if r["portfolio"] == network
            and r["policy"] == ("retain_pilot_only" if network == "pilot" else "retain_pilot_expand_obsbot")
        ]
        missing = []
        for r in selected:
            site = r["site"]
            strategy = r["strategy"]
            status = elig[network, site, strategy]
            if site not in coords:
                missing.append(site)
                continue
            lon, lat = coords[site]
            ax.scatter(
                lon,
                lat,
                marker={"panda": "s", "telephone": "o", "obsbot": "^"}[strategy],
                facecolors="none" if status == "hypothetical" else "#34465b",
                edgecolors="black",
                s=38,
            )
            if len(selected) < LABEL_LIMIT:
                ax.annotate(site, (lon, lat), xytext=(4, 2), textcoords="offset points", fontsize=7)
        ax.set_title(network.upper().replace("_", " + "))
        ax.set_xlabel("Longitude (°E)")
        ax.set_ylabel("Latitude (°)")
        ax.grid(alpha=0.2)
        if missing:
            ax.set_xlabel("Unlocated: " + ", ".join(missing))
    fig.suptitle(
        "Regional assignments under conditional OBSBOT expansion\n"
        "Square: incumbent Panda    Triangle: OBSBOT    Circle: telephone    Open: hypothetical"
    )

    _save(fig, out, "assignments")
    _research_plot(out)
    _policy_maps(root, out)
    _decision_diagrams(out)
    _joint_research_plot(out)


def _research_plot(out: Path) -> None:
    registry = _rows(out / "registry.csv")
    fig, axes = plt.subplots(1, 2, figsize=(11, 4), layout="constrained")
    for ax, view in zip(axes, ("health_system", "societal_bounded"), strict=True):
        for network in sorted({r["portfolio"] for r in registry}):
            series = [
                r
                for r in registry
                if r["portfolio"] == network
                and r["perspective"] == view
                and r["endpoint"] == "eventual_transfers"
                and r["design"] == "balanced"
            ]
            ax.plot([1, 2, 3], [float(r["break_even_budget"]) / 1000 for r in series], marker="o", label=network)
        ax.axhline(0, color="black", lw=0.8)
        ax.set_title(view.replace("_", " "))
        ax.set_xlabel("Years recruiting")
        ax.set_ylabel("Break-even study budget (AUD thousands)")
        ax.legend()
    _save(fig, out, "research-value")


def _policy_maps(root: Path, out: Path) -> None:
    records = map_records(root)
    with (out / "map-ledger.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)
    boundary = json.loads((root / "config/voi-queensland.geojson").read_text())["features"][0]["geometry"]
    polygons = boundary["coordinates"] if boundary["type"] == "MultiPolygon" else [boundary["coordinates"]]
    decisions = _rows(out / "decisions.csv")
    for network in sorted({r["portfolio"] for r in records}):
        groups = _geography_groups(records, network)
        fig, axes = plt.subplots(1, len(groups), figsize=(12, 6), squeeze=False, layout="constrained")
        for ax, variants in zip(axes.flat, groups, strict=True):
            _map_panel(ax, variants, polygons)
        evpi = next(
            r["evpi"]
            for r in decisions
            if r["portfolio"] == network
            and r["activity"] == "contacts_1"
            and r["scenario"] == "attenuated"
            and r["decision_set"] == "conditional_expansion"
            and r["perspective"] == "health_system"
        )
        fig.suptitle(
            network.replace("_", " + ") + f" — network-level annual EVPI AUD {float(evpi):,.0f}\n"
            "Filled: reported operation; open: hypothetical. Diamond: shared expansion location; "
            "equipment varies by policy.",
            fontsize=11,
        )
        fig.supxlabel(
            "Site IDs: map-ledger.csv. Boundary: Made with Natural Earth. Facility points: © State of Queensland 2024.",
            fontsize=8,
        )
        fig.canvas.draw()
        fig.set_layout_engine("none")
        for ax, variants in zip(axes.flat, groups, strict=True):
            _label_panel(ax, variants, polygons, network)
        _save(fig, out, "policies-" + network)
    (out / "figure-captions.txt").write_text(
        "Policy maps reconcile all policy/site assignments to eligibility. Shared expansion panels draw "
        "identical geography once; map-ledger.csv gives every device assignment. Filled symbols indicate "
        "reported operation; open symbols indicate hypothetical eligibility. Yarrabah is a labelled locality "
        "without an invented point. Network EVPI is conditional-expansion health-system information value "
        "under the attenuated effect and one contact per episode; it is not a site saving. Coordinates WGS84. "
        "Natural Earth boundaries are public domain. Registry figures show illustrative observable-endpoint "
        "learning with explicit bias, recruitment, collection costs and delay, not identified causal effects.\n"
    )


def _geography_groups(records: list, network: str) -> list:
    groups = {}
    for policy in sorted({r["policy"] for r in records if r["portfolio"] == network}):
        selected = [r for r in records if r["portfolio"] == network and r["policy"] == policy]
        signature = tuple(
            (
                r["site"],
                r["strategy"] == "telephone",
                r["site"] in {"Atherton", "Mareeba", "Innisfail"},
                r["eligibility"],
            )
            for r in selected
        )
        groups.setdefault(signature, []).append(selected)
    return list(groups.values())


def _map_panel(ax: Axes, variants: list, polygons: list) -> None:
    selected = variants[0]
    for polygon in polygons:
        for ring in polygon:
            ax.plot([p[0] for p in ring], [p[1] for p in ring], color="0.65", lw=0.6, zorder=0)
    located = [r for r in selected if r["longitude"]]
    for r in located:
        shared = len(variants) > 1 and r["site"] not in {"Atherton", "Mareeba", "Innisfail"}
        marker = (
            "D"
            if shared
            else {"telephone": "o", "panda": "s", "obsbot": "^", "mobile": "D", "fixed": "P"}[r["strategy"]]
        )
        point = float(r["longitude"]), float(r["latitude"])
        ax.scatter(
            *point,
            marker=marker,
            s=35,
            facecolors="0.2" if r["eligibility"] == "reported_operation" else "white",
            edgecolors="black",
        )
    if located:
        xs = [float(r["longitude"]) for r in located]
        ys = [float(r["latitude"]) for r in located]
        ax.set_xlim(min(xs) - 0.4, max(xs) + 0.4)
        ax.set_ylim(min(ys) - 0.4, max(ys) + 0.4)
    title = (
        "Shared expansion geography\nPanda / OBSBOT / mobile / fixed"
        if len(variants) > 1
        else selected[0]["policy"].replace("retain_pilot_only", "Retain pilot").replace("telephone", "Telephone")
    )
    ax.set_title(title, fontsize=10)
    missing = [r["site_id"] + ": " + r["site"] for r in selected if not r["longitude"]]
    if missing:
        ax.text(0.02, 0.02, "Locality only: " + "; ".join(missing), transform=ax.transAxes, fontsize=7, wrap=True)
    ax.set_xlabel("Longitude (°E)")
    ax.set_ylabel("Latitude (°)")
    ax.grid(alpha=0.15)


def _decision_diagrams(out: Path) -> None:
    decisions = [
        r
        for r in _rows(out / "decisions.csv")
        if r["portfolio"] == "chhhs"
        and r["activity"] == "contacts_1"
        and r["scenario"] == "attenuated"
        and r["perspective"] == "health_system"
    ]
    reported = max(float(r["expected_saving"]) for r in decisions if r["decision_set"] == "reported_operation")
    conditional = max(float(r["expected_saving"]) for r in decisions if r["decision_set"] == "conditional_expansion")
    for name, boxes in (
        (
            "graphical-abstract",
            [
                "Rural neonatal consultation\nTelephone or video + specialist",
                "Clinical course\nImmediate transfer / local care\nPossible delayed rescue",
                (
                    f"CHHHS model: health-system resources\nRetain pilot +AUD {reported:,.0f}/year\n"
                    f"Conditional expansion +AUD {conditional:,.0f}/year"
                ),
                "Research decision\nClarify billing; compare registry value\nProjected outcomes, not observed effects",
            ],
        ),
        (
            "research-process",
            [
                "Before commitment\nClarify billing agreement",
                "Clinical episodes\nLink repeats; compare telephone/video\nRecord timing and eventual disposition",
                "During recruitment\nRetain pilot; collect 1-3 years",
                "After results available\nUpdate policy choice\nPurchase equipment for remaining horizon",
            ],
        ),
    ):
        fig, ax = plt.subplots(figsize=(12, 3), layout="constrained")
        ax.set_xlim(0, 4)
        ax.set_ylim(0, 1)
        ax.axis("off")
        for i, text in enumerate(boxes):
            ax.text(
                i + 0.45,
                0.5,
                text,
                ha="center",
                va="center",
                fontsize=9,
                bbox={
                    "boxstyle": "round,pad=.7",
                    "facecolor": "white",
                    "edgecolor": "black",
                    "linestyle": "--" if i in {2, 3} or (name == "research-process" and i == 0) else "-",
                },
            )
            if i < len(boxes) - 1:
                ax.annotate("", xy=(i + 1.03, 0.5), xytext=(i + 0.87, 0.5), arrowprops={"arrowstyle": "->"})
        ax.set_title(
            "Clinical events and management decisions"
            if name == "graphical-abstract"
            else "Evidence timing and investment decisions",
            fontsize=12,
        )
        ax.text(
            2,
            0.06,
            "Solid: clinical events. Dashed: management/research decisions. "
            "Model projections, not observed clinical effects.",
            ha="center",
            fontsize=8,
        )
        _save(fig, out, name)


def _joint_research_plot(out: Path) -> None:
    rows = _rows(out / "registry-joint-double.csv")
    fig, axes = plt.subplots(2, 2, figsize=(11, 7), layout="constrained")
    for row_axes, view in zip(axes, ("health_system", "societal_bounded"), strict=True):
        for ax, metric in zip(row_axes, ("gross_remaining_value", "break_even_budget"), strict=True):
            for index, network in enumerate(sorted({r["portfolio"] for r in rows})):
                series = [
                    [
                        float(r[metric]) / 1000
                        for r in rows
                        if r["portfolio"] == network
                        and r["perspective"] == view
                        and r["decision_set"] == "conditional_expansion"
                        and r["activity_id"] == "contacts_1"
                        and r["design"] == "balanced"
                        and r["cohort"] == "pilot_existing"
                        and r["endpoint"] == "eventual_transfers"
                        and int(r["recruitment_years"]) == years
                    ]
                    for years in (1, 2, 3)
                ]
                subset = [
                    r
                    for r in rows
                    if r["portfolio"] == network
                    and r["perspective"] == view
                    and r["decision_set"] == "conditional_expansion"
                    and r["activity_id"] == "contacts_1"
                    and r["design"] == "balanced"
                    and r["cohort"] == "pilot_existing"
                    and r["endpoint"] == "eventual_transfers"
                ]
                baseline = {r["policy_before"] for r in subset}
                if len(baseline) != 1:
                    msg = "Research action label requires a stable pre-study mean policy"
                    raise ValueError(msg)
                current = baseline.pop()
                actions = []
                for years in (1, 2, 3):
                    net = np.mean([float(r["net_value"]) for r in subset if int(r["recruitment_years"]) == years])
                    actions.append("E" if net > 0 else "P" if current == "retain_pilot_only" else "A")
                ax.errorbar(
                    [1, 2, 3],
                    [sum(a) / len(a) for a in series],
                    yerr=[3.182446 * float(np.std(a, ddof=1)) / len(a) ** 0.5 for a in series],
                    marker=("o", "s", "^", "D")[index],
                    linestyle=("-", "--", ":", "-.")[index],
                    label=network + " [" + "/".join(actions) + "]",
                    capsize=3,
                )
            ax.axhline(0, color="black", lw=0.6)
            ax.set_title(view.replace("_", " ") + " / " + metric.replace("_", " "), fontsize=10)
            ax.set_xlabel("Years recruiting (findings then become available)")
            ax.set_ylabel("AUD thousands")
            ax.legend(fontsize=8)
    fig.suptitle(
        "Projected registry value: joint model uncertainty, five-year horizon\n"
        "Equal attenuated/null scenario prior; observable endpoint under stated bias assumptions\n"
        "Actions at 1/2/3 years: E collect evidence; P retain pilot; A adopt now. Conditional point estimates.",
        fontsize=11,
    )
    _save(fig, out, "research-value-joint")
    billing = [r for r in _rows(out / "registry-cash-policy-consistent.csv") if r["grid_points_per_dimension"] == "33"]
    fig, axes = plt.subplots(1, 2, figsize=(10, 4), layout="constrained")
    for ax, known in zip(axes, ("False", "True"), strict=True):
        series = [r for r in billing if r["billing_known"] == known]
        for metric in ("gross_sample_value", "break_even_budget"):
            ax.plot(
                [float(r["years"]) for r in series],
                [float(r[metric]) for r in series],
                marker="o",
                label=metric.replace("_", " "),
            )
        ax.axhline(0, color="black", lw=0.6)
        ax.set_title("Billing " + ("clarified" if known == "True" else "uncertain"))
        ax.set_xlabel("Years recruiting")
        ax.set_ylabel("CHHHS cash AUD over five years")
        ax.legend(fontsize=8)
    fig.suptitle(
        "Conditional district cash scenario: registry before/after billing clarification\n"
        "Fixed-wing liability known; cash-capture priors; point programme costs; legacy known-baseline signal",
        fontsize=10,
    )
    _save(fig, out, "research-billing")


def _site_labels(ax: Axes, selected: list) -> None:
    boxes = []
    renderer = ax.figure.canvas.get_renderer()
    bounds = ax.get_window_extent()
    for row in selected:
        if not row["longitude"]:
            continue
        point = float(row["longitude"]), float(row["latitude"])
        placed = False
        for radius in (7, 15, 24, 34, 46, 60, 78, 100, 125):
            for dx, dy in (
                (radius, radius),
                (-radius, radius),
                (radius, -radius),
                (-radius, -radius),
                (0, radius),
                (0, -radius),
                (radius, 0),
                (-radius, 0),
            ):
                text = ax.annotate(
                    row["site_id"],
                    point,
                    xytext=(dx, dy),
                    textcoords="offset points",
                    fontsize=8,
                    ha="center",
                    va="center",
                    bbox={"facecolor": "white", "edgecolor": "none", "pad": 0.4},
                    arrowprops={"arrowstyle": "-", "lw": 0.4},
                )
                text.update_positions(renderer)
                text.update_bbox_position_size(renderer)
                box = text.get_bbox_patch().get_window_extent(renderer).expanded(1.05, 1.05)
                if (
                    bounds.contains(box.x0, box.y0)
                    and bounds.contains(box.x1, box.y1)
                    and not any(box.overlaps(b) for b in boxes)
                ):
                    boxes.append(box)
                    placed = True
                    break
                text.remove()
            if placed:
                break
        if not placed:
            msg = "Cannot place nonoverlapping site label: " + row["site"]
            raise ValueError(msg)


def _label_panel(ax: Axes, variants: list, polygons: list, network: str) -> None:
    selected = variants[0]
    southeast = [
        r
        for r in selected
        if r["longitude"] and float(r["longitude"]) > SOUTHEAST_WEST and float(r["latitude"]) < SOUTHEAST_NORTH
    ]
    if network == "chhhs_tchhs":
        cape = [r for r in selected if r["latitude"] and float(r["latitude"]) > CAPE_SOUTH]
        inset = ax.inset_axes([0.04, 0.13, 0.46, 0.38])
        _map_panel(inset, [[r for r in v if r["site"] in {c["site"] for c in cape}] for v in variants], polygons)
        inset.set_title("")
        inset.set_title("Torres and Cape (inset)", fontsize=7, loc="right", pad=2)
        inset.tick_params(labelsize=6)
        inset.set_xlabel("")
        inset.set_ylabel("")
        ax.figure.canvas.draw()
        _site_labels(inset, cape)
        _site_labels(ax, selected)
        return
    if network != "spokes" or not southeast:
        _site_labels(ax, selected)
        return
    inset = ax.inset_axes([0.03, 0.12, 0.46, 0.32])
    _map_panel(
        inset, [[r for r in variant if r["site"] in {s["site"] for s in southeast}] for variant in variants], polygons
    )
    inset.set_title("")
    inset.set_title("South-east spokes (inset)", fontsize=7, loc="right", pad=2)
    inset.tick_params(labelsize=6)
    inset.set_xlabel("")
    inset.set_ylabel("")
    ax.figure.canvas.draw()
    _site_labels(ax, [r for r in selected if r not in southeast])
    _site_labels(inset, southeast)
