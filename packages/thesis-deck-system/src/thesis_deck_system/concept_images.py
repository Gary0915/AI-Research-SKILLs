"""Abstract conceptual-image provider boundary; never a scientific evidence source."""

from __future__ import annotations


def validate_concept_provider(provider: dict) -> list[str]:
    required = {"provider_id", "image_capable", "generation_provenance_required", "allowed_evidence_statuses"}
    if set(provider) != required:
        return ["P3-CONCEPT-PROVIDER-CONTRACT"]
    if not isinstance(provider["provider_id"], str) or not provider["image_capable"]:
        return ["P3-CONCEPT-PROVIDER-CAPABILITY"]
    if provider["generation_provenance_required"] is not True:
        return ["P3-CONCEPT-PROVENANCE"]
    if provider["allowed_evidence_statuses"] != ["non_evidence"]:
        return ["P3-CONCEPT-EVIDENCE-STATUS"]
    return []
