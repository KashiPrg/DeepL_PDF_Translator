import wx

from settings import Settings
from wx.lib.agw import ultimatelistctrl as ULC


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
        self.__pages.InsertPage(0, RegularExpressionsWindow.StartLinesPage(self.__pages), "翻訳開始条件")
        self.__pages.InsertPage(1, RegularExpressionsWindow.EndLinesPage(self.__pages), "翻訳終了条件")
        self.__pages.InsertPage(2, RegularExpressionsWindow.IgnoreLinesPage(self.__pages), "無視条件")
        self.__pages.InsertPage(3, RegularExpressionsWindow.ChartStartLinesPage(self.__pages), "図表開始条件")

        self.Show()

    class RE_SubPage(wx.Panel):
        """
        タブの基本設計
        """
        def __init__(self, parent, Settings):
            super().__init__(parent)
            # 該当箇所の設定
            self._Settings = Settings

            self._sizer = wx.BoxSizer(wx.VERTICAL)

            # 全体の有効化のチェックボックス
            self._chkbx_enabled_overall = wx.CheckBox(self, wx.ID_ANY, "この項目を有効にする")
            self._chkbx_enabled_overall.SetValue(self._Settings.enabled_overall)
            self._chkbx_enabled_overall.Bind(wx.EVT_CHECKBOX, self._CheckBox_EnabledOverall_Event)
            self._sizer.Add(self._chkbx_enabled_overall, flag=wx.ALIGN_LEFT | wx.TOP | wx.LEFT, border=5)

            # リストボックスと各種メニュー
            self._lv_sizer = wx.BoxSizer(wx.HORIZONTAL)
            # チェックボックス付きのリストボックス
            # ULC.ULC_HAS_VARIABLE_ROW_HEIGHT と ULC.ULC_REPORT を兼ね備えていないとチェックボックスなどのウィジェットを追加できない
            self._listbox = ULC.UltimateListCtrl(self, agwStyle=ULC.ULC_HAS_VARIABLE_ROW_HEIGHT | ULC.ULC_REPORT | ULC.ULC_VRULES)
            self._lv_sizer.Add(self._listbox, proportion=1, flag=wx.EXPAND | wx.RIGHT, border=3)
            self._ListBox_AddColumns()  # 列を追加
            self._chkbx_enable_list = []
            self._chkbx_ignorecase_list = []
            self._ListBox_AddItems()    # 項目を追加
            # 各種メニュー
            splitter_label = "----------"
            splitter_color = wx.Colour(200, 200, 200)
            self._lv_menusizer = wx.BoxSizer(wx.VERTICAL)
            self._add_button = wx.Button(self, label="追加")
            self._lv_menusizer.Add(self._add_button)
            self._edit_button = wx.Button(self, label="編集")
            self._lv_menusizer.Add(self._edit_button, flag=wx.TOP, border=3)
            splitter1 = wx.StaticText(self, label=splitter_label)
            splitter1.SetForegroundColour(splitter_color)
            self._lv_menusizer.Add(splitter1, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=5)
            self._top_button = wx.Button(self, label="最上位へ")
            self._lv_menusizer.Add(self._top_button)
            self._up_button = wx.Button(self, label="一つ上へ")
            self._lv_menusizer.Add(self._up_button, flag=wx.TOP, border=10)
            self._down_button = wx.Button(self, label="一つ下へ")
            self._lv_menusizer.Add(self._down_button, flag=wx.TOP, border=3)
            self._bottom_button = wx.Button(self, label="最下位へ")
            self._lv_menusizer.Add(self._bottom_button, flag=wx.TOP, border=10)
            splitter2 = wx.StaticText(self, label=splitter_label)
            splitter2.SetForegroundColour(splitter_color)
            self._lv_menusizer.Add(splitter2, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=5)
            self._undo_button = wx.Button(self, label="Undo")
            self._lv_menusizer.Add(self._undo_button)
            self._redo_button = wx.Button(self, label="Redo")
            self._lv_menusizer.Add(self._redo_button, flag=wx.TOP, border=3)
            self._lv_sizer.Add(self._lv_menusizer, flag=wx.ALIGN_TOP)
            self._sizer.Add(self._lv_sizer, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)

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

        def _CheckBox_EnabledOverall_Event(self, event):
            """
            全体の有効化のチェックボックスを押した時のイベント
            """
            self._Settings.enabled_overall = self._chkbx_enabled_overall.GetValue()
            if self._chkbx_enabled_overall.GetValue():
                self._listbox.Enable()
            else:
                self._listbox.Disable()

        def _ListBox_AddColumns(self):
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
                info._format = 2
                return info

            self._listbox.InsertColumnInfo(0, gen_column_header("", "全ての項目を一括で切り替えます。", 1))
            self._listbox.SetColumnWidth(0, 25)     # 幅を設定
            self._listbox.InsertColumnInfo(1, gen_column_header("大小無視", "大文字と小文字を区別するかを管理します。\nこのヘッダのチェックボックスで全ての項目を一括で切り替えられます。", 1))
            self._listbox.SetColumnWidth(1, 75)
            self._listbox.InsertColumnInfo(2, gen_column_header("正規表現パターン", "このパターンに適合する行に、対応する操作が行われます。"))
            self._listbox.SetColumnWidth(2, 225)
            self._listbox.InsertColumnInfo(3, gen_column_header("例", "正規表現パターンに適合する文字列の例です。"))
            self._listbox.SetColumnWidth(3, 250)
            self._listbox.InsertColumnInfo(4, gen_column_header("備考", "正規表現パターンに対する備考や注意を書いてください。"))
            self._listbox.SetColumnWidth(4, 350)

        def _ListBox_AddItems(self):
            for i in range(len(self._Settings.enabled_list)):
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
                chkbx_enable.SetBackgroundColour(color)
                chkbx_ignorecase.SetBackgroundColour(color)
                self._chkbx_enable_list.append(chkbx_enable)
                self._chkbx_ignorecase_list.append(chkbx_ignorecase)

                # 行の各列へのアイテムの追加
                self._listbox.SetItemWindow(i, 0, chkbx_enable)
                self._listbox.SetItemWindow(i, 1, chkbx_ignorecase)
                self._listbox.SetStringItem(i, 2, self._Settings.pattern_list[i])
                self._listbox.SetStringItem(i, 3, self._Settings.example_list[i])
                self._listbox.SetStringItem(i, 4, self._Settings.remarks_list[i])

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
        開始条件を扱うページ
        """
        def __init__(self, parent):
            super().__init__(parent, Settings.RegularExpressions.EndLines())

    class IgnoreLinesPage(RE_SubPage):
        """
        開始条件を扱うページ
        """
        def __init__(self, parent):
            super().__init__(parent, Settings.RegularExpressions.IgnoreLines())

    class ChartStartLinesPage(RE_SubPage):
        """
        開始条件を扱うページ
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
