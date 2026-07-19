import math

import pandas as pd

from chemical_process_analytics.kpis import (
    alarm_burden_per_100_hours,
    confirm_persistent_alerts,
    false_alarm_rate,
    fault_detection_rate,
    label_alert_events,
    median_detection_delay,
    process_stability_rate,
)


def test_persistence_and_event_labelling() -> None:
    raw = pd.Series([False, True, True, False, True, True, True, False])
    confirmed = confirm_persistent_alerts(raw, minimum_samples=3)
    assert confirmed.tolist() == [False, False, False, False, False, False, True, False]
    assert label_alert_events(confirmed).tolist() == [0, 0, 0, 0, 0, 0, 1, 0]


def test_decision_kpis() -> None:
    frame = pd.DataFrame(
        {
            "faultNumber": [0, 0, 1, 1, 1, 1, 2, 2],
            "simulationRun": [1, 1, 1, 1, 2, 2, 1, 1],
            "sample": [1, 2, 5, 6, 5, 6, 5, 6],
            "confirmed_alert": [False, True, False, True, False, False, True, True],
        }
    )
    assert math.isclose(fault_detection_rate(frame), 2 / 3)
    assert median_detection_delay(frame, onset_sample=5) == 1.5
    assert false_alarm_rate(frame, normal_mask=frame["faultNumber"].eq(0)) == 0.5
    assert process_stability_rate(frame) == 0.5


def test_alarm_burden() -> None:
    frame = pd.DataFrame({"alert_event_id": [0, 1, 1, 0, 2, 0]})
    assert math.isclose(alarm_burden_per_100_hours(frame), 666.6666666666667)
