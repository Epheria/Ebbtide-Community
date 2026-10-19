# 녹음 파일 제출 안내

[English](../VOICE_SUBMISSIONS.md) · [UI·대본 번역 안내](CONTRIBUTION_WORKFLOW.md)

**배정받은 비공개 Google Drive 폴더에 녹음 파일을 올리고, 작업 시트에서 `Ready to submit`을 체크해 주세요.** 관리자 계정의 연결 스크립트가 파일을 확인하고, 작업자가 수정할 수 없는 제출 기준본을 별도로 보관한 뒤 접수 기록을 남깁니다. 이후 다른 검수자가 해당 파일을 듣고 승인하면 GitHub 봇이 **제출 목록만 담은 PR**을 만듭니다. 녹음 원본은 Drive에 보관합니다.

체크박스는 접수 요청입니다. 체크만으로 녹음이 승인되거나 PR이 생성·병합되거나 게임에 반영되지는 않습니다. 관리자가 Google 권한 승인과 작업 배정을 마치고 GitHub 워크플로를 기본 브랜치에 반영해야 실제로 동작합니다. 공개 참고용 양식에서는 제출할 수 없습니다.

## 성우·녹음 작업자

1. Discord 티켓이나 [음성 작업 지원서](../../../../issues/new?template=voice_actor.yml)로 지원해 주세요. 전체 분량을 녹음하기 전에 배역과 기여 약관을 합의합니다.
2. 관리자가 언어, 배역, 캐스팅 슬롯, 녹음 버전과 정확한 대사 ID를 배정할 때까지 기다립니다. 비공개 업로드 폴더와 전용 작업 시트를 받으세요. 공개 대본 시트는 참고 자료입니다.
3. 대사 하나에 파일 하나를 만듭니다. 파일명은 `SL_Select.flac`처럼 배정된 ID 뒤에 `.flac` 또는 `.wav`를 붙입니다. 같은 이름의 현재 파일은 하나만 두고, 지정된 폴더 바로 안에 올립니다. 하위 폴더, 바로가기, ZIP, 중복 파일명은 받지 않습니다.
4. `Recording Uploads` 탭의 `Take file`에 실제 파일명을 넣습니다. `Drive URL`은 비워도 됩니다. 연결 스크립트가 폴더에서 정확한 이름으로 찾습니다. 링크를 넣는다면 폴더 링크가 아닌 해당 Drive 파일의 직접 링크를 사용하세요.
5. **배정된 모든 대사**를 올린 다음 각 행의 `Ready to submit`을 체크합니다. 모든 배정 행이 함께 체크되어 있어야 합니다. 일부만 제출해야 한다면 관리자에게 작업 범위를 나눠 달라고 요청하세요.
6. `Result`를 확인하세요. 성공하면 `Submitted`와 접수 해시가 표시되고 체크가 해제됩니다. `Not submitted`라면 안내된 문제를 고친 뒤 다시 체크하세요. 아무 반응이 없다면 관리자에게 문의하세요. 체크가 남아 있다는 이유만으로 접수가 끝난 것은 아닙니다.
7. 청취 검수를 기다립니다. 재녹음이 필요하면 업로드 폴더의 현재 파일을 교체하고 다시 체크하세요. 파일 내용이 바뀌면 새 접수 기록이 생깁니다. 보관된 제출 기준본을 직접 수정하거나 비공개 녹음 링크를 공개 채널에 올리지 마세요.

녹음 제출에 Git 설치, 저장소 복제, 개인 GitHub 토큰은 필요하지 않습니다. 관리자가 작업자를 대신해 미리보기를 요청할 수 있습니다. 최종 청취 승인 담당자는 본인의 GitHub 계정이 필요합니다.

### 녹음 사양

- FLAC 또는 PCM WAV. 모노, 44.1/48 kHz, 16/24 bit. FLAC을 권장합니다.
- **파일당 20 MiB, 한 번의 제출에 100 MiB, 작업당 200개 대사**까지 받습니다. 넘는 작업은 관리자와 나눕니다.
- 음악·잔향·무전 필터 없이 잡음이 적은 원음으로 녹음합니다. 무전 효과는 게임에서 넣습니다.
- 클리핑을 피하고 대사 앞뒤에 약 0.5초 여유를 둡니다.
- [CONTRIBUTOR_TERMS.md](../../CONTRIBUTOR_TERMS.md)를 읽어 주세요. 본인의 목소리여야 하며 AI 생성·변조 음성은 받지 않습니다. 만 18세 미만은 보호자의 동의도 필요합니다.

스크립트는 WAV/FLAC 기본 헤더, 채널·샘플 형식, 이름, 파일 해시를 확인합니다. 전체 음성을 디코딩하거나 잡음, 클리핑, 발음, 연기, 게임 적합성을 판단하지 않습니다. 사람이 직접 들어야 합니다.

## 청취 검수자

관리자가 **접수 당시 별도로 보관한 파일**의 읽기 권한을 검수자에게 개별로 제공합니다. 공개 목록에 Drive URL이 있어도 권한 없이는 파일을 열 수 없습니다. 작업자에게 폴더를 공개로 바꿔 달라고 요청하지 마세요.

배정된 **Voice recording work order** GitHub 이슈에 댓글로 명령을 입력합니다.

```text
/voice preview
```

봇이 저장한 미리보기를 열고, 그 미리보기에 연결된 비공개 기준 파일을 모두 들어 주세요. 배정 언어·대본·상황·대사 ID와 비교합니다. 음질, 배역의 일관성, 기여 약관과 재녹음 내용을 확인합니다. 작업자의 업로드 폴더는 이후 교체될 수 있으므로 그것만 듣고 승인하면 안 됩니다.

해당 미리보기를 승인한다면 배정된 검수자가 댓글을 남깁니다.

```text
/voice approve <sha256>
```

봇의 미리보기 답변에서 `Digest:` 뒤 **64글자 전체**를 복사해 `<sha256>`만 바꿉니다. 작업자와 검수자는 서로 다른 GitHub 사용자여야 합니다. 봇이 변경 여부를 다시 확인한 뒤 목록 PR을 만들고, 관리자가 검토·병합합니다. 접수 내용·대본·대상 파일이 바뀌었다면 봇 안내에 따라 새 미리보기나 배정을 준비합니다.

## 관리자

### 작업 배정

[Voice recording work order](../../../../issues/new?template=voice_work_order.yml)를 만들고 언어, 배역, 캐스팅 슬롯, 양의 정수인 녹음 버전, 작업자, 별도 검수자, 공개 열람용 접수 시트와 탭, 처음·마지막 대사 ID를 넣습니다. 탭 이름은 `Recording Outbox`입니다. 비공개 폴더 ID, 이메일, 티켓 내용은 공개 이슈에 넣지 마세요.

```text
/voice assign
```

관리자가 위 댓글을 남기고 봇의 배정 확인을 기다립니다. 대사 ID와 대본 해시가 작업 등록부에 고정됩니다. 캐스팅 슬롯은 합의한 다른 캐릭터를 구분하는 값입니다. 다른 사람의 배정을 피하려고 임의로 만들지 않습니다. 다른 언어로 녹음하려면 먼저 승인된 대사 번역이 저장소에 반영되어 있어야 합니다. 정식 대사 ID가 없는 기획안은 배정하지 않습니다.

작업마다 **관리자가 소유한 별도 작업 시트**를 만들고 `Recording Uploads` 양식을 복사합니다. 작업자에게 연결된 Apps Script나 관리자 설정을 공유하지 않습니다. 파일명을 미리 채우고 참고·원문 열을 보호합니다. 작업자에게 `Drive URL`과 `Ready to submit`만 편집하도록 허용합니다. 확장자를 바꿔야 하면 관리자가 파일명을 수정할 수 있습니다. 특정 사용자에게만 공유하고 “링크가 있는 모든 사용자 편집”은 사용하지 않습니다.

비공개 Incoming 아래에 전용 업로드 폴더를 만들고 해당 작업자에게만 업로드·편집 권한을 줍니다. Received 아래에는 관리자를 제외하고 접근할 수 없는 작업별 보관 폴더를 만듭니다. 상위 폴더와 보관 폴더는 관리자 전용으로 두고, 검수자에게는 제출 기준 파일의 읽기 권한만 개별로 제공합니다. 진행 중인 작업끼리 시트나 폴더를 재사용하지 마세요.

### 관리자 연결 스크립트 설치

1. 관리자 Drive의 **독립형 Apps Script 프로젝트**를 사용합니다. 작업자에게 공유된 폴더 밖에 만들고 프로젝트 자체도 공유하지 않습니다. 공유 시트의 확장 프로그램 메뉴에서 만들면 시트 편집자가 스크립트도 수정할 수 있으므로 사용하지 않습니다.
2. [`Code.gs`](../../tools/drive_voice_bridge/Code.gs)와 [`appsscript.json`](../../tools/drive_voice_bridge/appsscript.json)을 복사합니다. 웹 앱 배포는 필요하지 않습니다.
3. `bootstrapOwnerConfiguration`의 시트·폴더 ID를 확인하고 관리자로 실행합니다. Google 권한 화면에서 Drive 읽기·복사, Sheets 쓰기, 트리거 설치, 계정 식별 권한을 승인해야 합니다. GitHub 자격 증명이나 OAuth 토큰을 시트·설정 객체·저장소에 적지 않습니다.
4. `coordinatorHealthCheck`를 실행합니다. 배정 목록이 비어 있어도 점검할 수 있으며, 가짜 작업자나 트리거를 만들지 않습니다. 초기 설정 함수를 다시 실행해도 기존 배정은 보존합니다.
5. 작업을 실제로 합의한 뒤 관리자 전용 임시 함수에서 `setupCoordinator(config)`를 호출합니다. 아래 구조에 봇의 `/voice assign` 답변에 나온 `Script SHA256`과 대사 ID를 넣습니다. 답변을 찾기 어렵다면 `community-voice-state` 브랜치의 해당 이슈 항목에서 `script_hash`를 확인합니다. 게임 버전·시트 제목·파일명으로 해시를 추측하지 않습니다. 설정하면 작업 시트마다 관리자 권한의 편집 트리거를 설치하고 공개 Outbox를 관리자 전용 편집으로 보호합니다.
6. 실제 작업자·검수자와 한 번 확인합니다. 작업자가 체크하고, 관리자 접수가 끝나고, 검수자가 기준 파일을 열 수 있어야 합니다. 코드 검사나 빈 배정 목록 점검만으로 실제 파일 제출을 검증했다고 보지는 않습니다.

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

위 코드는 예시이며 실제 배정이 아닙니다. 설정할 때 **진행 중인 전체 목록**을 넣어야 합니다. 빠진 작업의 트리거는 해제됩니다. 한 프로젝트는 동시에 18개 작업 시트까지 사용합니다. 설정은 비공개 프로젝트의 Script Properties에 저장됩니다. 완료·취소한 작업은 목록에서 제거하세요.

독립형 프로젝트에는 시트 메뉴를 만들지 않습니다. Google의 사용자 메뉴는 시트에 연결된 스크립트가 필요하기 때문입니다. 관리자는 비공개 스크립트 편집기에서 `submitReadyRecordings`를 직접 실행해 재시도할 수 있습니다. 작업자는 체크박스를 편집하면 됩니다. API나 다른 스크립트가 체크 값을 써 넣으면 편집 트리거가 실행되지 않습니다.

Google 공식 문서: [독립형 스크립트](https://developers.google.com/apps-script/guides/standalone), [설치형 트리거](https://developers.google.com/apps-script/guides/triggers/installable), [연결된 스크립트 접근 권한](https://developers.google.com/apps-script/guides/bound), [사용자 메뉴 제약](https://developers.google.com/apps-script/reference/base/menu).

### 입력·접수 열

작업자의 `Recording Uploads` 첫 행:

```text
Take file,Drive URL,Ready to submit,Result
```

`Ready to submit`은 실제 체크박스입니다. `TRUE`라는 글자를 직접 입력하지 마세요. `Result`는 스크립트의 접수 결과이며 청취 승인 상태가 아닙니다.

입력 탭에는 내용이 있는 대사 행을 200개까지만 둡니다. Outbox는 접수 데이터 20,000행까지 읽습니다. 한도에 도달하면 관리자가 완료·취소된 작업의 기록을 별도 읽기 전용 보관본으로 옮겨야 합니다. 진행 중인 작업의 기록은 유지합니다.

공개 열람·관리자 전용 편집인 `Recording Outbox` 첫 행:

```text
Work order,Take file,Drive snapshot,SHA256,Bytes,MIME type,Revision,Submitted,Script SHA256
```

- `Work order`: 정확한 GitHub 작업 이슈 번호.
- `Take file`: 확장자를 제외한 정식 대사 ID.
- `Drive snapshot`: 관리자가 소유한 제출 기준 파일의 직접 링크. 링크만으로 접근 권한이 생기지 않습니다.
- `SHA256`, `Bytes`, `MIME type`: 파일 해시, 정확한 바이트 수, `audio/wav` 또는 `audio/flac`.
- `Revision`: 이슈·대본 해시·대사 순서·파일명·파일 해시를 묶은 64글자 접수 해시. 새 접수는 직전 기록도 함께 묶으므로 이전 음성으로 되돌려도 과거 기록을 재사용하지 않고 새 현재 기록을 만듭니다.
- `Submitted`: `2026-10-20T00:00:00Z` 형식의 UTC 접수 시각.
- `Script SHA256`: 발화문과 원문 상황까지 포함하는 배정 당시의 `script_hash`.

연결 스크립트는 배정 폴더 바로 아래에 있는 정해진 이름의 파일만 받습니다. 작업자 파일이나 공유 권한을 변경하지 않고 관리자가 소유한 비공개 사본을 만듭니다. 모든 사본이 확인된 뒤 접수 목록 전체를 한 번에 기록합니다.

파일 내용이 같은 재시도는 기존 접수와 사본을 재사용합니다. 바뀐 파일은 새 접수 해시가 생깁니다. 사본을 일부 만들다 멈춰도 승인이나 PR은 생성하지 않습니다. 다시 시도하면 일치하는 사본을 재사용합니다. Outbox 기록 자체가 일부만 있거나 맞지 않으면 관리자 확인이 필요합니다. 오류를 넘기려고 승인으로 표시하지 마세요. 이전 접수는 검수 기록으로 보존합니다.

### 마무리

미리보기와 청취 승인이 끝나면 봇은 목록만 담은 PR을 엽니다. 승인된 비공개 파일과 해시를 기록하며 WAV/FLAC을 공개 GitHub에 올리거나 Drive를 공개하거나 Unity로 가져오지는 않습니다.

관리자가 검토·병합하고 `/voice sync`로 상태를 맞춥니다. 열린 PR이 없을 때는 `/voice release`로 취소할 수 있습니다. PR이 열려 있다면 먼저 닫아야 합니다. 완료한 대사를 다시 녹음할 때는 더 높은 녹음 버전으로 새 작업을 만듭니다. 대본이 바뀌었다면 새 원문 기준으로 배정도 갱신합니다.

개발자가 승인된 비공개 사본을 내려받아 SHA-256이 맞는지 확인한 뒤 게임에 반영합니다. 청취 승인, GitHub 병합, 게임 반영은 각각 별도 단계입니다.
