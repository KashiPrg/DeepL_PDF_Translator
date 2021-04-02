import json

from copy import deepcopy
from data import default_settings, language_dict
from pathlib import Path
from utils import ClassProperty, classproperty


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


class Settings(metaclass=ClassProperty):
    """
    設定を扱うクラス
    """

    # エイリアシング
    @classproperty
    def __settings(cls):
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
    @classproperty
    def target_language(cls):
        return cls.__settings["str_target_lang"]

    @target_language.setter
    def target_language(cls, str_language):
        cls.__settings["str_target_lang"] = str_language

    @classproperty
    def target_language_for_translate(cls):
        return language_dict[cls.__settings["str_target_lang"]]

    # 使用ウェブブラウザ
    @classproperty
    def web_browser(cls):
        return cls.__settings["str_web_browser"]

    @web_browser.setter
    def web_browser(cls, str_web_browser):
        cls.__settings["str_web_browser"] = str_web_browser

    # 翻訳文を一文ごとに改行するか
    @classproperty
    def add_target_return(cls):
        return cls.__settings["bool_add_target_return"]

    @add_target_return.setter
    def add_target_return(cls, bool_add_target_return):
        cls.__settings["bool_add_target_return"] = bool_add_target_return

    # 出力をMarkdown式にするか
    @classproperty
    def output_type_markdown(cls):
        return cls.__settings["bool_output_type_markdown"]

    @output_type_markdown.setter
    def output_type_markdown(cls, bool_output_type_markdown):
        cls.__settings["bool_output_type_markdown"] = bool_output_type_markdown

    # 原文を出力するか
    @classproperty
    def output_source(cls):
        return cls.__settings["bool_output_source"]

    @output_source.setter
    def output_source(cls, bool_output_source):
        cls.__settings["bool_output_source"] = bool_output_source

    # Markdown形式において、原文をコメントとして出力するか
    @classproperty
    def source_as_comment(cls):
        return cls.__settings["bool_source_as_comment"]

    @source_as_comment.setter
    def source_as_comment(cls, bool_source_as_comment):
        cls.__settings["bool_source_as_comment"] = bool_source_as_comment

    class RegularExpressions(metaclass=ClassProperty):
        """
        正規表現まわりの設定を扱うクラス
        """
        # エイリアシング
        @classproperty
        def __subsettings(cls):
            return settings()["regular_expressions"]

        class StartLines(metaclass=ClassProperty):
            # エイリアシング
            @classproperty
            def __subsettings(cls):
                return settings()["regular_expressions"]["start_lines"]

            # この種類の正規表現の全体的なフラグ
            @classproperty
            def enabled_overall(cls):
                return cls.__subsettings["bool_enabled_overall"]

            @enabled_overall.setter
            def enabled_overall(cls, bool_enabled_overall):
                cls.__subsettings["bool_enabled_overall"] = bool_enabled_overall

            # この種類の正規表現にヒットした箇所を出力するか
            @classproperty
            def output_hit_lines(cls):
                return cls.__subsettings["bool_output_hit_lines"]

            @output_hit_lines.setter
            def output_hit_lines(cls, bool_output_hit_lines):
                cls.__subsettings["bool_output_hit_lines"] = bool_output_hit_lines

        class EndLines(metaclass=ClassProperty):
            # エイリアシング
            @classproperty
            def __subsettings(cls):
                return settings()["regular_expressions"]["end_lines"]

            # この種類の正規表現の全体的なフラグ
            @classproperty
            def enabled_overall(cls):
                return cls.__subsettings["bool_enabled_overall"]

            @enabled_overall.setter
            def enabled_overall(cls, bool_enabled_overall):
                cls.__subsettings["bool_enabled_overall"] = bool_enabled_overall

            # この種類の正規表現にヒットした箇所を出力するか
            @classproperty
            def output_hit_lines(cls):
                return cls.__subsettings["bool_output_hit_lines"]

            @output_hit_lines.setter
            def output_hit_lines(cls, bool_output_hit_lines):
                cls.__subsettings["bool_output_hit_lines"] = bool_output_hit_lines

        class IgnoreLines(metaclass=ClassProperty):
            # エイリアシング
            @classproperty
            def __subsettings(cls):
                return settings()["regular_expressions"]["ignore_lines"]

            # この種類の正規表現の全体的なフラグ
            @classproperty
            def enabled_overall(cls):
                return cls.__subsettings["bool_enabled_overall"]

            @enabled_overall.setter
            def enabled_overall(cls, bool_enabled_overall):
                cls.__subsettings["bool_enabled_overall"] = bool_enabled_overall

            # この種類の正規表現にヒットした箇所を出力するか
            @classproperty
            def output_hit_lines(cls):
                return cls.__subsettings["bool_output_hit_lines"]

            @output_hit_lines.setter
            def output_hit_lines(cls, bool_output_hit_lines):
                cls.__subsettings["bool_output_hit_lines"] = bool_output_hit_lines

        class ReplaceParts(metaclass=ClassProperty):
            # エイリアシング
            @classproperty
            def __subsettings(cls):
                return settings()["regular_expressions"]["replace_parts"]

            class Standard(metaclass=ClassProperty):
                # エイリアシング
                @classproperty
                def __subsettings(cls):
                    return settings()["regular_expressions"]["replace_parts"]["standard"]

                # この種類の正規表現の全体的なフラグ
                @classproperty
                def enabled_overall(cls):
                    return cls.__subsettings["bool_enabled_overall"]

                @enabled_overall.setter
                def enabled_overall(cls, bool_enabled_overall):
                    cls.__subsettings["bool_enabled_overall"] = bool_enabled_overall

                # この種類の正規表現にヒットした箇所を出力するか
                @classproperty
                def output_hit_lines(cls):
                    return cls.__subsettings["bool_output_hit_lines"]

                @output_hit_lines.setter
                def output_hit_lines(cls, bool_output_hit_lines):
                    cls.__subsettings["bool_output_hit_lines"] = bool_output_hit_lines

            class Markdown(metaclass=ClassProperty):
                # エイリアシング
                @classproperty
                def __subsettings(cls):
                    return settings()["regular_expressions"]["replace_parts"]["markdown"]

                # この種類の正規表現の全体的なフラグ
                @classproperty
                def enabled_overall(cls):
                    return cls.__subsettings["bool_enabled_overall"]

                @enabled_overall.setter
                def enabled_overall(cls, bool_enabled_overall):
                    cls.__subsettings["bool_enabled_overall"] = bool_enabled_overall

                # この種類の正規表現にヒットした箇所を出力するか
                @classproperty
                def output_hit_lines(cls):
                    return cls.__subsettings["bool_output_hit_lines"]

                @output_hit_lines.setter
                def output_hit_lines(cls, bool_output_hit_lines):
                    cls.__subsettings["bool_output_hit_lines"] = bool_output_hit_lines

        class ChartStartLines(metaclass=ClassProperty):
            # エイリアシング
            @classproperty
            def __subsettings(cls):
                return settings()["regular_expressions"]["chart_start_lines"]

            # この種類の正規表現の全体的なフラグ
            @classproperty
            def enabled_overall(cls):
                return cls.__subsettings["bool_enabled_overall"]

            @enabled_overall.setter
            def enabled_overall(cls, bool_enabled_overall):
                cls.__subsettings["bool_enabled_overall"] = bool_enabled_overall

            # この種類の正規表現にヒットした箇所を出力するか
            @classproperty
            def output_hit_lines(cls):
                return cls.__subsettings["bool_output_hit_lines"]

            @output_hit_lines.setter
            def output_hit_lines(cls, bool_output_hit_lines):
                cls.__subsettings["bool_output_hit_lines"] = bool_output_hit_lines

        class ReturnLines(metaclass=ClassProperty):
            # エイリアシング
            @classproperty
            def __subsettings(cls):
                return settings()["regular_expressions"]["return_lines"]

            class Possibility(metaclass=ClassProperty):
                # エイリアシング
                @classproperty
                def __subsettings(cls):
                    return settings()["regular_expressions"]["return_lines"]["possibility"]

                # この種類の正規表現の全体的なフラグ
                @classproperty
                def enabled_overall(cls):
                    return cls.__subsettings["bool_enabled_overall"]

                @enabled_overall.setter
                def enabled_overall(cls, bool_enabled_overall):
                    cls.__subsettings["bool_enabled_overall"] = bool_enabled_overall

                # この種類の正規表現にヒットした箇所を出力するか
                @classproperty
                def output_hit_lines(cls):
                    return cls.__subsettings["bool_output_hit_lines"]

                @output_hit_lines.setter
                def output_hit_lines(cls, bool_output_hit_lines):
                    cls.__subsettings["bool_output_hit_lines"] = bool_output_hit_lines

            class Ignore(metaclass=ClassProperty):
                # エイリアシング
                @classproperty
                def __subsettings(cls):
                    return settings()["regular_expressions"]["return_lines"]["ignore"]

                # この種類の正規表現の全体的なフラグ
                @classproperty
                def enabled_overall(cls):
                    return cls.__subsettings["bool_enabled_overall"]

                @enabled_overall.setter
                def enabled_overall(cls, bool_enabled_overall):
                    cls.__subsettings["bool_enabled_overall"] = bool_enabled_overall

                # この種類の正規表現にヒットした箇所を出力するか
                @classproperty
                def output_hit_lines(cls):
                    return cls.__subsettings["bool_output_hit_lines"]

                @output_hit_lines.setter
                def output_hit_lines(cls, bool_output_hit_lines):
                    cls.__subsettings["bool_output_hit_lines"] = bool_output_hit_lines

        class HeaderLines(metaclass=ClassProperty):
            # エイリアシング
            @classproperty
            def __subsettings(cls):
                return settings()["regular_expressions"]["header_lines"]

            # この種類の正規表現の全体的なフラグ
            @classproperty
            def enabled_overall(cls):
                return cls.__subsettings["bool_enabled_overall"]

            @enabled_overall.setter
            def enabled_overall(cls, bool_enabled_overall):
                cls.__subsettings["bool_enabled_overall"] = bool_enabled_overall

            # この種類の正規表現にヒットした箇所を出力するか
            @classproperty
            def output_hit_lines(cls):
                return cls.__subsettings["bool_output_hit_lines"]

            @output_hit_lines.setter
            def output_hit_lines(cls, bool_output_hit_lines):
                cls.__subsettings["bool_output_hit_lines"] = bool_output_hit_lines
