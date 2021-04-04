from enum import Enum


class MainWindow_MenuBar_Menu(Enum):
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


class Browser(Enum):
    CHROME = "Chrome"
    EDGE = "Edge"
    FIREFOX = "FireFox"


class Target_Lang(Enum):
    BULGARIAN = "ブルガリア語"
    CHINESE_SIMPLIFIED = "中国語(簡体字)"
    CZECH = "チェコ語"
    DANISH = "デンマーク語"
    DUTCH = "オランダ語"
    ENGLISH_GB = "英語(イギリス)"
    ENGLISH_US = "英語(アメリカ)"
    ESTONIAN = "エストニア語"
    FINNISH = "フィンランド語"
    FRENCH = "フランス語"
    GERMAN = "ドイツ語"
    GREEK = "ギリシャ語"
    HUNGARIAN = "ハンガリー語"
    ITALIAN = "イタリア語"
    JAPANESE = "日本語"
    LATVIAN = "ラトビア語"
    LITHUANIAN = "リトアニア語"
    POLISH = "ポーランド語"
    PORTUGUESE = "ポルトガル語"
    PORTUGUESE_BR = "ポルトガル語(ブラジル)"
    ROMANIAN = "ルーマニア語"
    RUSSIAN = "ロシア語"
    SLOVAK = "スロバキア語"
    SLOVENIAN = "スロベニア語"
    SPANISH = "スペイン語"
    SWEDISH = "スウェーデン語"


language_dict = {
    Target_Lang.BULGARIAN.value: "bg-BG",
    Target_Lang.CHINESE_SIMPLIFIED.value: "zh-ZH",
    Target_Lang.CZECH.value: "cs-CS",
    Target_Lang.DANISH.value: "da-DA",
    Target_Lang.DUTCH.value: "nl-NL",
    Target_Lang.ENGLISH_GB.value: "en-GB",
    Target_Lang.ENGLISH_US.value: "en-US",
    Target_Lang.ESTONIAN.value: "et-ET",
    Target_Lang.FINNISH.value: "fi-FI",
    Target_Lang.FRENCH.value: "fr-FR",
    Target_Lang.GERMAN.value: "de-DE",
    Target_Lang.GREEK.value: "el-EL",
    Target_Lang.HUNGARIAN.value: "hu-HU",
    Target_Lang.ITALIAN.value: "it-IT",
    Target_Lang.JAPANESE.value: "ja-JA",
    Target_Lang.LATVIAN.value: "lv-LV",
    Target_Lang.LITHUANIAN.value: "lt-LT",
    Target_Lang.POLISH.value: "pl-PL",
    Target_Lang.PORTUGUESE.value: "pt-PT",
    Target_Lang.PORTUGUESE_BR.value: "pt-BR",
    Target_Lang.ROMANIAN.value: "ro-RO",
    Target_Lang.RUSSIAN.value: "ru-RU",
    Target_Lang.SLOVAK.value: "sk-SK",
    Target_Lang.SLOVENIAN.value: "sl-SL",
    Target_Lang.SPANISH.value: "es-ES",
    Target_Lang.SWEDISH.value: "sv-SV"
}


default_settings = {
    "str_target_lang": Target_Lang.JAPANESE.value,
    "str_web_browser": Browser.CHROME.value,
    "bool_minimize_translation_window": True,
    "bool_add_target_return": True,
    "bool_output_type_markdown": True,
    "bool_output_source": True,
    "bool_source_as_comment": True,
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
                True
            ],
            "list_bool_ignore_case": [
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
                "見出し",
                "数字の末尾にピリオドが無い見出し あまりうまく動作しない",
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
