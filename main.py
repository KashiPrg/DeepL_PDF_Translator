import wx

from deeplmanager import Browser, DeepLManager
from pdftranslator import PDFTranslator


class MyFileDropTarget(wx.FileDropTarget):
    def __init__(self, window):
        wx.FileDropTarget.__init__(self)
        self.window = window

    # ウィンドウにファイルがドロップされた時
    def OnDropFiles(self, x, y, filenames):
        # 各種チェックボックスの値を取得
        add_japanese_return = self.window.chkbx_japanese_return.Value
        output_type_markdown = self.window.chkbx_return_markdown.Value
        output_source = self.window.chkbx_output_source.Value
        source_as_comment = self.window.chkbx_source_as_comment.Value

        # 選択に応じたブラウザを用意
        deepLManager = DeepLManager(self.window.GetBrowserSelection())

        p_tl = PDFTranslator(
            deepLManager,
            add_japanese_return,
            output_type_markdown,
            output_source,
            source_as_comment,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            False
        )

        for fn in filenames:
            p_tl.PDFTranslate(fn)

        deepLManager.closeWindow()

        return True


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

        # ブラウザ選択のラベル
        browser_label = wx.StaticText(p, -1, "使用ウェブブラウザ")
        sizer.Add(browser_label, flag=wx.ALIGN_LEFT | wx.TOP | wx.LEFT, border=10)

        # ブラウザ選択のコンボボックス
        self.browser_combo = WindowFrame.BrowserCombo(p)
        self.browser_combo.SetStringSelection(Browser.CHROME.value)
        sizer.Add(self.browser_combo, flag=wx.ALIGN_LEFT | wx.LEFT | wx.BOTTOM, border=10)

        # 各種チェックボックス
        self.chkbx_japanese_return = wx.CheckBox(p, -1, "翻訳文を一文ごとに改行する")
        self.chkbx_japanese_return.SetToolTip("出力された日本語の翻訳文を、\"。\"の位置で改行します")
        self.chkbx_japanese_return.SetValue(True)
        sizer.Add(self.chkbx_japanese_return, flag=wx.ALIGN_LEFT | wx.TOP | wx.LEFT, border=10)

        self.chkbx_return_markdown = wx.CheckBox(p, -1, "出力をMarkdown式にする")
        self.chkbx_return_markdown.SetToolTip("見出しや改行をMarkdown式にします")
        self.chkbx_return_markdown.SetValue(True)
        sizer.Add(self.chkbx_return_markdown, flag=wx.ALIGN_LEFT | wx.LEFT, border=10)

        self.chkbx_output_source = wx.CheckBox(p, -1, "原文を出力する")
        self.chkbx_output_source.SetToolTip("原文と翻訳文をセットで出力します。")
        self.chkbx_output_source.SetValue(True)
        sizer.Add(self.chkbx_output_source, flag=wx.ALIGN_LEFT | wx.LEFT, border=10)

        self.chkbx_source_as_comment = wx.CheckBox(p, -1, "原文をコメントとして出力する")
        self.chkbx_source_as_comment.SetToolTip("Markdown形式において、原文をコメントとして出力します。")
        self.chkbx_source_as_comment.SetValue(True)
        sizer.Add(self.chkbx_source_as_comment, flag=wx.ALIGN_LEFT | wx.LEFT, border=10)

        p.SetSizer(sizer)

        dt = MyFileDropTarget(self)
        self.SetDropTarget(dt)
        self.Show()

    def GetBrowserSelection(self):
        """
        ブラウザ選択のコンボボックスで何を選択しているかを取得する

        Returns:
            string: 選択しているウェブブラウザの名前
        """
        return self.browser_combo.GetStringSelection()

    # ブラウザ選択のコンボボックス
    class BrowserCombo(wx.ComboBox):
        """
        ブラウザ選択のコンボボックス

        Args:
            parent: 親要素
        """
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
        """
        メニューバーの[ファイル]
        """
        def __init__(self):
            super().__init__()
            self.Append(10000, "翻訳対象のPDFファイルを開く")

    class EditMenu(wx.Menu):
        """
        メニューバーの[編集]
        """
        def __init__(self):
            super().__init__()
            self.Append(20000, "翻訳開始条件の正規表現を編集")
            self.Append(20100, "翻訳終了条件の正規表現を編集")
            self.start_ignore = self.AppendCheckItem(20001, "翻訳開始条件を無視して最初から翻訳する")
            self.end_ignore = self.AppendCheckItem(20101, "翻訳終了条件を無視して最後まで翻訳する")
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
