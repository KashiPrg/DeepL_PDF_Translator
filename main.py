import wx

from data import Target_Lang, Browser, MainWindow_MenuBar_Menu, MainWindow_ComboBox_ID, MainWindow_CheckBox_ID
# from deeplmanager import DeepLManager
from pathlib import Path
from pdftranslator import PDFTranslate
from settings import Settings
from threading import Thread
from utils import ProgressBar


class ProgressWindow(wx.Frame):
    """
    プログレスバーを擁するウインドウ

    wx.ProgressDialogが機能しないため自作
    """
    def __init__(self, parent, title, text, buttontext="キャンセル", maxprogress=100, progress_on_title=False):
        # タイトルの末尾に進捗状況を載せるか
        self.__progress_on_title = progress_on_title
        # 進捗の最大段階(最低1)
        self.__maxprogress = max(1, maxprogress)
        self.__progress = 0
        progress = self.__GetProgressText()
        self.__title = title
        super().__init__(
            parent,
            title=self.__title + (progress if self.__progress_on_title else ""),
            size=(450, 160),
            style=wx.CAPTION
        )
        # ウインドウの背景
        self.__background = wx.Panel(self)
        # 翻訳中……などのテキスト
        self.__text = wx.StaticText(self.__background, label=text, pos=(25, 18))
        # 進捗を表す文字列
        self.__progresstext = wx.StaticText(self.__background, label=progress, pos=(25, 45))
        # 進捗を表すバー
        self.__progressbar = ProgressBar(self.__background, (25, 63), (384, 12), self.__maxprogress)
        # キャンセルボタン
        self.__cancelbutton = wx.Button(self.__background, label=buttontext, pos=(329, 85), size=(80, 25))
        self.__cancelbutton.SetToolTip("現在DeepLで実行中の翻訳を最後に、翻訳を中止します。")
        self.__cancelbutton.Bind(wx.EVT_BUTTON, self.CancelButtonEvent)
        # キャンセルボタンが押されたか
        self.__canceled = False
        self.Show()

    def CancelButtonEvent(self, event):
        """
        キャンセルボタンが押された時のイベント
        """
        self.__progressbar.Freeze()
        self.__canceled = True

    def IsCanceled(self):
        """
        キャンセルボタンが押されたか
        """
        return self.__canceled

    def ChangeMaxProgress(self, maxprogress):
        # 新しい最大進捗を適用
        self.__maxprogress = maxprogress
        # 現在の進捗がはみ出ていたら戻す
        self.__progress = max(0, min(self.__maxprogress, self.__progress))
        # バー側も更新
        self.__progressbar.ChangeMaxProgress(self.__maxprogress)
        # 自身の表示も更新
        self.UpdateProgress(self.__progress)

    def UpdateProgress(self, progress):
        """
        進捗を更新する

        Args:
            progress (int): 進捗
        """
        # 0～最大の間に収める
        self.__progress = max(0, min(self.__maxprogress, progress))
        # 進捗テキストを更新
        progress = self.__GetProgressText()
        if self.__progress_on_title:
            self.SetTitle(self.__title + progress)
        self.__progresstext.SetLabelText(progress)
        # プログレスバーを更新
        self.__progressbar.Update(self.__progress)

    def __GetProgressText(self):
        return "(" + str(self.__progress) + "/" + str(self.__maxprogress) + ")"

    def UpdateText(self, text):
        """
        ウインドウのテキストを更新する

        Args:
            text (string): テキスト
        """
        self.__text.SetLabelText(text)


def Translation_Threading(main_window, filename):
    fn = Path(filename).name
    progress_window = ProgressWindow(
        main_window,
        fn + "を翻訳中",
        fn + "を翻訳中…",
        buttontext="翻訳中止",
        progress_on_title=True)
    th = Thread(target=PDFTranslate, args=(main_window, progress_window, filename))
    th.setDaemon(True)  # アプリが終了したらこのスレッドも終了する
    th.start()


class MyFileDropTarget(wx.FileDropTarget):
    def __init__(self, window):
        wx.FileDropTarget.__init__(self)
        self.window = window

    # ウィンドウにファイルがドロップされた時
    def OnDropFiles(self, x, y, filenames):

        for fn in filenames:
            Translation_Threading(self.window, fn)
            # PDFTranslate(fn)

        return True


class WindowFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="DeepL PDF Translator", size=(500, 250))

        # ウインドウを閉じた時のイベント
        self.Bind(wx.EVT_CLOSE, self.Window_Close_Event)

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
        self.target_lang_combo = WindowFrame.TargetLangCombo(p, MainWindow_ComboBox_ID.TARGET_LANG.value)  # 下で設定したクラスから引っ張ってくる
        self.target_lang_combo.SetStringSelection(Settings.target_language)     # 最初の値を設定ファイルから引っ張ってくる
        self.target_lang_combo.Bind(wx.EVT_COMBOBOX, self.TargetLangCombo_Event)   # 選択時のイベントを設定
        sizer.Add(self.target_lang_combo, flag=wx.ALIGN_LEFT | wx.LEFT, border=10)

        # ブラウザ選択のラベル
        browser_label = wx.StaticText(p, -1, "使用ウェブブラウザ")
        sizer.Add(browser_label, flag=wx.ALIGN_LEFT | wx.LEFT, border=10)

        # ブラウザ選択のコンボボックス
        self.browser_combo = WindowFrame.BrowserCombo(p, MainWindow_ComboBox_ID.WEB_BROWSER.value)
        self.browser_combo.SetStringSelection(Settings.web_browser)
        self.browser_combo.Bind(wx.EVT_COMBOBOX, self.BrowserCombo_Event)
        sizer.Add(self.browser_combo, flag=wx.ALIGN_LEFT | wx.LEFT | wx.BOTTOM, border=10)

        # 各種チェックボックス
        self.chkbx_target_return = wx.CheckBox(p, MainWindow_CheckBox_ID.ADD_TARGET_RETURN.value, "翻訳文を一文ごとに改行する")
        self.chkbx_target_return.SetToolTip("出力された日本語の翻訳文を、\"。\"の位置で改行します")
        self.chkbx_target_return.SetValue(Settings.add_target_return)
        self.chkbx_target_return.Bind(wx.EVT_CHECKBOX, self.CheckBox_TargetReturn_Event)
        sizer.Add(self.chkbx_target_return, flag=wx.ALIGN_LEFT | wx.TOP | wx.LEFT, border=10)

        self.chkbx_return_markdown = wx.CheckBox(p, MainWindow_CheckBox_ID.OUTPUT_TYPE_MARKDOWN.value, "出力をMarkdown式にする")
        self.chkbx_return_markdown.SetToolTip("見出しや改行をMarkdown式にします")
        self.chkbx_return_markdown.SetValue(Settings.output_type_markdown)
        self.chkbx_return_markdown.Bind(wx.EVT_CHECKBOX, self.CheckBox_ReturnMarkdown_Event)
        sizer.Add(self.chkbx_return_markdown, flag=wx.ALIGN_LEFT | wx.LEFT, border=10)

        self.chkbx_output_source = wx.CheckBox(p, MainWindow_CheckBox_ID.OUTPUT_SOURCE.value, "原文を出力する")
        self.chkbx_output_source.SetToolTip("原文と翻訳文をセットで出力します。")
        self.chkbx_output_source.SetValue(Settings.output_source)
        self.chkbx_output_source.Bind(wx.EVT_CHECKBOX, self.CheckBox_OutputSource_Event)
        sizer.Add(self.chkbx_output_source, flag=wx.ALIGN_LEFT | wx.LEFT, border=10)

        self.chkbx_source_as_comment = wx.CheckBox(p, MainWindow_CheckBox_ID.SOURCE_AS_COMMENT.value, "原文をコメントとして出力する")
        self.chkbx_source_as_comment.SetToolTip("Markdown形式において、原文をコメントとして出力します。")
        self.chkbx_source_as_comment.SetValue(Settings.source_as_comment)
        self.chkbx_source_as_comment.Bind(wx.EVT_CHECKBOX, self.CheckBox_SourceAsComment_Event)
        sizer.Add(self.chkbx_source_as_comment, flag=wx.ALIGN_LEFT | wx.LEFT, border=10)

        p.SetSizer(sizer)

        dt = MyFileDropTarget(self)
        self.SetDropTarget(dt)
        self.Show()

    # ウィンドウを閉じるときに発生するイベント
    def Window_Close_Event(self, event):
        Settings.SaveSettings()  # 変更した設定を保存する
        self.Destroy()  # イベントを発行すると自動では閉じなくなるので手動で閉じる

    # 各種チェックボックス選択時に発生するイベント
    def CheckBox_TargetReturn_Event(self, event):
        Settings.add_target_return = self.chkbx_target_return.GetValue()

    def CheckBox_ReturnMarkdown_Event(self, event):
        Settings.output_type_markdown = self.chkbx_return_markdown.GetValue()

    def CheckBox_OutputSource_Event(self, event):
        Settings.output_source = self.chkbx_output_source.GetValue()

    def CheckBox_SourceAsComment_Event(self, event):
        Settings.source_as_comment = self.chkbx_source_as_comment.GetValue()

    def TargetLangCombo_Event(self, event):
        """
        言語選択のコンボボックス選択時に発生するイベント
        """
        Settings.target_language = self.GetTargetLangSelection()

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
        Settings.web_browser = self.GetBrowserSelection()

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
        if event_id == MainWindow_MenuBar_Menu.OPEN_PDF_FILE.value:
            self.OpenAndTranslatePDF()

    class FileMenu(wx.Menu):
        """
        メニューバーの[ファイル]
        """
        def __init__(self):
            super().__init__()
            self.Append(MainWindow_MenuBar_Menu.OPEN_PDF_FILE.value, "翻訳対象のPDFファイルを開く")

    def OpenAndTranslatePDF(self):
        # ファイル選択ダイアログを作成
        dialog = wx.FileDialog(
            None,
            message="翻訳対象のPDFファイルを選択してください",
            wildcard="PDF file(*.pdf) | *.pdf",
            style=wx.FD_OPEN)

        # ファイルを選択させる
        dialog.ShowModal()

        return PDFTranslate(self, dialog.GetPath())

    class EditMenu(wx.Menu):
        """
        メニューバーの[編集]
        """
        def __init__(self):
            super().__init__()
            self.Append(MainWindow_MenuBar_Menu.EDIT_START_RE.value, "翻訳開始条件の正規表現を編集")
            self.Append(MainWindow_MenuBar_Menu.EDIT_END_RE.value, "翻訳終了条件の正規表現を編集")
            self.start_ignore = self.AppendCheckItem(MainWindow_MenuBar_Menu.CHECKBOX_IGNORE_START_CONDITION.value, "翻訳開始条件を無視して最初から翻訳する")
            self.end_ignore = self.AppendCheckItem(MainWindow_MenuBar_Menu.CHECKBOX_IGNORE_END_CONDITION.value, "翻訳終了条件を無視して最後まで翻訳する")
            self.AppendSeparator()
            self.Append(MainWindow_MenuBar_Menu.EDIT_IGNORE_RE.value, "無視条件の正規表現を編集")
            self.Append(MainWindow_MenuBar_Menu.EDIT_RETURN_RE.value, "段落終了条件の正規表現を編集")
            self.Append(MainWindow_MenuBar_Menu.EDIT_RETURN_IGNORE_RE.value, "段落終了無視条件の正規表現を編集")
            self.Append(MainWindow_MenuBar_Menu.EDIT_REPLACE_RE.value, "置換条件の正規表現を編集")
            self.Append(MainWindow_MenuBar_Menu.EDIT_HEADER_RE.value, "見出し条件の正規表現を編集")


if __name__ == '__main__':
    app = wx.App()
    WindowFrame()
    app.MainLoop()
