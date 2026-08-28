"""Provider-neutral, privacy-aware image review capability preflight."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ImageReviewPreflight:
    status: str
    reason: str
    professor_fidelity_status: str


def preflight_image_review(provider: dict, *, private_reference: bool) -> ImageReviewPreflight:
    required = {"provider_id", "image_capable", "hash_binding_supported", "private_content_allowed", "approved_for_private_exemplars", "egress_mode", "retention_class", "supported_input_forms"}
    if set(provider) != required:
        return ImageReviewPreflight("blocked_visual_review", "provider capability contract is incomplete", "blocked_visual_review")
    if not isinstance(provider["provider_id"], str) or not provider["image_capable"]:
        return ImageReviewPreflight("blocked_visual_review", "provider is not image capable", "blocked_visual_review")
    if not provider["hash_binding_supported"]:
        return ImageReviewPreflight("blocked_visual_review", "provider cannot bind render hashes", "blocked_visual_review")
    if not private_reference:
        if "repository_relative_path" not in provider["supported_input_forms"]:
            return ImageReviewPreflight("blocked_visual_review", "provider lacks an authorized sanitized input form", "blocked_visual_review")
        return ImageReviewPreflight("approved_sanitized_only", "sanitized render review is allowed", "blocked_visual_review")
    if not provider["private_content_allowed"] or not provider["approved_for_private_exemplars"]:
        return ImageReviewPreflight("blocked_visual_review", "private authorization is absent", "blocked_visual_review")
    if provider["egress_mode"] not in {"local_only", "approved_private_enclave"}:
        return ImageReviewPreflight("blocked_visual_review", "provider egress mode is not permitted", "blocked_visual_review")
    if provider["retention_class"] not in {"ephemeral", "approved_private_retention"}:
        return ImageReviewPreflight("blocked_visual_review", "provider retention policy is not permitted", "blocked_visual_review")
    if "local_private_handle" not in provider["supported_input_forms"]:
        return ImageReviewPreflight("blocked_visual_review", "provider lacks an authorized private input form", "blocked_visual_review")
    return ImageReviewPreflight("approved", "private review capability is approved", "pending_private_reference_review")
