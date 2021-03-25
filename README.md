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
- 上記の機能を用いてもヘッダーやフッターが本文中に入り込んでしまう際の除去

などの機能がありますが、現状GUIからは操作できないので、直接コードをいじる必要があります。その他の不満点も同様です。  
また、主な対象は英字論文を想定しているので、それ以外のPDF文書の翻訳については動作を保証していません(特に現実の書類をスキャンした文書など)。

## 動作環境

OS: Windows, MacOS, Linux系(動作未確認)  
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

で入手可能です。その後、

```
pip install --upgrade pip
pip install -r requirements.txt
```

を実行して必要なライブラリをインストールし、対応するWebDriverを`drivers`ディレクトリに入れて起動してください。  
なお、その際にセキュリティによってWebDriverが起動できない場合があります。  
その場合は、`システム環境設定 > セキュリティとプライバシー`からWebDriverの実行を許可してください。

</details>

---

## バージョン履歴

### v0.3.1
<details open>

- MacOS, Chromeでの動作を確認
- MacOS環境下にて、DeepLのページで以前の翻訳対象文を削除できない問題を修正

</details>

### v0.3.0
<details open>

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
