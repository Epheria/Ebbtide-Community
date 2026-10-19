# Voice

Every voice line in Ebbtide is currently AI voiced, and all of them are to be replaced by real voice actors: pilots, helicopter crews, ship officers, vehicle crews and infantry squads.

## How it works

1. **Audition.** Post a short take in the Discord submissions channel, reading the sample lines pinned there.
2. **Casting.** If your voice fits a role, a maintainer contacts you and opens a private ticket.
3. **Script.** Your role's full script is added to `scripts/<role>.csv`: file name, situation, tone and line.
4. **Delivery.** Open a pull request that adds your takes to `takes/<role>/<your name>/`, one file per line, named exactly as in the script.
5. **Review.** We listen, ask for retakes if needed, merge, and bring the lines into the next build.

## Recording specs

Record clean and dry; the game adds radio effects itself.

- FLAC preferred (smaller), or WAV. Mono, 48 kHz, 24-bit (44.1 kHz / 16-bit is fine too).
- No reverb, effects, music or radio filter.
- A quiet room, with no echo or background noise.
- Loudest peaks around -3 dB, never clipping.
- One line per file, with about half a second of silence before and after.

## Before you send anything

Read [../CONTRIBUTOR_TERMS.md](../CONTRIBUTOR_TERMS.md), especially the part on voice recordings. If you are under 18, a parent or guardian needs to agree with you.
