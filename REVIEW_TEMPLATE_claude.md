# XYONA Review Template (Claude v2)

Use this format for technical reviews. Keep it short, reproducible, and falsifiable.

## Review Rules (read before starting — these are project rules, not suggestions)

You are reviewing a mature, professional C++ codebase written by experienced engineers.
Apply these rules strictly before assigning any severity:

1. **Assume intent.** Unconventional patterns are likely deliberate. Do not flag them without concrete evidence of breakage.
2. **Blocker requires proof.** A Blocker must have a direct, traceable path to crash / data loss / RT-safety violation / security issue. Theoretical risk does not qualify.
3. **One finding per issue.** Do not list the same concern under multiple findings or severities.
4. **Evidence-only findings.** If you cannot confirm a defect from the provided code, it does not belong in Findings. File it under *Unverified Hypotheses* instead.
5. **Active downgrade check.** For every Finding, actively consider the next-lower severity and document in *Severity justification* why it does not fit. If you cannot articulate a concrete reason, use the lower severity.
6. **Confidence must match evidence.** High confidence requires direct code evidence. Anything inferred or assumed is Medium or Low confidence.
7. **Do not invent risk.** Do not escalate severity because a pattern "could" be misused in a future scenario not present in the current changeset.

### Verification rules (binding — apply during evidence gathering, not at the end)

These rules exist because the most common review failures are missed
bypasses, missed asymmetries between parallel pipelines, and hallucinated
test gaps. They do not weaken defect detection — they sharpen it.

8. **Negative claims require a grep.** Any finding or paragraph of the form
   *"no test exists"*, *"no caller exists"*, *"no documentation exists"*,
   *"never invoked"* must cite the exact grep / search command and its empty
   output. Never accept a sub-agent's negative claim verbatim — re-run the
   search yourself. If you did not grep, the only allowed phrasing is
   *"not verified"*, and the concern goes into *Unverified Hypotheses*,
   not Findings.

9. **Trace the symbol, not the definition.** For every contract enum,
   service, policy, or eligibility purpose introduced or modified by the
   changeset (e.g. `ParamTargetPurpose::Recording`, `ParamSmoothingKind::HostRamp`,
   `ParamModulationMode::*`), grep all call sites and produce a one-line
   inventory: *symbol → producers / consumers / values actually passed*.
   - Unused enum values are a smoking gun.
   - Single-call-site services are a smoking gun.
   - Asymmetric purpose usage across parallel consumers is a smoking gun.
   These are likely **Bypass** findings (see defect-form classification),
   not theoretical concerns. Do not downgrade them on the assumption of
   "deliberate".

10. **Symmetry table for parallel consumers.** When the changeset describes
    N consumers of the same data or contract (e.g. Recorder / Playback /
    PreparedRuntime reading the same lanes; realtime vs. offline render
    paths; load vs. save persistence), produce a small explicit table
    *consumer × validation layer × parameters used* before writing any
    finding about that area. Findings on parallel pipelines must cite a
    row of that table. Asymmetries (one consumer enforces a check, the
    others don't) are typically **Medium**, not Low — surface them.

11. **Read at least two call sites for every central service.** Reading
    only the header / definition is insufficient. For every service or
    policy that the changeset claims is "enforced everywhere", open
    a minimum of two distinct call sites and verify the arguments
    actually passed. If only one call site exists for a service the
    report claims is universal, that asymmetry is the finding.

### Defect-form classification (apply before writing the Claim field)

Every Finding must fit exactly one shape. Naming the shape disciplines
the Claim, Evidence, and Recommendation fields.

| Shape | Definition | Typical severity |
|---|---|---|
| **Bypass** | A validation, eligibility check, or policy exists in code but is not invoked at every entry point. | Medium–High |
| **Silent failure** | A check fires correctly, but produces no observable signal (no diagnostic, no UI surface, no log on a non-RT path). | Low–Medium |
| **Missing capability** | A documented contract, enum value, or persisted field has no runtime implementation. | Medium |
| **Drift risk** | Parallel paths duplicate validation logic and could diverge under future change. | Low / Semantics |
| **Test gap** | A behavioural guarantee is unenforced by tests. *Only valid if rule 8 was applied — grep first.* | Low |
| **Contract violation** | RT-safety, ABI, or persistence invariant breaks under a documented input. | High–Blocker |

If a Finding straddles two shapes, it is probably two Findings — or the
shape is wrong. The shape determines the recommendation form: Bypass →
add the missing call; Silent failure → add a diagnostic; Drift risk →
introduce a shared validator; etc.

### Calibration: detection bias check

Before submitting, ask explicitly:

- Did I check every introduced enum value for actual call-site usage?
- Did I produce a symmetry table for every parallel-consumer area in the
  changeset?
- Did I grep before writing any sentence containing "no", "never",
  "missing", or "not"?
- For each Medium I downgraded to Low/Semantics: was the downgrade
  because of evidence, or because the count seemed high?

Under-reporting is a failure mode equal to over-reporting. The
calibration anchor (0–2 High, 0–5 Medium) is a *typical* range for
mature work — if a changeset spans many parallel pipelines, asymmetry
findings can legitimately push Medium higher. Do not suppress real
Bypass / Silent-failure / Missing-capability findings to fit the anchor.

### Severity definitions (strict)

| Severity | Requires |
|---|---|
| Blocker | Proven crash / data loss / RT-safety violation / security issue with direct code evidence and repro path |
| High | Reproducible functional bug with clear impact — not merely theoretical |
| Medium | Real issue, no immediate harm, but should be addressed before release |
| Low | Minor issue, style, naming, small improvement — no functional impact |
| Semantics | Architectural opinion, naming preference, future consideration — evidence-backed but subjective |

### Expected severity distribution (calibration anchor)

A typical review of a well-maintained changeset produces:

- **Blocker:** 0 (rare — most reviews have none)
- **High:** 0–2
- **Medium:** 0–5
- **Low / Semantics:** unlimited

If your review exceeds these ranges, re-examine the higher-severity findings first and apply the *Active downgrade check* before finalizing.

### Self-check before submitting

Before you output the review, verify for every Finding:

- [ ] Evidence cites a concrete file/line/symbol, not a paraphrase.
- [ ] *Severity justification* explicitly addresses why the next-lower severity was rejected.
- [ ] Confidence level matches the directness of the evidence.
- [ ] No duplicate concerns across findings.
- [ ] No unverified hypotheses filed as Findings.
- [ ] Count of Blocker/High findings is within expected range, or re-examined.
- [ ] **Defect-form** named for every Finding (Bypass / Silent failure / Missing capability / Drift risk / Test gap / Contract violation).
- [ ] **Symbol-trace inventory** completed for every contract enum / service / policy in the changeset.
- [ ] **Symmetry table** produced for every parallel-consumer area; asymmetries surfaced.
- [ ] Every negative claim ("no", "never", "missing", "not invoked") has a grep command attached, or is moved to *Unverified Hypotheses*.
- [ ] At least two call sites read per central service the changeset claims to enforce universally.

---

## Meta

- Review target:
- Scope/changeset:
- Review type: Architecture / Bugfix / UI / Audio / State / Build
- Reviewer:
- Date:
- Commit / bundle:

---

## Final Classification

- Hard defects (Blocker / High):
- Likely risks (Medium):
- Product/semantics issues (Low / Semantics):
- Unverified hypotheses: (see section below — must not be counted here)

---

## Executive Summary

- ...

---

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

---

## Findings

Create one block per finding. Use the exact fields below.
Findings must be evidence-backed. Unverified concerns go into the *Unverified Hypotheses* section.

### Finding

- Severity: Blocker / High / Medium / Low / Semantics
- Confidence: High / Medium / Low
- Defect form: Bypass / Silent failure / Missing capability / Drift risk / Test gap / Contract violation
- Severity justification: (why does the next-lower severity not fit? Be concrete. For Bypass: name the call sites that enforce vs. the call site that skips.)
- Claim:
- Evidence: (exact file / line / symbol — no paraphrasing. For negative claims, attach the grep command.)
- Symbol trace: (for Bypass / Drift / Missing-capability findings — one line per producer/consumer with the value actually passed.)
- Counter-check: (what would disprove this finding?)
- Verification path: (concrete steps to reproduce or confirm)
- Impact:
- Recommendation:

---

## Unverified Hypotheses

Concerns that could not be confirmed from the provided code alone.
These are *not* Findings and do *not* contribute to the Final Classification.

- Hypothesis:
- Why unverified:
- How to verify:

---

## Tests / Verification

- Built locally:
- Tests executed:
- Repro steps:
- Expected:
- Observed:

---

## Risk / Regression

- Risk:
- Affected areas:
- Migration / compatibility:
- Rollback:

---

## Docs / Follow-ups

- Docs updates:
- TODOs / follow-ups:

---

## Appendix: Sub-agent briefing block

Paste the following block verbatim into every Explore / research sub-agent
prompt used for this review. It mirrors the verification rules above so
sub-agents do not silently weaken the evidence chain.

```text
You are gathering evidence for a strict, falsifiable code review
(REVIEW_TEMPLATE_claude.md). Apply these rules:

1. Symbol trace, not definition reading. For every contract enum,
   service, policy, or eligibility purpose introduced or modified by the
   changeset, grep ALL call sites and list each as
   "<file:line> — <value passed>". Flag unused enum values, single-call
   services, and asymmetric purpose usage as "Bypass-VERDACHT" with the
   enforcing vs. missing call sites named.

2. Negative claims require a grep. Any sentence containing "no", "never",
   "missing", "kein", or "not invoked" MUST cite the exact grep command
   and its empty output. If you did not grep, write "nicht überprüft" /
   "not verified" instead — never assert absence from intuition.

3. Two-call-site minimum. For every central service or policy the
   report claims is "enforced everywhere", open at least two distinct
   call sites and quote the arguments actually passed. If only one
   exists, that asymmetry is the finding.

4. Symmetry table for parallel consumers. When N consumers read the
   same data (recorder/playback/runtime, realtime/offline, load/save),
   produce a small explicit table:
   "consumer | validation layer | parameters used".
   Asymmetries are the most likely defect locations.

5. Mark every observation as one of: BESTÄTIGT (with file:line),
   VERDACHT (suspect, needs follow-up), or NICHT ÜBERPRÜFT (no grep
   performed). Do not mix the categories.

Output: file:line per claim, max <word_budget> words, no speculation
without code reference.
```
