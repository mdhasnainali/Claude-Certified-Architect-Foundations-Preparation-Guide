# 4_5_sla.py — Python 3.13+, offline. How often must you submit batches to meet a 30-hour SLA?
SLA_H, BATCH_MAX_H = (
    30,
    24,
)  # promise to the business · worst-case batch processing time

for window_h in (2, 4, 6, 8):
    worst = (
        window_h + BATCH_MAX_H
    )  # a document arriving just after a submission waits a full window
    status = "OK" if worst < SLA_H else "no margin" if worst == SLA_H else "MISSES SLA"
    print(f"submit every {window_h} h → worst case {worst} h → {status}")
