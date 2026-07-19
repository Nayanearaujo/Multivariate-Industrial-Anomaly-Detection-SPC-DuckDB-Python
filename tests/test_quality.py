import pandas as pd

from chemical_process_analytics.quality import run_integrity


def test_run_integrity_detects_complete_and_incomplete_runs() -> None:
    frame = pd.DataFrame(
        {
            "split": ["train"] * 5 + ["train"] * 4,
            "simulationRun": [1] * 5 + [2] * 4,
            "sample": [1, 2, 3, 4, 5, 1, 2, 4, 5],
        }
    )
    result = run_integrity(frame, {"train": 5}).set_index("simulation_run")
    assert bool(result.loc[1, "is_complete"])
    assert not bool(result.loc[2, "is_complete"])
    assert result.loc[2, "missing_sequence_steps"] == 1
