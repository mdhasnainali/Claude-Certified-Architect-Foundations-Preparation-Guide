# 4_5_batch_run.py — anthropic 2.13. Run: uv run --with anthropic python 4_5_batch_run.py  (takes minutes, up to 24 h)
import time
import anthropic
from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
from anthropic.types.messages.batch_create_params import Request

client = anthropic.Anthropic()
INVOICES = {
    "inv-001": "Invoice A. Hosting $120. Total $120.",
    "inv-002": "Invoice B. Support $80. Total $80.",
    "inv-003": "Invoice C. Licences $1,440. Total $1,440.",
}


def build_request(doc_id: str, text: str) -> Request:
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
    requests=[build_request(doc_id, text) for doc_id, text in INVOICES.items()]
)
while (
    batch := client.messages.batches.retrieve(batch.id)
).processing_status != "ended":
    time.sleep(60)  # most batches end within 1 hour; the hard limit is 24 hours

failed_ids = []
# results arrive in ANY order → match them by custom_id
for entry in client.messages.batches.results(batch.id):
    if entry.result.type == "succeeded":
        print(
            entry.custom_id,
            "→",
            next(
                block.text
                for block in entry.result.message.content
                if block.type == "text"
            ),
        )
    else:
        failed_ids.append(entry.custom_id)  # errored / expired / canceled
print("resubmit only these:", failed_ids)
