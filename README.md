# LIGGGHTS dump の `ITEM: ENTRIES ...` ヘッダ置換ツール

LIGGGHTS の `dump` ファイルに含まれるヘッダ行 **`ITEM: ENTRIES ...`** を、指定した文字列に一括置換するためのシンプルなスクリプトです。  
標準ライブラリのみで動作し、**上書き（in-place）** と **別名保存** の両方に対応します。

> 以降、スクリプト名は例として `replace_entries_header.py` と表記します（任意名で構いません）。

---

## 目次

- [特徴](#特徴)
- [要件](#要件)
- [インストール](#インストール)
- [使い方](#使い方)
  - [基本](#基本)
  - [オプション](#オプション)
  - [使用例](#使用例)
  - [動作の詳細](#動作の詳細)
- [よくある質問](#よくある質問)
- [開発](#開発)
- [ライセンス](#ライセンス)

---

## 特徴

- `^ITEM: ENTRIES `（行頭一致）の行だけを置換
- グロブ（例: `post/forcechain-*.dmp`）や複数ファイルにまとめて対応
- 既定は **別名保存**：`<元ファイル名><suffix><拡張子>`（デフォルト `-renamed`）
- `--inplace` で安全に **上書き**（一時ファイルに書き出してから置換→置換後に置換）
- エンコーディング指定（既定: `utf-8`、読み込み時の不正文字は `errors="replace"` で回避）
- 失敗時はファイルごとにエラーを表示しつつ処理継続

## 要件

- Python 3.8+（標準ライブラリのみ使用）

## インストール

リポジトリを取得してスクリプトを手元に置くだけで使えます。

```bash
git clone <your-repo-url>
cd <your-repo>
# 任意：実行権限を付与（UNIX系）
chmod +x replace_entries_header.py
```

## 使い方

### 基本

```
python replace_entries_header.py -H "ITEM: ENTRIES <置換後の列名...>" <入力ファイル群 or グロブ>
```

**重要**: `-H/--header` には **`ITEM: ENTRIES` を含む完全な置換後1行** を渡してください。  
（例）`"ITEM: ENTRIES x1 y1 z1 nx ny area"`

### オプション

| オプション | 必須 | 既定値 | 説明 |
|---|:---:|---|---|
| `-H`, `--header` | ✅ | なし | 置換後のヘッダ 1 行（`ITEM: ENTRIES ...` を含む完全な行） |
| `inputs...` | ✅ | なし | 入力ファイルまたはグロブ（例: `post/forcechain-*.dmp`） |
| `--inplace` |  | `False` | 上書き（in-place）で置換。指定しない場合は別名保存 |
| `--suffix` |  | `-renamed` | 別名保存時のサフィックス（拡張子の直前に付与） |
| `--encoding` |  | `utf-8` | 文字コード（読み込みは `errors="replace"` でフォールバック） |

ヘルプの表示：

```bash
python replace_entries_header.py -h
```

### 使用例

**1) 別名保存（デフォルト）**

```bash
python replace_entries_header.py   -H "ITEM: ENTRIES x1 y1 z1 nx ny area"   post/forcechain-*.dmp
```
出力例：`post/forcechain-001-renamed.dmp`, `post/forcechain-002-renamed.dmp` …

**2) 上書き（in-place）**

```bash
python replace_entries_header.py   -H "ITEM: ENTRIES id fx fy fz radius"   --inplace   post/forcechain-*.dmp
```

**3) 文字コードを指定**（例：`cp932`）

```bash
python replace_entries_header.py   -H "ITEM: ENTRIES x y z"   --encoding cp932   data/*.dmp
```

**4) ファイルとグロブを混在指定**

```bash
python replace_entries_header.py -H "ITEM: ENTRIES x y z" a.dmp b.dmp post/*.dmp
```

### 動作の詳細

- 置換対象は **行頭が `ITEM: ENTRIES ` で始まる行のみ**（正規表現 `^ITEM: ENTRIES `）。
- `--inplace` 時は、**一時ファイルに全行を書き出してから原本へアトミックに置換**。
- 入力に一致がない場合、`No input files found.` を標準エラー出力し、終了コード 1 を返します。
- 各ファイルの処理結果は `OK: <src> -> <dst>`、失敗時は `NG: Error processing <src>: <理由>` を標準エラー出力します。
- 既定の別名保存では、`<stem><suffix><suffix>` ではなく、`<stem><suffix><ext>` の形で保存します（例：`foo.dmp` → `foo-renamed.dmp`）。

#### 置換前後の例

置換前（抜粋）:

```text
ITEM: TIMESTEP
12345
ITEM: NUMBER OF ENTRIES
100
ITEM: ENTRIES id fx fy fz
...
```

置換後（例：`-H "ITEM: ENTRIES x1 y1 z1 nx ny area"` を指定）:

```text
ITEM: TIMESTEP
12345
ITEM: NUMBER OF ENTRIES
100
ITEM: ENTRIES x1 y1 z1 nx ny area
...
```

> 注：`ITEM: NUMBER OF ENTRIES` など他のヘッダは変更しません。

## よくある質問

**Q. `ITEM: ENTRIES` だけ（末尾に空白も列名もない）行は置換されますか？**  
A. 本ツールは `^ITEM: ENTRIES␠`（末尾に半角スペースがある形）にマッチします。`ITEM: ENTRIES` だけの行はデータに依存しますが、一般的な dump では列見出しが続くため本実装に合わせています。必要なら正規表現を調整してください。

**Q. 上書き時の安全性は？**  
A. 一時ファイルへ書いた後に `shutil.move` で置換するため、途中失敗で原本が壊れる可能性を低減しています。とはいえ、重要データは事前バックアップを推奨します。

## 開発

- 依存：標準ライブラリのみ（`argparse`, `glob`, `re`, `pathlib`, `tempfile`, `shutil` など）
- テスト：大きなファイルでもストリーム処理で動作しますが、十分な空き容量を確保してください（特に `--inplace` 時も一時ファイルを作成します）。

## ライセンス

本リポジトリは **MIT License** です。詳細は [LICENSE](./LICENSE) を参照してください。
