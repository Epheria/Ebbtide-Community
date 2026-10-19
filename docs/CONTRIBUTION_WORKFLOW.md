# Translation work orders

## Choose your language

| Language | Guide |
| --- | --- |
| English | This page |
| 한국어 | [사용법 읽기](ko/CONTRIBUTION_WORKFLOW.md) |
| 日本語 | [使い方を読む](ja/CONTRIBUTION_WORKFLOW.md) |
| 简体中文 | [阅读使用指南](zh-Hans/CONTRIBUTION_WORKFLOW.md) |
| 繁體中文 | [閱讀使用指南](zh-Hant/CONTRIBUTION_WORKFLOW.md) |
| Português (Brasil) | [Ler o guia](pt-BR/CONTRIBUTION_WORKFLOW.md) |
| Español | [Leer la guía](es/CONTRIBUTION_WORKFLOW.md) |
| Français | [Lire le guide](fr/CONTRIBUTION_WORKFLOW.md) |
| Deutsch | [Anleitung lesen](de/CONTRIBUTION_WORKFLOW.md) |
| Русский | [Читать руководство](ru/CONTRIBUTION_WORKFLOW.md) |
| Polski | [Przeczytaj instrukcję](pl/CONTRIBUTION_WORKFLOW.md) |
| Italiano | [Leggi la guida](it/CONTRIBUTION_WORKFLOW.md) |
| Türkçe | [Kılavuzu oku](tr/CONTRIBUTION_WORKFLOW.md) |
| Українська | [Читати посібник](uk/CONTRIBUTION_WORKFLOW.md) |
| ไทย | [อ่านคู่มือ](th/CONTRIBUTION_WORKFLOW.md) |
| Română | [Citește ghidul](ro/CONTRIBUTION_WORKFLOW.md) |
| Čeština | [Přečíst návod](cs/CONTRIBUTION_WORKFLOW.md) |

Commands, issue field labels, CSV column names and status values stay in English because the bot reads them exactly. Localized guides explain the same workflow. The English guide is the reference when instructions differ; native wording corrections are welcome.

## Overview

Google Sheets is the place to write and review a translation. A GitHub work order reserves its scope, records who is responsible, and controls when an approved copy becomes a pull request.

**Editing a sheet does not update the repository or the game.** The bot imports an exact reviewed snapshot into a pull request. A maintainer still reviews and merges that pull request, and the developer brings the result into a game build.

This workflow covers existing UI strings and written voice-script translations. Recorded audio, auditions, new dialogue drafts, and text without a source ID use their own preparation process.

Community translations use the work-order bot to open their delivery pull request. A manually created translation pull request cannot bypass the reservation and snapshot approval steps.

Post commands as comments on the assigned GitHub work-order issue. When approving, copy all 64 characters after `Digest:` in the bot's preview reply and replace only `<sha256>` in the example command. Keep the command in English; do not paste the placeholder itself.

## Who does what

| Person | Responsibility |
| --- | --- |
| Contributor | Writes the assigned translation in the sheet and requests a preview. |
| Reviewer | Checks context, terminology, natural wording, and the exact preview. Approves its digest using their own GitHub account. |
| Maintainer | Creates or checks the work order, reserves the range, manages sheet access, reviews the resulting pull request, and merges it. |

The contributor and reviewer must be different GitHub users. The bot checks identity and file structure; it does not decide whether a translation reads naturally.

People can do their translation work entirely in Google Sheets. They do not need to install Git, clone the repository, or make their own pull request. The person who approves a preview needs a GitHub account. If the contributor needs help using GitHub comments, a maintainer can request the preview for them.

## 1. Agree on a small task

Apply through the existing translator issue or a Discord support ticket. A maintainer agrees on the language, contributor, reviewer, and scope before work starts.

The private applicant sheet is an intake queue. It is not the reservation register, and its contents should not be copied into public GitHub issues.

Open a **Translation work order** issue with these fields:

| Field | What to enter |
| --- | --- |
| Kind | `ui` or `voice-text` |
| Locale | Repository locale code, such as `ja`, `ru`, or `pt-BR` |
| Table or voice role | Existing source table or role name, without a path or `.csv` extension |
| Contributor | One GitHub login, without `@` |
| Reviewer | A different GitHub login, without `@` |
| Spreadsheet URL | The Google Sheets workbook used for this task |
| Sheet tab | Exact worksheet tab name |
| First key | First existing source key to include |
| Last key | Last existing source key to include |

The range includes both endpoints in **canonical source-file order**, not alphabetical order or the sheet's current row order. It can contain at most 200 keys. For voice text, the key is the script's `file` identifier, without `.wav` or `.flac`.

Use one locale and one UI table or voice role per work order. A short range is easier to review and creates fewer conflicts when game text changes.

## 2. Reserve it before translating

A maintainer comments:

```text
/work assign
```

Wait for the bot to confirm the reservation. Filling in an issue, closing an issue, or typing a name into a sheet does not reserve or release work.

The bot records the assignment in `registry.json` on the `community-work-state` branch. It freezes the issue's fields, exact source keys, and source hash. It rejects an overlap with another active assignment for the same kind, locale, and table or voice role. Different locales can work on the same source keys.

Editing the issue body later does not change the active assignment. Ask a maintainer to release it and create a corrected reservation if the scope, workbook, contributor, or reviewer needs to change.

## 3. Write in the sheet

A maintainer supplies the current source rows and grants edit access to the assigned people. The workbook must be readable by the bot without a Google login, but its editing permission should be restricted to the people working on it.

Keep source keys and English text protected. Give contributors access only to the input cells they need. Do not turn on “Anyone with the link can edit.” Sheet permissions and protected ranges are set manually; the GitHub bot does not manage Google permissions.

For UI translation, keep the four CSV columns:

```text
key,en,translation,status
```

Use a tab containing rows from the single UI table named in the work order. A combined master list of keys from several tables is a reference, not a directly importable work-order tab. The bot checks all populated rows in the selected tab against that source table.

Edit `translation` and use the existing `status` values. A UI row is ready for import only when `status` is blank. Rows marked `review` or `outdated` are held. A blank status alone is not approval; the separate review step below is required.

For written voice translations, keep these exact column headings in this order:

```text
Take file,English source,Translation,Review status,Notes,Role,Situation,Tone,Current voices,Source readiness,Source file,Source record
```

The existing Japanese, Russian, and Korean voice tabs use this layout. The bot filters rows by the exact `Role` value, such as `carrier_jet_pilot`, then selects the reserved `Take file` keys. Fill `Translation` and mark reviewed rows `Approved` in `Review status`.

Approved text is written to `voice/translations/<locale>/<role>.csv` using `key,en,translation,status`. This imports written lines only. It does not approve a recording or establish that a draft line is implemented in the game.

In either kind of task:

- Keep placeholders, required tags, and line-break tokens intact.
- Keep the source key and English text identical to the assigned source.
- Fill every translation in the reserved range before previewing it.
- Treat spreadsheet cells as text. Do not use formulas to fetch or build a translation.
- Keep private contact details, ticket messages, and audition files out of the work-order workbook and issue.

If a task is too large to finish, split or release it with a maintainer instead of leaving partly completed reserved work indefinitely.

## 4. Request and review a preview

The assigned contributor, assigned reviewer, or a maintainer comments:

```text
/work preview
```

The bot reads the reserved range from the public Google Sheets CSV export. It checks the frozen source, status, non-empty translations, and required variables. It also checks the repository's current translation so a later approval can detect changes made by somebody else.

The bot saves an immutable snapshot and posts its SHA-256 digest with a link to review it. Review the actual snapshot, not just the issue summary or the live sheet. The snapshot is the proposed content; the sheet can change after a preview.

The reviewer checks:

- Meaning and context against the English source.
- Natural wording and consistent glossary terms.
- UI length or spoken delivery where relevant.
- Placeholder placement, tags, and line breaks.

If a change is needed, edit the sheet and run `/work preview` again. Use the new digest. A preview link is a review artifact, not permission to merge.

## 5. Approve the exact snapshot

Only the assigned reviewer comments, replacing the example with the complete digest from the preview:

```text
/work approve <sha256>
```

The bot verifies the reviewer, fetches the sheet again, and requires it to match the approved snapshot. It also checks that the source and target repository content have not changed since the preview. A sheet or target-file change requires a new preview. A canonical source-table change requires a fresh assignment, as described below.

On success, the bot opens a pull request with the validated files. It does **not** merge the pull request. The sheet's `Approved` value or an ordinary “looks good” comment cannot substitute for this command.

A maintainer reviews the diff and merges the pull request after its checks pass. Until then, the work remains reserved. Review conversations about the proposed files belong in that pull request so the final changes are easy to follow.

The trusted `reviewed-sheet` policy checks the PR against its recorded work order and approved snapshot. It reads PR files as data and runs trusted default-branch code. It rejects a manual translation PR, a changed delivery file, or extra files bundled into an approved translation delivery. Editing a bot branch after approval cannot substitute new text for the reviewed snapshot.

## 6. Finish or release the reservation

After the pull request is merged or closed, run:

```text
/work sync
```

This reconciles its state: a merged pull request completes the task; a closed, unmerged pull request releases it. Check the bot's confirmation rather than assuming the issue status changed the reservation.

The coordinator also synchronizes a recorded bot pull request when GitHub sends its closed event. Use `/work sync` to reconcile manually if that automatic run did not finish. For an open pull request, `/work sync` also requests its checks again; use it if check dispatch failed after the PR was created.

To cancel an assignment before a pull request exists, a maintainer comments:

```text
/work release
```

An open pull request must be closed before release. This prevents two active submissions for the same reserved range.

## Command reference

| Command | Who can run it | Result |
| --- | --- | --- |
| `/work assign` | Maintainer | Freezes the work order and reserves the source range. |
| `/work preview` | Assigned contributor, assigned reviewer, or maintainer | Validates and saves a snapshot for review. |
| `/work approve <sha256>` | Assigned reviewer | Rechecks that exact snapshot and opens a pull request. |
| `/work release` | Maintainer | Cancels a reservation when there is no open pull request. |
| `/work sync` | Maintainer | Reconciles a merged or closed pull request with the register. |

## When game text changes

Do not create a new workbook for every game version. Stable source IDs let existing translations survive normal source updates. Add new source rows through the repository's source update process and mark changed translations for review as described in [Localization](../localization/README.md).

An assigned task uses a frozen source snapshot of its whole UI table or voice role. If that canonical table changes before approval, the bot stops the import, even if the reserved keys themselves are unchanged. A maintainer closes any open delivery PR, releases the old work order, updates the sheet's source rows, and creates a new work-order issue. Preserve the volunteer's existing translation while checking it against the refreshed source; the reviewer then reviews a new preview. Tasks for other source tables can continue.

A planning row without a real source ID is not ready for this importer. Keep it in planning until the developer adds its canonical source entry. Do not invent production IDs or upload a whole sheet merely to include future content.

## Maintainer setup and limits

Enable the work-order workflow only after its code and issue form are merged into the default branch. The state register is kept on `community-work-state`; do not manually edit it during active commands.

The workflow uses the repository's `GITHUB_TOKEN`, with the repository permissions needed to write the state and bot branch, comment on issues, and create pull requests. It does not need a Google OAuth connection or a personal access token. Google access is limited to reading the public CSV export.

In the repository's Actions settings, permit GitHub Actions to create pull requests. Keep the bot's identity separate from a human language reviewer.

Do not rely on a bot-created pull request starting ordinary `pull_request` workflows. The importer validates its candidate files before creating a pull request. It explicitly dispatches `check.yml` for the bot branch and `delivery-policy.yml` from the trusted default branch for that PR number.

Protect the default branch with both required checks: `check` and the `reviewed-sheet` commit status. The policy workflow must be able to publish that status. Verify that both checks finish successfully before merging; creating the workflow files alone does not enforce a repository's branch protection settings.

The reservation register prevents overlapping assignments, and the required delivery policy prevents manual translation PRs from bypassing those assignments. Neither manages Google Sheets editing permissions. Restrict sheet editing and keep source columns protected.

Automatic checks catch structural problems and stale content. Human review remains responsible for translation quality, context, contributor terms, and suitability for the game.
