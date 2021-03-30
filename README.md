# DeepL PDF Translator

PDFファイルを無料版のDeepLで自動的に翻訳するソフトです。  
PDFファイルから人力で文章をコピーして、随所に挟まる改行を消してペーストして、翻訳文をまたコピーして……という作業からの解放を目的としています。

## 使い方

1. `pip_install.bat`を起動するか(Windows)、`pip install -r requirements.txt`で必要なライブラリを入手してください。事前に`pip install --upgrade pip`でpipをアップデートしておくと、エラーが減るかもしれません。パーミッションエラーでインストールが正常に完了しない場合は、管理者権限で実行してください。
2. `drivers`ディレクトリに、利用するブラウザのバージョンに合うWebDriverを入れてください。入手先は**動作環境**の欄に記載します。同梱していない理由は、再配布に関わるトラブルを回避するためです。
3. `python main.py`で起動するとウィンドウが出るので、そこに翻訳したいPDFファイルをドラッグ&ドロップしてください。複数ファイルの入力にも対応しています。
4. 翻訳が終わると`output`ディレクトリにtxtファイルが出力されます。

最低限の翻訳機能に加えて、

- 指定の部分での翻訳開始/終了(翻訳が乱れやすい冒頭や、翻訳の不要な参考文献などを除く用)
- 指定の文字列を含む行の無視(ヘッダーやフッター、ページ数などを除く用)
- 指定の文字列を含む行で改行(文末や見出し用)
- 略語などの、文末っぽく見えるが文末ではない部分では改行しないよう指定する
- Markdown形式での出力(見出しと見なす文字列を指定すればMarkdown式の見出しで出力)
- 上記の機能を用いてもヘッダーやフッターが本文中に入り込んでしまう際の除去

などの機能がありますが、現状ほとんどGUIからは操作できないので、直接コードをいじる必要があります。その他の不満点も同様です。  
ただし、v0.4.1時点で、**適切な設定(特に無視やノイズ除去)を行えばかなり実用に耐える翻訳文を出力できるようになっています**。  
また、製作者がObsidianというMarkdownメモアプリの利用者なので、**Obsidianユーザにはかなり恩恵がある設計**になっています。

また、主な対象は英字論文を想定しているので、それ以外のPDF文書の翻訳については動作を保証していません(特に現実の書類をスキャンした文書など)。

## 動作環境

OS: Windows, MacOS  
Python: 3.7.9
- Chrome
- Edge
- FireFox

[WebDriver for Chrome](https://sites.google.com/a/chromium.org/chromedriver/downloads)  
[WebDriver for Edge](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/#downloads)  
[WebDriver for Firefox](https://github.com/mozilla/geckodriver/releases)

ご使用のWebブラウザのバージョンに合わせたWebDriverをダウンロードしてください。

### 注意点

<details>
<summary>MacOSで実行する場合</summary>

```
This program needs access to the screen. Please run with a Framework build of python, and only when you are logged in on the main display of your Mac.
```

という出力がなされ、GUIが出現しない場合があります。  
その場合は、Framework buildのPythonを入手してください。  
pyenvを利用している場合は、

```
env PYTHON_CONFIGURE_OPTS="--enable-framework" pyenv install 3.7.9
```

で入手可能です。その後、pyenvで利用するPythonのバージョンを3.7.9に切り替え、

```
pip install --upgrade pip
pip install -r requirements.txt
```

を実行して必要なライブラリをインストールし、対応するWebDriverを`drivers`ディレクトリに入れて起動してください。  
なお、その際にセキュリティによってWebDriverが起動できない場合があります。  
その場合は、`システム環境設定 > セキュリティとプライバシー`からWebDriverの実行を許可してください。

</details>

---

## 既知の不具合

- Linux(Ubuntu)において、抽出されるテキストが明らかに少なく、正常に動作しない。
- `1.2.3 Header`のような、見出し番号の末尾にピリオドが付いていない番号振りの見出しについて、Markdown式の見出しを適切な大きさに設定することができない。また、そのような見出しの日本語訳の先頭の番号を適切に除去することができない。

<details>
<summary>例</summary>

```
原文
1 Header1
1.1 Header2

理想
## Header1
ヘッダー1
### Header2
ヘッダー2

現実
## Header1
ヘッダー1
## Header2
1 ヘッダー2
```

</details>

## 実装したい機能

- 環境を整えるのが苦手な人のために、実行可能ファイルとしてリリースしたい(優先度はWindows > Mac > Linuxで。Linux使いの人は自分で環境を整えられるはず)
- ↑を実現するために、webdriverを自動でダウンロードする機能が欲しい
- 翻訳先の言語を選択できるようにしたい
- 翻訳の進捗をプログレスバーで表示したい
- 現状実装している機能をGUIで利用できるようにしたい
- 各種正規表現をGUIで追加・編集・削除・インポート・エクスポートできるようにしたい
- 正規表現で大文字小文字を区別するかを設定できるようにしたい
- GUIをいじった場合にその結果を保存しておき、再度立ち上げたときに同じ設定になるようにしたい
- Windowsだとウインドウにファイルをドロップしてから翻訳が終わるまでの間応答なしになる問題をなんとかしたい
- Markdown(Obsidian)出力時に参考文献への参照を脚注に加工して出力したい
- 現在は翻訳完了の基準を、「翻訳中のポップアップが出ておらず、翻訳文に"\[...\]"という文字列がない」としているが、翻訳が終了していないときは翻訳文の欄に収縮する青い枠が出現するので、そのCSSセレクタがわかればより正確に翻訳完了のタイミングがわかり、高速化が図れる。ただし、現状では(そう設計しているわけではないが何故か)**一度翻訳が開始するまでは規定の時間が経過した状態で翻訳完了の条件を満たしてもそうとは見なされない**ようなので、喫緊の問題でではない。
- 複数タブでDeepLページを開くことによる翻訳作業の並列化。ただし、月額課金を行わない状態での文書まるごと自動翻訳という時点でかなりグレーな領域に踏み込んでいる上、同一IPからの複窓&大量の翻訳要求は確実に検知されるので実装優先度はごく低い。現状でも他事をしている間に翻訳は終わるので。

## バージョン履歴

### v0.5.0
<details open>

- ファイル選択メニューから翻訳対象を選択可能に

</details>

### v0.4.2
<details>

- 各種正規表現にヒットした行の出力機能を強化

</details>

### v0.4.1
<details>

- `翻訳文を一文ごとに改行する`のチェックを外すと出力が空文字列になる問題を修正
- 原文を出力するかどうか選べる機能を追加
- Markdownでの出力時、原文をコメントとして出力する機能を追加
- 翻訳完了の基準を変更し、翻訳作業を高速化

</details>

### v0.4.0
<details>

- 見出しの識別が上手く動作しなかった問題を修正
- Markdown式で見出しを出力する機能を追加
- Markdown用の除去/置換機能を追加
- 一行ごとの改行・Markdown式の出力を管理するGUIのチェックボックスを追加

</details>

### v0.3.1
<details>

- MacOS, Chromeでの動作を確認
- MacOS環境下にて、DeepLのページで以前の翻訳対象文を削除できない問題を修正

</details>

### v0.3.0
<details>

- 翻訳を開始/終了する位置を正規表現によって指定可能に
- フォーマットの都合上混じってしまうノイズの除去/置換機能を追加
- 翻訳文を一文ごとに改行する機能を追加(Markdown方式にも対応)
- 後に文が続きそうな略語(et al. や e.g.など)では改行しないように修正
- 行末のハイフン(-)の処理を修正

</details>

### v0.2.0
<details>

- MacOS、Linuxに対応(動作未確認)
- Edge、FireFoxに対応
- ブラウザの選択機能を追加

</details>

### v0.1.0
<details>

- 最低限の翻訳機能を実装
- 文書先頭あたりはレイアウトが複雑なので、有効な翻訳はほぼ無理
- ページにまたがる文章や、図表を挟んだ文章の順序が怪しい
- 画像周辺の文章に謎の文字列が入ることがある。画像のタグか何かか？
- 総評として、全て人力でコピペする労力からは解放されるが、まだまだ修正のコストが高い。

</details>

## 免責事項

私(KashiPrg)は、このアプリケーションによってもたらされたいかなる損害に関しても一切責任を負いません。
