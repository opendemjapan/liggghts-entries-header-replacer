# LIGGGHTS dump の `ITEM: ENTRIES ...` ヘッダ置換ツール

 LIGGGHTS の `dump` ファイルに含まれるヘッダ行 **`ITEM: ENTRIES ...`** を 指定した文字列に一括置換するスクリプトである. 標準ライブラリのみで動作し, **上書き (in‑place)** と **別名保存** の両方に対応する.

 > 以降, スクリプト名は例として `replace_entries_header.py` と表記する (任意名でよい).

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

- `^ITEM: ENTRIES ` (行頭一致) の行のみを置換する.
- グロブ (例: `post/forcechain-*.dmp`) や複数ファイルにまとめて対応する.
- 既定は **別名保存**: `<元ファイル名><suffix><拡張子>` (デフォルト `-renamed`).
- `--inplace` で安全に **上書き** する (一時ファイルへ書き出し, `shutil.move` によりアトミックに差し替える).
- エンコーディング指定に対応する (既定: `utf-8`, 読み込み時の不正文字は `errors="replace"` で回避).
- 失敗時はファイルごとにエラーを表示しつつ処理を継続する.

## 要件

- Python 3.8+ (標準ライブラリのみ使用).

## インストール

 リポジトリを取得し, スクリプトを手元に置けば利用できる.

```bash
git clone <your-repo-url>
cd <your-repo>
# 任意: 実行権限を付与 (UNIX 系)
chmod +x replace_entries_header.py
```

## 使い方

### 基本

```bash
python replace_entries_header.py -H "ITEM: ENTRIES <置換後の列名...>" <入力ファイル群 または グロブ>
```

 **重要**: `-H/--header` には **`ITEM: ENTRIES` を含む完全な置換後 1 行** を渡すこと.  
 例: `"ITEM: ENTRIES x1 y1 z1 nx ny area"`.

### オプション

| オプション | 必須 | 既定値 | 説明 |
|---|---|---|---|
| `-H`, `--header` | はい | なし | 置換後のヘッダ 1 行 (`ITEM: ENTRIES ...` を含む完全な行). |
| `inputs...` | はい | なし | 入力ファイル または グロブ (例: `post/forcechain-*.dmp`). |
| `--inplace` | いいえ | `False` | 上書き (in‑place) で置換する. 指定しない場合は別名保存. |
| `--suffix` | いいえ | `-renamed` | 別名保存時のサフィックス (拡張子の直前に付与). |
| `--encoding` | いいえ | `utf-8` | 文字コード. 読み込みは `errors="replace"` でフォールバック. |

 ヘルプの表示:

```bash
python replace_entries_header.py -h
```

### 使用例

**1) 別名保存 (デフォルト).**

```bash
python replace_entries_header.py   -H "ITEM: ENTRIES x1 y1 z1 nx ny area"   post/forcechain-*.dmp
```
 出力例: `post/forcechain-001-renamed.dmp`, `post/forcechain-002-renamed.dmp` ...

**2) 上書き (in‑place).**

```bash
python replace_entries_header.py   -H "ITEM: ENTRIES id fx fy fz radius"   --inplace   post/forcechain-*.dmp
```

**3) 文字コードを指定 (例: `cp932`).**

```bash
python replace_entries_header.py   -H "ITEM: ENTRIES x y z"   --encoding cp932   data/*.dmp
```

**4) ファイルとグロブを混在指定.**

```bash
python replace_entries_header.py -H "ITEM: ENTRIES x y z" a.dmp b.dmp post/*.dmp
```

### 動作の詳細

- 置換対象は **行頭が `ITEM: ENTRIES ` で始まる行のみ** である (正規表現 `^ITEM: ENTRIES `).
- `--inplace` 指定時は **全行を一時ファイルへ書き出したのちに原本をアトミックに差し替える**.
- 入力に一致がない場合は `No input files found.` を標準エラー出力し, 終了コード 1 を返す.
- 各ファイルの処理結果は `OK: <src> -> <dst>` を表示し, 失敗時は `NG: Error processing <src>: <理由>` を標準エラー出力する.
- 既定の別名保存では `<stem><suffix><ext>` の形で保存する (例: `foo.dmp` → `foo-renamed.dmp`).

#### 置換前後の例

 置換前 (抜粋):

```text
ITEM: TIMESTEP
12345
ITEM: NUMBER OF ENTRIES
100
ITEM: ENTRIES id fx fy fz
...
```

 置換後 (例: `-H "ITEM: ENTRIES x1 y1 z1 nx ny area"` を指定):

```text
ITEM: TIMESTEP
12345
ITEM: NUMBER OF ENTRIES
100
ITEM: ENTRIES x1 y1 z1 nx ny area
...
```

 > 注: `ITEM: NUMBER OF ENTRIES` など他のヘッダは変更しない.

## よくある質問

**Q. `ITEM: ENTRIES` だけの行 (末尾に空白も列名もない) は置換対象になるか.**  
A. 本実装は `^ITEM: ENTRIES␠` (末尾に半角スペースがある形) にマッチする. `ITEM: ENTRIES` だけの行はデータに依存するが, 一般的な dump では列見出しが続くため本設定としている. 必要に応じて正規表現を変更すればよい.

**Q. 上書き時の安全性はどうか.**  
A. 一時ファイルへ書いた後に `shutil.move` で差し替えるため, 処理途中の失敗で原本が破損する可能性を低減できる. 重要データは事前にバックアップを推奨する.

## 開発

- 依存: 標準ライブラリのみ (`argparse`, `glob`, `re`, `pathlib`, `tempfile`, `shutil` など).
- 備考: 大きなファイルでも行単位のストリーム処理で動作するが, 十分な空き容量を確保すること (`--inplace` 指定時も一時ファイルを作成する).

## ライセンス

 本リポジトリは **MIT License** である. 詳細は [LICENSE](./LICENSE) を参照のこと.
