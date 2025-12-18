# Week 0–2 実行タスクリスト（クリーンルーム＋最小インフラ＋監視）

## Definition of Done（Week 0–2）
- [ ] クリーンルーム手順が文書化され、研究・コード・データの出自（provenance）が追跡可能
- [ ] データ（Spot/Forward/金利/ボラ/主要マクロ）の取得→正規化→保存→QCが自動で回る
- [ ] バックテスト用の最小データモデル（OHLC/ミッド/スプレッド/フォワード/金利）が揃い、再現可能
- [ ] 監視（P&L、エクスポ、レバ、コスト、異常約定、DD）の日次レポート＋アラート条件が動く

## A. クリーンルーム確立（最重要）
### A1. 物理・アカウント分離（即日）
- [ ] 新規PC/新規クラウド/新規Gitを使用（前職端末・前職アカウントは一切使用しない）
- [ ] パスワード管理・2FA・鍵管理（Secrets直書き禁止）

### A2. クリーンルーム・ポリシー（必須）
- [x] `CLEAN_ROOM_POLICY.md` に以下を明記
  - 持ち出し禁止対象: コード、モデル仕様、研究ノート、データ、顧客情報、価格条件、執行ノウハウ等
  - 設計・実装の原則: 公開情報・自前実験・正当ライセンスのデータのみ
  - 禁止事項: 前職パラメータ値・しきい値・重み・例外処理の再現を狙わない

### A3. 証跡（自作の証明）運用
- [x] 研究ノート（1実験=1ページ）
  - 仮説、データソース、前処理、指標定義、パラメータ範囲、結果、採否理由
  - 実行日時、コードのコミットID、データスナップショットID
- [x] Provenance台帳: `PROVENANCE.yaml`
  - データ提供元、契約/ライセンス、取得方法、取得時刻、改変内容、保存先
- [x] 意思決定ログ: `DECISIONS.md`
  - 仕様の理由（しきい値・ゲート・停止条件は必須）

## B. インフラ最小構成（2週間）
### B1. 推奨最小スタック
- [ ] 言語: Python
- [x] 実行: CLI（`make` or `task`）+ OSスケジューラ
- [ ] 保存: Parquet + DuckDB（または Postgres）
- [ ] バージョン: Git（プライベート）
- [x] 実験再現: データスナップショットID必須
- [x] ログ: JSONの構造化ログ

### B2. リポジトリ構成（最小で監査可能）
```
/data_pipeline
  /ingest
  /normalize
  /qc
  /store
/research
  /notebooks_or_reports
  EXPERIMENT_LOG.md
/trading
  /features
  /signals
  /portfolio
  /tca
  /risk
/ops
  /configs
  /alerts
  RUNBOOK.md
PROVENANCE.yaml
CLEAN_ROOM_POLICY.md
DECISIONS.md
```

### B3. データモデル（v1.0最小カラム）
- Spot（バー/EOD）: `ts`(UTC), `pair`, `mid`, `bid`, `ask`（可能なら `open/high/low/close`）
- Forward（1M）: `ts`, `pair`, `fwd_1m_mid`, `spot_mid`
- 金利（OIS/短期）: `ts`, `ccy`, `ois_1m`
- ボラ: `ts`, `pair`, `realized_vol_20d`, `spread_stress`
- 主要マクロ: `ts`, `series_id`, `value`

### B4. 正規化ルール
- タイムゾーンはUTCに統一
- 通貨ペア表記は1方式固定（例: `EURUSD`）
- 欠損は埋めずに欠損フラグを付与
- 1Mロールのカレンダールールを固定

### B5. QC（品質検査）
- 価格ギャップ: 日次で |r| > 8σ 相当はフラグ
- スプレッド異常: SpreadStress = spread / median_60d(spread)
  - SpreadStress > 1.5 は新規禁止候補
- フォワード整合: ln(F/S) の符号・桁が極端ならフラグ
- 休日/薄商い: 時間帯/曜日ルールで抑制

## 監視（Week 0–2で最低限稼働）
### 監視KPI（毎日更新）
- P&L（スリーブ別・ペア別）
- エクスポージャ（通貨別、USDネット、グロス）
- レバ（グロス、想定ボラ、実現ボラ）
- コスト（期待コストbps、実測コストbps、乖離比）
- 異常約定（スリッページ急増、リジェクト率、約定遅延）
- DD（当日/週次/月次/最大）

### アラート条件（v1.0最小セット）
- 日次損失 <= -2.0%（当日新規停止）
- 週次損失 <= -3.5%（リスク半減 + Satellite停止）
- 月次損失 <= -6.0%（月内新規停止）
- DD >= 12%（新規停止）／DD >= 15%（フラット化）
- SpreadStress > 1.5（該当ペア新規禁止）
- 実測コストが期待の1.2倍超（20取引平均）→ Satellite M2禁止 + 回転抑制

## 2週間の作業割付
### Week 0（Day 1–5）
1. [x] `CLEAN_ROOM_POLICY.md`、`PROVENANCE.yaml`、研究ノート雛形を作成
2. [x] リポジトリ雛形と実行コマンド体系（`make spot_pipeline`）を確立
3. [x] Spot取得→保存→QC→日次更新を通す（CSV→SQLiteの最小パイプライン）
   - 実装: `data_pipeline/ingest/spot.py`、`data_pipeline/normalize/spot.py`、`data_pipeline/qc/spot.py`、`data_pipeline/store/spot.py`、`data_pipeline/pipeline/run_spot_daily.py`
4. [ ] 監視の器：日次で指標を集計してファイルに出す

### Week 1（Day 6–10）
1. [ ] Forward（1M）と金利（OIS/短期）を追加、整合QCを追加
2. [ ] ボラ指標（FXVol20、VolJump、SpreadStress）を日次生成
3. [ ] 期待コスト（ExpCost_bps）を算出して保存

### Week 2（Day 11–14）
1. [ ] 監視レポート（日次）を定型化（CSV/HTML/PDF等）
2. [ ] アラート判定（ルールベース）を実装し、ログに残す
   - 実装済み: `ops/alerts/monitor.py`（判定ロジックのみ）
3. [ ] 再現性テスト：同一日付で再実行して同じ結果になることを確認
