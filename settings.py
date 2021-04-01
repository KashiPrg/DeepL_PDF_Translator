import json

from copy import deepcopy
from deeplmanager import Browser, language_dict, Target_Lang
from pathlib import Path


default_settings = {
    "main_window": {
        "str_target_lang": Target_Lang.JAPANESE.value,
        "str_web_browser": Browser.CHROME.value,
        "bool_add_target_return": True,
        "bool_output_type_markdown": True,
        "bool_output_source": True,
        "bool_source_as_comment": True
    },
    "regular_expressions": {
        "start_lines": {
            "bool_enabled_overall": True,
            "bool_output_hit_lines": False,
            "list_bool_enabled": [
                True,
                True,
                True
            ],
            "list_bool_ignore_case": [
                True,
                False,
                False
            ],
            "list_str_pattern": [
                r"\d+\s*\.?\s*introduction",
                r"Introduction\s*$",
                r"INTRODUCTION\s*$"
            ],
            "list_str_example": [
                "1.2.3. Introduction",
                "(...) Introduction",
                "(...) INTRODUCTION"
            ],
            "list_str_remarks": [
                "前書きより前はレイアウトが自動抽出に適していないことが多い",
                "先頭だけ大文字",
                "全部大文字用"
            ]
        },
        "end_lines": {
            "bool_enabled_overall": True,
            "bool_output_hit_lines": False,
            "list_bool_enabled": [
                True,
                True,
                True
            ],
            "list_bool_ignore_case": [
                True,
                False,
                False
            ],
            "list_str_pattern": [
                r"^\s*references?\s*$",
                r"References?\s*$",
                r"REFERENCES?\s*$"
            ],
            "list_str_example": [
                "(文頭)References(文末)",
                "References(文末)",
                "REFERENCES(文末)"
            ],
            "list_str_remarks": [
                "参考文献以降は抽出しない",
                "sはあっても無くてもいい",
                "全部大文字用"
            ]
        },
        "ignore_lines": {
            "bool_enabled_overall": True,
            "bool_output_hit_lines": False,
            "list_bool_enabled": [
                True,
                True,
                True,
                True
            ],
            "list_bool_ignore_case": [
                False,
                True,
                False,
                False
            ],
            "list_str_pattern": [
                r"^\s*\d+\s*:\s*\d+\s*$",
                r"^\s*\d+\s*of\s*\d+\s*$",
                r"^\s*.\s*$",
                r"^.*(\S{1,3}\s+){9,}.*$"
            ],
            "list_str_example": [
                "2 : 32",
                "4 of 14",
                "a",
                "T h i s i s a p e n ."
            ],
            "list_str_remarks": [
                "ページ数",
                "ページ数",
                "なにか一文字しか無い",
                "縦書きや特殊レイアウトなどの影響でぶつ切れの語が極端に多い"
            ]
        },
        "replace_parts": {
            "standard": {
                "bool_enabled_overall": True,
                "bool_output_hit_lines": False,
                "list_bool_enabled": [
                    False,
                    False
                ],
                "list_bool_ignore_case": [
                    False,
                    True
                ],
                "list_str_pattern": [
                    r"\s*\d*\s*:\s*\d*\s*",
                    r"\s*\d+\s*of\s*\d+\s*"
                ],
                "list_str_target": [
                    " ",
                    " "
                ],
                "list_str_example": [
                    "2 : 32",
                    "4 of 14"
                ],
                "list_str_remarks": [
                    "ページ数カウント 簡単な分必要な箇所でも引っかかりやすいので注意",
                    "ページ数カウント 一般的な表現でもあるので注意"
                ]
            },
            "markdown": {
                "bool_enabled_overall": True,
                "bool_output_hit_lines": False,
                "list_bool_enabled": [
                    True
                ],
                "list_bool_ignore_case": [
                    False
                ],
                "list_str_pattern": [
                    r"^\s*•"
                ],
                "list_str_target": [
                    "-"
                ],
                "list_str_example": [
                    "文頭の•(黒丸)"
                ],
                "list_str_remarks": [
                    "箇条書きをMarkdown用に置き換える"
                ]
            }
        },
        "chart_start_lines": {
            "bool_enabled_overall": True,
            "bool_output_hit_lines": False,
            "list_bool_enabled": [
                True
            ],
            "list_bool_ignore_case": [
                True
            ],
            "list_str_pattern": [
                r"^\s*(Fig\.|Figure|Table)\s*\d+\s*(\.|:|;)"
            ],
            "list_str_example": [
                "Fig. 1. | Figure 2: | Table3;"
            ],
            "list_str_remarks": [
                "図表"
            ]
        },
        "return_lines": {
            "possibility": {
                "bool_enabled_overall": True,
                "bool_output_hit_lines": False,
                "list_bool_enabled": [
                    True,
                    True,
                    True,
                    True,
                    True,
                    True,
                    True,
                    True,
                    True,
                    True,
                    True,
                    True
                ],
                "list_bool_ignore_case": [
                    False,
                    False,
                    False,
                    False,
                    True,
                    True,
                    True,
                    True,
                    True,
                    True,
                    True,
                    True
                ],
                "list_str_pattern": [
                    r"(\.|:|;)\s*$",
                    r"\(\d+\)\s*$",
                    r"^\s*(\d+\s*\.\s*)+.{3,45}\s*$",
                    r"^\s*(\d+\s*\.\s*)*\d+\s*.{3,45}\s*$",
                    r"^\s*(\d+\s*\.?)?\s*introduction\s*$",
                    r"^\s*(\d+\s*\.?)?\s*related works?\s*$",
                    r"^\s*(\d+\s*\.?)?\s*overview\s*$",
                    r"^\s*(\d+\s*\.?)?\s*algorithm\s*$",
                    r"^\s*(\d+\s*\.?)?\s*experimental results?\s*$",
                    r"^\s*(\d+\s*\.?)?\s*conclusions?\s*$",
                    r"^\s*(\d+\s*\.?)?\s*acknowledgements?\s*$",
                    r"^\s*(\d+\s*\.?)?\s*references?\s*$"
                ],
                "list_str_example": [
                    "a pen. | as follows:",
                    "1 + 1 = 2 (1)",
                    "1.2.3. Header",
                    "1.2.3 Header",
                    "1. Introduction",
                    "2. RELATED WORKS",
                    "3 Overview",
                    "4 ALGORITHM",
                    "Experimental Result",
                    "CONCLUSION",
                    "ACKNOWLEDGEMENTS",
                    "References"
                ],
                "list_str_remarks": [
                    "文末全般 行の右端にあればヒット",
                    "数式番号",
                    "見出し",
                    "数字の末尾にピリオドが無い見出し",
                    "はじめに",
                    "関連研究",
                    "概要",
                    "提案手法のアルゴリズム",
                    "実験結果",
                    "結論",
                    "謝辞",
                    "参考文献"
                ]
            },
            "ignore": {
                "bool_enabled_overall": True,
                "bool_output_hit_lines": False,
                "list_bool_enabled": [
                    True,
                    True,
                    True,
                    True,
                    True,
                    True,
                    True,
                    True
                ],
                "list_bool_ignore_case": [
                    False,
                    False,
                    False,
                    False,
                    False,
                    False,
                    False,
                    False
                ],
                "list_str_pattern": [
                    r"\s+(e\.g|et al|etc|ex)\.$",
                    r"\s+(ff|figs?|Figs?)\.$",
                    r"\s+(i\.e|illus)\.$",
                    r"\s+ll\.$",
                    r"\s+(Mr|Ms|Mrs)\.$",
                    r"\s+(pp|par|pt)\.$",
                    r"\s+sec\.$",
                    r"\[(?!.*\]).*$"
                ],
                "list_str_example": [
                    "e.g. | et al. | etc. | ex.",
                    "ff. | fig. | figs.",
                    "i.e. | illus.",
                    "ll.",
                    "Mr. | Ms. | Mrs.",
                    "pp. | par. | pt.",
                    "sec.",
                    "[Author et al. 2018;"
                ],
                "list_str_remarks": [
                    "eで始まって後ろに何か続きそうな略語",
                    "fで始まって後ろに何か続きそうな略語",
                    "iで始まって後ろに何か続きそうな略語",
                    "lで始まって後ろに何か続きそうな略語",
                    "Mr.やMs.などの確実に文末ではないもの",
                    "pで始まって後ろに何か続きそうな略語",
                    "sで始まって後ろに何か続きそうな略語",
                    "\"[\" が始まっているが \"]\" で閉じられていない箇所"
                ]
            }
        },
        "header_lines": {
            "bool_enabled_overall": True,
            "bool_output_hit_lines": False,
            "list_bool_enabled": [],
            "list_bool_ignore_case": [],
            "list_str_pattern": [
                r"^\s*(\d+\s*\.\s*)+.{3,45}\s*$",
                r"^\s*(\d+\s*\.\s*)*\d+\s*.{3,45}\s*$",
                r"^\s*(\d+\s*\.?)?\s*introduction\s*$",
                r"^\s*(\d+\s*\.?)?\s*related works?\s*$",
                r"^\s*(\d+\s*\.?)?\s*overview\s*$",
                r"^\s*(\d+\s*\.?)?\s*algorithm\s*$",
                r"^\s*(\d+\s*\.?)?\s*experimental results?\s*$",
                r"^\s*(\d+\s*\.?)?\s*conclusions?\s*$",
                r"^\s*(\d+\s*\.?)?\s*acknowledgements?\s*$",
                r"^\s*(\d+\s*\.?)?\s*references?\s*$"
            ],
            "list_str_depth_count": [
                r"\d+\s*\.\s*",  # 1.2.3. の"数字."の数が多いほど見出しが小さくなる(#の数が多くなる)
                r"\d+",
                r"^$",
                r"^$",
                r"^$",
                r"^$",
                r"^$",
                r"^$",
                r"^$",
                r"^$"
            ],
            "list_str_target_remove": [
                r"\d+\s*\.\s*",
                r"\s*(\d+\s*\.\s*)*\d+\s*",
                r"\d+\s*\.\s*",
                r"\d+\s*\.\s*",
                r"\d+\s*\.\s*",
                r"\d+\s*\.\s*",
                r"\d+\s*\.\s*",
                r"\d+\s*\.\s*",
                r"\d+\s*\.\s*",
                r"\d+\s*\.\s*"
            ],
            "list_str_max_size": [
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
            ],
            "list_str_example": [
                "1.2.3. Header",
                "1.2.3 Header 末尾にピリオドが無いパターンはあまりうまく動作しない",
                "1. Introduction",
                "2. RELATED WORKS",
                "3 Overview",
                "4 ALGORITHM",
                "Experimental Result",
                "CONCLUSION",
                "ACKNOWLEDGEMENTS",
                "References"
            ],
            "list_str_remarks": [
                "見出し",
                "数字の末尾にピリオドが無い見出し",
                "はじめに",
                "関連研究",
                "概要",
                "提案手法のアルゴリズム",
                "実験結果",
                "結論",
                "謝辞",
                "参考文献"
            ]
        }
    }
}


class Singleton(object):
    """
    このクラスを継承したクラスは、インスタンスが1つ以下しか形成されないことを保証する。
    最初にインスタンスを生成するときは普通と変わらず生成され、
    2回目以降に生成するときは1回目に生成したインスタンスを返す。
    """
    def __new__(cls, *args, **kargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super(Singleton, cls).__new__(cls)
        return cls._instance


class Settings(Singleton):
    """
    設定を扱うクラス。
    Singletonパターンを実装しているため、複数回インスタンスを生成しても同じインスタンスを返す。
    """
    def __init__(self):
        self.__settings_path = Path("settings.json")
        # settings.jsonが存在しない場合はデフォルト設定を出力
        if not self.__settings_path.exists():
            self.SaveSettings(save_default=True)

        # settings.jsonを読み取って設定を取得
        self.LoadSettings()

        # アップデートなどで設定の一部が欠けているときはデフォルト設定で追加
        lack_of_settings = Settings.SettingComplement(self.settings, default_settings)

        # 設定が欠けていた場合はsettings.jsonに保存し直す
        if lack_of_settings:
            self.SaveSettings()

    @staticmethod
    def SettingComplement(settings, def_settings):
        """
        現在の設定とデフォルト設定を比べ、欠けている要素があればデフォルト設定で補完する

        Args:
            settings (dict): 現在の設定
            def_settings (dict): デフォルト設定

        Returns:
            bool: 欠けている設定があったか
        """
        lack_of_settings = False
        for s in def_settings.keys():
            # デフォルト設定において、一つ下の階層も辞書だった場合
            if isinstance(def_settings[s], dict):
                # 現在の設定でセクションが欠けていれば追加
                if not (s in settings) or not isinstance(settings[s], dict):
                    settings[s] = {}
                    lack_of_settings = True
                # 現在の設定でセクションがあってもその中の要素が欠けているかもしれないので、
                # 一つ下の階層で再帰的に繰り返す
                lack_of_settings |= Settings.SettingComplement(settings[s], def_settings[s])
            # デフォルト設定において、ひとつ下の階層に要素があった場合
            else:
                # 現在の設定において要素が欠けていれば追加
                # リストなどもあるため、デフォルト設定の改ざんを防ぐ目的でdeepcopyを用いる
                if not (s in settings):
                    settings[s] = deepcopy(def_settings[s])
                    lack_of_settings = True

        return lack_of_settings

    def SaveSettings(self, save_default=False):
        """
        設定を保存する

        Args:
            save_default (bool, optional): デフォルト設定を保存するか
        """
        with open(str(self.__settings_path), "w", encoding="utf-8") as f:
            json.dump(
                default_settings if save_default else self.settings,
                f,
                ensure_ascii=False,
                indent=4,
                separators=(",", ": ")
            )

    def LoadSettings(self, load_default=False):
        """
        設定を読み込む

        Args:
            load_default (bool, optional): デフォルト設定を読み込むか
        """
        if load_default:
            self.settings = deepcopy(default_settings)
            return

        with open(str(self.__settings_path), "r", encoding="utf-8") as f:
            self.settings = json.load(f)

    @property
    def TargetLanguage(self):
        return language_dict[self.settings["main_window"]["str_target_lang"]]
