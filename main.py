import re
import wx

from deeplmanager import Browser, DeepLManager
from pathlib import Path
from pdfminer.high_level import extract_text
from pdfminer.pdfparser import PDFSyntaxError
from res import RegularExpressions


class MyFileDropTarget(wx.FileDropTarget):
    __deepLManager = None

    __add_japanese_return = True    # 日本語の文章において一文ごとに改行
    __output_type_markdown = True   # 出力をMarkdown式にする
    __output_source = True     # 英語テキストを出力する
    __source_as_comment = True  # Markdown形式において、英語をコメントとして出力する

    __debug_output_extracted_text = False    # 抽出されたままのテキストを出力する
    __debug_output_mode = ""

    def __init__(self, window):
        wx.FileDropTarget.__init__(self)
        self.window = window

    # ウィンドウにファイルがドロップされた時
    def OnDropFiles(self, x, y, filenames):
        # 各種チェックボックスの値を取得
        self.__add_japanese_return = self.window.chkbx_japanese_return.Value
        self.__output_type_markdown = self.window.chkbx_return_markdown.Value
        self.__output_source = self.window.chkbx_output_source.Value
        self.__source_as_comment = self.window.chkbx_source_as_comment.Value

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
                    for sl in RegularExpressions.start_lines:
                        if re.search(sl, t, flags=re.IGNORECASE):
                            lines_extracting = True
                    # 翻訳を打ち切る合図となる文字列を探す
                    for el in RegularExpressions.end_lines:
                        if re.search(el, t, flags=re.IGNORECASE):
                            lines_extracting = False
                    # 翻訳をしないことになったなら、その文字列は飛ばす
                    if not lines_extracting:
                        continue

                    # 翻訳を開始しても、無視する文字列なら飛ばす
                    for il in RegularExpressions.ignore_lines:
                        if re.search(il, t, flags=re.IGNORECASE):
                            skipLine = True
                            break
                    if skipLine:
                        skipLine = False
                        continue

                    # 置換すべき文字列があったなら置換する
                    for ri in range(len(RegularExpressions.replace_source)):
                        t = re.sub(
                            RegularExpressions.replace_source[ri],
                            RegularExpressions.replace_target[ri],
                            t
                        )
                    if self.__output_type_markdown:
                        for mri in range(len(RegularExpressions.markdown_replace_source)):
                            t = re.sub(
                                RegularExpressions.markdown_replace_source[mri],
                                RegularExpressions.markdown_replace_target[mri],
                                t
                            )

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
            outputFilePath = Path("output/" + Path(filenames[fi]).stem + ("_extracted" if self.__debug_output_extracted_text else "") + ".txt")

            with open(outputFilePath, mode="w", encoding="utf-8") as f:
                # デバッグ用の抽出テキスト出力モード
                if self.__debug_output_extracted_text:
                    # 改行位置を出力
                    if self.__debug_output_mode == "return":
                        print("改行位置となり得る行を抽出して" + str(outputFilePath) + "に出力します。")
                        for tl in textlines:
                            for rl in RegularExpressions.return_lines:
                                if re.search(rl, tl, flags=re.IGNORECASE):
                                    f.write(tl + "\n")
                                    break
                    # 改行を無視する位置を出力
                    elif self.__debug_output_mode == "return_ignore":
                        print("改行を無視する行を抽出して" + str(outputFilePath) + "に出力します。")
                        for tl in textlines:
                            for rl in RegularExpressions.return_lines:
                                if re.search(rl, tl, flags=re.IGNORECASE):
                                    for ril in RegularExpressions.return_ignore_lines:
                                        if re.search(ril, tl, flags=re.IGNORECASE):
                                            f.write(tl + "\n")
                                            break
                                    break
                    # ベタ打ち
                    else:
                        print("抽出されたテキストをそのまま" + str(outputFilePath) + "に出力します。")
                        f.write("\n".join(textlines))
                # 通常の翻訳モード
                else:
                    tl_units = []
                    too_long_flags = []
                    paragraphs = []     # 段落ごとに分けて格納
                    parslen = 0         # paragraphsの総文字数
                    par_buffer = ""     # 今扱っている段落の文字列
                    chart_buffer = ""   # 図表の説明の文字列
                    chartParagraph = False     # 図表の説明の段落を扱っているフラグ
                    tooLongParagraph = False    # 長過ぎる段落を扱っているフラグ
                    # tooLongMessage = "(一段落が5000文字以上となる可能性があるため、自動での適切な翻訳ができません。手動で分割して翻訳してください。)\n\n"
                    for i in range(len(textlines)):
                        # 図表の説明は本文を寸断している事が多いため、
                        # 図表を示す文字列が文頭に現れた場合は別口で処理する
                        # 例：Fig. 1. | Figure2: | Table 3. など
                        if re.search(r"^(Fig\.|Figure|Table)\s*\d+(\.|:)", textlines[i], flags=re.IGNORECASE):
                            chartParagraph = True

                        # 待ち時間を短くするために、DeepLの制限ギリギリまで文字数を詰める
                        # 現在扱っている文字列までの長さを算出
                        currentLen = parslen + len(textlines[i])
                        if chartParagraph:
                            currentLen += len(chart_buffer)
                        else:
                            currentLen += len(par_buffer)

                        if not tooLongParagraph and currentLen > 4800:
                            # 5000文字を超えそうになったら、それまでの段落を翻訳にかける
                            if parslen > 0:
                                # print("processing line " + str(i + 1) + "/" + str(len(textlines)) + "...")
                                tl_units.append(paragraphs)
                                too_long_flags.append(False)
                                # self.__tl_and_write(paragraphs, f)

                                parslen = 0
                                paragraphs = []
                            # 1段落で5000文字を超えるなら、手動での翻訳をお願いする
                            else:
                                tooLongParagraph = True

                        # 文末っぽい表現がされていたり、
                        # その他return_linesに含まれる正規表現に当てはまればそこを文末と見なす
                        return_flag = False
                        for rl in RegularExpressions.return_lines:
                            if re.search(rl, textlines[i], flags=re.IGNORECASE):
                                return_flag = True
                                break

                        # ただし、よくある略語だったりする場合は文末とは見なさない
                        if return_flag:
                            for ril in RegularExpressions.return_ignore_lines:
                                if re.search(ril, textlines[i]):
                                    return_flag = False
                                    break

                        end_of_file = i == len(textlines) - 1   # ファイルの終端フラグ
                        if return_flag or end_of_file:
                            temp = ""
                            if chartParagraph:
                                temp = chart_buffer
                                chart_buffer = ""
                            else:
                                temp = par_buffer
                                par_buffer = ""
                            # 5000字を超える一段落は、自動での翻訳を行わない
                            # ファイルの終端でもそれは変わらない
                            if tooLongParagraph:
                                tl_units.append([temp + textlines[i]])
                                too_long_flags.append(True)
                                # f.write(temp + textlines[i] + "\n\n" + tooLongMessage)
                            else:
                                # 長すぎない場合は翻訳待ちの段落として追加
                                temp += textlines[i]
                                parslen += len(temp)
                                paragraphs.append(temp)
                                # ファイルの終端の場合は最後に翻訳と書き込みを行う
                                if end_of_file:
                                    # print("Processing last line...")
                                    tl_units.append(paragraphs)
                                    too_long_flags.append(False)
                                    # self.__tl_and_write(paragraphs, f)
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

                    # 翻訳作業
                    part_len = len(tl_units)
                    for i in range(part_len):
                        if too_long_flags[i]:
                            # 長過ぎる段落(5000字以上)の場合は自動翻訳できない旨を併記して原文を出力
                            # この場合は設定にかかわらず、原文をコメントアウトせずに出力する
                            f.write(tl_units[i][0] + "\n\n(一段落が5000文字以上となる可能性があるため、自動での適切な翻訳ができません。手動で分割して翻訳してください。)\n\n")
                        else:
                            # それ以外の場合は翻訳を実行
                            print("全体の " + str(i + 1) + "/" + str(part_len + 1) + " を翻訳しています……")
                            self.__tl_and_write(tl_units[i], f)

        self.__deepLManager.closeWindow()

        return True

    # 翻訳とファイルへの書き込みを行う
    def __tl_and_write(self, paragraphs, f):
        translated = self.__deepLManager.translate(
            "\n".join(paragraphs)).splitlines()

        tl_processed = []
        for tl in translated:
            if self.__add_japanese_return:
                # 翻訳文を一文ごとに改行する
                if self.__output_type_markdown:
                    # Markdown方式の改行
                    tl = re.sub(r"(。|．)", "。  \n", tl)
                else:
                    # 通常の改行
                    tl = re.sub(r"(。|．)", "。\n", tl)
            else:
                # 改行しない
                tl = re.sub(r"．", "。", tl)    # 句点を統一
            tl_processed.append(tl)

        for i in range(len(paragraphs)):
            # Markdown方式で出力する場合は見出しに#を加える
            header_line_hit = False
            if self.__output_type_markdown:
                for j in range(len(RegularExpressions.header_lines)):
                    if re.search(RegularExpressions.header_lines[j], paragraphs[i], flags=re.IGNORECASE):
                        header_line_hit = True
                        # 見出しの深さを算出 & #を出力
                        depth = max(1, len(re.findall(
                            RegularExpressions.header_depth_count[j],
                            paragraphs[i])))
                        f.write("#" * min(RegularExpressions.header_max_size[j] + depth - 1, 6) + " ")

                        # 原文の出力を行う場合
                        if self.__output_source:
                            # 原文の見出しとその直下に見出しの日本語訳を出力
                            f.write(paragraphs[i] + "\n")
                            # 日本語の見出し部分の先頭(1.2.など)を削除
                            tl_processed[i] = re.sub(
                                RegularExpressions.header_japanese_remove[j],
                                "", tl_processed[i])

                        f.write(tl_processed[i] + ("\n" if tl_processed[i][-1] == "\n" else "\n\n"))
                        break
                if not header_line_hit:
                    if self.__output_source and self.__source_as_comment:
                        # Markdown式の出力かつ原文の出力が有効で、
                        # 見出しでない場合はコメントとして加工する
                        paragraphs[i] = "%%" + paragraphs[i] + "%%"
            if not header_line_hit:
                # 見出しでない場合の出力
                if self.__output_source:
                    f.write(paragraphs[i] + "\n\n")
                f.write(tl_processed[i] + ("\n" if tl_processed[i][-1] == "\n" else "\n\n"))


class WindowFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="DeepL PDF Translator", size=(500, 250))

        # メニューバーを設定
        menu_bar = wx.MenuBar()
        menu_bar.Append(WindowFrame.FileMenu(), "ファイル")
        menu_bar.Append(WindowFrame.EditMenu(), "編集")
        self.SetMenuBar(menu_bar)

        p = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        label = wx.StaticText(p, -1, "File name:")
        self.text = wx.TextCtrl(p, -1, "", size=(400, -1))
        sizer.Add(label, 0, wx.ALL, 5)
        sizer.Add(self.text, 0, wx.ALL, 5)

        # ブラウザ選択のコンボボックス
        self.browser_combo = WindowFrame.BrowserCombo(p)
        self.browser_combo.SetStringSelection(Browser.CHROME.value)
        sizer.Add(
            self.browser_combo,
            flag=wx.ALIGN_LEFT | wx.TOP | wx.LEFT | wx.BOTTOM, border=10)

        # 各種チェックボックス
        self.chkbx_japanese_return = wx.CheckBox(
            p, -1, "翻訳文を一文ごとに改行する")
        self.chkbx_japanese_return.SetToolTip(
            "出力された日本語の翻訳文を、\"。\"の位置で改行します"
        )
        self.chkbx_japanese_return.SetValue(True)
        sizer.Add(
            self.chkbx_japanese_return,
            flag=wx.ALIGN_LEFT | wx.TOP | wx.LEFT, border=10)

        self.chkbx_return_markdown = wx.CheckBox(
            p, -1, "出力をMarkdown式にする")
        self.chkbx_return_markdown.SetToolTip(
            "見出しや改行をMarkdown式にします"
        )
        self.chkbx_return_markdown.SetValue(True)
        sizer.Add(
            self.chkbx_return_markdown,
            flag=wx.ALIGN_LEFT | wx.LEFT, border=10)

        self.chkbx_output_source = wx.CheckBox(
            p, -1, "原文を出力する")
        self.chkbx_output_source.SetToolTip(
            "原文と翻訳文をセットで出力します。"
        )
        self.chkbx_output_source.SetValue(True)
        sizer.Add(
            self.chkbx_output_source,
            flag=wx.ALIGN_LEFT | wx.LEFT, border=10)

        self.chkbx_source_as_comment = wx.CheckBox(
            p, -1, "原文をコメントとして出力する")
        self.chkbx_source_as_comment.SetToolTip(
            "Markdown形式において、原文をコメントとして出力します。"
        )
        self.chkbx_source_as_comment.SetValue(True)
        sizer.Add(
            self.chkbx_source_as_comment,
            flag=wx.ALIGN_LEFT | wx.LEFT, border=10)

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

    class FileMenu(wx.Menu):
        def __init__(self):
            super().__init__()
            self.Append(10000, "翻訳対象のPDFファイルを開く")

    class EditMenu(wx.Menu):
        def __init__(self):
            super().__init__()
            self.Append(20000, "翻訳開始条件の正規表現を編集")
            self.Append(20100, "翻訳終了条件の正規表現を編集")
            self.start_ignore = self.AppendCheckItem(
                20001, "翻訳開始条件を無視して最初から翻訳する")
            self.end_ignore = self.AppendCheckItem(
                20101, "翻訳終了条件を無視して最後まで翻訳する")
            self.AppendSeparator()
            self.Append(20200, "無視条件の正規表現を編集")
            self.Append(20300, "段落終了条件の正規表現を編集")
            self.Append(20400, "段落終了無視条件の正規表現を編集")
            self.Append(20500, "置換条件の正規表現を編集")
            self.Append(20600, "見出し条件の正規表現を編集")


if __name__ == '__main__':
    app = wx.App()
    WindowFrame()
    app.MainLoop()
