# Kanban Board

Firebase Firestore をバックエンドにしたシンプルなカンバンボード。デスクトップ版とモバイル版の2ファイル構成。

## ファイル構成

| ファイル | 説明 |
|---|---|
| `kanban.html` | デスクトップ向け。3カラム横並びレイアウト |
| `kanban-mobile.html` | モバイル向け。タブ切り替えUI、Safe Area対応 |

## 機能

- **3ステータス管理**: Todo / Doing / Done
- **カテゴリ**: Daily / Personal / Work / Study / Kids / Other
- **ドラッグ&ドロップ**: カード間の移動・並び替え
- **ピン留め**: 重要タスクをカラム上部に固定
- **毎日の繰り返しタスク**: テンプレート登録で毎日自動追加
- **カテゴリフィルター**: チップで絞り込み表示
- **リアルタイム同期**: Firestore `onSnapshot` で複数端末同期
- **完了エフェクト**: タスク完了時にコンフェッティアニメーション

## 使い方

HTMLファイルをブラウザで直接開くだけで動作します（Firebase接続済み）。

```
open kanban.html         # デスクトップ
open kanban-mobile.html  # モバイル
```

## 技術スタック

- Vanilla JS (ES Modules)
- Firebase Firestore v12（CDN）
- CSS カスタムプロパティ
- HTML5 Drag and Drop API

## データ

Firestore の `tasks` / `repeats` コレクションにデータを保存。初回起動時にデフォルトタスクを投入し、以降はリアルタイムリスナーで同期します。
