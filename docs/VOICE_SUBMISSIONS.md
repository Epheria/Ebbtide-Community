# Recording submissions

[한국어](ko/VOICE_SUBMISSIONS.md) · [Written translation workflow](CONTRIBUTION_WORKFLOW.md)

**Upload recordings to your assigned private Google Drive folder. Check `Ready to submit` in your working sheet to request intake.** The owner bridge checks the files, freezes private copies and writes a receipt. A separate reviewer must listen and approve the exact preview before the GitHub bot creates a **manifest-only pull request**. Audio files stay in Drive.

A checkbox is a submission request. It does not approve a recording, open a PR by itself, merge anything, or put audio into the game. The owner must authorize the Google bridge and register the assignment; the GitHub workflows must be on the default branch. An unassigned reference template cannot submit files.

## For voice actors

1. Apply through a Discord ticket or the [voice actor application](../../../issues/new?template=voice_actor.yml). Agree on a small role and the contributor terms before recording the full script.
2. Wait for a maintainer to reserve the exact take IDs, language, casting slot and recording version. Receive your private upload folder and working sheet. The public workbook is a reference, not the upload location.
3. Record one line per file. Use the exact assigned take ID plus `.flac` or `.wav`, such as `SL_Select.flac`. Keep one current file with that name directly in the assigned folder. Subfolders, shortcuts, ZIPs and duplicate filenames are not accepted.
4. In `Recording Uploads`, enter the exact filename in `Take file`. `Drive URL` may be blank; the bridge finds the unique exact filename in your folder. If you paste a link, use the direct Drive file link, not a folder or a link to another website.
5. Upload **every take in the assignment**, then check `Ready to submit` for each row. All assigned rows must be checked together. Ask the maintainer to split a large assignment rather than submitting only part of it.
6. Read `Result`. Success says `Submitted` and gives a receipt digest. The checkboxes reset so you can request another intake after corrections. If it says `Not submitted`, fix the stated issue and check again. If nothing happens, contact the coordinator; do not assume the files were received.
7. Wait for listening review. For a retake, replace the current file in your incoming folder and check the rows again. Changed bytes create a new receipt. Do not edit a frozen copy or post private audio links publicly.

You do not need Git, a local repository or a personal GitHub token to upload audio. A maintainer can run the preview command for you. The independent reviewer needs their own GitHub account to approve it.

### Recording format

- FLAC or PCM WAV; mono, 44.1 or 48 kHz, 16 or 24 bit. FLAC is preferred.
- At most **20 MiB per file**, **100 MiB per submission**, and **200 assigned takes**. A coordinator can split work orders to fit those limits.
- Clean, dry voice: no music, reverb, radio filter or other processing. The game adds radio effects.
- Avoid clipping; leave roughly half a second before and after the line.
- Read [CONTRIBUTOR_TERMS.md](../CONTRIBUTOR_TERMS.md). The voice must be your own, without AI generation or alteration. A parent or guardian must agree for contributors under 18.

The bridge checks basic WAV/FLAC headers, sample format, names and byte hashes. It does not fully decode audio or judge noise, clipping, pronunciation, acting or suitability. Human listening remains required.

## For reviewers

The coordinator gives the assigned reviewer read access to the **frozen receipt files**, individually. A public Drive file URL in the manifest does not grant access. Do not ask actors to make their upload folder public.

Commands are comments on the assigned **Voice recording work order** issue:

```text
/voice preview
```

Open the bot's saved snapshot. Listen to every private frozen file referenced by that snapshot; compare the spoken language and lines against the assigned script, context and take IDs. Check recording quality, casting continuity, contributor terms and any retakes. Checking a live incoming folder is insufficient because an actor can replace those files later.

When the exact snapshot is acceptable, the assigned reviewer comments:

```text
/voice approve <sha256>
```

Copy all 64 characters after `Digest:` in the preview reply. Replace only `<sha256>`. The reviewer and actor must be different GitHub users. Approval creates the manifest PR after the bot rechecks its bindings; a maintainer still reviews and merges it. If the receipt, source or target has changed, prepare a fresh preview or assignment as instructed by the bot.

## For coordinators

### Reserve the work

Open a [Voice recording work order](../../../issues/new?template=voice_work_order.yml) with the exact locale, role, casting slot, positive recording version, actor, independent reviewer, public reader Outbox workbook/tab and inclusive first/last take IDs. Use `Recording Outbox` as the sheet tab. Do not put private folder IDs, emails or ticket text in the public issue.

Comment:

```text
/voice assign
```

Wait for the bot's reservation confirmation. The source IDs and script hash are frozen in the register. A separate casting slot is for an agreed distinct character, not a way to take somebody else's reservation. Localized recording requires committed, approved spoken translations; drafts without canonical take IDs are not recordable assignments.

Create an owner-owned working spreadsheet per work order. Copy only the `Recording Uploads` input layout; do not share a bound Apps Script project or the owner configuration. Pre-fill the exact filenames and protect the reference/source fields. Allow the actor to edit `Drive URL` and `Ready to submit`; the coordinator can correct filenames when a different permitted extension is used. Limit sharing to named people. Never use “Anyone with the link can edit.”

Under the private Incoming root, create a dedicated upload folder. Give only that actor named-person upload/edit access. Under the private Received root, create an owner-only archive folder for the work order. Root folders and archive folders must stay owner-only; reviewers receive viewer access to selected frozen files, not folder editing rights. Do not reuse folders or workbooks between active assignments.

### Owner bridge installation

1. Create a **standalone**, owner-only Apps Script project in the owner's Drive, outside contributor-shared folders. Do not create it from the shared spreadsheet's Extensions menu. Spreadsheet editors can edit a container-bound script, which would expose the owner's privileged trigger code.
2. Copy [`Code.gs`](../tools/drive_voice_bridge/Code.gs) and [`appsscript.json`](../tools/drive_voice_bridge/appsscript.json) into that private project. Keep the project unshared. There is no web app deployment.
3. Review the workbook/folder IDs in `bootstrapOwnerConfiguration`. Run it as the owner and complete Google's permission screen. Google Drive read/copy, Sheets write, trigger installation and owner identity are required. No GitHub credential or OAuth token is stored in a cell, configuration object or repository.
4. Run `coordinatorHealthCheck`. An empty registry is valid and creates no actor assignments or triggers. The bootstrap preserves a registry that is already configured; it does not reset it.
5. For an agreed assignment, call `setupCoordinator(config)` from an owner-only temporary wrapper function using the structure below. Copy `Script SHA256` from the bot's `/voice assign` reply and its canonical keys; the fallback is `script_hash` in the issue's entry on `community-voice-state`. Do not guess the hash from a spreadsheet title, game version or filename. Setup installs one owner-authorized edit trigger for each registered working workbook and protects the public Outbox against non-owner edits.
6. Test the real assignment once with its actor and reviewer. The actor checks the boxes, the owner sees a successful intake, and the reviewer opens the frozen files. A code test or an empty-registry health check does not prove that a real upload can be submitted.

```javascript
function configureAssignedWork() {
  return setupCoordinator({
    coordinatorSpreadsheetId: 'PUBLIC_READER_OUTBOX_WORKBOOK_ID',
    incomingRootFolderId: 'PRIVATE_INCOMING_ROOT_ID',
    archiveRootFolderId: 'PRIVATE_RECEIVED_ROOT_ID',
    assignments: [{
      issue: 123,
      workingSpreadsheetId: 'OWNER_OWNED_ACTOR_WORKBOOK_ID',
      uploadFolderId: 'PRIVATE_ASSIGNED_INCOMING_SUBFOLDER_ID',
      archiveFolderId: 'OWNER_ONLY_RECEIVED_SUBFOLDER_ID',
      locale: 'en', role: 'squad_leader', slot: 'leader_alpha',
      keys: ['SL_Select', 'SL_Hold'],
      scriptHash: 'COPY_EXACT_64_CHARACTER_SCRIPT_HASH_FROM_BOT_REGISTER'
    }]
  });
}
```

That is an example, not an assigned task. Pass the full active registry each time; omitted assignments lose their triggers. Keep at most 18 active working workbooks in one project. The config is stored in the private project's Script Properties. Remove inactive assignments after the work has completed or been released.

The standalone project intentionally has no spreadsheet custom menu: Google requires container-bound code for those menus. The owner can run `submitReadyRecordings` from the private script editor as a manual fallback. The ordinary actor action is editing the checkbox; API writes or other scripts do not fire the installable edit trigger.

Google permissions documentation: [standalone scripts](https://developers.google.com/apps-script/guides/standalone), [installable triggers](https://developers.google.com/apps-script/guides/triggers/installable), [bound-script access](https://developers.google.com/apps-script/guides/bound), [custom menu limitation](https://developers.google.com/apps-script/reference/base/menu).

### Input and receipt schema

The actor workbook's `Recording Uploads` begins with:

```text
Take file,Drive URL,Ready to submit,Result
```

`Ready to submit` is a real Google Sheets checkbox (`TRUE`/`FALSE` boolean), not text typed as `TRUE`. `Result` is output for the coordinator bridge, not a review decision.

Keep at most 200 populated take rows in the input tab. Outbox reads are bounded to 20,000 receipt rows. At capacity, the owner must preserve completed or released work-order receipts in a separate read-only archive before removing them from the active Outbox. Keep active work-order records in place.

The public reader, owner-writable `Recording Outbox` begins with:

```text
Work order,Take file,Drive snapshot,SHA256,Bytes,MIME type,Revision,Submitted,Script SHA256
```

- `Work order`: exact GitHub issue number.
- `Take file`: canonical take ID without its audio extension.
- `Drive snapshot`: direct file URL to the owner-owned frozen copy. File permission stays private; a URL is not an access grant.
- `SHA256`, `Bytes`, `MIME type`: checksum, exact size and normalized `audio/wav` or `audio/flac`.
- `Revision`: 64-character digest binding the issue, assigned script hash and the whole ordered batch of filenames and byte hashes. A new intake also binds the previous receipt, so reverting to old audio creates a fresh current revision rather than reactivating a historical one.
- `Submitted`: UTC timestamp such as `2026-10-20T00:00:00Z`.
- `Script SHA256`: the exact assignment `script_hash`, including spoken text and source context.

The bridge accepts files only directly inside the registered upload folder and only under assigned names. It creates private, owner-owned copies rather than changing the actor's files or permissions. It writes the entire receipt batch only after all copies have been checked.

An unchanged retry reuses the receipt and copies; changed bytes create a new revision. If intake stops after making some private copies, no approval or PR is created. Retrying reuses matching partial copies. An incomplete or inconsistent Outbox receipt stops intake and needs owner reconciliation; do not mark it approved to get past the error. Preserve previous receipts for the review record.

### Finish

After preview and listening approval, the bot opens a manifest-only PR. The manifest records which private files and hashes were approved. It does not upload WAV/FLAC to public GitHub, share Drive files publicly, or import audio into Unity.

A maintainer checks and merges it. Synchronize the work order with `/voice sync`; cancel an assignment without an open PR using `/voice release`. Close an open delivery PR before releasing its reservation. Re-recording completed takes uses a fresh work order and a higher recording version; refresh source assignments when script content changes.

The developer downloads the approved private copies, verifies their SHA-256 checksums and brings them into the game separately. Listening approval, GitHub merge and game integration are different completion steps.
