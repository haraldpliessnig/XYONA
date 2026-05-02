# XYONA Review Template

Use this format for technical reviews. Keep it short, reproducible, and falsifiable.

## Review Contract

- Review code first. Do not infer defects without concrete code evidence.
- Do not call something a blocker without a counter-check and a concrete verification path.
- Separate hard defects, likely risks, product semantics, and unverified hypotheses.
- If confidence is limited, label it explicitly instead of overstating certainty.

## Meta

- Review target:
- Scope/changeset:
- Review type: Architecture / Bugfix / UI / Audio / State / Build
- Reviewer:
- Date:
- Commit / bundle:

## Final Classification

- Hard defects:
- Likely risks:
- Product/semantics issues:
- Unverified hypotheses:

## Executive Summary

- ...

## Focus

- [ ] Audio RT-safety (no allocs/locks in audio thread)
- [ ] GraphPlan / PDC / CommitRouter / MonitorRtParams
- [ ] Parameter flow (ParameterCenter -> ParamUpdateBridge -> Queue)
- [ ] State / persistence (ProjectState, ValueTree)
- [ ] UI / theme tokens (CoreTokens, Ui* controls, no hardcodes)
- [ ] Rendering (CPU-first path, optional GPU / Skia experiments)
- [ ] Help / i18n (HelpCenter, gettext)
- [ ] Build / CMake / vcpkg
- [ ] Tests (unit, integration, audio)

## Findings

Create one block per finding. Use the exact fields below.

### Finding

- Severity: Blocker / High / Medium / Low / Semantics
- Confidence: High / Medium / Low
- Claim:
- Evidence:
- Counter-check:
- Verification path:
- Impact:
- Recommendation:

### Finding

- Severity:
- Confidence:
- Claim:
- Evidence:
- Counter-check:
- Verification path:
- Impact:
- Recommendation:

## Tests / Verification

- Built locally:
- Tests executed:
- Repro steps:
- Expected:
- Observed:

## Risk / Regression

- Risk:
- Affected areas:
- Migration / compatibility:
- Rollback:

## Docs / Follow-ups

- Docs updates:
- TODOs / follow-ups:
