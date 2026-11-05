"""Exact finite-state and endpoint-likelihood oracles for registry information."""

from pathlib import Path

import numpy as np
import pytest

from scripts.registry_joint import (
    RegistryRun,
    StudyDesign,
    binomial_mass,
    conditional_states,
    contrast_likelihood,
    finite_information,
    research_budget,
    study_counts,
)
from src.activity import ActivitySpec
from src.perspectives_v7 import cost_only_evpi


def test_uninformative_and_perfect_registry_signals() -> None:
    payoffs = np.array([[10.0, 0.0], [0.0, 10.0]])
    assert finite_information(payoffs, np.full((2, 3), 1 / 3)) == pytest.approx(0)
    assert finite_information(payoffs, np.eye(2)) == pytest.approx(5)


def test_contrast_information_is_bounded_and_grows_with_recruitment() -> None:
    payoffs = np.array([[10.0, 0.0], [0.0, 10.0]])
    risks = np.array([[0.5, 0.1], [0.5, 0.5]])
    short = finite_information(payoffs, contrast_likelihood(risks, 10, 10, 0))
    long = finite_information(payoffs, contrast_likelihood(risks, 1000, 1000, 0))
    assert 0 <= short <= long <= 5 + 1e-7
    assert long == pytest.approx(5, abs=1e-5)


def test_findings_after_horizon_cannot_change_prior_decisions() -> None:
    gross, delay, budget = research_budget(100, np.array([0.0, 5.0]), 0, 3, 2)
    assert gross == 0
    assert delay == 10
    assert budget == -10


def test_unlearned_cost_uncertainty_is_integrated_not_identified_by_signal() -> None:
    payoffs = np.array([[8.0, 0.0], [12.0, 0.0], [0.0, 8.0], [0.0, 12.0]])
    signal = np.repeat(np.eye(2), 2, axis=0)
    conditional = payoffs.reshape(2, 2, 2).mean(axis=1)
    assert finite_information(payoffs, signal) == pytest.approx(finite_information(conditional, np.eye(2)))


def test_count_likelihood_exact_case_and_extreme_probabilities() -> None:
    np.testing.assert_allclose(binomial_mass(2, 0.5), [0.25, 0.5, 0.25])
    np.testing.assert_allclose(binomial_mass(2, 0), [1, 0, 0])
    np.testing.assert_allclose(binomial_mass(2, 1), [0, 0, 1])
    assert binomial_mass(1000, 0.001).sum() == pytest.approx(1, abs=1e-10)


def test_conditional_model_projection_integrates_nuisance_draws() -> None:

    root = Path(__file__).resolve().parents[1]
    state = conditional_states(root, "pilot", 0, RegistryRun(4, 8, ActivitySpec(), "contacts_1"), conditional=False)
    assert state.values["health_system"].shape == (8, 2)
    assert {cohort for cohort, _ in state.risks} == {"pilot_existing"}
    for view, values in state.values.items():
        assert cost_only_evpi(values) <= state.bounds[view] + 1e-7


def test_odd_completed_count_is_not_lost_between_arms() -> None:
    counts = study_counts(37.56686331726971, 2, StudyDesign("balanced", 0.8, 0.95, 0.5, 0.02, 1))
    assert counts["completed"] == 57
    assert counts["effective_control_n"] + counts["effective_video_n"] == 57
