# Voice

Every voice line in Ebbtide is currently AI voiced, and all of them are to be replaced by real voice actors: pilots, helicopter crews, ship officers, vehicle crews and infantry squads.

## How it works

1. **Audition.** Post a short take in the Discord submissions channel, reading the sample lines pinned there.
2. **Casting.** If your voice fits a role, a maintainer contacts you and opens a private ticket.
3. **Script.** Your role's full script is added to `scripts/<role>.csv`: file name, situation, tone and line.
4. **Delivery.** Upload your takes to your assigned private Drive folder and check `Ready to submit` in your working sheet. One file per line, named exactly as in the script. See the [recording submission guide](../docs/VOICE_SUBMISSIONS.md) ([한국어](../docs/ko/VOICE_SUBMISSIONS.md)). Do not add audio to a public pull request.
5. **Review.** The owner bridge freezes private copies and publishes a receipt. A separate reviewer listens and approves the exact preview; the bot opens a manifest-only PR. A maintainer merges it, and the developer brings approved audio into the game separately.

The checkbox requests intake; it does not create a PR or approve the recording. A maintainer must first register the assignment and activate the owner-only Google connection. Written script translations use the [translation workflow](../docs/CONTRIBUTION_WORKFLOW.md).

## Recording specs

Record clean and dry; the game adds radio effects itself.

- FLAC preferred (smaller), or WAV. Mono, 48 kHz, 24-bit (44.1 kHz / 16-bit is fine too).
- No reverb, effects, music or radio filter.
- A quiet room, with no echo or background noise.
- Loudest peaks around -3 dB, never clipping.
- One line per file, with about half a second of silence before and after.

## Before you send anything

Read [../CONTRIBUTOR_TERMS.md](../CONTRIBUTOR_TERMS.md), especially the part on voice recordings. If you are under 18, a parent or guardian needs to agree with you.
