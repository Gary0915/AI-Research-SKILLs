# Phase 3 Final Visual Composition Closure Design

## Purpose

Transform the CP5-I structural acceptance deck into a fresh, source-bound
scientific presentation without changing the CP5 architecture or opening any
private exemplar.  `PythonPptxAssembler` remains the sole public PPTX writer.

## Authority and projection

Canonical result/evidence/experiment state is authoritative.  A deterministic
presentation semantic projection derives visible fields, notes-only fields,
deduplication decisions, semantic layout role, and figure placement from the
committed Phase 2 SlideSpec and materialized state.  It never mutates Ledger
or source SlideSpecs.

Result rendering is bound to an explicit result trace.  Each visible quantity,
central value, uncertainty, unit, experiment output, and takeaway must match
the materialized source result.  Multi-metric results retain each supported
metric; unsupported quantitative values are not invented.

## Composition

The final deck has a fresh metadata cover and the existing nineteen H001/H002
source slides.  Each slide receives a semantic layout role and archetype,
title/text/primary-visual regions, a style bundle, and a presentation rule.
Fishbone, experiment, mechanism, result, and comparison figures are placed as
primary visuals only through their approved/native-plan-or-explicit-fallback
authority.  Internal IDs, serialized structures, cursors, and provenance move
to speaker notes unless explicitly scientific visible labels.

## Verification

Execution-derived audits prove semantic fidelity, layout/archetype binding,
and governed figure placement.  Structural package QA, optional deterministic
render QA, privacy/package scans, and release gates remain independent.  A
blocked renderer, image-capable review, or native PowerPoint environment is
reported truthfully and cannot become a PASS through structural validity.

## Scope boundaries

No CP5-J, second PPTX backend, private source access, production scientific
invention, template binary reuse, or new external architecture is allowed.
