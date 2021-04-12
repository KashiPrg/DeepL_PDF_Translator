import wx

from copy import deepcopy
from data import res_introduction
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


class RegularExpressionsWindow(wx.Frame):
    def __init__(self, parent):
        super().__init__(
            parent,
            title="正規表現の編集",
            size=(960, 540)
        )

        # タブによるページを構成するためのコンポーネント
        self.__pages = wx.Notebook(self)

        # タブを追加
        self.__pages.InsertPage(0, RegularExpressionsWindow.IntroductionPage(self.__pages), "概要説明")
        self.__pages.InsertPage(1, RegularExpressionsWindow.StartLinesPage(self.__pages), "抽出開始条件")
        self.__pages.InsertPage(2, RegularExpressionsWindow.EndLinesPage(self.__pages), "抽出終了条件")
        self.__pages.InsertPage(3, RegularExpressionsWindow.IgnoreLinesPage(self.__pages), "無視条件")
        self.__pages.InsertPage(4, RegularExpressionsWindow.ChartStartLinesPage(self.__pages), "図表開始条件")

        self.Show()

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
        def __init__(self, parent, Settings):
            super().__init__(parent)
            # 該当箇所の設定
            self._Settings = Settings
            # 設定から値をコピー
            self._Copy_SettingLists()

            # 操作関数のリストとその引数のリスト
            self._operation_list = []
            self._operation_args = []
            # 「現在、履歴のどの位置を表示しているか」を示すマーカー(Undo, Redoで利用)
            self._history_marker = 0

            self._sizer = wx.BoxSizer(wx.VERTICAL)

            # 全体の有効化のチェックボックス
            self._chkbx_enabled_overall = wx.CheckBox(self, wx.ID_ANY, "この項目を有効にする")
            self._chkbx_enabled_overall.SetValue(self._enabled_overall)
            self._chkbx_enabled_overall.Bind(wx.EVT_CHECKBOX, self._CheckBox_EnabledOverall_Event)
            self._sizer.Add(self._chkbx_enabled_overall, flag=wx.ALIGN_LEFT | wx.TOP | wx.LEFT, border=5)

            # リストボックスと各種メニュー
            self._lb_sizer = wx.BoxSizer(wx.HORIZONTAL)
            self._lb_boxsizer = wx.BoxSizer(wx.VERTICAL)
            # チェックボックス付きのリストボックス
            self._Prepare_ListBox()
            self._lb_sizer.Add(self._lb_boxsizer, proportion=1, flag=wx.EXPAND | wx.RIGHT, border=3)
            # 各種メニュー
            splitter_label = "----------"
            splitter_color = wx.Colour(200, 200, 200)
            self._lb_menusizer = wx.BoxSizer(wx.VERTICAL)
            self._add_button = wx.Button(self, label="追加")    # 追加ボタン
            self._add_button.Bind(wx.EVT_BUTTON, self._Button_Add_Event)
            self._lb_menusizer.Add(self._add_button)
            self._edit_button = wx.Button(self, label="編集")   # 編集ボタン
            self._lb_menusizer.Add(self._edit_button, flag=wx.TOP, border=3)
            splitter1 = wx.StaticText(self, label=splitter_label)
            splitter1.SetForegroundColour(splitter_color)
            self._lb_menusizer.Add(splitter1, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=5)
            self._top_button = wx.Button(self, label="最上位へ")    # 移動ボタン類
            self._lb_menusizer.Add(self._top_button)
            self._up_button = wx.Button(self, label="一つ上へ")
            self._lb_menusizer.Add(self._up_button, flag=wx.TOP, border=10)
            self._down_button = wx.Button(self, label="一つ下へ")
            self._lb_menusizer.Add(self._down_button, flag=wx.TOP, border=3)
            self._bottom_button = wx.Button(self, label="最下位へ")
            self._lb_menusizer.Add(self._bottom_button, flag=wx.TOP, border=10)
            splitter2 = wx.StaticText(self, label=splitter_label)
            splitter2.SetForegroundColour(splitter_color)
            self._lb_menusizer.Add(splitter2, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=5)
            self._undo_button = wx.Button(self, label="Undo")   # 一つ戻る
            self._undo_button.Bind(wx.EVT_BUTTON, self._Button_Undo_Event)
            self._lb_menusizer.Add(self._undo_button)
            self._redo_button = wx.Button(self, label="Redo")   # 一つ進む
            self._redo_button.Bind(wx.EVT_BUTTON, self._Button_Redo_Event)
            self._lb_menusizer.Add(self._redo_button, flag=wx.TOP, border=3)
            self._lb_sizer.Add(self._lb_menusizer, flag=wx.ALIGN_TOP)
            self._sizer.Add(self._lb_sizer, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)

            # OK・適用・キャンセルボタン
            self._buttonsizer = wx.BoxSizer(wx.HORIZONTAL)
            self._ok_button = wx.Button(self, label="OK")
            self._buttonsizer.Add(self._ok_button)
            self._applybutton = wx.Button(self, label="適用")
            self._buttonsizer.Add(self._applybutton, flag=wx.LEFT, border=12)
            self._cancelbutton = wx.Button(self, label="キャンセル")
            self._buttonsizer.Add(self._cancelbutton, flag=wx.LEFT, border=12)
            self._sizer.Add(self._buttonsizer, flag=wx.ALIGN_RIGHT | wx.RIGHT | wx.BOTTOM, border=5)

            self.SetSizer(self._sizer)
            self.Refresh()

        def _CheckBox_EnabledOverall_Event(self, event):
            """
            全体の有効化のチェックボックスを押した時の処理
            """
            self._Settings.enabled_overall = self._chkbx_enabled_overall.GetValue()
            if self._chkbx_enabled_overall.GetValue():
                self._listbox.Enable()
            else:
                self._listbox.Disable()

        def _Button_Add_Event(self, event):
            """
            追加ボタンを押した時の処理
            """
            self._Add_Operation(self._ListBox_AddItem, [-1, True, False, "test", "test", "test"])

        def _Button_Undo_Event(self, event):
            """
            Undo(一つ戻る)ボタンを押した時の処理
            """
            # マーカーを一つ戻してリストボックスを更新
            if self._history_marker > 0:
                self._history_marker -= 1
            self._Apply_Operations()

        def _Button_Redo_Event(self, event):
            """
            Redo(一つ進む)ボタンを押した時の処理
            """
            # マーカーを一つ進めてリストボックスを更新
            if self._history_marker < len(self._operation_list):
                self._history_marker += 1
            self._Apply_Operations()

        def _Prepare_ListBox(self):
            """
            リストボックスを用意する
            """
            # ULC.ULC_HAS_VARIABLE_ROW_HEIGHT と ULC.ULC_REPORT を兼ね備えていないとチェックボックスなどのウィジェットを追加できない
            self._listbox = ULC.UltimateListCtrl(self, agwStyle=ULC.ULC_HAS_VARIABLE_ROW_HEIGHT | ULC.ULC_REPORT | ULC.ULC_VRULES)
            self._ListBox_PrepareColumns()  # 列を追加
            self._chkbx_enable_list = []        # 有効化のチェックボックスのリスト
            self._chkbx_ignorecase_list = []    # 大文字小文字無視のチェックボックスのリスト
            self._ListBox_PrepareItems()    # 項目を追加
            self._lb_boxsizer.Add(self._listbox, proportion=1, flag=wx.EXPAND)

        def _Refresh_ListBox(self):
            """
            リストボックスの表示を更新する
            """
            # リストボックスをSizerから除きつつ破棄
            self._lb_boxsizer.Detach(0)

            # 古いリストボックスをギリギリまで保持しておくことで画面のチラつきを抑える
            temp = self._listbox        # 古いリストボックスを退避
            self._Prepare_ListBox()     # 新しいリストボックスを用意
            self._lb_boxsizer.Layout()  # 新しいリストボックスを配置
            temp.Destroy()              # 古いリストボックスを破棄

        def _ListBox_PrepareColumns(self):
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

            self._listbox.InsertColumnInfo(0, gen_column_header("", "全ての項目を一括で切り替えます。", 1, mask | ULC.ULC_MASK_CHECK))
            self._listbox.SetColumnWidth(0, 25)     # 幅を設定
            self._listbox.InsertColumnInfo(1, gen_column_header("大小無視", "大文字と小文字を区別するかを管理します。\nこのヘッダのチェックボックスで全ての項目を一括で切り替えられます。", 1))
            self._listbox.SetColumnWidth(1, 60)
            self._listbox.InsertColumnInfo(2, gen_column_header("正規表現パターン", "このパターンに適合する行に、対応する操作が行われます。"))
            self._listbox.SetColumnWidth(2, 225)
            self._listbox.InsertColumnInfo(3, gen_column_header("例", "正規表現パターンに適合する文字列の例です。"))
            self._listbox.SetColumnWidth(3, 250)
            self._listbox.InsertColumnInfo(4, gen_column_header("備考", "正規表現パターンに対する備考や注意を書いてください。"))
            self._listbox.SetColumnWidth(4, 350)

        def _ListBox_PrepareItems(self):
            """
            リストボックスに既存の項目を並べる
            """
            for i in range(len(self._enabled_list)):
                # 一行ごとに色を互い違いにする
                if i % 2:
                    color = wx.Colour(230, 230, 230)    # 濃い灰色
                else:
                    color = wx.Colour(250, 250, 250)    # 淡い灰色

                # 行の挿入と色の設定
                self._listbox.InsertStringItem(i, "")
                self._listbox.SetItemBackgroundColour(i, color)

                # チェックボックスの用意
                chkbx_enable = RegularExpressionsWindow.ListCheckBox(self._listbox, i)
                chkbx_ignorecase = RegularExpressionsWindow.ListCheckBox(self._listbox, i)
                chkbx_enable.SetValue(self._enabled_list[i])   # 設定に基づいて初期値を設定
                chkbx_ignorecase.SetValue(self._ignorecase_list[i])
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
                self._listbox.SetStringItem(i, 2, self._pattern_list[i])
                self._listbox.SetStringItem(i, 3, self._example_list[i])
                self._listbox.SetStringItem(i, 4, self._remarks_list[i])

        def _Copy_SettingLists(self):
            """
            設定から値をコピーする
            """
            self._enabled_overall = self._Settings.enabled_overall
            self._enabled_list = deepcopy(self._Settings.enabled_list)
            self._ignorecase_list = deepcopy(self._Settings.ignorecase_list)
            self._pattern_list = deepcopy(self._Settings.pattern_list)
            self._example_list = deepcopy(self._Settings.example_list)
            self._remarks_list = deepcopy(self._Settings.remarks_list)

        def _Add_Operation(self, func, argument):
            # もし履歴をさかのぼっていたら、それ以後の操作を破棄する
            if self._history_marker < len(self._operation_list):
                self._operation_list = self._operation_list[:self._history_marker]
                self._operation_args = self._operation_args[:self._history_marker]

            # 操作を追加し、マーカーを一つ進める
            self._operation_list.append(func)
            self._operation_args.append(argument)
            self._history_marker += 1

            # 操作を適用して画面を更新
            self._Apply_Operations()

        def _Apply_Operations(self):
            """
            今までに行われた(登録された)操作を実行し、その結果をウインドウに表示する
            """
            # 初期状態として設定をコピー
            self._Copy_SettingLists()

            # 登録された操作を順次実行(Undoで履歴をさかのぼっていたらその位置まで)
            for i in range(self._history_marker):
                handler(self._operation_list[i], self._operation_args[i])

            # 画面の更新
            self._Refresh_ListBox()

        def _Set_EnabledOverall(self, state):
            self._enabled_overall = state

        def _ListBox_MoveItem(self, arguments):
            """
            リストボックスの要素(一つ)を移動する

            他の要素は移動した要素に合わせてずれる

            Args:
                arguments: 引数のリスト(0: 移動させたい要素の元の位置(int), 1: 移動先の位置(int))
            """
            item_position = arguments[0]
            target_position = arguments[1]

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

            # 要素を移動
            move_listitem(self._enabled_list, item_position, target_position)
            move_listitem(self._ignorecase_list, item_position, target_position)
            move_listitem(self._pattern_list, item_position, target_position)
            move_listitem(self._example_list, item_position, target_position)
            move_listitem(self._remarks_list, item_position, target_position)

        def _ListBox_AddItem(self, arguments):
            """
            リストボックスに要素を追加する

            Args:
                arguments: 引数のリスト(0: 挿入位置(int), 1: 有効/無効(bool), 2: 大文字小文字無視(bool), 3: 正規表現パターン(str), 4: マッチ例(str), 5: 備考(str))
            """
            position = arguments[0]
            enabled = arguments[1]
            ignorecase = arguments[2]
            pattern = arguments[3]
            example = arguments[4]
            remarks = arguments[5]

            # 挿入位置の指定がリストの長さを逸脱しているか、負の値のときは末尾に指定
            if (position > len(self._enabled_list)) or position < 0:
                position = len(self._enabled_list)

            # 要素を挿入
            self._enabled_list.insert(position, enabled)
            self._ignorecase_list.insert(position, ignorecase)
            self._pattern_list.insert(position, pattern)
            self._example_list.insert(position, example)
            self._remarks_list.insert(position, remarks)

        def _ListBox_RemoveItem(self, position):
            """
            指定した位置の要素を削除する

            Args:
                position (int): 削除したい要素の位置
            """
            del self._enabled_list[position]
            del self._ignorecase_list[position]
            del self._pattern_list[position]
            del self._example_list[position]
            del self._remarks_list[position]

    class ListCheckBox(wx.CheckBox):
        """
        行番号を内包したチェックボックス
        """
        def __init__(self, parent, row_num):
            super().__init__(parent)
            self.row_num = row_num

    class StartLinesPage(RE_SubPage):
        """
        開始条件を扱うページ
        """
        def __init__(self, parent):
            super().__init__(parent, Settings.RegularExpressions.StartLines())

    class EndLinesPage(RE_SubPage):
        """
        終了条件を扱うページ
        """
        def __init__(self, parent):
            super().__init__(parent, Settings.RegularExpressions.EndLines())

    class IgnoreLinesPage(RE_SubPage):
        """
        無視条件を扱うページ
        """
        def __init__(self, parent):
            super().__init__(parent, Settings.RegularExpressions.IgnoreLines())

    class ChartStartLinesPage(RE_SubPage):
        """
        図表開始条件を扱うページ
        """
        def __init__(self, parent):
            super().__init__(parent, Settings.RegularExpressions.ChartStartLines())


class RegularExpressions:
    # このリストに含まれる正規表現に当てはまる文字列から翻訳を開始する
    start_lines = [r"[0-9]+\s*\.?\s*introduction", r"introduction$"]
    # このリストに含まれる正規表現に当てはまる文字列で翻訳を打ち切る
    end_lines = [r"^references?$"]

    # このリストに含まれる正規表現に当てはまる文字列は無視する
    ignore_lines = [
        r"^\s*ACM Trans",
        r"^\s*[0-9]*:[0-9]*\s*$",   # ページ数
        r"^\s*[0-9]*\s*of\s*[0-9]*\s*$",     # ページ数
        r"^\s*.\s*$",   # なにか一文字しか無い 後でユーザが何文字まで無視するか設定できるようにしたい
        r"^.*(.{1,3}\s+){10,}.*$",  # ぶつ切れの語が極端に多い
        r"Peng Wang, Lingjie Liu, Nenglun Chen, Hung-Kuo Chu, Christian Theobalt, and Wenping Wang$",
        r"^\s*Multimodal Technologies and Interact\s*",
        r"^www.mdpi.com/journal/mti$",
        r"^\s*Li et al\.\s*$",
        r"^\s*Exertion-Aware Path Generation\s*$"
    ]

    # フォーマットの都合上どうしても入ってしまうノイズを置換する
    # これはそのノイズ候補のリスト
    # 一般的な表現の場合は諸刃の剣となるので注意
    # また、リストの最初に近いほど優先して処理される
    replace_source = [
        r"\s*[0-9]+\s*of\s*[0-9]+\s*",   # "1 of 9" などのページカウント
        r"\s*Li et al\.\s*"
    ]
    # ノイズをどのような文字列に置換するか
    replace_target = [
        " ",
        " "
    ]

    # markdown用の置換リスト
    markdown_replace_source = [
        "•"
    ]
    markdown_replace_target = [
        "-"
    ]

    # このリストに含まれる正規表現に当てはまる文字列がある行で改行する
    return_lines = [
        r"(\.|:|;|\([0-9]+\))\s*$",   # 文末(計算式や箇条書きなども含む)
        r"^\s*([0-9]+\s*\.\s*)+.{3,45}\s*$",    # 見出し
        r"^\s*([0-9]+\s*\.\s*)*[0-9]+\s*.{3,45}\s*$",    # 見出し ↑よりも条件が緩いので注意
        r"^([0-9]+\s*\.?)?\s*introduction$",    # 数字がない場合にも対応
        r"^([0-9]+\s*\.?)?\s*related works?$",
        r"^([0-9]+\s*\.?)?\s*overview$",
        r"^([0-9]+\s*\.?)?\s*algorithm$",
        r"^([0-9]+\s*\.?)?\s*experimental results?$",
        r"^([0-9]+\s*\.?)?\s*conclusions?$",
        r"^([0-9]+\s*\.?)?\s*acknowledgements?$",
        r"^([0-9]+\s*\.?)?\s*references?$"
    ]
    # このリストに含まれる正規表現に当てはまる文字列があるとき、
    # 改行対象でも改行しない
    # 主にその略語の後に文が続きそうなものが対象
    # 単なる略語は文末にも存在し得るので対象外
    # 参考：[参考文献リストやデータベースに出てくる略語・用語一覧]
    # (https://www.dl.itc.u-tokyo.ac.jp/gacos/supportbook/16.html)
    return_ignore_lines = [
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

    # markdown方式で出力する時、この正規表現に当てはまる行を見出しとして扱う
    header_lines = [
        r"^\s*([0-9]+\s*\.\s*)+.{3,45}\s*$",     # "1.2.3. aaaa" などにヒット
        r"^\s*([0-9]+\s*\.\s*)*[0-9]+\s*.{3,45}\s*$",    # "1.2.3 aaaa" などにヒット
        r"^([0-9]+\s*\.?)?\s*introduction$",    # 数字がない場合にも対応
        r"^([0-9]+\s*\.?)?\s*related works?$",
        r"^([0-9]+\s*\.?)?\s*overview$",
        r"^([0-9]+\s*\.?)?\s*algorithm$",
        r"^([0-9]+\s*\.?)?\s*experimental results?$",
        r"^([0-9]+\s*\.?)?\s*conclusions?$",
        r"^([0-9]+\s*\.?)?\s*acknowledgements?$",
        r"^([0-9]+\s*\.?)?\s*references?$"
    ]
    # 見出しの大きさを決定するためのパターン
    # header_linesの要素と対応する形で記述する
    header_depth_count = [
        r"[0-9]+\s*\.\s*",  # 1.2.3. の"数字."の数が多いほど見出しが小さくなる(#の数が多くなる)
        r"[0-9]+",
        r"^$",
        r"^$",
        r"^$",
        r"^$",
        r"^$",
        r"^$",
        r"^$",
        r"^$"
    ]
    # 見出しの日本語訳の先頭の数字などを消すためのパターン
    header_target_remove = [
        r"[0-9]+\s*\.\s*",
        r"\s*([0-9]+\s*\.\s*)*[0-9]+\s*",
        r"[0-9]+\s*\.\s*",
        r"[0-9]+\s*\.\s*",
        r"[0-9]+\s*\.\s*",
        r"[0-9]+\s*\.\s*",
        r"[0-9]+\s*\.\s*",
        r"[0-9]+\s*\.\s*",
        r"[0-9]+\s*\.\s*",
        r"[0-9]+\s*\.\s*"
    ]
    # 見出しの最大の大きさ 1が最大で6が最小
    # header_linesの要素と対応する形で記述する
    header_max_size = [
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2,
        2
    ]
