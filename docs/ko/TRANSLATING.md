# 현지화

> **UI·대본 번역 안내:** `ui`와 `voice-text`는 작업 범위 배정, 별도 검수자의 승인, 봇 제출 절차를 따릅니다. 먼저 [한국어 작업 안내](CONTRIBUTION_WORKFLOW.md)를 읽어 주세요. 아래의 Git 직접 편집·수동 PR 제출 절차는 이 두 종류의 번역에는 적용되지 않습니다. 파일 형식 설명은 계속 참고할 수 있으며, 녹음·오디션은 별도로 진행합니다.

*이 페이지는 AI의 도움을 받아 번역했습니다. 한국어가 모국어라면 풀 리퀘스트로 번역을 다듬어 주세요. 기준이 되는 문서는 [영어판](../../localization/README.md)입니다.*

번역할 수 있게 준비해 둔 Ebbtide의 인터페이스 텍스트입니다. 게임은 한국어로 쓰였고, 다른 모든 언어는 영어를 원문으로 삼아 번역합니다.

## 폴더

아래 경로는 모두 [`localization/`](../../localization/) 폴더를 기준으로 합니다.

| 경로 | 들어 있는 것 |
| --- | --- |
| `source/strings/<Table>.csv` | 현재 게임 텍스트: `key`, `en`, `ko`. 수정하지 마세요. 게임에서 다시 생성됩니다. |
| `source/SNAPSHOT` | 현재 원문 스냅샷의 날짜와 크기 |
| `translations/<lang>/<Table>.csv` | 언어마다 폴더 하나: `key`, `en`, `translation`, `status` |
| `glossary.csv` | 고유명사와 군사 용어, 그리고 각각을 어떻게 다룰지 |

언어 폴더 이름에는 `de`, `fr`, `pt-BR`, `ro`, `zh-Hans` 같은 코드를 씁니다.

## 번역하는 방법

1. 번역할 언어로 [번역가 이슈](https://github.com/Epheria/Ebbtide-Community/issues/new?template=translator.yml)를 엽니다. 관리자가 언어 폴더를 만들어 드립니다.
2. `translations/<lang>/` 안의 파일을 수정합니다. `translation` 열만 채워 주세요.
3. 자리 표시자는 영어와 똑같이 남겨 주세요. `{0}`, `{1}`, `<b>` 같은 리치 텍스트 태그, 줄바꿈 `\n`이 해당합니다. 문장 안에서 위치는 옮겨도 됩니다.
4. 고유명사와 용어는 `glossary.csv`에서 확인하세요.
5. 풀 리퀘스트를 엽니다. 빠진 자리 표시자나 깨진 행이 있으면 자동 검사가 알려 줍니다.

잘 모르겠는 행은 `translation`을 비워 두세요. 비어 있는 행은 게임에서 영어로 나옵니다.

### CSV 파일 편집

- 작은 수정은 GitHub 웹 편집기로 충분합니다.
- 작업량이 많으면 LibreOffice Calc나 Google Sheets를 쓰세요. 가져올 때는 UTF-8, 쉼표 구분으로 열고, 내보낼 때도 같은 네 열을 그대로 둔 채 UTF-8 CSV로 저장합니다.
- Microsoft Excel은 "CSV UTF-8"로 저장할 때만 쓰세요(한국어 Excel에서는 "CSV UTF-8(쉼표로 분리)"). 다른 형식으로 저장하면 영어가 아닌 글자가 깨집니다.

## `status` 열

| 값 | 뜻 | 할 일 |
| --- | --- | --- |
| (비어 있음) | 문제없음, 또는 아직 번역 전 | `translation`이 비어 있으면 번역합니다 |
| `outdated` | 번역한 뒤에 영어 원문이 바뀌었습니다 | 번역을 고친 뒤 status를 비웁니다 |
| `review` | 리뷰어가 한 번 더 보고 싶어 합니다 | 풀 리퀘스트에서 논의합니다 |

## 게임 텍스트가 바뀔 때

게임이 아직 개발 중이라 영어 텍스트가 자주 추가되고, 바뀌고, 삭제됩니다. 원문이 갱신되면 관리자가 `python tools/l10n.py update`를 실행합니다. 이 명령은 다음 일을 합니다.

- 새 행을 추가하고, 번역 칸은 비워 둡니다.
- 영어가 바뀐 행은 `outdated`로 표시하고, 기존 번역은 그대로 남겨 둡니다.
- 게임에서 사라진 행은 삭제합니다.

## 관리자용

```bash
python tools/export_unity_strings.py --project <path to the Unity project>  # refresh the source (needs PyYAML)
python tools/l10n.py update                                                 # sync every language
python tools/l10n.py init <lang>                                            # open a new language
python tools/l10n.py check                                                  # the same check the pull requests run
python tools/l10n.py status                                                 # progress per language
```

스토리 장면(컷신 대사)은 아직 들어 있지 않습니다. 대본이 확정되면 추가할 예정입니다.
