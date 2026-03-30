# USE_CASES.md

<!--
このファイルでは、ユースケース仕様をテキストで記述する。
UMLの Fully Dressed Use Case を簡略化し、Domain / State / Operations と
トレースしやすい構造にしている。

関係:
- States: INTERACTION_FLOW.md の状態IDを参照する。
- Operations: REQUIREMENT.md の Public Operations / APIs の OP_ID を参照する。
- Domain: DOMAIN_ER.md のエンティティ・ルールと整合している必要がある。

ルール:
- 各ユースケースは UC-ID 単位で 1 ブロックとして記述する。
- Precondition / Postcondition はできる限り Domain の用語で書く。
- States / Operations は配列のように [] 内にIDを列挙する。
- ErrorCases は代表的なものだけでよいが、「どう扱うか」も簡潔に書くこと。
-->

## Use Cases

### UC-1

- UC_ID: `UC_DEFINE_REQUIREMENTS_WITH_ARCHITECT`
- Title: 要件定義 PR を作成して承認完了まで進める
- Actor: プロジェクト作成者

- Goal: 要件整理用 Issue 上で Architect Bot と複数回対話し、`docs/` 配下の要件定義ドキュメントを完成させ、要件定義 PR を作成して承認完了まで進める。

- Precondition: テンプレートリポジトリから対象の開発用リポジトリが作成済みである。Bot が利用可能である。初期段階では GitHub App は未導入でもよいが、将来的には GitHub App によりサーバー上の Bot を自動起動する前提で設計する。
- Postcondition: 要件定義 PR が作成され、Manager またはユーザーの承認を得たうえでクローズされている。要件不足があった場合は失敗ではなく、Architect Bot との追加対話を経て `docs/` が更新されている。

- States: [ `STATE_REPOSITORY_CREATED` -> `STATE_REQUIREMENT_ISSUE_READY` -> `STATE_REQUIREMENT_DISCOVERY_IN_PROGRESS` -> `STATE_REQUIREMENT_PR_OPEN` -> `STATE_REQUIREMENT_APPROVED` -> `STATE_REQUIREMENT_PR_CLOSED` ]
  <!-- INTERACTION_FLOW.md の状態ID列。例: [STATE_HOME -> STATE_PROFILE_EDIT -> STATE_PROFILE_VIEW] -->

- Operations: [ `OP_CREATE_PROJECT_REPOSITORY`, `OP_OPEN_REQUIREMENT_DISCOVERY`, `OP_REPLY_TO_ARCHITECT`, `OP_UPDATE_REQUIREMENT_DOCUMENTS`, `OP_CREATE_REQUIREMENT_PR`, `OP_APPROVE_REQUIREMENT_PR`, `OP_CLOSE_REQUIREMENT_PR` ]
  <!-- REQUIREMENT.md の OP_ID や主要な操作名を列挙する。 -->

- ErrorCases:
  - 要件整理用 Issue が自動または手動で用意されず、Architect Bot との対話を開始できない。この場合は Issue 作成経路を再確認し、必要なら手動で起票する。
  - Architect Bot が応答しない、または継続対話を更新できない。この場合は Bot 実行経路を確認し、再実行または代替手段で対話を継続する。
  - 要件定義 PR の作成、レビュー、承認のいずれかでフローが停止する。この場合は停止した段階を特定し、コメントや再実行でフローを再開する。

---

### UC-2

- UC_ID: `UC_ORCHESTRATE_DELIVERY_WITH_MANAGER`
- Title: Manager ジョブが実装計画とレビューを継続管理する
- Actor: システム自動起動ジョブ

- Goal: 要件定義 PR の作成を契機に Manager 向けジョブを自動起動し、要件定義の確認、差し戻し判断、マイルストーン設定、Issue 分割、Engineer 成果物のレビューと承認を継続的に行い、最終的に要件達成まで開発全体を管理する。

- Precondition: 要件定義 PR が作成済みである。PR 作成時に GitHub Actions などで Manager 向けジョブを自動起動できる。`docs/` は Manager の判断により差し戻し後に更新される可能性がある。
- Postcondition: Architect が定義した要件が十分に満たされたと Manager が判断し、関連する実装 PR と Issue が承認または完了状態に整理されている。必要に応じて Issue の追加、変更、削除とユーザー確認が記録されている。

- States: [ `STATE_REQUIREMENT_PR_OPEN` -> `STATE_MANAGER_REVIEW_IN_PROGRESS` -> `STATE_REQUIREMENT_CHANGES_REQUESTED` -> `STATE_REQUIREMENT_APPROVED` -> `STATE_REQUIREMENT_PR_CLOSED` -> `STATE_MILESTONE_PLANNING` -> `STATE_IMPLEMENTATION_BACKLOG_READY` -> `STATE_IMPLEMENTATION_PR_OPEN` -> `STATE_IMPLEMENTATION_REVIEW_IN_PROGRESS` -> `STATE_USER_DECISION_REQUIRED` -> `STATE_DELIVERY_COMPLETED` ]

- Operations: [ `OP_TRIGGER_MANAGER_JOB`, `OP_REVIEW_REQUIREMENT_PR`, `OP_REQUEST_ARCHITECT_CHANGES`, `OP_DEFINE_MILESTONE`, `OP_CREATE_IMPLEMENTATION_ISSUES`, `OP_REVIEW_ENGINEER_PR`, `OP_APPROVE_ENGINEER_PR`, `OP_UPDATE_OR_CLOSE_ISSUE`, `OP_ESCALATE_TO_USER` ]

- ErrorCases:
  - Manager ジョブが自動起動されず、要件定義 PR レビューが開始されない。この場合は起動トリガーを確認し、再実行する。
  - Engineer の差し戻しが規定回数を超えても解決せず、Manager だけでは進行判断できない。この場合は解決困難としてユーザー確認に切り替える。
  - マイルストーン定義や Issue 分割の途中で前提要件の不足が見つかる。この場合は Architect への差し戻しまたは追加確認を行ってから再計画する。

---

### UC-3

- UC_ID: `UC_IMPLEMENT_ISSUE_WITH_ENGINEER`
- Title: Engineer ジョブが Issue から実装 PR を作成し承認完了まで進める
- Actor: システム自動起動ジョブ

- Goal: Manager が作成した実装 Issue を契機に Engineer 向けジョブを自動起動し、実装、テスト、PR 作成、差し戻し対応を繰り返して承認とマージ完了まで進める。

- Precondition: Manager により対象の実装 Issue が作成済みである。Engineer 向けジョブを Issue 起点で自動起動できる。対象 Issue には実装に必要な要件、受け入れ条件、関連ドキュメントへの参照が含まれている。
- Postcondition: 実装 PR が承認済みかつマージ済みである。実装不能と判断した場合は PR を作成せず、既存の issue template に沿ったブロッカーコメントが Issue に記録され、Manager が次の判断を行える状態になっている。

- States: [ `STATE_IMPLEMENTATION_BACKLOG_READY` -> `STATE_ENGINEER_JOB_RUNNING` -> `STATE_TEST_FIX_IN_PROGRESS` -> `STATE_IMPLEMENTATION_PR_OPEN` -> `STATE_IMPLEMENTATION_BLOCKED` -> `STATE_ENGINEER_CHANGES_REQUESTED` -> `STATE_IMPLEMENTATION_PR_APPROVED` -> `STATE_IMPLEMENTATION_PR_MERGED` ]

- Operations: [ `OP_TRIGGER_ENGINEER_JOB`, `OP_IMPLEMENT_ISSUE`, `OP_RUN_TEST_SUITE`, `OP_PUSH_IMPLEMENTATION_BRANCH`, `OP_CREATE_IMPLEMENTATION_PR`, `OP_REPLY_TO_MANAGER_FEEDBACK`, `OP_REPORT_IMPLEMENTATION_BLOCKER`, `OP_MERGE_IMPLEMENTATION_PR` ]

- ErrorCases:
  - Engineer が依存不足、設計矛盾、権限不足などにより実装不能と判断する。この場合は PR の代わりに Issue コメントでブロッカー内容を報告する。
  - テスト失敗が長期にわたり解消せず、修正を繰り返しても受け入れ条件を満たせない。この場合は実装不能とみなし、Manager に判断を委ねる。
  - Manager からの差し戻し後に修正方針が確定できない。この場合は Issue と PR の文脈を整理し、必要に応じて追加質問またはブロッカー報告を行う。