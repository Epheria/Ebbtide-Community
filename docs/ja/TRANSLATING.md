# ローカライズ

*このページは AI の支援を受けて翻訳しました。日本語が母語の方は、プルリクエストで改善にご協力いただけるとうれしいです。基準となるのは[英語版](../../localization/README.md)です。*

Ebbtide のインターフェースのテキストを、翻訳しやすい形でまとめています。ゲームは韓国語で書かれていて、ほかのすべての言語は英語を原文にしています。

## フォルダー

以下のパスは、[`localization/`](../../localization/) フォルダーの中の場所です。

| パス | 内容 |
| --- | --- |
| `source/strings/<Table>.csv` | 現在のゲームテキスト：`key`、`en`、`ko`。ゲームから再生成されるので、編集しないでください。 |
| `source/SNAPSHOT` | 現在の原文スナップショットの日付とサイズ |
| `translations/<lang>/<Table>.csv` | 言語ごとに 1 フォルダー：`key`、`en`、`translation`、`status` |
| `glossary.csv` | 固有名詞や軍事用語と、その扱い方 |

言語フォルダーには `de`、`fr`、`pt-BR`、`ro`、`zh-Hans` のようなコードを使います。日本語は `ja` です。

## 翻訳の手順

1. 自分の言語の[翻訳者用の Issue](https://github.com/Epheria/Ebbtide-Community/issues/new?template=translator.yml) を作成します。メンテナーが言語フォルダーを作成します。
2. `translations/<lang>/` の中のファイルを編集します。書き込むのは `translation` 列だけです。
3. プレースホルダーはすべて英語と同じ形のまま残してください。`{0}`、`{1}`、`<b>` などのリッチテキストタグ、`\n` の改行がこれに当たります。文の中で位置を動かすのはかまいません。
4. 固有名詞や用語は `glossary.csv` で確認してください。
5. プルリクエストを作成します。プレースホルダーの抜けや壊れた行があれば、自動チェックが知らせてくれます。

自信がない行は、`translation` を空のままにしてください。空の行は、ゲーム内で英語が表示されます。

### CSV ファイルの編集

- 小さな変更なら、GitHub のウェブエディターで十分です。
- 大きな作業には LibreOffice Calc か Google スプレッドシートを使ってください。UTF-8・カンマ区切りで読み込み、同じ 4 列のまま UTF-8 の CSV で書き出します。
- Microsoft Excel は、「CSV UTF-8 (コンマ区切り)」で保存する場合を除いて避けてください。ほかの形式では、日本語など英語以外の文字が文字化けします。

## `status` 列

| 値 | 意味 | すること |
| --- | --- | --- |
| （空欄） | 問題なし、またはまだ翻訳されていない | 空欄なら翻訳してください |
| `outdated` | 翻訳したあとで英語のテキストが変わった | 翻訳を更新してから、status を空欄に戻す |
| `review` | レビュアーがもう一度確認したい | プルリクエストで話し合う |

## ゲームのテキストが変わったとき

ゲームはまだ開発中なので、英語のテキストはよく追加・変更・削除されます。原文が更新されると、メンテナーが `python tools/l10n.py update` を実行します。これで次のことが行われます。

- 新しい行を、翻訳が空の状態で追加します。
- 英語が変わった行に `outdated` の印を付けます。以前の翻訳はそのまま残ります。
- ゲームからなくなった行を削除します。

## メンテナー向け

```bash
python tools/export_unity_strings.py --project <path to the Unity project>  # refresh the source (needs PyYAML)
python tools/l10n.py update                                                 # sync every language
python tools/l10n.py init <lang>                                            # open a new language
python tools/l10n.py check                                                  # the same check the pull requests run
python tools/l10n.py status                                                 # progress per language
```

ストーリーシーン（カットシーンの会話）はまだ含まれていません。台本が確定したら追加します。
