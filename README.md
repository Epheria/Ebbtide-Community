# Ebbtide Community

**English** · [Español](docs/es/README.md) · [Русский](docs/ru/README.md) · [한국어](docs/ko/README.md) · [日本語](docs/ja/README.md) · [Polski](docs/pl/README.md) · [Türkçe](docs/tr/README.md) · [Français](docs/fr/README.md)

This is where the community helps build Ebbtide: translations, voice acting, and other contributions that go into the game.

Ebbtide is a top-down zombie survival game with real-time command, made by one developer. Many parts of the game started with AI-generated voices, music and translations. The goal of this repository is to replace them, piece by piece, with work made by real people from the community.

## Ways to help

| Area | How to start | Where the work goes |
| --- | --- | --- |
| Translation | Open a [translator issue](../../issues/new?template=translator.yml) | [`localization/`](localization/) |
| Voice acting | Audition in the Discord submissions channel, or open a [voice actor issue](../../issues/new?template=voice_actor.yml) | [`voice/`](voice/) |
| Music, sound and art | Share your work in the Discord submissions channel first | A folder is added once work is picked |
| Playtest feedback | Join the playtest when it opens and report in Discord | Not in this repository |

## How a contribution gets into the game

1. Apply with an issue, or get picked from the Discord submissions channel.
2. Read [CONTRIBUTOR_TERMS.md](CONTRIBUTOR_TERMS.md). You keep ownership of your work; you allow it to be used in Ebbtide.
3. For UI or voice-script translations, get a [work order](../../issues/new?template=work_order.yml) assigned and write in its Google Sheet.
4. A separate reviewer approves the exact sheet snapshot. The bot opens a pull request and automatic checks verify it against that approval.
5. Approved work is merged here, and the developer brings it into the next build.

Every contributor is credited in the game under the name they choose.

## Ground rules

- Submit only your own original work.
- No AI-generated translations, voices, music or art. The whole point is real people's work.
- Be kind in reviews. Most people here are volunteers.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the details.

For task reservations, sheet review and export commands, read the [work-order guide](docs/CONTRIBUTION_WORKFLOW.md).

**[Usage guides in 17 languages](docs/CONTRIBUTION_WORKFLOW.md#choose-your-language)** — choose your language for contributor, reviewer and maintainer instructions.

## Community workspaces

- [Contribution hub](https://docs.google.com/spreadsheets/d/1cqM9Qxld-GjaQj6rIUxeZrGchZwrnBu-3Eq5SdBbGaY/edit): start here for language needs, source versions and the workflow.
- [UI translation template](https://docs.google.com/spreadsheets/d/1YegbTot6iaszCQV2_3O_yM_oCkkGGqeUVl1m52xzmbM/edit): a maintainer supplies a working copy for an assigned language.
- [Voice scripts and localization](https://docs.google.com/spreadsheets/d/1ObgnTm9lYXfxNpR1gkrFSkhU_OmkFCkIqfEqps0S-Vs/edit): English scripts and written voice translations.

The shared reference workbooks are read-only. Ask a maintainer for your assigned working sheet before starting.

## Status

- Translation: open. The English source is a snapshot of a game still in development. Source changes block stale sheet exports; a maintainer refreshes the working sheet before reassignment.
- Voice acting: auditions first. Scripts for all 21 roles are in [`voice/scripts/`](voice/scripts/).
