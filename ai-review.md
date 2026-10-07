# AI review guide (Tier 3) — using Gemini

Tier 3 uses **Gemini on the web** (gemini.google.com) as the reviewing model. Section 5.3 of the project plan requires the reviewing model to differ from the code-generating model, and Gemini belongs to a different model family from the tool used to generate code.

Why Gemini: students get the Pro plan for free, so future interns can repeat this process at no cost.

Why the web app rather than Gemini CLI (recorded 2026-10-06): when signing in to Gemini CLI with a personal Google account, Google reports that the "Gemini Code Assist for individuals" plan **no longer supports Gemini CLI** and asks users to move to Antigravity. The student Pro plan does not apply to that route. With a free API key, Google may use submitted content for training, which is not acceptable for company code.

---

## 0. Before sending any code — required reading

During review, **the feature's source code is uploaded to Google's servers**.

1. **Your mentor must allow you to send code to Gemini.** Without permission, do not do it. Verbal permission is fine, but record the date of approval in section 2.
2. **Turn off activity saving.** On gemini.google.com, go to **Settings → Activity** (Gemini Apps Activity) and **turn it off**. When off, conversations are not used to improve the model. Google still keeps conversations briefly to operate the service.
3. **The script automatically drops the contents of secret files** (`.env`, `*.pem`, `*.key`…) and records only their names. Even so, **run `gitleaks` first** (see `automated-scanning.md`). A key inside ordinary code is still sent along with the code.
4. Input files live in `review-input/` and **must not be committed** (already listed in `.gitignore`), because they contain raw source code.

---

## 1. Account setup (once)

1. Sign in to gemini.google.com with the Google account that has the student Pro plan.
2. Turn off activity as in section 0.2.

---

## 2. Choose and fix the model

In the model picker on gemini.google.com, **choose the Pro model**, since Tier 3 needs deep reasoning.

**Keep exactly one model for the whole project.** Switching models midway makes Tier 3 figures for different features incomparable.

| Item | Value |
| --- | --- |
| Reviewing model | 3.1 Pro, with "Extended thinking" on |
| Date chosen | 2026-10-07 |
| Mentor approved sending code externally | 2026-10-07 |

---

## 3. Output language

Students on this project come from different countries, so the AI's answer can be written in the language each student reads best:

| `--lang` | Language |
| --- | --- |
| `en` (default) | English |
| `zh-Hant` | Traditional Chinese (繁體中文) |
| `vi` | Vietnamese (Tiếng Việt) |

Only headings and descriptions are translated. Criterion codes (C01–C12), answers (Yes / No / Insufficient information), severity (High / Medium / Low), file paths and code identifiers always stay in English, so results from different students can be compared and copied into `log.csv` without translation.

All repository files, scripts, `log.csv` columns and log entries are in English regardless of the output language you choose.

---

## 4. Preparing each feature

You need two things:

1. **A requirements file**, e.g. `requirements-<feature name>.md`: describes what the feature **must do**, written as a requirements document.
   - **Do not paste the original prompt used to generate the code** (section 5.3). Given the original prompt, the reviewing model tends to just confirm what was asked for.
   - State business conditions explicitly, e.g. "only the creator can edit", "only count approved orders". Criteria C04 and C06 rely on these conditions.
2. **The directory containing the feature's source code.**

---

## 5. Running the review

Only do this **after** filling in the *Manual check* column and running the Tier 1 scans.

**Step 1 — Create the input file:**

```bash
./review.sh [--lang en|zh-Hant|vi] <feature-name> requirements-<name>.md <code-dir>
```

The script creates two files:

- `review-input/review-<name>.txt`: contains the **fixed review prompt** (with the chosen output language), the checklist, the requirements file and the source code (excluding `node_modules`, `.git` and build directories). The prompt is the same for every feature, so results are comparable.
- `review-<name>.md`: the results skeleton, with the header already filled in (including the output language).

If `review-<name>.md` already exists, the script stops without overwriting it. The first result is research data; do not re-run to get a "nicer" result.

**Step 2 — Send to Gemini:**

1. Open a **new conversation** on gemini.google.com. Use a separate conversation for each feature so Gemini does not remember earlier runs.
2. Select the model recorded in section 2.
3. Upload `review-input/review-<name>.txt`, then type exactly: **`Follow the INSTRUCTIONS section at the top of the attached file exactly.`**
4. Time it from sending until Gemini finishes answering.

**Step 3 — Save the result:**

1. Click Gemini's copy button and paste the answer **verbatim** at the end of `review-<name>.md`, without editing.
2. Fill in the model name and waiting time in the header.

---

## 6. Reading results and updating the log

1. Record each finding in the *AI review findings* column of `log.csv` as `<criterion code> at <location>, severity <High/Medium/Low>`.
2. **Do not classify true/false at this step.** Classification happens during consolidation (task T6), to compute the true-positive and false-positive rates (reliability table, section 8).
3. Findings that match `semgrep` results are recorded in both columns (see `automated-scanning.md` section 3).
4. Read the *Open questions* section carefully. If most criteria are "Insufficient information", server-side code may have been left out.

---

## 7. Cross-checking (optional)

Section 5.3 suggests cross-checking with two models. You can upload the same input file to a second model and compare the two results. **Where the two models disagree is where a human needs to look closely.**

---

## 8. Known limitations

- The Pro plan **limits how many Pro-model requests you can make per day**. When you run out, wait until the next day; **do not switch to another model** to continue.
- Very large code may exceed the upload limit. In that case, include only the directory with the code for the feature under review.
- The model may invent locations that do not exist. The prompt forbids this, but you must still open the actual file and line to check before trusting it.
- Sending and pasting results are manual steps, so it is easy to forget the waiting time. Fill it in as soon as you paste the result.
