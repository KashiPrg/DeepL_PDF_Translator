import wx

from copy import copy, deepcopy
from data import RegularExpressionsWindow_MenuBar_Menu, res_introduction, res_default_column_labels, res_default_column_tips, res_default_column_widths, res_replace_column_labels, res_replace_column_tips, res_replace_column_widths, res_header_column_labels, res_header_column_tips, res_header_column_widths
from settings import Settings
from wx.lib.agw import ultimatelistctrl as ULC
from wx.lib.scrolledpanel import ScrolledPanel


def handler(func, *args):
    """
    メソッドを実行するメソッド

    Args:
        func (pointer of function): 実行対象のメソッド

    Returns:
        実行したメソッドの戻り値
    """
    return func(*args)


def move_listitem(target_list, index, target_pos):
    """リストの要素を移動させる

    Args:
        target_list (list): 対象のリスト
        index (int): 移動させたい要素の位置
        target_pos (int): 移動先の位置
    """
    if index > target_pos:
        target_list[target_pos], target_list[target_pos + 1:index + 1] = target_list[index], target_list[target_pos:index]
    elif index < target_pos:
        target_list[target_pos], target_list[index:target_pos] = target_list[index], target_list[index + 1:target_pos + 1]


class InputItemInfoWindow(wx.Frame):
    """
    リストボックスの項目の情報を入力するウインドウ(抽象クラス)
    """
    def __init__(self, parent_window, title, window_minsize, window_maxsize):
        super().__init__(parent_window, title=title, size=window_minsize, style=wx.CAPTION | wx.CLOSE_BOX | wx.RESIZE_BORDER | wx.FRAME_NO_TASKBAR | wx.FRAME_FLOAT_ON_PARENT)

        # 各種Sizerやボタンを用意、その他初期化
        self.__Initiate(parent_window, window_minsize, window_maxsize)

    def Destroy(self):
        # 親ウインドウを有効化してから閉じる
        self.__parent_window.Enable()
        super().Destroy()

    def _Window_Close_Event(self, event):
        """
        ウインドウを閉じる時の処理
        """
        # 何もせずに閉じる
        self.__parent_window.Enable()
        self.Destroy()

    def _Button_OK_Event(self, event):
        """
        OKボタンを押した時の処理

        継承クラスで実装されなければならない
        """
        pass

    def __Initiate(self, parent_window, window_minsize, window_maxsize):
        """
        ウインドウ中のウィジェット以外の要素を初期化する

        Args:
            parent_window (wx.Frame): 親ウインドウ
            parent_tab (RegularExpressionsWindow.RE_SubPage): 親タブ
            operation (pointer of function): AddItemやEditItemなどの行いたい操作
            position (int): 操作対象の項目の位置
            window_minsize (wx.Size): このウインドウの最小の大きさ
            window_maxsize (wx.Size): このウインドウの最大の大きさ
        """

        self.Bind(wx.EVT_CLOSE, self._Window_Close_Event)

        # 最小・最大サイズを設定
        self.SetMinSize(window_minsize)
        self.SetMaxSize(window_maxsize)

        # 親ウインドウと親タブ、対象の操作、対象の場所を保持
        self.__parent_window = parent_window
        # 他の操作がされないように親ウインドウを無効化
        self.__parent_window.Disable()

        # 背景用パネル
        self.__background = wx.Panel(self)

        # ウインドウ全体のSizer
        self.__sizer = wx.BoxSizer(wx.VERTICAL)
        self.__background.SetSizer(self.__sizer)
        self.__subsizer = wx.BoxSizer(wx.VERTICAL)  # 四隅の余白用のSizer
        self.__sizer.Add(self.__subsizer, proportion=1, flag=wx.EXPAND | wx.ALL, border=15)

        # チェックボックス用のSizer
        self.__chkbx_sizer = wx.BoxSizer(wx.VERTICAL)
        self.__subsizer.Add(self.__chkbx_sizer, flag=wx.EXPAND | wx.BOTTOM, border=10)

        # ラベルと入力フィールド用のSizer
        self.__lf_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.__subsizer.Add(self.__lf_sizer, proportion=1, flag=wx.EXPAND)

        # 入力フィールドのラベル用のSizer
        self.__label_sizer = wx.BoxSizer(wx.VERTICAL)
        self.__lf_sizer.Add(self.__label_sizer, flag=wx.EXPAND | wx.RIGHT, border=5)

        # 入力フィールド用のSizer
        self.__field_sizer = wx.BoxSizer(wx.VERTICAL)
        self.__lf_sizer.Add(self.__field_sizer, proportion=1, flag=wx.EXPAND)

        # 各種ボタン用のSizer
        self.__button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.__subsizer.Add(self.__button_sizer, flag=wx.ALIGN_RIGHT)

        # 各種ボタン
        self.__button_ok = wx.Button(self.__background, label="OK")
        self.__button_ok.Bind(wx.EVT_BUTTON, self._Button_OK_Event)
        self.__button_sizer.Add(self.__button_ok)
        self.__button_cancel = wx.Button(self.__background, label="キャンセル")
        self.__button_cancel.Bind(wx.EVT_BUTTON, self._Window_Close_Event)
        self.__button_sizer.Add(self.__button_cancel, flag=wx.LEFT, border=12)

    def _Add_CheckBox(self, label, checked):
        """
        ウインドウにチェックボックスを追加する

        Args:
            label (str): チェックボックスのラベル
            checked (bool): 最初からチェックされているか

        Returns:
            wx.CheckBox: 追加されたチェックボックス
        """
        chkbx = wx.CheckBox(self.__background, label=label)
        chkbx.SetValue(checked)
        self.__chkbx_sizer.Add(chkbx)

        return chkbx

    def _Add_FieldLabel(self, label):
        """
        ウインドウに入力フィールドのラベルを追加する

        Args:
            label (str): 入力フィールドのラベル
        """
        label = wx.StaticText(self.__background, label=label)
        self.__label_sizer.Add(label, proportion=1)

    def _Add_InputField(self, pre_filled_value=""):
        """
        ウインドウに入力フィールドを追加する

        Args:
            pre_filled_value (str, optional): 入力フィールドに初めから入力されている値

        Returns:
            wx.TextCtrl: 追加された入力フィールド
        """
        field_sizer = wx.BoxSizer(wx.VERTICAL)
        self.__field_sizer.Add(field_sizer, proportion=1, flag=wx.EXPAND)
        input_field = wx.TextCtrl(self.__background, value=pre_filled_value)
        field_sizer.Add(input_field, flag=wx.EXPAND)

        return input_field

    def _Add_NumberInputField(self, pre_filled_value=2):
        """
        ウインドウに入力フィールドを追加する

        Args:
            pre_filled_value (int, optional): 入力フィールドに初めから入力されている値

        Returns:
            wx.SpinCtrl: 追加された入力フィールド
        """
        field_sizer = wx.BoxSizer(wx.VERTICAL)
        self.__field_sizer.Add(field_sizer, proportion=1, flag=wx.EXPAND)
        input_field = wx.SpinCtrl(self.__background, min=1, max=6, initial=pre_filled_value)
        field_sizer.Add(input_field)

        return input_field


class InputItemInfoWindow_Ordinary(InputItemInfoWindow):
    """
    リストボックスの項目の情報を入力するウインドウ(汎用)
    """
    def __init__(self, parent_window, title, window_minsize, window_maxsize, parent_tab, operation, position, enabled=True, ignorecase=False, pattern="", example="", remarks=""):
        super().__init__(parent_window, title, window_minsize, window_maxsize)

        self.__parent_tab = parent_tab
        self.__operation = operation
        self.__position = position

        # チェックボックス
        self.__chkbx_enabled = self._Add_CheckBox("有効化", enabled)
        self.__chkbx_ignorecase = self._Add_CheckBox("大文字と小文字の違いを無視する", ignorecase)

        # 入力フィールドのラベル
        self._Add_FieldLabel("正規表現パターン :")
        self._Add_FieldLabel("マッチング例 :")
        self._Add_FieldLabel("備考 :")

        # 入力フィールド
        self.__field_pattern = self._Add_InputField(pattern)
        self.__field_example = self._Add_InputField(example)
        self.__field_remarks = self._Add_InputField(remarks)

        self.Show()

    def _Button_OK_Event(self, event):
        """
        OKボタンを押した時の処理
        """
        # 親タブに操作を追加してウインドウを閉じる
        enabled = self.__chkbx_enabled.GetValue()
        ignorecase = self.__chkbx_ignorecase.GetValue()
        pattern = self.__field_pattern.GetValue()
        example = self.__field_example.GetValue()
        remarks = self.__field_remarks.GetValue()

        self.__parent_tab.Add_Operation(self.__operation, [self.__position, enabled, ignorecase, pattern, example, remarks])

        self.Destroy()


class InputItemInfoWindow_Replace(InputItemInfoWindow):
    """
    リストボックスの項目の情報を入力するウインドウ(置換ページ用)
    """
    def __init__(self, parent_window, title, window_minsize, window_maxsize, parent_tab, operation, position, enabled=True, ignorecase=False, pattern="", target="", example="", remarks=""):
        super().__init__(parent_window, title, window_minsize, window_maxsize)

        self.__parent_tab = parent_tab
        self.__operation = operation
        self.__position = position

        # チェックボックス
        self.__chkbx_enabled = self._Add_CheckBox("有効化", enabled)
        self.__chkbx_ignorecase = self._Add_CheckBox("大文字と小文字の違いを無視する", ignorecase)

        # 入力フィールドのラベル
        self._Add_FieldLabel("正規表現パターン :")
        self._Add_FieldLabel("置換後の文字列 :")
        self._Add_FieldLabel("マッチング例 :")
        self._Add_FieldLabel("備考 :")

        # 入力フィールド
        self.__field_pattern = self._Add_InputField(pattern)
        self.__field_target = self._Add_InputField(target)
        self.__field_example = self._Add_InputField(example)
        self.__field_remarks = self._Add_InputField(remarks)

        self.Show()

    def _Button_OK_Event(self, event):
        """
        OKボタンを押した時の処理
        """
        # 親タブに操作を追加してウインドウを閉じる
        enabled = self.__chkbx_enabled.GetValue()
        ignorecase = self.__chkbx_ignorecase.GetValue()
        pattern = self.__field_pattern.GetValue()
        target = self.__field_target.GetValue()
        example = self.__field_example.GetValue()
        remarks = self.__field_remarks.GetValue()

        self.__parent_tab.Add_Operation(self.__operation, [self.__position, enabled, ignorecase, pattern, target, example, remarks])

        self.Destroy()


class InputItemInfoWindow_Header(InputItemInfoWindow):
    """
    リストボックスの項目の情報を入力するウインドウ(置換ページ用)
    """
    def __init__(self, parent_window, title, window_minsize, window_maxsize, parent_tab, operation, position, enabled=True, ignorecase=False, pattern="", depth_count="", target_remove="", max_size=2, example="", remarks=""):
        super().__init__(parent_window, title, window_minsize, window_maxsize)

        self.__parent_tab = parent_tab
        self.__operation = operation
        self.__position = position

        # チェックボックス
        self.__chkbx_enabled = self._Add_CheckBox("有効化", enabled)
        self.__chkbx_ignorecase = self._Add_CheckBox("大文字と小文字の違いを無視する", ignorecase)

        # 入力フィールドのラベル
        self._Add_FieldLabel("正規表現パターン :")
        self._Add_FieldLabel("見出しの深さ判定 :")
        self._Add_FieldLabel("訳文から除く文字列 :")
        self._Add_FieldLabel("見出しの最大サイズ :")
        self._Add_FieldLabel("マッチング例 :")
        self._Add_FieldLabel("備考 :")

        # 入力フィールド
        self.__field_pattern = self._Add_InputField(pattern)
        self.__field_depth_count = self._Add_InputField(depth_count)
        self.__field_target_remove = self._Add_InputField(target_remove)
        self.__field_max_size = self._Add_NumberInputField(max_size)
        self.__field_example = self._Add_InputField(example)
        self.__field_remarks = self._Add_InputField(remarks)

        self.Show()

    def _Button_OK_Event(self, event):
        """
        OKボタンを押した時の処理
        """
        # 親タブに操作を追加してウインドウを閉じる
        enabled = self.__chkbx_enabled.GetValue()
        ignorecase = self.__chkbx_ignorecase.GetValue()
        pattern = self.__field_pattern.GetValue()
        depth_count = self.__field_depth_count.GetValue()
        target_remove = self.__field_target_remove.GetValue()
        max_size = self.__field_max_size.GetValue()
        example = self.__field_example.GetValue()
        remarks = self.__field_remarks.GetValue()

        self.__parent_tab.Add_Operation(self.__operation, [self.__position, enabled, ignorecase, pattern, depth_count, target_remove, max_size, example, remarks])

        self.Destroy()


class RegularExpressionsWindow(wx.Frame):
    def __init__(self, parent):
        super().__init__(
            parent,
            title="正規表現の編集",
            size=(960, 540)
        )
        self.__parent = parent  # 親の保持

        self.Bind(wx.EVT_CLOSE, self.__Window_Close_Event)

        # メニューバーを設定
        self.__menu_bar = wx.MenuBar()
        self.__setting_menu = RegularExpressionsWindow.SettingMenu()
        self.__menu_bar.Append(self.__setting_menu, "設定")
        self.Bind(wx.EVT_MENU, self.__Menu_Event)
        self.SetMenuBar(self.__menu_bar)

        # 背景パネル
        self.__background = wx.Panel(self)

        # ウインドウ全体のSizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.__background.SetSizer(sizer)

        # タブによるページを構成するためのコンポーネント
        self.__pages_sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.__pages_sizer, proportion=1, flag=wx.EXPAND)
        # タブを用意
        self.__Prepare_SubPage(Settings.RegularExpressions().show_markdown_settings)

        # OK・適用・キャンセルボタン
        buttonsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.__ok_button = wx.Button(self.__background, label="OK")
        self.__ok_button.Bind(wx.EVT_BUTTON, self.__Button_OK_Event)
        self.__ok_button.Disable()
        buttonsizer.Add(self.__ok_button)
        self.__apply_button = wx.Button(self.__background, label="適用")
        self.__apply_button.Bind(wx.EVT_BUTTON, self.__Button_Apply_Event)
        self.__apply_button.Disable()
        buttonsizer.Add(self.__apply_button, flag=wx.LEFT, border=12)
        self.__cancel_button = wx.Button(self.__background, label="キャンセル")
        self.__cancel_button.Bind(wx.EVT_BUTTON, self.__Button_Cancel_Event)
        buttonsizer.Add(self.__cancel_button, flag=wx.LEFT, border=12)
        sizer.Add(buttonsizer, flag=wx.ALIGN_RIGHT | wx.TOP | wx.RIGHT | wx.BOTTOM, border=5)

        self.Show()

    def Destroy(self):
        """
        ウインドウが閉じられたということをメインウインドウに知らせてから閉じる
        """
        self.__parent.res_window_destroyed = True
        super().Destroy()

    def __Window_Close_Event(self, event):
        """
        ウインドウを閉じる時の処理
        """
        if not self.__TabIsEdited():
            # タブが一つも編集されていなければそのまま閉じる
            self.Destroy()

        else:
            # 編集されていれば、そのまま閉じるかどうか聞く
            dialog = wx.MessageDialog(self, "変更内容を保存しますか？", "正規表現の編集", wx.CENTRE | wx.YES_NO | wx.CANCEL)
            dialog.SetYesNoCancelLabels("保存する", "保存しない", "キャンセル")     # ボタンラベルの変更

            choice = dialog.ShowModal()     # 選択を取得
            if choice == wx.ID_YES:
                # 保存して閉じる(OKボタンと同等の処理)
                self.__Button_OK_Event(None)
            elif choice == wx.ID_NO:
                # 何もせずに閉じる
                self.Destroy()
            # それ以外の場合(キャンセルボタンを押した場合)は何もしないしウインドウも閉じない

    def __ApplyAndSaveSettings(self):
        """
        各タブにおける設定を反映する
        """
        for t in self.__tabs:
            t.ApplySettings()

        Settings.SaveSettings()

    def __Button_OK_Event(self, event):
        """
        OKボタンを押した時の処理
        """
        self.__ApplyAndSaveSettings()
        self.Destroy()

    def __Button_Apply_Event(self, event):
        """
        Applyボタンを押した時の処理
        """
        # 設定に編集を保存
        self.__ApplyAndSaveSettings()
        # OK,Applyボタンを無効に
        self.SwitchButtonsState()

    def __Button_Cancel_Event(self, event):
        """
        キャンセルボタンを押した時の処理
        """
        self.Destroy()

    def __TabIsEdited(self):
        """
        どれか一つでもタブが編集されたかを返す

        Returns:
            bool: どれか一つでもタブが編集されたか
        """
        edited = False
        for t in self.__tabs:
            edited |= t.IsEdited()

        return edited

    def SwitchButtonsState(self):
        """
        どれか一つでもタブが編集されているならOK・Applyボタンを有効にし、編集されていないなら無効にする
        """
        if self.__TabIsEdited():
            self.__ok_button.Enable()
            self.__apply_button.Enable()
        else:
            self.__ok_button.Disable()
            self.__apply_button.Disable()

    def __Prepare_SubPage(self, show_markdown_settings):
        """
        タブページを用意する

        Args:
            show_markdown_settings (bool): Markdownに関わるタブページを表示するか
        """
        self.__pages = wx.Notebook(self.__background)
        self.__pages_sizer.Add(self.__pages, proportion=1, flag=wx.EXPAND)

        # 条件によっては追加されないページもある
        self.__tabs = []
        self.__tabs.append(RegularExpressionsWindow.StartLinesPage(self, self.__pages))
        self.__tabs.append(RegularExpressionsWindow.EndLinesPage(self, self.__pages))
        self.__tabs.append(RegularExpressionsWindow.IgnoreLinesPage(self, self.__pages))
        self.__tabs.append(RegularExpressionsWindow.StandardReplaceLinesPage(self, self.__pages))
        if show_markdown_settings:
            self.__tabs.append(RegularExpressionsWindow.MarkdownReplaceLinesPage(self, self.__pages))
        self.__tabs.append(RegularExpressionsWindow.ChartStartLinesPage(self, self.__pages))
        self.__tabs.append(RegularExpressionsWindow.PossibilityReturnLinesPage(self, self.__pages))
        self.__tabs.append(RegularExpressionsWindow.IgnoreReturnLinesPage(self, self.__pages))
        if show_markdown_settings:
            self.__tabs.append(RegularExpressionsWindow.HeaderLinesPage(self, self.__pages))

        tabs = copy(self.__tabs)
        tab_number = [i for i in range(1, len(tabs) + 1)]

        # タブを追加
        self.__pages.InsertPage(0, RegularExpressionsWindow.IntroductionPage(self.__pages), "概要説明")
        self.__pages.InsertPage(tab_number.pop(0), tabs.pop(0), "抽出開始条件")
        self.__pages.InsertPage(tab_number.pop(0), tabs.pop(0), "抽出終了条件")
        self.__pages.InsertPage(tab_number.pop(0), tabs.pop(0), "無視条件")
        self.__pages.InsertPage(tab_number.pop(0), tabs.pop(0), "置換条件")
        if show_markdown_settings:
            self.__pages.InsertPage(tab_number.pop(0), tabs.pop(0), "置換条件(Markdown)")
        self.__pages.InsertPage(tab_number.pop(0), tabs.pop(0), "図表開始条件")
        self.__pages.InsertPage(tab_number.pop(0), tabs.pop(0), "改行条件")
        self.__pages.InsertPage(tab_number.pop(0), tabs.pop(0), "改行無視条件")
        if show_markdown_settings:
            self.__pages.InsertPage(tab_number.pop(0), tabs.pop(0), "見出し条件")

    def __Refresh_SubPage(self, show_markdown_settings):
        """
        タブページの表示を更新する
        """
        # タブページをSizerから除く(破棄はしない)
        self.__pages_sizer.Detach(0)

        # 古いタブページをギリギリまで保持しておくことで画面のチラつきを抑える
        temp = self.__pages        # 古いタブページを退避
        self.__Prepare_SubPage(Settings.RegularExpressions().show_markdown_settings)     # 新しいタブページを用意
        self.__pages_sizer.Layout()  # 新しいタブページを配置
        temp.Destroy()              # 古いタブページを破棄

    def __Menu_Event(self, event):
        """
        選ばれたメニューに応じて処理を行う
        """
        selected_menu = event.GetId()
        if selected_menu == RegularExpressionsWindow_MenuBar_Menu.SHOW_MARKDOWN_SETTINGS.value:     # Markdown用の設定を表示する
            Settings.RegularExpressions().show_markdown_settings = self.__setting_menu.menu_chkbx_show_markdown_settings.IsChecked()    # 設定に反映
            self.__Refresh_SubPage(Settings.RegularExpressions().show_markdown_settings)

    class SettingMenu(wx.Menu):
        """
        メニューバーの「設定」
        """
        def __init__(self):
            super().__init__()
            self.menu_chkbx_show_markdown_settings = self.AppendCheckItem(RegularExpressionsWindow_MenuBar_Menu.SHOW_MARKDOWN_SETTINGS.value, "Markdown用の設定を表示する")
            self.menu_chkbx_show_markdown_settings.Check(Settings.RegularExpressions().show_markdown_settings)  # 最初からチェックされているか

    class IntroductionPage(wx.Panel):
        """
        概要説明のページ
        """
        def __init__(self, parent):
            super().__init__(parent)
            # ウインドウ全体のSizer
            sizer = wx.BoxSizer(wx.VERTICAL)
            self.SetSizer(sizer)

            # スクロールするパネルの設定
            self.__scroll_panel = ScrolledPanel(self)
            self.__scroll_panel.SetupScrolling()
            panel_sizer = wx.BoxSizer(wx.VERTICAL)     # スクロールするパネル内部のSizer
            self.__scroll_panel.SetSizer(panel_sizer)
            sizer.Add(self.__scroll_panel, proportion=1, flag=wx.EXPAND)

            # 説明用テキスト
            page_sizer = wx.BoxSizer(wx.VERTICAL)
            self.__text = wx.StaticText(self.__scroll_panel, id=wx.ID_ANY, label=res_introduction)
            page_sizer.Add(self.__text, flag=wx.ALIGN_LEFT)

            # ページの上下左右に余白を設ける
            panel_sizer.Add(page_sizer, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)

    class RE_SubPage(wx.Panel):
        """
        タブの基本設計
        """
        def __init__(self, window, parent, Settings, column_labels=res_default_column_labels, column_tips=res_default_column_tips, column_widths=res_default_column_widths):
            self._window = window
            super().__init__(parent)
            # 該当箇所の設定
            self._Settings = Settings
            # 設定から値をコピー
            self._Initiate_SettingLists()

            # 操作関数のリストとその引数のリスト
            self._operation_list = []
            self._operation_args = []
            # 「現在、履歴のどの位置を表示しているか」を示すマーカー(Undo, Redoで利用)
            self._history_marker = 0
            # Applyされたときのマーカーの位置
            self._applied_marker = 0

            self._sizer = wx.BoxSizer(wx.VERTICAL)

            # 全体の有効化のチェックボックス
            self._chkbx_enabled_overall = wx.CheckBox(self, wx.ID_ANY, "この項目を有効にする")
            self._chkbx_enabled_overall.SetValue(self._enabled_overall_edited)
            self._chkbx_enabled_overall.Bind(wx.EVT_CHECKBOX, self._CheckBox_EnabledOverall_Event)
            self._sizer.Add(self._chkbx_enabled_overall, flag=wx.ALIGN_LEFT | wx.TOP | wx.LEFT, border=5)
            # ヒット行出力のチェックボックス
            self._chkbx_output_hit_lines = wx.CheckBox(self, wx.ID_ANY, "この条件に適合した行をテキストファイルに出力する")
            self._chkbx_output_hit_lines.SetValue(self._output_hit_lines_edited)
            self._chkbx_output_hit_lines.Bind(wx.EVT_CHECKBOX, self._CheckBox_OutputHitLines_Event)
            self._sizer.Add(self._chkbx_output_hit_lines, flag=wx.ALIGN_LEFT | wx.LEFT, border=5)

            # リストボックスのヘッダに関する情報を保存
            self.__column_labels = column_labels
            self.__column_tips = column_tips
            self.__column_widths = column_widths

            # リストボックスと各種メニュー
            self._lb_sizer = wx.BoxSizer(wx.HORIZONTAL)
            self._lb_boxsizer = wx.BoxSizer(wx.VERTICAL)
            # チェックボックス付きのリストボックス
            self._Prepare_ListBox(self.__column_labels, self.__column_tips, self.__column_widths)
            self._lb_sizer.Add(self._lb_boxsizer, proportion=1, flag=wx.EXPAND | wx.RIGHT, border=3)
            # 各種メニュー
            splitter_label = "----------"
            splitter_color = wx.Colour(200, 200, 200)
            self._lb_menusizer = wx.BoxSizer(wx.VERTICAL)
            self._add_button = wx.Button(self, label="追加")    # 追加ボタン
            self._add_button.Bind(wx.EVT_BUTTON, self._Button_Add_Event)
            self._lb_menusizer.Add(self._add_button)
            self._edit_button = wx.Button(self, label="編集")   # 編集ボタン
            self._edit_button.Bind(wx.EVT_BUTTON, self._Button_Edit_Event)
            self._edit_button.Disable()
            self._lb_menusizer.Add(self._edit_button, flag=wx.TOP, border=3)
            self._delete_button = wx.Button(self, label="削除")
            self._delete_button.Bind(wx.EVT_BUTTON, self._Button_Delete_Event)
            self._delete_button.Disable()
            self._lb_menusizer.Add(self._delete_button, flag=wx.TOP, border=10)
            splitter1 = wx.StaticText(self, label=splitter_label)
            splitter1.SetForegroundColour(splitter_color)
            self._lb_menusizer.Add(splitter1, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=5)
            self._top_button = wx.Button(self, label="最上位へ")    # 移動ボタン類
            self._top_button.Bind(wx.EVT_BUTTON, self._Button_Top_Event)
            self._top_button.Disable()
            self._lb_menusizer.Add(self._top_button)
            self._up_button = wx.Button(self, label="一つ上へ")
            self._up_button.Bind(wx.EVT_BUTTON, self._Button_Up_Event)
            self._up_button.Disable()
            self._lb_menusizer.Add(self._up_button, flag=wx.TOP, border=10)
            self._down_button = wx.Button(self, label="一つ下へ")
            self._down_button.Bind(wx.EVT_BUTTON, self._Button_Down_Event)
            self._down_button.Disable()
            self._lb_menusizer.Add(self._down_button, flag=wx.TOP, border=3)
            self._bottom_button = wx.Button(self, label="最下位へ")
            self._bottom_button.Bind(wx.EVT_BUTTON, self._Button_Bottom_Event)
            self._bottom_button.Disable()
            self._lb_menusizer.Add(self._bottom_button, flag=wx.TOP, border=10)
            splitter2 = wx.StaticText(self, label=splitter_label)
            splitter2.SetForegroundColour(splitter_color)
            self._lb_menusizer.Add(splitter2, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=5)
            self._undo_button = wx.Button(self, label="Undo")   # 一つ戻る
            self._undo_button.Bind(wx.EVT_BUTTON, self._Button_Undo_Event)
            self._undo_button.Disable()     # 最初は無効化
            self._lb_menusizer.Add(self._undo_button)
            self._redo_button = wx.Button(self, label="Redo")   # 一つ進む
            self._redo_button.Bind(wx.EVT_BUTTON, self._Button_Redo_Event)
            self._redo_button.Disable()     # 最初は無効化
            self._lb_menusizer.Add(self._redo_button, flag=wx.TOP, border=3)
            self._lb_sizer.Add(self._lb_menusizer, flag=wx.ALIGN_TOP)
            self._sizer.Add(self._lb_sizer, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)

            self.SetSizer(self._sizer)
            self.Refresh()

        def _ListBox_ItemSelected_Event(self, event):
            """
            リストボックスの項目が選択された時の処理
            """
            # 各種ボタンをアクティベート
            self._edit_button.Enable()
            self._delete_button.Enable()
            self._top_button.Enable()
            self._up_button.Enable()
            self._down_button.Enable()
            self._bottom_button.Enable()

        def _ListBox_ItemDeselected_Event(self, event):
            """
            リストボックスの項目の選択が解除された時の処理
            """
            self._edit_button.Disable()
            self._delete_button.Disable()
            self._top_button.Disable()
            self._up_button.Disable()
            self._down_button.Disable()
            self._bottom_button.Disable()

        def _CheckBox_EnabledOverall_Event(self, event):
            """
            全体の有効化のチェックボックスを押した時の処理
            """
            # チェックボックスから値を取得し、一時設定に反映
            enabled_overall = self._chkbx_enabled_overall.GetValue()
            self._enabled_overall_edited = enabled_overall

            # 履歴に操作を追加
            self.Add_Operation(self._Set_EnabledOverall, enabled_overall)

        def _CheckBox_OutputHitLines_Event(self, event):
            """
            全体の有効化のチェックボックスを押した時の処理
            """
            # チェックボックスから値を取得し、一時設定に反映
            output_hit_lines = self._chkbx_output_hit_lines.GetValue()
            self._output_hit_lines_edited = output_hit_lines

            # 履歴に操作を追加
            self.Add_Operation(self._Set_OutputHitLines, output_hit_lines)

        def _CheckBox_Enable_Event(self, event):
            """
            リスト項目の有効化のチェックボックスを押した時の処理
            """
            # IDが行番号と一致しているので取得し、対応する値を一時設定に反映
            id = event.GetId()
            enabled = self._chkbx_enable_list[id].GetValue()
            self._enabled_list_edited[id] = enabled

            # 履歴に操作を追加
            self.Add_Operation(self._ListBox_SwitchEnabled, [id, enabled])

        def _CheckBox_IgnoreCase_Event(self, event):
            """
            リスト項目の大文字小文字無視の有効化のチェックボックスを押した時の処理
            """
            # IDが行番号と一致しているので取得し、対応する値を一時設定に反映
            id = event.GetId()
            enabled = self._chkbx_ignorecase_list[id].GetValue()
            self._ignorecase_list_edited[id] = enabled

            # 履歴に操作を追加
            self.Add_Operation(self._ListBox_SwitchIgnoreCase, [id, enabled])

        def _Button_Add_Event(self, event):
            """
            追加ボタンを押した時の処理
            """
            # 選択された項目のインデックスを取得 何も選択されていないなら負の値になり、末尾に追加される
            index = self._ListBox_SelectedItemIndex()

            # 入力ウインドウを出す
            # 入力ウインドウが出ても正規表現ウインドウの処理は続くため操作が可能(つまり追加ボタンを押しまくれば入力ウインドウが出しまくれる)だが、
            # 入力ウインドウ側で正規表現ウインドウを無効化することで、入力中に正規表現ウインドウ側で好き勝手することを禁止する
            InputItemInfoWindow_Ordinary(self._window, "項目の追加", wx.Size(500, 250), wx.Size(1000, 250), self, self._ListBox_AddItem, index)

        def _Button_Edit_Event(self, event):
            """
            編集ボタンを押した時の処理
            """
            # 選択された項目のインデックスを取得
            index = self._ListBox_SelectedItemIndex()

            # 何かが選択されているなら編集を実行
            if index >= 0:
                InputItemInfoWindow_Ordinary(
                    self._window,
                    "項目の編集",
                    wx.Size(500, 250),
                    wx.Size(1000, 250),
                    self,
                    self._ListBox_EditItem,
                    index,
                    self._enabled_list_edited[index],
                    self._ignorecase_list_edited[index],
                    self._pattern_list_edited[index],
                    self._example_list_edited[index],
                    self._remarks_list_edited[index])

        def _Button_Delete_Event(self, event):
            """
            削除ボタンを押した時の処理
            """
            # 選択された項目のインデックスを取得
            index = self._ListBox_SelectedItemIndex()

            # 何かが選択されているなら削除を実行
            if index >= 0:
                self.Add_Operation(self._ListBox_RemoveItem, index)

        def _Button_Top_Event(self, event):
            """
            「最上位へ」のボタンを押した時の処理
            """
            # 選択された項目のインデックスを取得
            index = self._ListBox_SelectedItemIndex()

            # 何かが選択されているなら移動
            if index >= 0:
                self.Add_Operation(self._ListBox_MoveItem, [index, 0])

        def _Button_Up_Event(self, event):
            """
            「一つ上へ」のボタンを押した時の処理
            """
            # 選択された項目のインデックスを取得
            index = self._ListBox_SelectedItemIndex()

            # 何かが選択されているなら移動
            if index >= 0:
                self.Add_Operation(self._ListBox_MoveItem, [index, max(index - 1, 0)])

        def _Button_Down_Event(self, event):
            """
            「一つ下へ」のボタンを押した時の処理
            """
            # 選択された項目のインデックスを取得
            index = self._ListBox_SelectedItemIndex()

            # 何かが選択されているなら移動
            if index >= 0:
                self.Add_Operation(self._ListBox_MoveItem, [index, min(index + 1, len(self._enabled_list_edited) - 1)])

        def _Button_Bottom_Event(self, event):
            """
            「最下位へ」のボタンを押した時の処理
            """
            # 選択された項目のインデックスを取得
            index = self._ListBox_SelectedItemIndex()

            # 何かが選択されているなら移動
            if index >= 0:
                self.Add_Operation(self._ListBox_MoveItem, [index, len(self._enabled_list_edited) - 1])

        def _Button_Undo_Event(self, event):
            """
            Undo(一つ戻る)ボタンを押した時の処理
            """
            # マーカーを一つ戻してリストボックスを更新
            if self._history_marker > 0:
                self._history_marker -= 1
            self._Apply_Operations()

            # 何も選択されていないなら各種操作メニューを無効化
            index = self._ListBox_SelectedItemIndex()
            if index < 0:
                self._ListBox_ItemDeselected_Event(None)

            # 親ウインドウのOK,Applyボタンの有効/無効を切り替える
            self._window.SwitchButtonsState()
            # 自身のボタンの有効/無効も切り替える
            self._Switch_UndoRedoButtonsState()

        def _Button_Redo_Event(self, event):
            """
            Redo(一つ進む)ボタンを押した時の処理
            """
            # マーカーを一つ進めてリストボックスを更新
            if self._history_marker < len(self._operation_list):
                self._history_marker += 1
            self._Apply_Operations()

            # 何も選択されていないなら各種操作メニューを無効化
            index = self._ListBox_SelectedItemIndex()
            if index < 0:
                self._ListBox_ItemDeselected_Event(None)

            # 親ウインドウのOK,Applyボタンの有効/無効を切り替える
            self._window.SwitchButtonsState()
            # 自身のボタンの有効/無効も切り替える
            self._Switch_UndoRedoButtonsState()

        def _Switch_UndoRedoButtonsState(self):
            """
            状態に応じてUndo, Redoボタンの有効/無効を切り替える
            """
            # これ以上遡る履歴がないならUndoボタンを無効にし、そうでないなら有効にする
            if self._history_marker == 0:
                self._undo_button.Disable()
            else:
                self._undo_button.Enable()
            # 最新の履歴に到達しているならRedoボタンを無効にし、そうでないなら有効にする
            if self._history_marker == len(self._operation_list):
                self._redo_button.Disable()
            else:
                self._redo_button.Enable()

        def _Prepare_ListBox(self, column_labels, column_tips, column_widths):
            """
            リストボックスを用意する
            """
            # ULC.ULC_HAS_VARIABLE_ROW_HEIGHT と ULC.ULC_REPORT を兼ね備えていないとチェックボックスなどのウィジェットを追加できない
            self._listbox = ULC.UltimateListCtrl(self, agwStyle=ULC.ULC_HAS_VARIABLE_ROW_HEIGHT | ULC.ULC_REPORT | ULC.ULC_VRULES | ULC.ULC_SINGLE_SEL)
            self._ListBox_PrepareColumns(column_labels, column_tips, column_widths)  # 列を追加
            self._chkbx_enable_list = []        # 有効化のチェックボックスのリスト
            self._chkbx_ignorecase_list = []    # 大文字小文字無視のチェックボックスのリスト
            self._ListBox_PrepareItems()    # 項目を追加
            self._listbox.Bind(wx.EVT_LIST_ITEM_SELECTED, self._ListBox_ItemSelected_Event)     # 項目選択時の処理をバインド
            self._listbox.Bind(wx.EVT_LIST_ITEM_DESELECTED, self._ListBox_ItemDeselected_Event)     # 項目選択解除時の処理をバインド
            self._lb_boxsizer.Add(self._listbox, proportion=1, flag=wx.EXPAND)

        def _Refresh_ListBox(self):
            """
            リストボックスの表示を更新する
            """
            # リストボックスをSizerから除く(破棄はしない)
            self._lb_boxsizer.Detach(0)

            # 古いリストボックスをギリギリまで保持しておくことで画面のチラつきを抑える
            temp = self._listbox        # 古いリストボックスを退避
            self._Prepare_ListBox(self.__column_labels, self.__column_tips, self.__column_widths)   # 新しいリストボックスを用意
            self._lb_boxsizer.Layout()  # 新しいリストボックスを配置
            temp.Destroy()              # 古いリストボックスを破棄

        def _ListBox_PrepareColumns(self, column_labels, column_tips, column_widths):
            """
            リストボックスに列を一通り追加する
            """
            # maskやformat、kindについて、詳しくは以下を参照
            # [wx.lib.agw.ultimatelistctrl.UltimateListItem — wxPython Phoenix 4.1.2a1 documentation]
            # (https://wxpython.org/Phoenix/docs/html/wx.lib.agw.ultimatelistctrl.UltimateListItem.html)
            # 簡単に言えば、
            # mask: textやformatなどの機能のうち、どれが有効か。ULC_MASK_TEXTが有効でなければ、テキストを設定しても表示されない
            # format: コンテンツの表示位置。左寄せか中央寄せか、など
            # kind: 0=ただの項目, 1=チェックボックス持ち, 2=ラジオボタン持ち

            # ヘッダなのでテキストと寄せ位置だけ有効
            mask = ULC.ULC_MASK_TEXT | ULC.ULC_MASK_FORMAT | ULC.ULC_MASK_TOOLTIP

            # 何回も同じことをするのでここでだけ使う関数を設定
            def gen_column_header(name, tooltip="", kind=0, mask=mask):
                info = ULC.UltimateListItem()
                info._text = name
                info._tooltip = tooltip
                info._kind = kind
                info._mask = mask
                info._format = ULC.ULC_FORMAT_LEFT
                return info

            for i in range(len(column_labels)):
                self._listbox.InsertColumnInfo(i, gen_column_header(column_labels[i], column_tips[i]))
                self._listbox.SetColumnWidth(i, column_widths[i])   # 幅を設定

        def _ListBox_PrepareItems(self):
            """
            リストボックスに既存の項目を並べる
            """
            for i in range(len(self._enabled_list_edited)):
                # 一行ごとに色を互い違いにする
                if i % 2:
                    color = wx.Colour(230, 230, 230)    # 濃い灰色
                else:
                    color = wx.Colour(250, 250, 250)    # 淡い灰色

                # 行の挿入と色の設定
                self._listbox.InsertStringItem(i, "")
                self._listbox.SetItemBackgroundColour(i, color)

                # チェックボックスの用意
                chkbx_enable = wx.CheckBox(self._listbox, id=i)
                chkbx_enable.Bind(wx.EVT_CHECKBOX, self._CheckBox_Enable_Event)
                chkbx_ignorecase = wx.CheckBox(self._listbox, id=i)
                chkbx_ignorecase.Bind(wx.EVT_CHECKBOX, self._CheckBox_IgnoreCase_Event)
                chkbx_enable.SetValue(self._enabled_list_edited[i])   # 設定に基づいて初期値を設定
                chkbx_ignorecase.SetValue(self._ignorecase_list_edited[i])
                chkbx_enable.SetBackgroundColour(color)
                chkbx_ignorecase.SetBackgroundColour(color)
                self._chkbx_enable_list.append(chkbx_enable)    # 後から追跡できるようにリストにセット
                self._chkbx_ignorecase_list.append(chkbx_ignorecase)

                # 行の各列へのアイテムの追加
                # どうやらヘッダとセルのアラインメントを別々で設定することはできないらしい……
                # と思っていたが、それ以外の操作もできている様子がないので、
                # できることはできるがなにか面倒な儀式を踏まないとできなさそうな予感
                self._listbox.SetItemWindow(i, 0, chkbx_enable)
                self._listbox.SetItemWindow(i, 1, chkbx_ignorecase)
                self._listbox.SetStringItem(i, 2, self._pattern_list_edited[i])
                self._listbox.SetStringItem(i, 3, self._example_list_edited[i])
                self._listbox.SetStringItem(i, 4, self._remarks_list_edited[i])

        def _Initiate_SettingLists(self):
            """
            一時設定を、編集ウインドウを開いた当初のものに戻す
            """
            # 設定から値をコピーしていない場合、初期値としてコピーする
            # コピーしてからの値の変更で設定ごと変えられないように、deepcopyでコピー
            if not hasattr(self, "_enabled_overall_initial"):
                self._enabled_overall_initial = self._Settings.enabled_overall
                self._output_hit_lines_initial = self._Settings.output_hit_lines
                self._enabled_list_initial = deepcopy(self._Settings.enabled_list)
                self._ignorecase_list_initial = deepcopy(self._Settings.ignorecase_list)
                self._pattern_list_initial = deepcopy(self._Settings.pattern_list)
                self._example_list_initial = deepcopy(self._Settings.example_list)
                self._remarks_list_initial = deepcopy(self._Settings.remarks_list)
            # 初期設定を反映
            self._enabled_overall_edited = self._enabled_overall_initial
            self._output_hit_lines_edited = self._output_hit_lines_initial
            self._enabled_list_edited = deepcopy(self._enabled_list_initial)
            self._ignorecase_list_edited = deepcopy(self._ignorecase_list_initial)
            self._pattern_list_edited = deepcopy(self._pattern_list_initial)
            self._example_list_edited = deepcopy(self._example_list_initial)
            self._remarks_list_edited = deepcopy(self._remarks_list_initial)

        def ApplySettings(self):
            """
            設定に値の変更を適用する
            """
            # コピーしてからの値の変更で設定ごと変えられないように、deepcopyでコピー
            self._Settings.enabled_overall = self._enabled_overall_edited
            self._Settings.output_hit_lines = self._output_hit_lines_edited
            self._Settings.enabled_list = deepcopy(self._enabled_list_edited)
            self._Settings.ignorecase_list = deepcopy(self._ignorecase_list_edited)
            self._Settings.pattern_list = deepcopy(self._pattern_list_edited)
            self._Settings.example_list = deepcopy(self._example_list_edited)
            self._Settings.remarks_list = deepcopy(self._remarks_list_edited)

            # どのマーカーの位置で保存されたかを記録
            self._applied_marker = self._history_marker

        def IsEdited(self):
            """
            編集された状態かどうかを返す

            Returns:
                bool: 編集された状態かどうか
            """
            return self._history_marker != self._applied_marker

        def Add_Operation(self, func, argument):
            """
            操作履歴に操作を追加する

            Args:
                func (pointer of function): 操作を行うメソッド
                argument: メソッドに入れる引数
            """
            # 履歴をさかのぼっていた場合
            if self._history_marker < len(self._operation_list):
                # それ以後の操作を破棄する
                self._operation_list = self._operation_list[:self._history_marker]
                self._operation_args = self._operation_args[:self._history_marker]
                # 保存マーカー位置が0より大きく(過去にApply済みで)、
                # マーカー位置が保存マーカー位置より前の場合、
                # この操作によって、Undo,Redoでは元の設定には戻らなくなったので、
                # 保存マーカー位置を絶対に到達できない位置にして、
                # 必ずIsEditedでTrueが返ってくるようにする
                if self._history_marker < self._applied_marker:
                    self._applied_marker = -1

            # 操作を追加し、マーカーを一つ進める
            self._operation_list.append(func)
            self._operation_args.append(argument)
            self._history_marker += 1

            # 親ウインドウのOK,Applyボタンの有効/無効を切り替える
            self._window.SwitchButtonsState()
            # Undo, Redoボタンの有効/無効も切り替える
            self._Switch_UndoRedoButtonsState()

            # 操作を適用して画面を更新
            self._Apply_Operations()

        def _Apply_Operations(self):
            """
            今までに行われた(登録された)操作を実行し、その結果をウインドウに表示する
            """
            # 初期状態として設定をコピー
            self._Initiate_SettingLists()

            # ウィジェット類を初期値に合わせる
            self._chkbx_enabled_overall.SetValue(self._enabled_overall_edited)     # 全体の有効化

            # 登録された操作を順次実行(Undoで履歴をさかのぼっていたらその位置まで)
            for i in range(self._history_marker):
                handler(self._operation_list[i], self._operation_args[i])

            # 画面の更新
            self._Refresh_ListBox()

            def stay_within_range(index):
                """
                入力indexの値をリストボックスの項目の範囲内に収める

                Args:
                    index (int): 対象の値

                Returns:
                    int: リストボックスの項目の範囲内に収められたindex
                """
                index = max(0, index)
                index = min(index, len(self._enabled_list_edited) - 1)
                return index

            # 最後の操作ごとの特別な処理
            if self._history_marker > 0:
                history_index = self._history_marker - 1
                # 最後の操作が追加か編集なら、編集した項目を選択し直す
                if self._operation_list[history_index] == self._ListBox_AddItem or self._operation_list[history_index] == self._ListBox_EditItem:
                    self._listbox.Select(stay_within_range(self._operation_args[history_index][0]))
                # 最後の操作が削除なら、削除した位置に来た項目を選択し直す
                elif self._operation_list[history_index] == self._ListBox_RemoveItem:
                    self._listbox.Select(stay_within_range(self._operation_args[history_index]))
                elif self._operation_list[history_index] == self._ListBox_MoveItem:
                    self._listbox.Select(stay_within_range(self._operation_args[history_index][1]))

        def _Set_EnabledOverall(self, state):
            """
            全体の有効/無効を切り替える

            Args:
                state (bool): 有効/無効
            """
            self._enabled_overall_edited = state
            self._chkbx_enabled_overall.SetValue(state)

        def _Set_OutputHitLines(self, state):
            """
            条件に適合した行の出力の有効/無効を切り替える

            Args:
                state (bool): 有効/無効
            """
            self._output_hit_lines_edited = state
            self._chkbx_output_hit_lines.SetValue(state)

        def _ListBox_SwitchEnabled(self, arguments):
            """リストボックスの要素(一つ)の有効/無効を切り替える

            Args:
                arguments: 引数のリスト(0: 要素が何行目にあるか(int), 1: 有効にするか無効にするか(bool))
            """
            # 引数リストから個々の値を取得
            index = arguments[0]
            enabled = arguments[1]
            # 一時設定とチェックボックスに反映
            self._enabled_list_edited[index] = enabled
            self._chkbx_enable_list[index].SetValue(enabled)

        def _ListBox_SwitchIgnoreCase(self, arguments):
            """リストボックスの要素(一つ)の大文字小文字無視の有効/無効を切り替える

            Args:
                arguments: 引数のリスト(0: 要素が何行目にあるか(int), 1: 有効にするか無効にするか(bool))
            """
            # 引数リストから個々の値を取得
            index = arguments[0]
            enabled = arguments[1]
            # 一時設定とチェックボックスに反映
            self._ignorecase_list_edited[index] = enabled  # 一時設定に反映
            self._chkbx_ignorecase_list[index].SetValue(enabled)

        def _ListBox_SelectedItemIndex(self):
            """
            選択された項目のインデックスを返す 何も選択されていないなら-1を返す
            """
            return self._listbox.GetFirstSelected()

        def _ListBox_MoveItem(self, arguments):
            """
            リストボックスの要素(一つ)を移動する

            他の要素は移動した要素に合わせてずれる

            Args:
                arguments: 引数のリスト(0: 移動させたい要素の元の位置(int), 1: 移動先の位置(int))
            """
            # 引数リストから個々の値を取得
            item_position = arguments[0]
            target_position = arguments[1]

            # 要素を移動
            move_listitem(self._enabled_list_edited, item_position, target_position)
            move_listitem(self._ignorecase_list_edited, item_position, target_position)
            move_listitem(self._pattern_list_edited, item_position, target_position)
            move_listitem(self._example_list_edited, item_position, target_position)
            move_listitem(self._remarks_list_edited, item_position, target_position)

        def _ListBox_AddItem(self, arguments):
            """
            リストボックスに要素を追加する

            Args:
                arguments: 引数のリスト(0: 挿入位置(int), 1: 有効/無効(bool), 2: 大文字小文字無視(bool), 3: 正規表現パターン(str), 4: マッチ例(str), 5: 備考(str))
            """
            # 引数リストから個々の値を取得
            position = arguments[0]
            enabled = arguments[1]
            ignorecase = arguments[2]
            pattern = arguments[3]
            example = arguments[4]
            remarks = arguments[5]

            # 挿入位置の指定がリストの長さを逸脱しているか、負の値のときは末尾に指定
            if (position > len(self._enabled_list_edited)) or position < 0:
                position = len(self._enabled_list_edited)

            # 要素を挿入
            self._enabled_list_edited.insert(position, enabled)
            self._ignorecase_list_edited.insert(position, ignorecase)
            self._pattern_list_edited.insert(position, pattern)
            self._example_list_edited.insert(position, example)
            self._remarks_list_edited.insert(position, remarks)

        def _ListBox_EditItem(self, arguments):
            """
            リストボックスの項目を編集する

            Args:
                arguments: 引数のリスト(0: 編集位置(int), 1: 有効/無効(bool), 2: 大文字小文字無視(bool), 3: 正規表現パターン(str), 4: マッチ例(str), 5: 備考(str))
            """
            position = arguments[0]
            self._ListBox_RemoveItem(position)
            self._ListBox_AddItem(arguments)

        def _ListBox_RemoveItem(self, position):
            """
            指定した位置の要素を削除する

            Args:
                position (int): 削除したい要素の位置
            """
            del self._enabled_list_edited[position]
            del self._ignorecase_list_edited[position]
            del self._pattern_list_edited[position]
            del self._example_list_edited[position]
            del self._remarks_list_edited[position]

    class StartLinesPage(RE_SubPage):
        """
        開始条件を扱うページ
        """
        def __init__(self, window, parent):
            super().__init__(window, parent, Settings.RegularExpressions.StartLines())

    class EndLinesPage(RE_SubPage):
        """
        終了条件を扱うページ
        """
        def __init__(self, window, parent):
            super().__init__(window, parent, Settings.RegularExpressions.EndLines())

    class IgnoreLinesPage(RE_SubPage):
        """
        無視条件を扱うページ
        """
        def __init__(self, window, parent):
            super().__init__(window, parent, Settings.RegularExpressions.IgnoreLines())

    class ReplaceLinesPage(RE_SubPage):
        """
        置換条件を扱うページのスーパークラス
        """
        def __init__(self, window, parent, Settings, column_labels=res_replace_column_labels, column_tips=res_replace_column_tips, column_widths=res_replace_column_widths):
            super().__init__(window, parent, Settings, column_labels, column_tips, column_widths)

        def _Button_Add_Event(self, event):
            """
            追加ボタンを押した時の処理
            """
            # 選択された項目のインデックスを取得 何も選択されていないなら負の値になり、末尾に追加される
            index = self._ListBox_SelectedItemIndex()

            InputItemInfoWindow_Replace(self._window, "項目の追加", wx.Size(500, 280), wx.Size(1000, 280), self, self._ListBox_AddItem, index)

        def _Button_Edit_Event(self, event):
            """
            編集ボタンを押した時の処理
            """
            # 選択された項目のインデックスを取得
            index = self._ListBox_SelectedItemIndex()

            # 何かが選択されているなら編集を実行
            if index >= 0:
                InputItemInfoWindow_Replace(
                    self._window,
                    "項目の編集",
                    wx.Size(500, 280),
                    wx.Size(1000, 280),
                    self,
                    self._ListBox_EditItem,
                    index,
                    self._enabled_list_edited[index],
                    self._ignorecase_list_edited[index],
                    self._pattern_list_edited[index],
                    self._target_list_edited[index],
                    self._example_list_edited[index],
                    self._remarks_list_edited[index])

        def _ListBox_PrepareItems(self):
            """
            リストボックスに既存の項目を並べる
            """
            for i in range(len(self._enabled_list_edited)):
                # 一行ごとに色を互い違いにする
                if i % 2:
                    color = wx.Colour(230, 230, 230)    # 濃い灰色
                else:
                    color = wx.Colour(250, 250, 250)    # 淡い灰色

                # 行の挿入と色の設定
                self._listbox.InsertStringItem(i, "")
                self._listbox.SetItemBackgroundColour(i, color)

                # チェックボックスの用意
                chkbx_enable = wx.CheckBox(self._listbox, id=i)
                chkbx_enable.Bind(wx.EVT_CHECKBOX, self._CheckBox_Enable_Event)
                chkbx_ignorecase = wx.CheckBox(self._listbox, id=i)
                chkbx_ignorecase.Bind(wx.EVT_CHECKBOX, self._CheckBox_IgnoreCase_Event)
                chkbx_enable.SetValue(self._enabled_list_edited[i])   # 設定に基づいて初期値を設定
                chkbx_ignorecase.SetValue(self._ignorecase_list_edited[i])
                chkbx_enable.SetBackgroundColour(color)
                chkbx_ignorecase.SetBackgroundColour(color)
                self._chkbx_enable_list.append(chkbx_enable)    # 後から追跡できるようにリストにセット
                self._chkbx_ignorecase_list.append(chkbx_ignorecase)

                # 行の各列へのアイテムの追加
                # どうやらヘッダとセルのアラインメントを別々で設定することはできないらしい……
                # と思っていたが、それ以外の操作もできている様子がないので、
                # できることはできるがなにか面倒な儀式を踏まないとできなさそうな予感
                self._listbox.SetItemWindow(i, 0, chkbx_enable)
                self._listbox.SetItemWindow(i, 1, chkbx_ignorecase)
                self._listbox.SetStringItem(i, 2, self._pattern_list_edited[i])
                self._listbox.SetStringItem(i, 3, self._target_list_edited[i])
                self._listbox.SetStringItem(i, 4, self._example_list_edited[i])
                self._listbox.SetStringItem(i, 5, self._remarks_list_edited[i])

        def _Initiate_SettingLists(self):
            """
            一時設定を、編集ウインドウを開いた当初のものに戻す
            """
            # 共通する処理はスーパークラスのメソッドで行う
            super()._Initiate_SettingLists()
            # 設定から値をコピーしていない場合、初期値としてコピーする
            # コピーしてからの値の変更で設定ごと変えられないように、deepcopyでコピー
            if not hasattr(self, "_target_list_initial"):
                self._target_list_initial = deepcopy(self._Settings.target_list)
            # 初期設定を反映
            self._target_list_edited = deepcopy(self._target_list_initial)

        def ApplySettings(self):
            """
            設定に値の変更を適用する
            """
            # 共通する処理はスーパークラスのメソッドで行う
            super().ApplySettings()
            # コピーしてからの値の変更で設定ごと変えられないように、deepcopyでコピー
            self._Settings.target_list = deepcopy(self._target_list_edited)

        def _ListBox_MoveItem(self, arguments):
            """
            リストボックスの要素(一つ)を移動する

            他の要素は移動した要素に合わせてずれる

            Args:
                arguments: 引数のリスト(0: 移動させたい要素の元の位置(int), 1: 移動先の位置(int))
            """
            # 共通する処理はスーパークラスのメソッドで行う
            super()._ListBox_MoveItem(arguments)
            # 引数リストから個々の値を取得
            item_position = arguments[0]
            target_position = arguments[1]

            # 要素を移動
            move_listitem(self._target_list_edited, item_position, target_position)

        def _ListBox_AddItem(self, arguments):
            """
            リストボックスに要素を追加する

            Args:
                arguments: 引数のリスト(0: 挿入位置(int), 1: 有効/無効(bool), 2: 大文字小文字無視(bool), 3: 正規表現パターン(str), 4: 置換後の文字列(str), 5: マッチ例(str), 6: 備考(str))
            """
            # 引数リストから個々の値を取得
            position = arguments[0]
            enabled = arguments[1]
            ignorecase = arguments[2]
            pattern = arguments[3]
            target = arguments[4]
            example = arguments[5]
            remarks = arguments[6]
            # 共通する処理はスーパークラスのメソッドで行う
            super()._ListBox_AddItem([position, enabled, ignorecase, pattern, example, remarks])

            # 挿入位置の指定がリストの長さを逸脱しているか、負の値のときは末尾に指定
            if (position > len(self._enabled_list_edited)) or position < 0:
                position = len(self._enabled_list_edited)

            # 要素を挿入
            self._target_list_edited.insert(position, target)

        def _ListBox_RemoveItem(self, position):
            """
            指定した位置の要素を削除する

            Args:
                position (int): 削除したい要素の位置
            """
            # 共通する処理はスーパークラスのメソッドで行う
            super()._ListBox_RemoveItem(position)
            del self._target_list_edited[position]

    class StandardReplaceLinesPage(ReplaceLinesPage):
        """
        置換条件を扱うページ
        """
        def __init__(self, window, parent):
            super().__init__(window, parent, Settings.RegularExpressions.ReplaceParts.Standard())

    class MarkdownReplaceLinesPage(ReplaceLinesPage):
        """
        置換条件(Markdown)を扱うページ
        """
        def __init__(self, window, parent):
            super().__init__(window, parent, Settings.RegularExpressions.ReplaceParts.Markdown())

    class ChartStartLinesPage(RE_SubPage):
        """
        図表開始条件を扱うページ
        """
        def __init__(self, window, parent):
            super().__init__(window, parent, Settings.RegularExpressions.ChartStartLines())

    class PossibilityReturnLinesPage(RE_SubPage):
        """
        改行条件を扱うページ
        """
        def __init__(self, window, parent):
            super().__init__(window, parent, Settings.RegularExpressions.ReturnLines.Possibility())

    class IgnoreReturnLinesPage(RE_SubPage):
        """
        改行無視条件を扱うページ
        """
        def __init__(self, window, parent):
            super().__init__(window, parent, Settings.RegularExpressions.ReturnLines.Ignore())

    class HeaderLinesPage(RE_SubPage):
        """
        置換条件を扱うページ
        """
        def __init__(self, window, parent):
            super().__init__(window, parent, Settings.RegularExpressions.HeaderLines(), res_header_column_labels, res_header_column_tips, res_header_column_widths)

        def _Button_Add_Event(self, event):
            """
            追加ボタンを押した時の処理
            """
            # 選択された項目のインデックスを取得 何も選択されていないなら負の値になり、末尾に追加される
            index = self._ListBox_SelectedItemIndex()

            InputItemInfoWindow_Header(self._window, "項目の追加", wx.Size(500, 340), wx.Size(1000, 340), self, self._ListBox_AddItem, index)

        def _Button_Edit_Event(self, event):
            """
            編集ボタンを押した時の処理
            """
            # 選択された項目のインデックスを取得
            index = self._ListBox_SelectedItemIndex()

            # 何かが選択されているなら編集を実行
            if index >= 0:
                InputItemInfoWindow_Header(
                    self._window,
                    "項目の編集",
                    wx.Size(500, 340),
                    wx.Size(1000, 340),
                    self,
                    self._ListBox_EditItem,
                    index,
                    self._enabled_list_edited[index],
                    self._ignorecase_list_edited[index],
                    self._pattern_list_edited[index],
                    self._depth_count_list_edited[index],
                    self._target_remove_list_edited[index],
                    self._max_size_list_edited[index],
                    self._example_list_edited[index],
                    self._remarks_list_edited[index])

        def _ListBox_PrepareItems(self):
            """
            リストボックスに既存の項目を並べる
            """
            for i in range(len(self._enabled_list_edited)):
                # 一行ごとに色を互い違いにする
                if i % 2:
                    color = wx.Colour(230, 230, 230)    # 濃い灰色
                else:
                    color = wx.Colour(250, 250, 250)    # 淡い灰色

                # 行の挿入と色の設定
                self._listbox.InsertStringItem(i, "")
                self._listbox.SetItemBackgroundColour(i, color)

                # チェックボックスの用意
                chkbx_enable = wx.CheckBox(self._listbox, id=i)
                chkbx_enable.Bind(wx.EVT_CHECKBOX, self._CheckBox_Enable_Event)
                chkbx_ignorecase = wx.CheckBox(self._listbox, id=i)
                chkbx_ignorecase.Bind(wx.EVT_CHECKBOX, self._CheckBox_IgnoreCase_Event)
                chkbx_enable.SetValue(self._enabled_list_edited[i])   # 設定に基づいて初期値を設定
                chkbx_ignorecase.SetValue(self._ignorecase_list_edited[i])
                chkbx_enable.SetBackgroundColour(color)
                chkbx_ignorecase.SetBackgroundColour(color)
                self._chkbx_enable_list.append(chkbx_enable)    # 後から追跡できるようにリストにセット
                self._chkbx_ignorecase_list.append(chkbx_ignorecase)

                # 行の各列へのアイテムの追加
                # どうやらヘッダとセルのアラインメントを別々で設定することはできないらしい……
                # と思っていたが、それ以外の操作もできている様子がないので、
                # できることはできるがなにか面倒な儀式を踏まないとできなさそうな予感
                self._listbox.SetItemWindow(i, 0, chkbx_enable)
                self._listbox.SetItemWindow(i, 1, chkbx_ignorecase)
                self._listbox.SetStringItem(i, 2, self._pattern_list_edited[i])
                self._listbox.SetStringItem(i, 3, self._depth_count_list_edited[i])
                self._listbox.SetStringItem(i, 4, self._target_remove_list_edited[i])
                self._listbox.SetStringItem(i, 5, str(self._max_size_list_edited[i]))
                self._listbox.SetStringItem(i, 6, self._example_list_edited[i])
                self._listbox.SetStringItem(i, 7, self._remarks_list_edited[i])

        def _Initiate_SettingLists(self):
            """
            一時設定を、編集ウインドウを開いた当初のものに戻す
            """
            # 共通する処理はスーパークラスのメソッドで行う
            super()._Initiate_SettingLists()
            # 設定から値をコピーしていない場合、初期値としてコピーする
            # コピーしてからの値の変更で設定ごと変えられないように、deepcopyでコピー
            if not hasattr(self, "_depth_count_list_initial"):
                self._depth_count_list_initial = deepcopy(self._Settings.depth_count_list)
                self._target_remove_list_initial = deepcopy(self._Settings.target_remove_list)
                self._max_size_list_initial = deepcopy(self._Settings.max_size_list)
            # 初期設定を反映
            self._depth_count_list_edited = deepcopy(self._depth_count_list_initial)
            self._target_remove_list_edited = deepcopy(self._target_remove_list_initial)
            self._max_size_list_edited = deepcopy(self._max_size_list_initial)

        def ApplySettings(self):
            """
            設定に値の変更を適用する
            """
            # 共通する処理はスーパークラスのメソッドで行う
            super().ApplySettings()
            # コピーしてからの値の変更で設定ごと変えられないように、deepcopyでコピー
            self._Settings.depth_count_list = deepcopy(self._depth_count_list_edited)
            self._Settings.target_remove_list = deepcopy(self._target_remove_list_edited)
            self._Settings.max_size_list = deepcopy(self._max_size_list_edited)

        def _ListBox_MoveItem(self, arguments):
            """
            リストボックスの要素(一つ)を移動する

            他の要素は移動した要素に合わせてずれる

            Args:
                arguments: 引数のリスト(0: 移動させたい要素の元の位置(int), 1: 移動先の位置(int))
            """
            # 共通する処理はスーパークラスのメソッドで行う
            super()._ListBox_MoveItem(arguments)
            # 引数リストから個々の値を取得
            item_position = arguments[0]
            target_position = arguments[1]

            # 要素を移動
            move_listitem(self._depth_count_list_edited, item_position, target_position)
            move_listitem(self._target_remove_list_edited, item_position, target_position)
            move_listitem(self._max_size_list_edited, item_position, target_position)

        def _ListBox_AddItem(self, arguments):
            """
            リストボックスに要素を追加する

            Args:
                arguments: 引数のリスト(0: 挿入位置(int), 1: 有効/無効(bool), 2: 大文字小文字無視(bool), 3: 正規表現パターン(str), 4: 見出しの深さ判定(str), 5: 訳文から除く文字列(str), 6: 見出しの最大サイズ(int), 7: マッチ例(str), 8: 備考(str))
            """
            # 引数リストから個々の値を取得
            position = arguments[0]
            enabled = arguments[1]
            ignorecase = arguments[2]
            pattern = arguments[3]
            depth_count = arguments[4]
            target_remove = arguments[5]
            max_size = arguments[6]
            example = arguments[7]
            remarks = arguments[8]
            # 共通する処理はスーパークラスのメソッドで行う
            super()._ListBox_AddItem([position, enabled, ignorecase, pattern, example, remarks])

            # 挿入位置の指定がリストの長さを逸脱しているか、負の値のときは末尾に指定
            if (position > len(self._enabled_list_edited)) or position < 0:
                position = len(self._enabled_list_edited)

            # 要素を挿入
            self._depth_count_list_edited.insert(position, depth_count)
            self._target_remove_list_edited.insert(position, target_remove)
            self._max_size_list_edited.insert(position, max_size)

        def _ListBox_RemoveItem(self, position):
            """
            指定した位置の要素を削除する

            Args:
                position (int): 削除したい要素の位置
            """
            # 共通する処理はスーパークラスのメソッドで行う
            super()._ListBox_RemoveItem(position)
            del self._depth_count_list_edited[position]
            del self._target_remove_list_edited[position]
            del self._max_size_list_edited[position]
