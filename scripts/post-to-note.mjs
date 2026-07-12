#!/usr/bin/env node
/**
 * post-to-note.mjs
 *
 * errsolved.com (Astro) の記事を note.com に自動投稿するスクリプト。
 *
 * note.com には投稿用の公式APIが存在しないため、ブラウザから取得した
 * ログイン用Cookie (note_gql_auth_token / _note_session_v5) を使って
 * 非公式のエンドポイントを呼び出しています。
 * note側の仕様変更で動かなくなる可能性がある点に注意してください。
 *
 * 使い方:
 *   node scripts/post-to-note.mjs src/pages/posts/example.md
 *
 * 必要な環境変数:
 *   NOTE_GQL_AUTH_TOKEN  ... note.com の Cookie "note_gql_auth_token" の値
 *   NOTE_SESSION_V5      ... note.com の Cookie "_note_session_v5" の値
 *   NOTE_XSRF_TOKEN       ... note.com の Cookie "XSRF-TOKEN" の値（URLデコード前でOK。任意だが推奨）
 *   SITE_BASE_URL         ... 元記事の公開先ベースURL（省略時 https://errsolved.com）
 *
 * 依存パッケージ（実行前に npm install --no-save gray-matter marked などでインストールしてください）:
 *   gray-matter, marked
 */

import { readFileSync } from "node:fs";
import path from "node:path";
import matter from "gray-matter";
import { marked } from "marked";

const NOTE_BASE = "https://note.com/api";
const SITE_BASE_URL = process.env.SITE_BASE_URL || "https://errsolved.com";

function getEnvOrThrow(name) {
  const v = process.env[name];
  if (!v) {
    throw new Error(`環境変数 ${name} が設定されていません。GitHub Secrets を確認してください。`);
  }
  return v;
}

function buildCookieHeader() {
  const authToken = getEnvOrThrow("NOTE_GQL_AUTH_TOKEN");
  const sessionV5 = getEnvOrThrow("NOTE_SESSION_V5");
  const xsrfRaw = process.env.NOTE_XSRF_TOKEN || "";

  const parts = [
    `note_gql_auth_token=${authToken}`,
    `_note_session_v5=${sessionV5}`,
  ];
  if (xsrfRaw) {
    parts.push(`XSRF-TOKEN=${xsrfRaw}`);
  }
  return { cookie: parts.join("; "), xsrfRaw };
}

function commonHeaders() {
  const { cookie, xsrfRaw } = buildCookieHeader();
  const headers = {
    "Content-Type": "application/json",
    "Origin": "https://editor.note.com",
    "Referer": "https://editor.note.com/",
    "Cookie": cookie,
    "User-Agent": "Mozilla/5.0 (compatible; errsolved-auto-poster/1.0)",
  };
  if (xsrfRaw) {
    // Cookie内はURLエンコードされていることが多いのでデコードしてヘッダーに渡す
    try {
      headers["X-XSRF-TOKEN"] = decodeURIComponent(xsrfRaw);
    } catch {
      headers["X-XSRF-TOKEN"] = xsrfRaw;
    }
  }
  return headers;
}

async function apiRequest(method, url, body) {
  const res = await fetch(url, {
    method,
    headers: commonHeaders(),
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  const text = await res.text();
  let json;
  try {
    json = text ? JSON.parse(text) : {};
  } catch {
    json = null;
  }

  if (!res.ok) {
    console.error(`[note API error] ${method} ${url} -> HTTP ${res.status}`);
    console.error(text);
    throw new Error(`note API request failed: ${method} ${url} (HTTP ${res.status})`);
  }

  return json;
}

function slugFromFilePath(filePath) {
  const base = path.basename(filePath);
  return base.replace(/\.(md|mdx)$/i, "");
}

function buildNoteBodyHtml({ markdownBody, originalUrl }) {
  const contentHtml = marked.parse(markdownBody);
  const introHtml =
    `<p>この記事は <a href="${originalUrl}">errsolved.com</a> に掲載したものです。` +
    `関連ツールや詳しい手順は元記事もあわせてご覧ください。</p><hr>`;
  return introHtml + contentHtml;
}

async function createDraft() {
  // 空のドラフトを作成し id を取得する
  const data = await apiRequest("POST", `${NOTE_BASE}/v1/text_notes`, {});
  const noteId = data?.data?.id;
  const noteKey = data?.data?.key;
  if (!noteId) {
    throw new Error(`text_notes 作成レスポンスから id を取得できませんでした: ${JSON.stringify(data)}`);
  }
  return { noteId, noteKey };
}

async function saveDraftBody({ noteId, title, bodyHtml }) {
  await apiRequest("POST", `${NOTE_BASE}/v1/text_notes/draft_save?id=${noteId}`, {
    name: title,
    body: bodyHtml,
  });
}

async function publishNote({ noteId, noteKey, tags }) {
  // note の公開エンドポイントは非公式かつ変更されやすい。
  // PUT /v1/text_notes/{id} に status: "published" を渡す方式を採用。
  return apiRequest("PUT", `${NOTE_BASE}/v1/text_notes/${noteId}`, {
    id: noteId,
    key: noteKey,
    status: "published",
    tags: tags.slice(0, 5),
    price: 0,
  });
}

async function main() {
  const filePath = process.argv[2];
  if (!filePath) {
    console.error("使い方: node scripts/post-to-note.mjs <markdownファイルパス>");
    process.exit(1);
  }

  const raw = readFileSync(filePath, "utf-8");
  const { data: frontmatter, content } = matter(raw);

  const title = frontmatter.title;
  const category = frontmatter.category;

  if (!title) {
    throw new Error(`${filePath} の frontmatter に title がありません`);
  }

  const slug = slugFromFilePath(filePath);
  const originalUrl = `${SITE_BASE_URL.replace(/\/$/, "")}/posts/${slug}/`;

  console.log(`[post-to-note] 対象記事: ${title}`);
  console.log(`[post-to-note] 元記事URL: ${originalUrl}`);

  const bodyHtml = buildNoteBodyHtml({ markdownBody: content, originalUrl });

  console.log("[post-to-note] 下書きを作成中...");
  const { noteId, noteKey } = await createDraft();
  console.log(`[post-to-note] note_id=${noteId}`);

  console.log("[post-to-note] 本文を保存中...");
  await saveDraftBody({ noteId, title, bodyHtml });

  const tags = category ? [category] : [];

  console.log("[post-to-note] 公開処理を実行中...");
  try {
    await publishNote({ noteId, noteKey, tags });
    console.log(`[post-to-note] 公開に成功しました: https://note.com/notes/${noteKey ?? noteId}`);
  } catch (err) {
    console.error("[post-to-note] 公開ステップで失敗しました。下書きとしては note.com に保存されています。");
    console.error("[post-to-note] note.com にログインして手動で公開するか、公開APIの仕様変更に合わせてスクリプトの修正が必要です。");
    throw err;
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
