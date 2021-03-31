import wx

from deeplmanager import Target_Lang, language_dict, Browser, DeepLManager
from enum import Enum
from pdftranslator import PDFTranslator
from settings import Settings, MainWindowSettings


class MenuBar_Menu(Enum):
    OPEN_PDF_FILE = 101
    EDIT_START_RE = 201
    EDIT_END_RE = 202
    CHECKBOX_IGNORE_START_CONDITION = 20101
    CHECKBOX_IGNORE_END_CONDITION = 20201
    EDIT_IGNORE_RE = 203
    EDIT_RETURN_RE = 204
    EDIT_RETURN_IGNORE_RE = 205
    EDIT_REPLACE_RE = 206
    EDIT_HEADER_RE = 207


class ComboBox_ID(Enum):
    TARGET_LANG = 1
    WEB_BROWSER = 2


class CheckBox_ID(Enum):
    ADD_TARGET_RETURN = 3
    RETURN_TYPE_MARKDOWN = 4
    OUTPUT_SOURCE = 5
    SOURCE_AS_COMMENT = 6


class MyFileDropTarget(wx.FileDropTarget):
    def __init__(self, window):
        wx.FileDropTarget.__init__(self)
        self.window = window

    # ウィンドウにファイルがドロップされた時
    def OnDropFiles(self, x, y, filenames):
        # 各種チェックボックスの値を取得
        add_target_return = self.window.chkbx_target_return.Value
        output_type_markdown = self.window.chkbx_return_markdown.Value
        output_source = self.window.chkbx_output_source.Value
        source_as_comment = self.window.chkbx_source_as_comment.Value

        # 選択に応じたブラウザを用意
        deepLManager = DeepLManager(self.window.GetBrowserSelection())

        p_tl = PDFTranslator(
            deepLManager,
            language_dict[self.window.GetTargetLangSelection()],
            add_target_return,
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

        # 設定を取得
        self.__settings = Settings()

        # メニューバーを設定
        menu_bar = wx.MenuBar()
        menu_bar.Append(WindowFrame.FileMenu(), "ファイル")
        menu_bar.Append(WindowFrame.EditMenu(), "編集")
        self.Bind(wx.EVT_MENU, self.Menu_Event)    # メニュー選択時のイベント
        self.SetMenuBar(menu_bar)

        p = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # 言語選択のラベル
        target_lang_label = wx.StaticText(p, -1, "翻訳先の言語")
        sizer.Add(target_lang_label, flag=wx.ALIGN_LEFT | wx.TOP | wx.LEFT, border=10)

        # 言語選択のコンボボックス
        self.target_lang_combo = WindowFrame.TargetLangCombo(p, ComboBox_ID.TARGET_LANG.value)  # 下で設定したクラスから引っ張ってくる
        self.target_lang_combo.SetStringSelection(self.__settings.GetMainWindowSetting(MainWindowSettings.STR_TARGET_LANG))     # 最初の値を設定ファイルから引っ張ってくる
        self.target_lang_combo.Bind(wx.EVT_COMBOBOX, self.TargetLangCombo_Event)   # 選択時のイベントを設定
        sizer.Add(self.target_lang_combo, flag=wx.ALIGN_LEFT | wx.LEFT, border=10)

        # ブラウザ選択のラベル
        browser_label = wx.StaticText(p, -1, "使用ウェブブラウザ")
        sizer.Add(browser_label, flag=wx.ALIGN_LEFT | wx.LEFT, border=10)

        # ブラウザ選択のコンボボックス
        self.browser_combo = WindowFrame.BrowserCombo(p, ComboBox_ID.WEB_BROWSER.value)
        self.browser_combo.SetStringSelection(self.__settings.GetMainWindowSetting(MainWindowSettings.STR_WEB_BROWSER))
        self.browser_combo.Bind(wx.EVT_COMBOBOX, self.BrowserCombo_Event)
        sizer.Add(self.browser_combo, flag=wx.ALIGN_LEFT | wx.LEFT | wx.BOTTOM, border=10)

        # 各種チェックボックス
        self.chkbx_target_return = wx.CheckBox(p, CheckBox_ID.ADD_TARGET_RETURN.value, "翻訳文を一文ごとに改行する")
        self.chkbx_target_return.SetToolTip("出力された日本語の翻訳文を、\"。\"の位置で改行します")
        self.chkbx_target_return.SetValue(self.__settings.GetMainWindowSetting(MainWindowSettings.BOOL_ADD_TARGET_RETURN))
        self.chkbx_target_return.Bind(wx.EVT_CHECKBOX, self.CheckBox_TargetReturn_Event)
        sizer.Add(self.chkbx_target_return, flag=wx.ALIGN_LEFT | wx.TOP | wx.LEFT, border=10)

        self.chkbx_return_markdown = wx.CheckBox(p, CheckBox_ID.RETURN_TYPE_MARKDOWN.value, "出力をMarkdown式にする")
        self.chkbx_return_markdown.SetToolTip("見出しや改行をMarkdown式にします")
        self.chkbx_return_markdown.SetValue(self.__settings.GetMainWindowSetting(MainWindowSettings.BOOL_RETURN_TYPE_MARKDOWN))
        self.chkbx_return_markdown.Bind(wx.EVT_CHECKBOX, self.CheckBox_ReturnMarkdown_Event)
        sizer.Add(self.chkbx_return_markdown, flag=wx.ALIGN_LEFT | wx.LEFT, border=10)

        self.chkbx_output_source = wx.CheckBox(p, CheckBox_ID.OUTPUT_SOURCE.value, "原文を出力する")
        self.chkbx_output_source.SetToolTip("原文と翻訳文をセットで出力します。")
        self.chkbx_output_source.SetValue(self.__settings.GetMainWindowSetting(MainWindowSettings.BOOL_OUTPUT_SOURCE))
        self.chkbx_output_source.Bind(wx.EVT_CHECKBOX, self.CheckBox_OutputSource_Event)
        sizer.Add(self.chkbx_output_source, flag=wx.ALIGN_LEFT | wx.LEFT, border=10)

        self.chkbx_source_as_comment = wx.CheckBox(p, CheckBox_ID.SOURCE_AS_COMMENT.value, "原文をコメントとして出力する")
        self.chkbx_source_as_comment.SetToolTip("Markdown形式において、原文をコメントとして出力します。")
        self.chkbx_source_as_comment.SetValue(self.__settings.GetMainWindowSetting(MainWindowSettings.BOOL_SOURCE_AS_COMMENT))
        self.chkbx_source_as_comment.Bind(wx.EVT_CHECKBOX, self.CheckBox_SourceAsComment_Event)
        sizer.Add(self.chkbx_source_as_comment, flag=wx.ALIGN_LEFT | wx.LEFT, border=10)

        p.SetSizer(sizer)

        dt = MyFileDropTarget(self)
        self.SetDropTarget(dt)
        self.Show()

    # 各種チェックボックス選択時に発生するイベント
    def CheckBox_TargetReturn_Event(self, event):
        self.__settings.SetMainWindowSetting(MainWindowSettings.BOOL_ADD_TARGET_RETURN, self.chkbx_target_return.GetValue())

    def CheckBox_ReturnMarkdown_Event(self, event):
        self.__settings.SetMainWindowSetting(MainWindowSettings.BOOL_RETURN_TYPE_MARKDOWN, self.chkbx_return_markdown.GetValue())

    def CheckBox_OutputSource_Event(self, event):
        self.__settings.SetMainWindowSetting(MainWindowSettings.BOOL_OUTPUT_SOURCE, self.chkbx_output_source.GetValue())

    def CheckBox_SourceAsComment_Event(self, event):
        self.__settings.SetMainWindowSetting(MainWindowSettings.BOOL_SOURCE_AS_COMMENT, self.chkbx_source_as_comment.GetValue())

    def TargetLangCombo_Event(self, event):
        """
        言語選択のコンボボックス選択時に発生するイベント
        """
        self.__settings.SetMainWindowSetting(MainWindowSettings.STR_TARGET_LANG, self.GetTargetLangSelection())

    def GetTargetLangSelection(self):
        """
        言語選択のコンボボックスで何を選択しているかを取得する

        Returns:
            string: 選択している言語の名前
        """
        return self.target_lang_combo.GetStringSelection()

    class TargetLangCombo(wx.ComboBox):
        """
        言語選択のコンボボックス

        Args:
            parent: 親要素
        """
        def __init__(self, parent, id):
            target_lang_combo_elements = [
                Target_Lang.BULGARIAN.value,
                Target_Lang.CHINESE_SIMPLIFIED.value,
                Target_Lang.CZECH.value,
                Target_Lang.DANISH.value,
                Target_Lang.DUTCH.value,
                Target_Lang.ENGLISH_GB.value,
                Target_Lang.ENGLISH_US.value,
                Target_Lang.ESTONIAN.value,
                Target_Lang.FINNISH.value,
                Target_Lang.FRENCH.value,
                Target_Lang.GERMAN.value,
                Target_Lang.GREEK.value,
                Target_Lang.HUNGARIAN.value,
                Target_Lang.ITALIAN.value,
                Target_Lang.JAPANESE.value,
                Target_Lang.LATVIAN.value,
                Target_Lang.LITHUANIAN.value,
                Target_Lang.POLISH.value,
                Target_Lang.PORTUGUESE.value,
                Target_Lang.PORTUGUESE_BR.value,
                Target_Lang.ROMANIAN.value,
                Target_Lang.RUSSIAN.value,
                Target_Lang.SLOVAK.value,
                Target_Lang.SLOVENIAN.value,
                Target_Lang.SPANISH.value,
                Target_Lang.SWEDISH.value
            ]
            super().__init__(parent, id, "言語を選択", choices=sorted(target_lang_combo_elements), style=wx.CB_READONLY)

    def BrowserCombo_Event(self, event):
        """
        ブラウザ選択のコンボボックス選択時に発生するイベント
        """
        self.__settings.SetMainWindowSetting(MainWindowSettings.STR_WEB_BROWSER, self.GetBrowserSelection())

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
        def __init__(self, parent, id):
            browser_combo_elements = (
                Browser.CHROME.value,
                Browser.EDGE.value,
                Browser.FIREFOX.value
            )
            super().__init__(parent, id, "ブラウザを選択", choices=browser_combo_elements, style=wx.CB_READONLY)

    def Menu_Event(self, event):
        """
        選ばれたメニューに応じて操作を行う
        """
        event_id = event.GetId()
        if event_id == MenuBar_Menu.OPEN_PDF_FILE.value:
            self.OpenAndTranslatePDF()

    class FileMenu(wx.Menu):
        """
        メニューバーの[ファイル]
        """
        def __init__(self):
            super().__init__()
            self.Append(MenuBar_Menu.OPEN_PDF_FILE.value, "翻訳対象のPDFファイルを開く")

    def OpenAndTranslatePDF(self):
        # ファイル選択ダイアログを作成
        dialog = wx.FileDialog(
            None,
            message="翻訳対象のPDFファイルを選択してください",
            wildcard="PDF file(*.pdf) | *.pdf",
            style=wx.FD_OPEN)

        # ファイルを選択させる
        dialog.ShowModal()

        p_tl = PDFTranslator(
            DeepLManager(self.GetBrowserSelection()),
            language_dict[self.GetTargetLangSelection()],
            self.chkbx_target_return.Value,
            self.chkbx_return_markdown.Value,
            self.chkbx_output_source.Value,
            self.chkbx_source_as_comment,
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

        return p_tl.PDFTranslate(dialog.GetPath())

    class EditMenu(wx.Menu):
        """
        メニューバーの[編集]
        """
        def __init__(self):
            super().__init__()
            self.Append(MenuBar_Menu.EDIT_START_RE.value, "翻訳開始条件の正規表現を編集")
            self.Append(MenuBar_Menu.EDIT_END_RE.value, "翻訳終了条件の正規表現を編集")
            self.start_ignore = self.AppendCheckItem(MenuBar_Menu.CHECKBOX_IGNORE_START_CONDITION.value, "翻訳開始条件を無視して最初から翻訳する")
            self.end_ignore = self.AppendCheckItem(MenuBar_Menu.CHECKBOX_IGNORE_END_CONDITION.value, "翻訳終了条件を無視して最後まで翻訳する")
            self.AppendSeparator()
            self.Append(MenuBar_Menu.EDIT_IGNORE_RE.value, "無視条件の正規表現を編集")
            self.Append(MenuBar_Menu.EDIT_RETURN_RE.value, "段落終了条件の正規表現を編集")
            self.Append(MenuBar_Menu.EDIT_RETURN_IGNORE_RE.value, "段落終了無視条件の正規表現を編集")
            self.Append(MenuBar_Menu.EDIT_REPLACE_RE.value, "置換条件の正規表現を編集")
            self.Append(MenuBar_Menu.EDIT_HEADER_RE.value, "見出し条件の正規表現を編集")


if __name__ == '__main__':
    app = wx.App()
    WindowFrame()
    app.MainLoop()
