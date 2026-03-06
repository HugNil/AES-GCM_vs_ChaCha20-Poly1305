import json


def make_json_message_exact_size(target_size: int) -> bytes:
    """
    Create a compact JSON message with exactly target_size bytes (UTF-8).
    Only the 'payload' field size changes.
    """

    if target_size < 20:
        raise ValueError("Target size too small for JSON structure.")

    base_obj = {
        "type": "test",
        "payload": ""
    }

    # Serialize once to measure overhead without payload
    base_json = json.dumps(base_obj, separators=(",", ":")).encode("utf-8")
    overhead = len(base_json)

    # payload characters are ASCII → 1 byte each
    payload_len = target_size - overhead

    if payload_len < 0:
        raise ValueError("Target size smaller than JSON overhead.")

    base_obj["payload"] = "A" * payload_len

    final_json = json.dumps(base_obj, separators=(",", ":")).encode("utf-8")

    # Safety check
    if len(final_json) != target_size:
        raise RuntimeError(
            f"Size mismatch: expected {target_size}, got {len(final_json)}"
        )

    return final_json # Return the JSON message as bytes