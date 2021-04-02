import json

from copy import deepcopy
from data import default_settings, language_dict
from pathlib import Path
from utils import ClassProperty, classproperty


class Settings(metaclass=ClassProperty):
    """
    設定を扱うクラス
    """
    __settings = None
    __settings_path = Path("settings.json")

    @classproperty
    def settings(cls):
        if not (cls.__settings is None):
            return cls.__settings

        # settings.jsonが存在しない場合はデフォルト設定を出力
        if not cls.__settings_path.exists():
            cls.SaveSettings(save_default=True)

        # settings.jsonを読み取って設定を取得
        cls.LoadSettings()

        # アップデートなどで設定の一部が欠けているときはデフォルト設定で追加
        lack_of_settings = Settings.SettingComplement(cls.__settings, default_settings)

        # 設定が欠けていた場合はsettings.jsonに保存し直す
        if lack_of_settings:
            cls.SaveSettings()

        return cls.__settings

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

    @classmethod
    def SaveSettings(cls, save_default=False):
        """
        設定を保存する

        Args:
            save_default (bool, optional): デフォルト設定を保存するか
        """
        with open(str(cls.__settings_path), "w", encoding="utf-8") as f:
            json.dump(
                default_settings if save_default else cls.settings,
                f,
                ensure_ascii=False,
                indent=4,
                separators=(",", ": ")
            )

    @classmethod
    def LoadSettings(cls, load_default=False):
        """
        設定を読み込む

        Args:
            load_default (bool, optional): デフォルト設定を読み込むか
        """
        if load_default:
            cls.__settings = deepcopy(default_settings)
            return

        with open(str(cls.__settings_path), "r", encoding="utf-8") as f:
            cls.__settings = json.load(f)

    @classproperty
    def TargetLanguage(cls):
        return language_dict[cls.settings["main_window"]["str_target_lang"]]
