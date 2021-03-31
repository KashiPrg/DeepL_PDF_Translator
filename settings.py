import json

from deeplmanager import Target_Lang, Browser
from enum import Enum
from pathlib import Path


class SectionNames(Enum):
    MAIN_WINDOW = "main_window"


class MainWindowSettings(Enum):
    STR_TARGET_LANG = "target_lang"
    STR_WEB_BROWSER = "web_browser"
    BOOL_ADD_TARGET_RETURN = "add_target_return"
    BOOL_RETURN_TYPE_MARKDOWN = "return_type_markdown"
    BOOL_OUTPUT_SOURCE = "output_source"
    BOOL_SOURCE_AS_COMMENT = "source_as_comment"


default_settings = {
    SectionNames.MAIN_WINDOW.value: {
        MainWindowSettings.STR_TARGET_LANG.value: Target_Lang.JAPANESE.value,
        MainWindowSettings.STR_WEB_BROWSER.value: Browser.CHROME.value,
        MainWindowSettings.BOOL_ADD_TARGET_RETURN.value: True,
        MainWindowSettings.BOOL_RETURN_TYPE_MARKDOWN.value: True,
        MainWindowSettings.BOOL_OUTPUT_SOURCE.value: True,
        MainWindowSettings.BOOL_SOURCE_AS_COMMENT.value: True
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
            with open(str(self.__settings_path), "w", encoding="utf-8") as f:
                json.dump(default_settings, f)

        # settings.jsonを読み取って設定を取得
        with open(str(self.__settings_path), "r", encoding="utf-8") as f:
            self.__settings = json.load(f)

        # アップデートなどで設定の一部が欠けているときはデフォルト設定で追加
        lack_of_settings = False
        for sec_name in default_settings.keys():
            # セクションが欠けているときはセクションを追加
            if not (sec_name in self.__settings):
                self.__settings[sec_name] = {}
                lack_of_settings = True
            for setting_name in default_settings[sec_name].keys():
                # セクションの中の設定が欠けている場合は追加
                if not (setting_name in self.__settings[sec_name]):
                    self.__settings[sec_name][setting_name] = default_settings[sec_name][setting_name]
                    lack_of_settings = True

        # 設定が欠けていた場合はsettings.jsonに保存し直す
        if lack_of_settings:
            with open(str(self.__settings_path), "w", encoding="utf-8") as f:
                json.dump(self.__settings, f)

    def GetSetting(self, section, key):
        """
        設定の値を取得する

        Args:
            section (string or SectionNames)): 設定のセクション名
            key (string, or Settings e.g. MainWindowSettings): 設定名
        """
        # sectionやkeyがEnumの値を取っているならstrに変換
        if not isinstance(section, str):
            section = section.value
        if not isinstance(key, str):
            key = key.value

        return self.__settings[section][key]

    def SetSetting(self, section, key, value, save_on_change=True):
        """
        設定の値を変更する

        Args:
            section (string or SectionNames): 設定のセクション名
            key (string, or Settings e.g. MainWindowSettings): 設定名
            value (type of the setting): 設定する値
            save_on_change (bool, optional): 設定を変更したときにsettings.jsonに保存するか

        Raises:
            TypeError: 設定の値の型と、設定する値の型が異なる場合に発生
        """
        # sectionやkeyがEnumの値を取っているならstrに変換
        if not isinstance(section, str):
            section = section.value
        if not isinstance(key, str):
            key = key.value

        # 元の設定の値の型と一致しているなら値を変更し、型が異なるなら例外発生
        if isinstance(value, type(default_settings[section][key])):
            self.__settings[section][key] = value
        else:
            raise TypeError("The type of a value of " + section + "." + key + " and the type of a value to be set are different.")

        if save_on_change:
            with open(str(self.__settings_path), "w", encoding="utf-8") as f:
                json.dump(self.__settings, f)

    def GetMainWindowSetting(self, key):
        """
        メインウインドウ(アプリを立ち上げて最初に出るウインドウ)の設定の値を取得する

        Args:
            key (string or MainWindowSettings): 設定の名前

        Returns:
            設定の値
        """
        return self.GetSetting(SectionNames.MAIN_WINDOW.value, key)

    def SetMainWindowSetting(self, key, value, save_on_change=True):
        """
        メインウインドウ(アプリを立ち上げて最初に出るウインドウ)の設定の値を変更する

        Args:
            key (string or MainWindowSettings): 設定の名前
            value (type of the setting): 設定する値
            save_on_change (bool, optional): 設定を変更したときにsettings.jsonに保存するか
        """
        self.SetSetting(SectionNames.MAIN_WINDOW.value, key, value, save_on_change)
