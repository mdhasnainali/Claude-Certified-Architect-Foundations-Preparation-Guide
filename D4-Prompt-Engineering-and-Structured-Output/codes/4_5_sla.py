# 4_5_sla.py — Python 3.13+, offline. How often must you submit batches to meet a 30-hour SLA?
SLA_HOURS = 30  # promise to the business
BATCH_MAX_HOURS = 24  # worst-case batch processing time

for window_hours in (2, 4, 6, 8):
    # a document arriving just after a submission waits a full window
    worst_case_hours = window_hours + BATCH_MAX_HOURS
    if worst_case_hours < SLA_HOURS:
        status = "OK"
    elif worst_case_hours == SLA_HOURS:
        status = "no margin"
    else:
        status = "MISSES SLA"
    print(f"submit every {window_hours} h → worst case {worst_case_hours} h → {status}")
