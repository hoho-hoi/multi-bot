# Project Requirements

<!--
このファイルはプロジェクトの要件定義のメインエントリです。
Goal / Domain / Interaction / Architecture の4本柱をまとめて記述します。

他の設計ファイルとの関係:
- ドメイン構造: DOMAIN_ER.md
- インタラクション状態遷移: INTERACTION_FLOW.md
- コンポーネント構成: ARCHITECTURE_DIAGRAM.md
- ユースケース詳細: USE_CASES.md

運用ルール:
- 「TBD」や空欄のままにせず、すべての項目に具体的な内容を埋めてから次フェーズに進むこと。
- 説明文は必要に応じて削除してよいが、見出し・項目名は原則残すこと。
-->

---

## 1. Overview (Goal / Scope)

### 1.1 Product Summary

<!-- プロジェクトの概要を短く定義する。 -->

- Goal: GitHub 上で要件定義、実装計画、実装、レビューを役割別 Bot が分担しながら進められるマルチ Bot 開発基盤を、将来の分離を見据えた monorepo で立ち上げる。
- Target Users: GitHub 上で新規ソフトウェア開発を進めるプロジェクト作成者、要件定義の依頼者、レビュー担当者、Bot 運用者。
- One-line Description: テンプレートから作成した GitHub リポジトリ上で、Architect・Manager・Engineer の各 Bot が Issue / PR / コメントを起点に自動連携する monorepo ベースの開発基盤。

### 1.2 Scope

<!--
スコープ内とスコープ外を明確に切り分ける。
「やらないこと」を書くことでスコープの暴走を防ぐ。
-->

- In Scope: テンプレートから作成された開発用リポジトリを対象に、要件整理用 Issue の起点管理、Architect による対話型要件定義、Manager による要件レビューとマイルストーン別 Issue 分割、Engineer による Issue 起点の自動実装と PR 作成、Manager による継続レビュー、role と provider の分離、control-plane と worker-runtime の疎結合設計、GitHub Actions 起点の自動ジョブ実行、将来の GitHub App 移行を見据えた抽象化。
- Out of Scope: 初期段階での本物の GitHub App 導入、installation token 発行、本番デプロイ、Kubernetes、複雑な DB 正規化、複数 provider の実稼働、実リポジトリへの高度な認可制御、完全自動マージ戦略、初回実装時点での複数リポジトリ分離。

### 1.3 Success Criteria & Constraints

<!--
成功判定の基準と、守るべき制約条件を記述する。
例: 指標(DAU, 継続率, 応答時間)や締切、対応プラットフォームなど。
-->

- Success Criteria: monorepo 内に責務境界が明確に定義されていること、control-plane と worker-runtime が shared contracts のみで接続されていること、Architect / Manager / Engineer の主要フローが `docs/` で一貫して説明できること、最小縦切りとして Issue コメント起点の Architect 応答が成立すること、Manager / Engineer の自動起動前提が設計上表現されていること。
- Constraints: 初期実装は monorepo を前提とし、role と provider を密結合させないこと、control-plane は worker-runtime の内部実装を直接参照しないこと、Cursor 固有処理は provider adapter に閉じ込めること、GitHub App は将来対応とし初期自動化は GitHub Actions などで代替すること、要件不足は異常ではなく対話で補完すること。

---

## 2. Domain Model (Domain)

### 2.1 Domain Entities

<!--
ドメインエンティティとその関係は DOMAIN_ER.md に mermaid の erDiagram 形式で記述する。

DOMAIN_ER.md では、各エンティティに storage_scope をコメントで付与する運用を想定する:
- Ephemeral          : 1操作 / 1フレーム内だけで完結する一時データ
- Session            : セッション(ログイン中, ゲーム1プレイ中 等)の間維持されるデータ
- DeviceLocal        : デバイス上に永続化され、主にそのデバイスだけで利用されるデータ
- UserPersistent     : ユーザアカウントに紐づき、複数デバイス間で共有されるデータ
- GlobalPersistent   : システム全体で共有される永続データ
-->

- Domain ER Diagram: see `DOMAIN_ER.md`  

### 2.2 Domain Notes (Optional)

<!--
ER 図だけでは表現しづらいルールや補足がある場合に記述する。
何もなければ空でもよい。
-->

- Notes: 主要ドメインは「GitHub リポジトリ上で複数 Bot が開発フローを進める運用」であり、永続データの中心は GitHub 上の Issue / PR / コメント / ドキュメントである。初期実装では Bot 実行状態やセッションは in-memory でもよいが、将来的にサーバー常駐型へ移行できる境界を維持する。

---

## 3. Interaction / UI / Operations

### 3.1 Interaction State Flow

<!--
システム全体のインタラクション状態遷移は INTERACTION_FLOW.md に mermaid flowchart で記述する。

ルール:
- ノードIDは状態(State)IDとして扱う（例: STATE_TITLE, STATE_IN_GAME 等）。
- 矢印には可能な限り「イベント名」をラベルとして付ける。
  例: |start_button_clicked|, |timer_expired|, |message_received| など。
-->

- Interaction State Diagram: see `INTERACTION_FLOW.md`  

### 3.2 Public Operations / APIs

<!--
クライアント(人間・他システム・外部アプリ等)から見える操作/インターフェースを列挙する。
Web の場合は HTTP パス、CLI の場合はコマンド、ゲーム/組み込みの場合は公開APIやメッセージ名など。

列挙した OP_ID は USE_CASES.md の Operations から参照される前提。
-->

| OP_ID | Interface / Path / Command | Summary |
|-------|----------------------------|---------|
| `OP_CREATE_PROJECT_REPOSITORY` | GitHub: use template repository | テンプレートから開発用リポジトリを作成する。 |
| `OP_OPEN_REQUIREMENT_DISCOVERY` | GitHub Issue: requirement discovery issue | 要件整理用 Issue を用意し、Architect との対話を開始できる状態にする。 |
| `OP_REPLY_TO_ARCHITECT` | GitHub Issue comment | プロジェクト作成者が要件補足や回答を返す。 |
| `OP_UPDATE_REQUIREMENT_DOCUMENTS` | Git branch update on `docs/` | Architect が `docs/` 配下の要件定義ドキュメントを更新する。 |
| `OP_CREATE_REQUIREMENT_PR` | GitHub Pull Request | 要件定義ドキュメントを PR として提出する。 |
| `OP_APPROVE_REQUIREMENT_PR` | GitHub Pull Request review | Manager またはユーザーが要件定義 PR を承認する。 |
| `OP_CLOSE_REQUIREMENT_PR` | GitHub Pull Request close / merge | 要件定義 PR をクローズし、要件定義フェーズを完了する。 |
| `OP_TRIGGER_MANAGER_JOB` | GitHub Actions on PR events | 要件定義 PR 作成や更新を契機に Manager ジョブを自動起動する。 |
| `OP_REVIEW_REQUIREMENT_PR` | Manager review workflow | Manager が `docs/` と PR 内容を確認する。 |
| `OP_REQUEST_ARCHITECT_CHANGES` | GitHub PR comment / review request changes | Manager が Architect に差し戻しを行う。 |
| `OP_DEFINE_MILESTONE` | Manager planning workflow | Manager が直近のマイルストーンを定義する。 |
| `OP_CREATE_IMPLEMENTATION_ISSUES` | GitHub Issue creation | マイルストーン到達までに必要な実装 Issue を作成する。 |
| `OP_UPDATE_OR_CLOSE_ISSUE` | GitHub Issue edit / close | Manager が Issue の内容変更、追加、削除、クローズを行う。 |
| `OP_ESCALATE_TO_USER` | GitHub Issue / PR comment to user | Manager が解決困難時にユーザーへ確認を求める。 |
| `OP_TRIGGER_ENGINEER_JOB` | GitHub Actions on Issue events | 実装 Issue を契機に Engineer ジョブを自動起動する。 |
| `OP_IMPLEMENT_ISSUE` | Engineer execution workflow | Engineer が Issue の要件に沿って実装を進める。 |
| `OP_RUN_TEST_SUITE` | Repository test command | Engineer がテストを実行し、失敗時は修正を継続する。 |
| `OP_PUSH_IMPLEMENTATION_BRANCH` | Git push | Engineer が実装ブランチを push する。 |
| `OP_CREATE_IMPLEMENTATION_PR` | GitHub Pull Request | Engineer が必須成果物として実装 PR を作成する。 |
| `OP_REVIEW_ENGINEER_PR` | Manager PR review workflow | Manager が Engineer PR をレビューする。 |
| `OP_REPLY_TO_MANAGER_FEEDBACK` | GitHub PR update | Engineer が差し戻し内容を反映し、再 push する。 |
| `OP_APPROVE_ENGINEER_PR` | GitHub Pull Request review approve | Manager が Engineer PR を承認する。 |
| `OP_REPORT_IMPLEMENTATION_BLOCKER` | GitHub Issue comment with template | Engineer が実装不能時に issue template 準拠のブロッカー報告を行う。 |
| `OP_MERGE_IMPLEMENTATION_PR` | GitHub Pull Request merge | 承認済み PR をマージして実装を完了する。 |

### 3.3 Use Cases

<!--
ユースケースの詳細仕様は USE_CASES.md に記述する。

ここでは「ユースケースの一覧」や「重要なユースケースIDだけ」を簡潔に列挙しておくとよい。
-->

- Key Use Case IDs: `UC_DEFINE_REQUIREMENTS_WITH_ARCHITECT`, `UC_ORCHESTRATE_DELIVERY_WITH_MANAGER`, `UC_IMPLEMENT_ISSUE_WITH_ENGINEER`

---

## 4. Architecture

### 4.1 Components & Data Flow

<!--
システムを構成する主要なコンポーネント(箱)とデータフローは ARCHITECTURE_DIAGRAM.md に mermaid flowchart で記述する。

ルール:
- ノードはコンポーネント(例: Frontend, API Server, GameServer, DeviceController 等)。
- 外部サービス・外部デバイスはノード名に「(外部)」を付ける。
- 矢印には可能な限り「代表的な操作/プロトコル名」をラベルとして付ける。
  例: |HTTP /api/login|, |gRPC Match|, |I2C Read| など。
-->

- Architecture Diagram: see `ARCHITECTURE_DIAGRAM.md`  

### 4.2 Storage Scope Policy

<!--
DOMAIN_ER.md で付与した storage_scope を、具体的なストレージ/媒体にマッピングする方針を記述する。
例: UserPersistent -> クラウドDB, Session -> サーバメモリ+キャッシュ 等。
-->

- Ephemeral: 1回の Bot 実行で組み立てるプロンプト、差分コンテキスト、テスト実行中の一時結果などはワーカープロセス内の一時メモリに保持する。
- Session: Issue / PR ごとの会話要約、最新の open questions、現在のフェーズ、直近のレビュー結果は control-plane 側の session store に保持する。初期実装は in-memory を許容し、将来は Redis や DB に置き換え可能とする。
- DeviceLocal: ワーカー実行用の一時 worktree、ローカルキャッシュ、Actions ランナー上の一時ファイルを配置する。消失前提のため唯一の正本にはしない。
- UserPersistent: 初期実装では専用のユーザー永続ストアは持たず、必要なユーザー情報は GitHub アカウントと Issue / PR 上の記録を参照する。
- GlobalPersistent: GitHub 上のリポジトリ、Issue、PR、コメント、`docs/`、テンプレート、shared contracts、監査用ログをシステムの主要な永続データとして扱う。

### 4.3 Non-Functional Requirements (Architecture-related)

<!--
アーキテクチャ設計に強く影響する非機能要件のみを記述する。
詳細なSLAや細かい数値要件がある場合は別ドキュメントに分けてもよい。
-->

- Performance / Throughput: 初期実装では高スループットよりもフローの明確さを優先するが、Issue / PR イベントごとに独立ジョブとして処理できる構造にし、将来的に並列ジョブ実行と再試行を追加しやすくする。
- Security / Authentication / Authorization: シークレットのハードコードは禁止し、GitHub 操作権限は最小権限で分離する。初期実装は GitHub Actions の認証を利用し、将来は GitHub App installation token へ移行できるよう抽象化する。ユーザー入力をそのまま実行コマンド化しない。
- Availability / Reliability / Backup: GitHub 上の Issue / PR / `docs/` を正本とし、ワーカー失敗時は同一イベントの再実行や再コメントで回復できる構造にする。長期状態は in-memory に閉じ込めず、将来外部ストアへ移行可能にする。
- Observability (Logging / Metrics / Tracing / Alerting): 各ジョブに trigger event、role、provider、repository、issue / PR 番号、結果サマリを紐づけてログ化し、後でジョブ履歴を追跡できるようにする。失敗時は GitHub コメントまたはログから停止地点を特定できることを重視する。
- Other NFRs: monorepo でも責務境界を維持し、将来 `template-repo`、`control-plane`、`worker-runtime` を分離しやすい構造を守る。role と provider の追加時に既存の runner や shared contracts を壊さない拡張性を優先する。