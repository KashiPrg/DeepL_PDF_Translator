import wx

from enum import Enum
from pathlib import Path
from pdfminer.high_level import extract_text
from pdfminer.pdfparser import PDFSyntaxError
from re import search, IGNORECASE
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from sys import stderr
from time import sleep


# DeepLでの翻訳を管理する
class DeepLManager:
    def __init__(self, browser):
        if browser == DeepLManager.Browser.CHROME:
            self.__webDriver = webdriver.Chrome(
                "./drivers/windows/chromedriver.exe")
        elif browser == DeepLManager.Browser.EDGE:
            self.__webDriver = webdriver.Edge(
                "./drivers/windows/msedgedriver.exe")
        else:
            # Firefoxはなぜかexecutable_pathで指定しないとエラーが起きる
            self.__webDriver = webdriver.Firefox(
                executable_path="./drivers/windows/geckodriver.exe")

    class Browser(Enum):
        CHROME = "chrome"
        EDGE = "edge"
        FIREFOX = "firefox"

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
            except NoSuchElementException:
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
    # このリストに含まれる正規表現に当てはまる文字列は無視する
    __ignore_lines = [r"^ACM Trans", r"^[0-9]:[0-9]", r"[0-9]:[0-9]$", r"•$", r"Peng Wang, Lingjie Liu, Nenglun Chen, Hung-Kuo Chu, Christian Theobalt, and Wenping Wang$"]
    # このリストに含まれる正規表現に当てはまる文字列がある行で改行する
    __return_lines = [r"(\.|:|\([0-9]+\))\s*$", r"[0-9]+\s*\.?\s*introduction", r"[0-9]+\s*\.?\s*related works?", r"[0-9]+\s*\.?\s*overview", r"[0-9]+\s*\.?\s*algorithm", r"[0-9]+\s*\.?\s*experimental results", r"[0-9]+\s*\.?\s*conclusions", r"acknowledgements", r"references"]

    def __init__(self, window):
        wx.FileDropTarget.__init__(self)
        self.window = window

    # ウィンドウにファイルがドロップされた時
    def OnDropFiles(self, x, y, filenames):
        # Chromeのブラウザを用意
        self.__deepLManager = DeepLManager(DeepLManager.Browser.FIREFOX)

        # DeepLのページを開く
        self.__deepLManager.openDeepLPage()

        # ファイルパスをテキストフィールドに表示
        for file in filenames:
            self.window.text.SetValue(file)

            # PDFからテキストを抽出
            textlines = []
            try:
                textlines = extract_text(file).splitlines()
            except PDFSyntaxError:
                # ドロップされたファイルがPDFでない場合は次へ
                print(file + " is not a PDF.")
                continue

            # 抽出したテキストから空行を除く
            temp = list(filter(lambda s: s != "", textlines))

            # 無視すべき文字列が入った行を除く
            textlines = []
            skipLine = False
            for t in temp:
                for il in self.__ignore_lines:
                    if search(il, t, flags=IGNORECASE):
                        skipLine = True
                        break
                if skipLine:
                    skipLine = False
                    continue

                # 行末が"-"の場合は取り除く
                if t[-1] == "-":
                    t = t[:-1]
                textlines.append(t)

            # 出力用のディレクトリを作成
            Path("output").mkdir(exist_ok=True)
            # 出力用ファイルのパス
            outputFilePath = Path("output/" + Path(file).stem + ".txt")

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

                    # 行末にピリオドまたはコロン、数字のみを含んだカッコがあるか、
                    # その他return_linesに含まれる正規表現に当てはまればそこを文末と見なす
                    return_flag = False
                    for rl in self.__return_lines:
                        if search(rl, textlines[i], flags=IGNORECASE):
                            return_flag = True
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
                        # 文末でない場合はスペースを加えた文字列をバッファに追加する
                        if chartParagraph:
                            chart_buffer += textlines[i] + " "
                        else:
                            par_buffer += textlines[i] + " "

        self.DeepLManager.closeWindow()

        return True

    # 翻訳とファイルへの書き込みを行う
    def __tl_and_write(self, paragraphs, f):
        translated = self.__deepLManager.translate(
            "\n".join(paragraphs)).splitlines()
        for i in range(len(paragraphs)):
            f.write(paragraphs[i] + "\n\n" + translated[i] + "\n\n")


class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None,
                          title="DeepL PDF Translator", size=(500, 200))
        p = wx.Panel(self)
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        label = wx.StaticText(p, -1, "File name:")
        self.text = wx.TextCtrl(p, -1, "", size=(400, -1))
        sizer.Add(label, 0, wx.ALL, 5)
        sizer.Add(self.text, 0, wx.ALL, 5)
        p.SetSizer(sizer)

        dt = MyFileDropTarget(self)
        self.SetDropTarget(dt)
        self.Show()


if __name__ == '__main__':
    app = wx.App()
    MyFrame()
    app.MainLoop()
