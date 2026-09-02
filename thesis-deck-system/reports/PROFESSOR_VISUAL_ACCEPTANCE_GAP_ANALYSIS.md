# Professor Visual Acceptance Gap Analysis

Status: `gap_analysis_complete`
Scope: read-only baseline assessment before candidate-code changes.
Baseline: `72ca8ada45119f5a2adad814b31f919f52b22099`

## Authority and boundary

The review deck retains the asymmetric authority already established by the
system: PSP-001 owns the thesis shell, Group Meeting evidence governs
experiment/result/problem/decision body composition, and TSMC/JDP evidence
governs introduction, literature, system, and strategy bodies.  Neither body
reference may replace the shell.  This assessment uses repository-tracked and
sanitized artifacts only; no private presentation source is needed.

## Baseline strengths

- PSP-001 provides measured 16:9 canvas, title, footer, and page-number
  geometry. Its body safe region is explicitly system-owned rather than
  misrepresented as professor-measured evidence.
- PTP-001 provides sixteen controlled typography roles and a no-uncontrolled-
  shrink policy, but its current role sizes are an engineering baseline rather
  than proof of projection-ready Chinese research typography.
- Ten body recipes, source-qualified body references, sixteen eligible
  candidates, and six multi-candidate cases provide a stable planner base.
- Existing reverse audits prove structural geometry, shell separation,
  typography-role control, style control, and occupancy. They do not prove
  human visual acceptance.

## Material gaps

The candidate deck is still dominated by generic planning labels instead of
production-length Traditional-Chinese research content. It has not yet shown
source-closed experiment setup, measurement-chain, literature, fishbone,
mechanism, result-discussion, comparison, or Go/No-Go fixtures. Nor does it
yet measure family-specific visual dominance, dashboard/card drift, realistic
caption/citation/table density, or meaningful A/B/C composition differences.

The resulting work will therefore add a review-only calibration layer rather
than reconstruct the planner or migrate historical slides. Each fixture will
retain canonical source references and dependency hashes. Unknown or
unmeasured facts will remain TBC/待驗證/尚未量測 or explicit
`synthetic_non_evidence`; they will not become measured results.

## Required calibration decisions

| Area | Authority | Planned proof |
| --- | --- | --- |
| Shell | PSP-001 | Preserve shell; audit no body override. |
| Titles and language | Research instructions + PTP-001 | Short Traditional-Chinese titles; mixed technical terms only where needed. |
| Experiment and results | Group Meeting body evidence | One dominant setup/plot and limited contextual decision content. |
| Literature and system | TSMC/JDP body evidence | Dominant source-bound schematic/figure, compact take-home, citation strip. |
| Typography | Source-supported targets + calibrated profile | Title 28–32 pt; main body 18–22 pt; table/main content >=16 pt; caption/citation >=10 pt. |
| Visual drift | System-calibrated prohibition | Reject dashboard/card grids, fixed four-box footer, giant debug labels, and fake variants. |
| Acceptance | Human reviewer | Manifest stores null selection and `pending`; no automatic human lock. |

The detailed, machine-readable assessment is
`thesis-deck-system/artifacts/phase3/professor-visual-acceptance-gap-matrix.json`.
