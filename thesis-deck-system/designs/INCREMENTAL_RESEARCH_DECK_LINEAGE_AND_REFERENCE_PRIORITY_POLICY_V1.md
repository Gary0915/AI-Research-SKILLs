# Incremental Research Deck Lineage and Reference Priority Policy v1

Status: reviewer design guidance

Baseline production commit: `94060296906ad91dd34fac8495578a383e87c26d`

This policy is intentionally narrow. It does not create a new Phase, replace the current thesis template, redesign CP5, or implement a general BuildGraph. It adds the minimum contracts required for a continuously growing research deck and for high-priority body-composition exemplars to influence layout without overriding shell or scientific truth.

## 1. Three independent authorities

### 1.1 Scientific truth authority

```text
canonical scientific objects
→ append-only Ledger
→ cursor materialization
→ SlideSpec
→ presentation semantic projection
```

No presentation exemplar may change scientific truth.

### 1.2 Shell authority

The existing sanitized thesis/professor shell remains authoritative for:

- canvas/aspect ratio;
- master/layout shell;
- background;
- footer/header;
- shell typography and theme roles;
- shell topology and measured recurring shell geometry.

New JDP/TSMC references must not replace this authority.

### 1.3 Body-composition authority

The new high-priority reference lineage may influence:

- normalized content-region composition;
- evidence capacity;
- photo/figure matrix patterns;
- caption placement;
- comparison structure;
- principle/equipment split;
- experiment/result evidence sequencing;
- focus callouts;
- connector semantics;
- information density.

Within equivalent body families, prefer later recurrent examples over earlier ones. Unique older body families remain usable.

## 2. Reference priority

Controlled body-reference order:

1. `JDP-TSMC-2026-0814`
2. `JDP-TSMC-2026-0730`
3. `JDP-TSMC-2026-0617`
4. `JDP-TSMC-2026-0604`
5. `JDP-TSMC-2026-0525`

Priority is ordinal, not a fabricated numeric quality score.

Conflict rule:

```text
same body family + compatible evidence + newer recurring exemplar
→ prefer newer geometry/composition evidence

older unique body family with no later equivalent
→ retain as valid supporting evidence
```

## 3. Canonical research deck vs meeting view

### 3.1 CanonicalResearchDeck

The canonical deck is a persistent research history. It grows over time and preserves accepted historical blocks.

It must not be regenerated conceptually from zero merely because a new experiment/event exists.

### 3.2 MeetingDeckView

A meeting view is an ordered selection over canonical slide identities.

It may include:

- shared context;
- active topic;
- recent results;
- current versioned snapshots;
- next actions.

Omitting a historical slide from a meeting view must not delete or supersede its canonical identity.

## 4. Minimum slide lineage contract

Add a closed contract equivalent to:

```text
SlideLineageRecord
  slide_id
  topic_id
  semantic_parent_id
  source_cursor
  lifecycle_policy
  dependency_hash
  composition_family
  body_reference_evidence_ids[]
  artifact_hash
  accepted_revision
```

All fields must be deterministic and bounded.

No free-form private reference content is stored.

### 4.1 lifecycle_policy

Required enum:

- `historical_stable`
- `append_after_semantic_parent`
- `versioned_snapshot`

Interpretation:

#### historical_stable

Completed evidence/history slide. Reuse while dependency hash is unchanged.

Examples:

- completed literature synthesis supporting an historical decision;
- completed experiment design;
- accepted result;
- accepted discussion/decision record.

#### append_after_semantic_parent

A new scientific slide inserted after the appropriate semantic parent or sibling block, not automatically at the physical end of the deck.

Examples:

- new experiment after its hypothesis/problem block;
- new result after its experiment;
- new production/application blueprint after method justification;
- new validation result after precision-improvement method.

#### versioned_snapshot

A changing current-state representation. New revisions are created while historical revisions remain addressable.

Examples:

- Fishbone;
- research map;
- current system blueprint;
- current integrated summary;
- future plan / schedule;
- progress roadmap;
- threshold/evaluation overview when upstream specification changes.

## 5. Materialization decision contract

Add a deterministic decision record equivalent to:

```text
SlideMaterializationDecision
  slide_id
  previous_artifact_hash
  current_dependency_hash
  previous_dependency_hash
  decision
  reason_code
  output_slide_id
  revision
```

Required decision enum:

- `reuse_exact`
- `append_new`
- `new_revision`
- `rebuild_dependency_changed`
- `exclude_from_meeting_view_only`

### 5.1 reuse_exact

Required when:

```text
same slide identity
AND dependency hash unchanged
AND accepted artifact available
AND no presentation-authority migration explicitly requires rebuild
```

Reuse must include the existing approved figure/native-plan bundle when its scientific input hash is unchanged.

### 5.2 append_new

Required for new child evidence. Insert after semantic parent according to canonical ordering rules.

### 5.3 new_revision

Required for versioned snapshot updates.

Never overwrite historical revision identity.

### 5.4 rebuild_dependency_changed

Required when any authoritative upstream input used by the slide changes.

The rebuild must be atomic across all dependent visible fields, formulas, figures, captions, threshold annotations, and summary statements.

This prevents mixed old/new slides.

### 5.5 exclude_from_meeting_view_only

The canonical slide remains valid but is intentionally omitted from the current meeting export.

## 6. Dependency hashing

The dependency hash must be based only on authoritative inputs actually consumed by the slide.

Examples:

### Result slide

- Result object;
- experiment/output identity;
- evidence refs;
- approved scientific figure input;
- presentation semantic rule;
- body-composition family/version.

### Experiment slide

- Experiment object;
- controls/variables/sample state;
- method/instrument refs;
- experiment-specific figure input;
- composition family/version.

### Threshold/evaluation slide

- dimensional specification;
- equations;
- derived thresholds;
- diagram input;
- explanatory summary fields.

A changed specification must invalidate every downstream field that depends on it.

## 7. Figure reuse policy

Figure reuse follows scientific input identity, not route identity.

```text
same normalized scientific figure input hash
+ same approved figure contract
→ reuse figure/approval/native plan

scientific figure input changed
→ regenerate through existing governed figure chain
```

Do not regenerate unchanged historical figures solely because a later research event was appended.

Do not reuse a representative route-only figure across scientifically different slides.

## 8. Composition family evidence

Add controlled body-composition family identities rather than copying complete source-slide geometry.

Recommended initial family IDs:

- `BCF-TEXT-TOP-DUAL-VISUAL`
- `BCF-PRINCIPLE-EQUIPMENT-SPLIT`
- `BCF-FEASIBILITY-EVIDENCE-MATRIX`
- `BCF-HARDWARE-DESIGN-PROCEDURE`
- `BCF-PHYSICAL-VALIDATION-MATRIX`
- `BCF-TECHNOLOGY-COMPARISON`
- `BCF-PROBLEM-TO-SOLUTION`
- `BCF-REAL-RESULT-VALIDATION`
- `BCF-LITERATURE-VISUAL-MATRIX`
- `BCF-THREE-COLUMN-PHYSICAL-COMPARISON`

These are body families, not replacement A01–A18 archetype IDs.

Mapping model:

```text
canonical archetype
+ semantic stage
+ body-composition family
+ shell authority
→ final SlideCompositionPlan
```

## 9. Body-reference evidence record

Use sanitized local-reference evidence only.

A controlled record may include:

```text
reference_id
reference_date
priority_rank
page_number
body_family_id
normalized_regions
asset_count
text_density_class
caption_pattern
focus_annotation_roles
connector_roles
recurrence_group_id
```

Forbidden:

- raw proprietary slide text;
- speaker notes;
- raw images/media;
- private/local paths;
- user source binaries;
- filenames if the privacy boundary classifies them as sensitive.

## 10. Incremental canonical ordering

Ordering is semantic, not physical append-only.

Minimum rules:

```text
new experiment
→ after owning hypothesis/problem/strategy context and prior experiments in that block

new result
→ after its experiment or previous result sequence

new discussion
→ after the results it integrates

new transition
→ between completed topic and next topic

new versioned snapshot
→ at the point in history when the revision became authoritative
```

Stable earlier slides retain identity even if new material is inserted before/after them in later exports.

## 11. Body reference recency vs accepted historical slides

A new higher-priority body exemplar does **not** automatically force all old accepted slides to rebuild.

Default:

```text
new reference evidence arrives
→ affects new slides and slides already invalidated for scientific reasons
```

Optional visual migration of accepted historical slides requires an explicit migration decision and should normally be deferred until a deliberate deck-wide visual normalization pass.

This preserves speed and historical stability.

## 12. Atomic stale-dependency prevention

A slide must never combine values from different dependency generations.

Add a validation invariant equivalent to:

```text
all visible semantic fields
all derived equations
all scientific figures
all callout labels
all summary values
share the same authoritative dependency generation
```

If one dependency changes and a dependent field is stale:

`FAIL_CLOSED`.

## 13. Performance rule

Incremental deck build is expected to reduce routine work:

```text
new research event
→ evaluate dependency graph only for affected slide lineage records
→ reuse unchanged accepted slide/figure bundles
→ materialize new/invalidated slides
→ assemble meeting/canonical view
```

The final release regression still validates the system, but production deck generation should not unnecessarily rebuild every historical figure/slide.

## 14. Minimum tests

Required test families:

1. append new result after semantic parent;
2. append new topic transition without duplicating old topic slides;
3. unchanged historical slide → `reuse_exact`;
4. unchanged figure scientific-input hash → reuse exact approval/native-plan bundle;
5. versioned Fishbone → `new_revision`, old revision preserved;
6. future-plan update → new snapshot revision;
7. meeting view omits canonical slide without deleting it;
8. upstream threshold specification changes → all dependent fields invalidated;
9. stale old summary with new formula/table → fail;
10. new body-reference priority does not rebuild unchanged historical content by default;
11. latest reference wins only within equivalent body family;
12. shell authority remains unchanged by body exemplar evidence.

## 15. Scope boundary

Do not implement in this bounded closure:

- general repository-wide content-addressed BuildGraph;
- full historical deck migration;
- complete professor Master/Layout physical reconstruction;
- new PPTX backend;
- private exemplar ingestion changes;
- broad Ledger architecture rewrite.

## 16. Acceptance principle

The intended product behavior is:

> The master research deck is a persistent, dependency-aware scientific history. Build each research block once, reuse it while valid, add new evidence where it belongs, version changing overview/state slides, and export meeting-specific views without deleting canonical history.
