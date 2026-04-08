# Kanban Board

Firebase Firestore をバックエンドにしたシンプルなカンバンボード。1ファイルでデスクトップ・モバイル両対応。

## ファイル構成

| ファイル | 説明 |
|---|---|
| `index.html` | デスクトップ・モバイル共通。レスポンシブ対応 |
| `check_kanban.py` | 停滞タスク・期日チェックスクリプト（サービスアカウント認証） |
| `collect_weather.py` | 習志野の気象データ取得。wttr.in + Open-Meteo フォールバック |
| `collect_browser_log.py` | Edge閲覧履歴の日次サマリー |
| `health_dashboard.py` | 体調×気象ダッシュボードHTML生成（ローカル用） |
| `add_tasks.js` | Firestoreへのタスク一括追加（Node.js / firebase-admin） |

## 機能

- **3ステータス管理**: Todo / Doing / Done
- **スイムレーン**: 仕事（上1/3固定）/ 個人（下2/3）に分離。カードのボタンでワンタップ切り替え
- **カテゴリ**: Daily / Personal / Work / Study / Kids / Other
- **期日設定**: 期限切れ・3日以内は色付きバッジで警告
- **毎日の繰り返し**: タスクに🔄フラグを付けると毎日 Todo に自動追加
- **ドラッグ&ドロップ**: デスクトップでカード移動・並び替え
- **スワイプ操作**: モバイルでカードをスワイプしてステータス変更
- **ピン留め**: 重要タスクをカラム上部に固定
- **カテゴリフィルター**: チップで絞り込み表示
- **リアルタイム同期**: Firestore `onSnapshot` で複数端末同期
- **完了エフェクト**: タスク完了時にコンフェッティアニメーション
- **気圧予報ウィジェット**: デスクトップのフィルターバーに7日間の気圧予報を表示（Open-Meteo API）。低気圧（<1005hPa）・急落日（≥-8hPa）を赤枠で警告

## 使い方

HTMLファイルをブラウザで直接開くだけで動作します（Firebase接続済み）。

```
open index.html
```

## 技術スタック

- Vanilla JS (ES Modules)
- Firebase Firestore v12（CDN）
- CSS カスタムプロパティ・メディアクエリ
- HTML5 Drag and Drop API（デスクトップ）
- Touch Events（モバイル）

## データ

Firestore の `tasks` コレクションにデータを保存。初回起動時にデフォルトタスクを投入し、以降はリアルタイムリスナーで同期します。

## 自動チェック（cron）

`check_kanban.py` を毎朝 8:03 に実行。Doing で 7 日以上停滞しているタスク・期日切れタスクを検知して `~/.claude/projects/.../memory/kanban_log.md` に記録します。サービスアカウント認証（`~/.firebase/kanban-service-account.json`）でFirestoreにアクセスします。

## 気象・体調連携

`collect_weather.py` で習志野の気象データを取得し、`health_log.md` に記録。前日比の気圧変化も Open-Meteo Archive API から取得して付与します。Kanbanのデスクトップ画面には7日間の気圧予報ウィジェットを表示。
