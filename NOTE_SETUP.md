# note.com 自動投稿セットアップ手順

errsolved.com の新規記事を GitHub push と同時に note.com へ自動公開する仕組みです。
**note.com には投稿用の公式APIが存在しません。** ここで使っているのは有志が解析した非公式エンドポイントで、ログイン中のブラウザから取得したCookieを使って認証します。note側の仕様変更で予告なく動かなくなる可能性がある点は理解した上でご利用ください（利用規約上のグレーゾーンでもあります）。

## 含まれるファイル

- `scripts/post-to-note.mjs` … 1記事をnote.comに下書き作成→公開するスクリプト
- `.github/workflows/post-to-note.yml` … `src/pages/posts/` に新しい記事がpushされたら自動実行するワークフロー

## 1. note.com のCookieを取得する

1. Chromeなどで https://note.com にログインしておく
2. デベロッパーツールを開く（F12 または右クリック→検証）
3. 「Application」タブ →「Cookies」→「https://note.com」を選択
4. 以下3つの値をコピーしておく（表示されているValueをそのまま使います）
   - `note_gql_auth_token`
   - `_note_session_v5`
   - `XSRF-TOKEN`（存在する場合。無くても動く可能性はありますが、あれば設定推奨）

これらは通常のログインセッションなので、**他人と共有しないでください**。また一定期間で失効します（失効するとワークフローが401/403エラーで失敗するので、その時は取り直して再登録してください）。

## 2. GitHub Secretsに登録する

リポジトリの `Settings` → `Secrets and variables` → `Actions` を開き、以下を登録します。

| 種類 | 名前 | 値 |
|---|---|---|
| Secret | `NOTE_GQL_AUTH_TOKEN` | 手順1でコピーした `note_gql_auth_token` |
| Secret | `NOTE_SESSION_V5` | 手順1でコピーした `_note_session_v5` |
| Secret | `NOTE_XSRF_TOKEN` | 手順1でコピーした `XSRF-TOKEN`（無ければ省略可） |
| Variable | `SITE_BASE_URL` | `https://errsolved.com`（省略時もこの値が使われます） |

Secretは`Secrets`タブ、Variableは`Variables`タブに分かれているので登録場所に注意してください。

## 3. 動作テスト

1. 実際にテスト用の記事を1本 `src/pages/posts/` に追加してpush
2. GitHubの「Actions」タブでワークフローの実行結果を確認
3. note.comの自分のページで、記事が公開されているか確認

初回は必ずテスト記事1本で動作確認してから、通常運用に入ることをおすすめします。

## 記事本文の扱いについて

note側の記事本文の冒頭に、自動で元記事（errsolved.com）へのリンクを挿入しています。文面を変えたい場合は `scripts/post-to-note.mjs` 内の `buildNoteBodyHtml` 関数を編集してください。

タグはfrontmatterの `category`（Git / Linux / Docker / Node.js / Cloudflare / Astro）をそのまま1つ設定しています。

## うまくいかない場合

- **401 / 403エラー**: Cookieが失効しています。手順1からやり直してSecretsを更新してください。
- **公開ステップだけ失敗する**: note.com側では下書きとして記事は作成済みです。ログインして手動で公開するか、エラーログの内容を確認して `publishNote` 関数のリクエスト内容を調整する必要があります（noteの非公式APIは仕様変更されることがあります）。
- **本文の見た目が崩れる**: Markdown→HTML変換（`marked`）の出力とnoteのエディタ仕様が完全には一致しない場合があります。実際に投稿された記事を見ながら `buildNoteBodyHtml` を調整してください。

## 運用上の注意

- 非公式API利用によるnoteアカウントの制限・凍結リスクはゼロではありません。最初は少数の記事で様子を見ることを推奨します。
- Cookieには強い権限があるため、GitHub Secretsの管理（リポジトリのコラボレーター権限など）に注意してください。
- 将来的にnote側がAPIの認証方式（reCAPTCHA導入など）を強化した場合、追加の対応が必要になる可能性があります。
