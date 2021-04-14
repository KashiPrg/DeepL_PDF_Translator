import json

from abc import ABCMeta, abstractmethod
from copy import deepcopy
from data import default_settings, language_dict
from pathlib import Path


settings_dict = None
settings_path = Path("settings.json")


def settings():
    if not (settings_dict is None):
        return settings_dict

    # settings.jsonが存在しない場合はデフォルト設定を出力
    if not settings_path.exists():
        Settings.SaveSettings(save_default=True)

    # settings.jsonを読み取って設定を取得
    Settings.LoadSettings()

    # アップデートなどで設定の一部が欠けているときはデフォルト設定で追加
    lack_of_settings = SettingComplement(settings_dict, default_settings)

    # 設定が欠けていた場合はsettings.jsonに保存し直す
    if lack_of_settings:
        Settings.SaveSettings()

    return settings_dict


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
            lack_of_settings |= SettingComplement(settings[s], def_settings[s])
        # デフォルト設定において、ひとつ下の階層に要素があった場合
        else:
            # 現在の設定において要素が欠けていれば追加
            # リストなどもあるため、デフォルト設定の改ざんを防ぐ目的でdeepcopyを用いる
            if not (s in settings):
                settings[s] = deepcopy(def_settings[s])
                lack_of_settings = True

    return lack_of_settings


class ConditionLines(metaclass=ABCMeta):
    """
    各種正規表現のための抽象クラス
    """
    @abstractmethod
    def _subsettings(self):
        """
        該当する正規表現の設定までツリーを下ったものを返すよう実装する

        つまりエイリアシング

        例： return settings()["regular_expressions"]["start_lines"]
        """
        pass

    # この種類の正規表現の全体的なフラグ
    @property
    def enabled_overall(self):
        return self._subsettings()["bool_enabled_overall"]

    @enabled_overall.setter
    def enabled_overall(self, bool_enabled_overall):
        self._subsettings()["bool_enabled_overall"] = bool_enabled_overall

    # この種類の正規表現にヒットした箇所を出力するか
    @property
    def output_hit_lines(self):
        return self._subsettings()["bool_output_hit_lines"]

    @output_hit_lines.setter
    def output_hit_lines(self, bool_output_hit_lines):
        self._subsettings()["bool_output_hit_lines"] = bool_output_hit_lines

    @property
    def enabled_list(self):
        return self._subsettings()["list_bool_enabled"]

    @enabled_list.setter
    def enabled_list(self, list_bool_enabled):
        self._subsettings()["list_bool_enabled"] = list_bool_enabled

    @property
    def ignorecase_list(self):
        return self._subsettings()["list_bool_ignore_case"]

    @ignorecase_list.setter
    def ignorecase_list(self, list_bool_ignore_case):
        self._subsettings()["list_bool_ignore_case"] = list_bool_ignore_case

    @property
    def pattern_list(self):
        return self._subsettings()["list_str_pattern"]

    @pattern_list.setter
    def pattern_list(self, list_str_pattern):
        self._subsettings()["list_str_pattern"] = list_str_pattern

    @property
    def example_list(self):
        return self._subsettings()["list_str_example"]

    @example_list.setter
    def example_list(self, list_str_example):
        self._subsettings()["list_str_example"] = list_str_example

    @property
    def remarks_list(self):
        return self._subsettings()["list_str_remarks"]

    @remarks_list.setter
    def remarks_list(self, list_str_remarks):
        self._subsettings()["list_str_remarks"] = list_str_remarks


class Settings():
    """
    設定を扱うクラス
    """

    # エイリアシング
    @property
    def __settings(self):
        return settings()

    @staticmethod
    def SaveSettings(save_default=False):
        """
        設定を保存する

        Args:
            save_default (bool, optional): デフォルト設定を保存するか
        """
        with open(str(settings_path), "w", encoding="utf-8") as f:
            json.dump(
                default_settings if save_default else settings(),
                f,
                ensure_ascii=False,
                indent=4,
                separators=(",", ": ")
            )

    @staticmethod
    def LoadSettings(load_default=False):
        """
        設定を読み込む

        Args:
            load_default (bool, optional): デフォルト設定を読み込むか
        """
        global settings_dict

        if load_default:
            settings_dict = deepcopy(default_settings)
            return

        with open(str(settings_path), "r", encoding="utf-8") as f:
            settings_dict = json.load(f)

    # 翻訳先の言語
    @property
    def target_language(self):
        return self.__settings["str_target_lang"]

    @target_language.setter
    def target_language(self, str_language):
        self.__settings["str_target_lang"] = str_language

    @property
    def target_language_for_translate(self):
        return language_dict[self.__settings["str_target_lang"]]

    # 使用ウェブブラウザ
    @property
    def web_browser(self):
        return self.__settings["str_web_browser"]

    @web_browser.setter
    def web_browser(self, str_web_browser):
        self.__settings["str_web_browser"] = str_web_browser

    # 翻訳ウインドウを自動で最小化するか
    @property
    def minimize_translation_window(self):
        return self.__settings["bool_minimize_translation_window"]

    @minimize_translation_window.setter
    def minimize_translation_window(self, bool_minimize_translation_window):
        self.__settings["bool_minimize_translation_window"] = bool_minimize_translation_window

    # 翻訳文を一文ごとに改行するか
    @property
    def add_target_return(self):
        return self.__settings["bool_add_target_return"]

    @add_target_return.setter
    def add_target_return(self, bool_add_target_return):
        self.__settings["bool_add_target_return"] = bool_add_target_return

    # 出力をMarkdown式にするか
    @property
    def output_type_markdown(self):
        return self.__settings["bool_output_type_markdown"]

    @output_type_markdown.setter
    def output_type_markdown(self, bool_output_type_markdown):
        self.__settings["bool_output_type_markdown"] = bool_output_type_markdown

    # 原文を出力するか
    @property
    def output_source(self):
        return self.__settings["bool_output_source"]

    @output_source.setter
    def output_source(self, bool_output_source):
        self.__settings["bool_output_source"] = bool_output_source

    # Markdown形式において、原文をコメントとして出力するか
    @property
    def source_as_comment(self):
        return self.__settings["bool_source_as_comment"]

    @source_as_comment.setter
    def source_as_comment(self, bool_source_as_comment):
        self.__settings["bool_source_as_comment"] = bool_source_as_comment

    class RegularExpressions:
        """
        正規表現まわりの設定を扱うクラス
        """
        def __subsettings(self):
            return settings()["regular_expressions"]

        @property
        def show_markdown_settings(self):
            return self.__subsettings()["bool_show_markdown_settings"]

        @show_markdown_settings.setter
        def show_markdown_settings(self, bool_show_markdown_settings):
            self.__subsettings()["bool_show_markdown_settings"] = bool_show_markdown_settings

        class StartLines(ConditionLines):
            def _subsettings(self):
                return settings()["regular_expressions"]["start_lines"]

        class EndLines(ConditionLines):
            def _subsettings(self):
                return settings()["regular_expressions"]["end_lines"]

        class IgnoreLines(ConditionLines):
            def _subsettings(self):
                return settings()["regular_expressions"]["ignore_lines"]

        class ReplaceParts:
            class Standard(ConditionLines):
                def _subsettings(self):
                    return settings()["regular_expressions"]["replace_parts"]["standard"]

                @property
                def target_list(self):
                    return self._subsettings()["list_str_target"]

                @target_list.setter
                def target_list(self, list_str_target):
                    self._subsettings()["list_str_target"] = list_str_target

            class Markdown(ConditionLines):
                def _subsettings(self):
                    return settings()["regular_expressions"]["replace_parts"]["markdown"]

                @property
                def target_list(self):
                    return self._subsettings()["list_str_target"]

                @target_list.setter
                def target_list(self, list_str_target):
                    self._subsettings()["list_str_target"] = list_str_target

        class ChartStartLines(ConditionLines):
            def _subsettings(self):
                return settings()["regular_expressions"]["chart_start_lines"]

        class ReturnLines:
            class Possibility(ConditionLines):
                def _subsettings(self):
                    return settings()["regular_expressions"]["return_lines"]["possibility"]

            class Ignore(ConditionLines):
                def _subsettings(self):
                    return settings()["regular_expressions"]["return_lines"]["ignore"]

        class HeaderLines(ConditionLines):
            def _subsettings(self):
                return settings()["regular_expressions"]["header_lines"]

            @property
            def depth_count_list(self):
                return self._subsettings()["list_str_depth_count"]

            @depth_count_list.setter
            def depth_count_list(self, list_str_depth_count):
                self._subsettings()["list_str_depth_count"] = list_str_depth_count

            @property
            def target_remove_list(self):
                return self._subsettings()["list_str_target_remove"]

            @target_remove_list.setter
            def target_remove_list(self, list_str_target_remove):
                self._subsettings()["list_str_target_remove"] = list_str_target_remove

            @property
            def max_size_list(self):
                return self._subsettings()["list_int_max_size"]

            @max_size_list.setter
            def max_size_list(self, list_int_max_size):
                self._subsettings()["list_int_max_size"] = list_int_max_size
