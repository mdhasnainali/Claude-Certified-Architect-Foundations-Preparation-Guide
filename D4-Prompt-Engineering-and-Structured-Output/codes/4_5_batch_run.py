# 4_5_batch_run.py — anthropic 2.13. Run: uv run --with anthropic python 4_5_batch_run.py  (takes minutes, up to 24 h)
import time
import anthropic
from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
from anthropic.types.messages.batch_create_params import Request

client = anthropic.Anthropic()
DOCS = {
    "inv-001": "Invoice A. Hosting $120. Total $120.",
    "inv-002": "Invoice B. Support $80. Total $80.",
    "inv-003": "Invoice C. Licences $1,440. Total $1,440.",
}


def request(doc_id: str, text: str) -> Request:
    return Request(
        custom_id=doc_id,
        params=MessageCreateParamsNonStreaming(
            model="claude-haiku-5-5",
            max_tokens=1000,
            messages=[
                {
                    "role": "user",
                    "content": f"Reply with the invoice total as a plain number.\n{text}",
                }
            ],
        ),
    )


batch = client.messages.batches.create(
    requests=[request(k, v) for k, v in DOCS.items()]
)
while (
    batch := client.messages.batches.retrieve(batch.id)
).processing_status != "ended":
    time.sleep(60)  # most batches end within 1 hour; the hard limit is 24 hours

failed = []
for res in client.messages.batches.results(
    batch.id
):  # results arrive in ANY order → key by custom_id
    if res.result.type == "succeeded":
        print(
            res.custom_id,
            "→",
            next(b.text for b in res.result.message.content if b.type == "text"),
        )
    else:
        failed.append(res.custom_id)  # errored / expired / canceled
print("resubmit only these:", failed)
