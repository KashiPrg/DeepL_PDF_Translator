import platform
import selenium.common.exceptions as sce
import wx

from enum import Enum
from pathlib import Path
from pdfminer.high_level import extract_text
from pdfminer.pdfparser import PDFSyntaxError
from re import search, IGNORECASE
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from sys import stderr
from time import sleep


class Browser(Enum):
    CHROME = "Chrome"
    EDGE = "Edge"
    FIREFOX = "FireFox"


# DeepLでの翻訳を管理する
class DeepLManager:
    webDriverURLs = {
        Browser.CHROME.value:
            "https://sites.google.com/a/chromium.org/chromedriver/downloads",
        Browser.EDGE.value:
            "https://developer.microsoft.com/en-us/" +
            "microsoft-edge/tools/webdriver/#downloads",
        Browser.FIREFOX.value:
            "https://github.com/mozilla/geckodriver/releases"
    }

    def __init__(self, browser):
        try:
            if platform.system() == "Windows":
                # Windowsなら実行ファイルに拡張子が付く
                if browser == Browser.CHROME.value:
                    self.__webDriver = webdriver.Chrome(
                        "./drivers/chromedriver.exe")
                elif browser == Browser.EDGE.value:
                    self.__webDriver = webdriver.Edge(
                        "./drivers/msedgedriver.exe")
                elif browser == Browser.FIREFOX.value:
                    # Firefoxはなぜかexecutable_pathで指定しないとエラーが起きる
                    self.__webDriver = webdriver.Firefox(
                        executable_path="./drivers/geckodriver.exe")
                else:
                    self.__invalidBrowser()
            else:
                # MacやLinux(Windows以外)なら拡張子は付かない
                if browser == Browser.CHROME.value:
                    self.__webDriver = webdriver.Chrome(
                        "./drivers/chromedriver")
                elif browser == Browser.EDGE.value:
                    self.__webDriver = webdriver.Edge(
                        "./drivers/msedgedriver")
                elif browser == Browser.FIREFOX.value:
                    self.__webDriver = webdriver.Firefox(
                        executable_path="./drivers/geckodriver")
                else:
                    self.__invalidBrowser()
        except sce.WebDriverException:
            wx.LogError(
                browser + "、または" + browser +
                "のWebDriverがインストールされていません。\n\n" +
                browser + "をインストールするか、" +
                browser + "のWebDriverを\n" +
                self.webDriverURLs[browser] + " から入手し、" +
                "driversディレクトリに配置してください。"
            )
            exit(1)

    def __invalidBrowser(self):
        wx.LogError("ブラウザの指定が無効な値です。")
        exit(1)

    # DeepLのタブを開く
    def openDeepLPage(self):
        # 今のタブがDeepLなら何もしない
        try:
            if self.__webDriver.current_url == \
               "https://www.deepl.com/translator":
                return
        except AttributeError:
            print("Error: webDriver is not initiated.", file=stderr)
            exit(1)

        # 他のタブにそのページがあるならそれを開いて終わり
        for tab in self.__webDriver.window_handles:
            self.__webDriver.switch_to.window(tab)
            if self.__webDriver.current_url == \
               "https://www.deepl.com/translator":
                return

        # もしDeepLのページを開いているタブが無ければ新たに開く
        # 新しいタブを開き、そのタブに移動
        self.__webDriver.execute_script("window.open('', '_blank');")
        self.__webDriver.switch_to.window(self.__webDriver.window_handles[-1])
        # DeepLに接続
        self.__webDriver.get("https://www.deepl.com/translator")

    # 渡された文を翻訳にかけ、訳文を返す
    def translate(self, text, first_wait_secs=30, wait_secs_max=60):
        # DeepLのページが開かれていなければ開く
        self.openDeepLPage()

        # 原文の入力欄を取得
        source_textarea = self.__webDriver.find_element_by_css_selector(
            "textarea.lmt__textarea.lmt__source_textarea."
            "lmt__textarea_base_style"
        )
        # Ctrl+Aで全選択し、前の文を消しつつ原文を入力
        source_textarea.send_keys(Keys.CONTROL, "a")
        source_textarea.send_keys(text)

        # 最初に5秒待つ
        sleep(first_wait_secs)

        # 翻訳の進行度を示すポップアップが無ければ翻訳完了と見なす
        # 制限時間内に翻訳が終了しなければ翻訳失敗と見なす
        wait_secs_sub = int(wait_secs_max - first_wait_secs)
        for i in range(wait_secs_sub):
            try:
                # 通常時はdiv.lmt_progress_popupだが、ポップアップが可視化するときは
                # lmt_progress_popup--visible(_2)が追加される
                _ = self.__webDriver.find_element_by_css_selector(
                    "div.lmt__progress_popup.lmt__progress_popup--visible."
                    "lmt__progress_popup--visible_2")
            except sce.NoSuchElementException:
                # ポップアップが無ければ抜け出す
                break
            # ポップアップがあり、かつ制限時間内ならばもう1秒待つ
            if i < wait_secs_sub - 1:
                sleep(1.0)
                continue
            else:
                # 制限時間を過ぎたら失敗
                # 段落と同じ数だけメッセージを生成
                num_pars = len(text.splitlines())
                messages = ["(翻訳に" + str(wait_secs_max) +
                            "秒以上を要するため失敗と見なしました)"
                            for _ in range(num_pars)]
                return "\n".join(messages)

        # 訳文の出力欄を取得し、訳文を取得
        translated = self.__webDriver.find_element_by_css_selector(
            "textarea.lmt__textarea.lmt__target_textarea."
            "lmt__textarea_base_style"
        ).get_property("value")

        return translated

    # ブラウザのウィンドウを閉じる
    def closeWindow(self):
        self.__webDriver.quit()


class MyFileDropTarget(wx.FileDropTarget):
    __deepLManager = None
    # このリストに含まれる正規表現に当てはまる文字列から翻訳を開始する
    __start_lines = [r"[0-9]+\s*\.?\s*introduction", r"introduction$"]
    # このリストに含まれる正規表現に当てはまる文字列で翻訳を打ち切る
    __end_lines = [r"^references?$"]
    # このリストに含まれる正規表現に当てはまる文字列は無視する
    __ignore_lines = [
        r"^\s*ACM Trans",
        r"^\s*[0-9]:[0-9]\s*$",     # ページ数
        r"^\s*[0-9]+\s*of\s*[0-9]+\s*$"     # ページ数
        r"•$",
        r"Peng Wang, Lingjie Liu, Nenglun Chen, Hung-Kuo Chu, Christian Theobalt, and Wenping Wang$",
        r"^\s*Multimodal Technologies and Interact\s*",
        r"^www.mdpi.com/journal/mti$",
        r"^\s*Li et al.\s*$",
        r"^\s*Exertion-Aware Path Generation\s*$"
    ]
    # このリストに含まれる正規表現に当てはまる文字列がある行で改行する
    __return_lines = [
        r"(\.|:|;|\([0-9]+\))\s*$",   # 文末(計算式や箇条書きなども含む)
        r"^\s*([0-9]+\s*\.\s*)+.{,45}\s*$"    # 見出し
        r"[0-9]+\s*\.?\s*introduction",
        r"[0-9]+\s*\.?\s*related works?",
        r"[0-9]+\s*\.?\s*overview",
        r"[0-9]+\s*\.?\s*algorithm",
        r"[0-9]+\s*\.?\s*experimental results",
        r"[0-9]+\s*\.?\s*conclusions",
        r"^acknowledgements$",
        r"^references?$"
    ]
    # このリストに含まれる正規表現に当てはまる文字列があるとき、
    # 改行対象でも改行しない
    # 主にその略語の後に文が続きそうなものが対象
    # 単なる略語は文末にも存在し得るので対象外
    # 参考：[参考文献リストやデータベースに出てくる略語・用語一覧]
    # (https://www.dl.itc.u-tokyo.ac.jp/gacos/supportbook/16.html)
    __return_ignore_lines = [
        r"\s+(e\.g|et al|etc|ex)\.$",
        r"\s+(ff|figs?)\.$",
        r"\s+(i\.e|illus)\.$",
        r"\s+ll\.$",
        r"\s+(Mr|Ms|Mrs)\.$",
        r"\s+(pp|par|pt)\.$",
        r"\s+sec\.$",
        # "["が始まっているが"]"で閉じられていない(参考文献表記の途中など)
        r"\[(?!.*\]).*$"
    ]

    def __init__(self, window):
        wx.FileDropTarget.__init__(self)
        self.window = window

    # ウィンドウにファイルがドロップされた時
    def OnDropFiles(self, x, y, filenames):
        # 選択に応じたブラウザを用意
        self.__deepLManager = DeepLManager(self.window.GetBrowserSelection())

        # DeepLのページを開く
        self.__deepLManager.openDeepLPage()

        # ファイルパスをテキストフィールドに表示
        for fi in range(len(filenames)):
            self.window.text.SetValue(filenames[fi])

            addedMessage = ""
            if fi == len(filenames) - 1:
                addedMessage = "\n翻訳を終了します。"
            else:
                addedMessage = "次のファイルの翻訳に移ります。"

            # PDFからテキストを抽出
            textlines = []
            try:
                textlines = extract_text(filenames[fi]).splitlines()
            except PDFSyntaxError:
                # ドロップされたファイルがPDFでない場合は次へ
                message = str(filenames[fi]) + "はPDF形式ではありません。"
                wx.MessageBox(message + addedMessage, "notPDF")
                continue

            # 抽出したテキストから空行を除く
            temp = list(filter(lambda s: s != "", textlines))

            # 除くべき行を除く
            ignore_start_condition = False
            while True:
                textlines = []
                lines_extracting = False    # テキストを抽出中か
                skipLine = False            # その行を飛ばすか
                # 開始条件を無視する場合
                if ignore_start_condition:
                    lines_extracting = True
                for t in temp:
                    # 翻訳を開始する合図となる文字列を探す
                    for sl in self.__start_lines:
                        if search(sl, t, flags=IGNORECASE):
                            lines_extracting = True
                    # 翻訳を打ち切る合図となる文字列を探す
                    for el in self.__end_lines:
                        if search(el, t, flags=IGNORECASE):
                            lines_extracting = False
                    # 翻訳をしないことになったなら、その文字列は飛ばす
                    if not lines_extracting:
                        continue

                    # 翻訳を開始しても、無視する文字列なら飛ばす
                    for il in self.__ignore_lines:
                        if search(il, t, flags=IGNORECASE):
                            skipLine = True
                            break
                    if skipLine:
                        skipLine = False
                        continue

                    textlines.append(t)
                # 行が一つ以上抽出されたなら抜け出す
                if len(textlines) != 0:
                    break
                else:
                    if not ignore_start_condition:
                        message_ignore_start_condition = wx.MessageBox(
                            "テキストが抽出されませんでした。\n"
                            "翻訳開始条件を無視して翻訳を行いますか？",
                            caption="テキストの抽出に失敗",
                            style=wx.YES | wx.NO)
                        if message_ignore_start_condition == wx.YES:
                            ignore_start_condition = True
                        else:
                            break
                    else:
                        break

            if len(textlines) == 0:
                wx.MessageBox(
                    "テキストが抽出されませんでした。" + addedMessage,
                    "テキストの抽出に失敗"
                )
                continue

            # 出力用のディレクトリを作成
            Path("output").mkdir(exist_ok=True)
            # 出力用ファイルのパス
            outputFilePath = Path("output/" + Path(filenames[fi]).stem + ".txt")

            with open(outputFilePath, mode="w", encoding="utf-8") as f:
                paragraphs = []     # 段落ごとに分けて格納
                parslen = 0         # paragraphsの総文字数
                par_buffer = ""     # 今扱っている段落の文字列
                chart_buffer = ""   # 図表の説明の文字列
                chartParagraph = False     # 図表の説明の段落を扱っているフラグ
                tooLongParagraph = False    # 長過ぎる段落を扱っているフラグ
                tooLongMessage = "(一段落が5000文字以上となる可能性があるため、" + \
                                 "自動での適切な翻訳ができません。" + \
                                 "手動で分割して翻訳してください。)\n\n"
                for i in range(len(textlines)):
                    # 図表の説明は本文を寸断している事が多いため、
                    # 図表を示す文字列が文頭に現れた場合は別口で処理する
                    # 例：Fig. 1. | Figure2: | Table 3. など
                    if search(r"^(Fig\.|Figure|Table)\s*\d+(\.|:)",
                              textlines[i], flags=IGNORECASE):
                        chartParagraph = True

                    # 待ち時間を短くするために、DeepLの制限ギリギリまで文字数を詰める
                    # 現在扱っている文字列までの長さを算出
                    currentLen = parslen + len(textlines[i])
                    if chartParagraph:
                        currentLen += len(chart_buffer)
                    else:
                        currentLen += len(par_buffer)
                    print("processing line " + str(i+1) + "/" + str(len(textlines)) + ".")

                    if not tooLongParagraph and currentLen > 4800:
                        # 5000文字を超えそうになったら、それまでの段落を翻訳にかける
                        if parslen > 0:
                            self.__tl_and_write(paragraphs, f)

                            parslen = 0
                            paragraphs = []
                        # 1段落で5000文字を超えるなら、手動での翻訳をお願いする
                        else:
                            tooLongParagraph = True

                    # 文末っぽい表現がされていたり、
                    # その他return_linesに含まれる正規表現に当てはまればそこを文末と見なす
                    return_flag = False
                    for rl in self.__return_lines:
                        if search(rl, textlines[i], flags=IGNORECASE):
                            return_flag = True
                            break

                    # ただし、よくある略語だったりする場合は文末とは見なさない
                    if return_flag:
                        for ril in self.__return_ignore_lines:
                            if search(ril, textlines[i]):
                                return_flag = False
                                break

                    end_of_file = i == len(textlines) - 1   # ファイルの終端フラグ
                    if return_flag or end_of_file:
                        # 5000字を超える一段落は、自動での翻訳を行わない
                        # ファイルの終端でもそれは変わらない
                        temp = ""
                        if tooLongParagraph:
                            if chartParagraph:
                                temp = chart_buffer
                                chart_buffer = ""
                            else:
                                temp = par_buffer
                                par_buffer = ""
                            f.write(temp + textlines[i] +
                                    "\n\n" + tooLongMessage)
                        else:
                            # 長すぎない場合は翻訳待ちの段落として追加
                            if chartParagraph:
                                temp = chart_buffer
                                chart_buffer = ""
                            else:
                                temp = par_buffer
                                par_buffer = ""
                            temp += textlines[i]
                            parslen += len(temp)
                            paragraphs.append(temp)
                            # ファイルの終端の場合は最後に翻訳と書き込みを行う
                            if end_of_file:
                                self.__tl_and_write(paragraphs, f)
                        chartParagraph = False
                    else:
                        # 文末でない場合は末尾に適切な処理を施してバッファに追加
                        temp = ""
                        if textlines[i][-1] == "-":
                            # 文末がハイフンなら除く
                            temp = textlines[i][:-1]
                        else:
                            # そうでないならスペース追加
                            temp = textlines[i] + " "

                        if chartParagraph:
                            chart_buffer += temp
                        else:
                            par_buffer += temp

        self.__deepLManager.closeWindow()

        return True

    # 翻訳とファイルへの書き込みを行う
    def __tl_and_write(self, paragraphs, f):
        translated = self.__deepLManager.translate(
            "\n".join(paragraphs)).splitlines()
        for i in range(len(paragraphs)):
            f.write(paragraphs[i] + "\n\n" + translated[i] + "\n\n")


class WindowFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None,
                          title="DeepL PDF Translator", size=(500, 200))
        p = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        label = wx.StaticText(p, -1, "File name:")
        self.text = wx.TextCtrl(p, -1, "", size=(400, -1))
        sizer.Add(label, 0, wx.ALL, 5)
        sizer.Add(self.text, 0, wx.ALL, 5)

        self.browser_combo = WindowFrame.BrowserCombo(p)
        self.browser_combo.SetStringSelection(Browser.CHROME.value)
        sizer.Add(self.browser_combo,
                  flag=wx.ALIGN_LEFT | wx.TOP | wx.LEFT | wx.BOTTOM, border=10)

        p.SetSizer(sizer)

        dt = MyFileDropTarget(self)
        self.SetDropTarget(dt)
        self.Show()

    def GetBrowserSelection(self):
        return self.browser_combo.GetStringSelection()

    class BrowserCombo(wx.ComboBox):
        def __init__(self, parent):
            browser_combo_elements = (
                Browser.CHROME.value,
                Browser.EDGE.value,
                Browser.FIREFOX.value
            )
            super().__init__(
                parent, wx.ID_ANY, "ブラウザを選択",
                choices=browser_combo_elements, style=wx.CB_READONLY
            )


if __name__ == '__main__':
    app = wx.App()
    WindowFrame()
    app.MainLoop()
