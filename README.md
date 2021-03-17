# DeepL PDF Translator

PDFファイルを無料版のDeepLで自動的に翻訳するソフトです。  
PDFファイルから人力で文章をコピーして、随所に挟まる改行を消してペーストして、翻訳文をまたコピーして……という作業からの解放を目的としています。

## 使い方

1. `pip_install.bat`を起動するか、`pip install -r requirements.txt`で必要なライブラリを入手してください。パーミッションエラーでインストールが正常に完了しない場合は、管理者権限で実行してください。
2. `drivers`ディレクトリに、利用するブラウザのバージョンに合うWebDriverを入れてください。入手先は**動作環境**の欄に記載します。同梱していない理由は、再配布に関わるトラブルを回避するためです。
3. `python main.py`で起動するとウィンドウが出るので、そこに翻訳したいPDFファイルをドラッグ&ドロップしてください。複数ファイルにも対応していますが面倒くさいので動作未確認です。
4. 翻訳が終わると`output`ディレクトリにtxtファイルが出力されます。

最低限の翻訳機能に加えて、正規表現に引っかかった部分の無視or改行機能がありますが、現状GUIからは操作できないので、直接コードをいじる必要があります。その他の不満点も同様です。  
また、主な対象は英字論文を想定しているので、それ以外のPDF文書の翻訳については動作を保証していません(特に現実の書類をスキャンした文書など)。

## 動作環境

OS: Windows, MacOS(動作未確認), Linux系(動作未確認)  
Python: 3.7.9
- Chrome
- Edge
- FireFox

[WebDriver for Chrome](https://sites.google.com/a/chromium.org/chromedriver/downloads)  
[WebDriver for Edge](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/#downloads)  
[WebDriver for Firefox](https://github.com/mozilla/geckodriver/releases)

## バージョン履歴

### v0.1.1
<details>

- MacOS、Linuxに対応(動作未確認)
- Edge、FireFoxに対応
- ブラウザの選択機能を追加

</details>

### v0.1.0
<details open>

- 最低限の翻訳機能を実装
- 文書先頭あたりはレイアウトが複雑なので、有効な翻訳はほぼ無理
- ページにまたがる文章や、図表を挟んだ文章の順序が怪しい
- 画像周辺の文章に謎の文字列が入ることがある。画像のタグか何かか？
- 総評として、全て人力でコピペする労力からは解放されるが、まだまだ修正のコストが高い。

</details>