import re
import selenium.common.exceptions as sce
import wx

from enum import Enum
from selenium import webdriver
from sys import stderr
from time import sleep
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager


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


class Browser(Enum):
    CHROME = "Chrome"
    EDGE = "Edge"
    FIREFOX = "FireFox"


# DeepLでの翻訳を管理する
class DeepLManager:

    # WebDriverを自動でダウンロードして、プログラム制御可能なWebブラウザを開く
    def __init__(self, browser):
        try:
            if browser == Browser.CHROME.value:
                self.__webDriver = webdriver.Chrome(ChromeDriverManager().install())
            elif browser == Browser.EDGE.value:
                self.__webDriver = webdriver.Edge(EdgeChromiumDriverManager().install())
            elif browser == Browser.FIREFOX.value:
                # Firefoxはなぜかexecutable_pathで指定しないとエラーが起きる
                self.__webDriver = webdriver.Firefox(executable_path=GeckoDriverManager().install())
            else:
                self.__invalidBrowser()
        except sce.WebDriverException:
            wx.LogError(browser + "がインストールされていません。\n\n" + browser + "をインストールするか、インストール済みの他の対応Webブラウザを選択してください。")
            exit(1)

    def __invalidBrowser(self):
        wx.LogError("ブラウザの指定が無効な値です。")
        exit(1)

    # DeepLのタブを開く
    def openDeepLPage(self):
        # 今のタブがDeepLなら何もしない
        try:
            if self.__webDriver.current_url == "https://www.deepl.com/translator":
                return
        except AttributeError:
            print("Error: webDriver is not initiated.", file=stderr)
            exit(1)

        # 他のタブにそのページがあるならそれを開いて終わり
        for tab in self.__webDriver.window_handles:
            self.__webDriver.switch_to.window(tab)
            if self.__webDriver.current_url == "https://www.deepl.com/translator":
                return

        # もしDeepLのページを開いているタブが無ければ新たに開く
        # 新しいタブを開き、そのタブに移動
        self.__webDriver.execute_script("window.open('', '_blank');")
        self.__webDriver.switch_to.window(self.__webDriver.window_handles[-1])
        # DeepLに接続
        self.__webDriver.get("https://www.deepl.com/translator")

    # 渡された文を翻訳にかけ、訳文を返す
    def translate(self, text, lang="ja-JA", first_wait_secs=10, wait_secs_max=60):
        # DeepLのページが開かれていなければ開く
        self.openDeepLPage()

        # 訳文の言語を選択するタブを開く
        self.__webDriver.find_element_by_xpath("//button[@dl-test='translator-target-lang-btn']").click()
        # 訳文の言語のボタンを押す
        self.__webDriver.find_element_by_xpath("//button[@dl-test='translator-lang-option-" + lang + "']").click()

        # 原文の入力欄を取得
        source_textarea = self.__webDriver.find_element_by_css_selector(
            "textarea.lmt__textarea.lmt__source_textarea.lmt__textarea_base_style")
        # Ctrl+Aで全選択し、前の文を消しつつ原文を入力
        source_textarea.clear()
        source_textarea.send_keys(text)

        # 最初に5秒待つ
        sleep(first_wait_secs)

        # 翻訳の進行度を示すポップアップが無ければ翻訳完了と見なす
        # 制限時間内に翻訳が終了しなければ翻訳失敗と見なす
        wait_secs_sub = int(wait_secs_max - first_wait_secs)
        for i in range(wait_secs_sub):
            try:
                # 通常時はdiv.lmt_progress_popupだが、ポップアップが可視化するときは
                # lmt_progress_popup--visible(_2)が追加される
                _ = self.__webDriver.find_element_by_css_selector(
                    "div.lmt__progress_popup.lmt__progress_popup--visible.lmt__progress_popup--visible_2")
            except sce.NoSuchElementException:
                # ポップアップが無く、かつ[...]が無ければ翻訳完了として抜け出す
                translated = self.__webDriver.find_element_by_css_selector(
                    "textarea.lmt__textarea.lmt__target_textarea.lmt__textarea_base_style").get_property("value")
                if not re.search(r"\[\.\.\.\]", translated):
                    break
            # ポップアップがあり、かつ制限時間内ならばもう1秒待つ
            if i < wait_secs_sub - 1:
                sleep(1.0)
                continue
            else:
                # 制限時間を過ぎたら失敗
                # 段落と同じ数だけメッセージを生成
                num_pars = len(text.splitlines())
                messages = ["(翻訳に" + str(wait_secs_max) + "秒以上を要するため失敗と見なしました)"] + ["" for _ in range(num_pars - 1)]
                return "\n".join(messages)

        # 訳文の出力欄を取得し、訳文を取得
        translated = self.__webDriver.find_element_by_css_selector(
            "textarea.lmt__textarea.lmt__target_textarea.lmt__textarea_base_style").get_property("value")

        return translated

    # ブラウザのウィンドウを閉じる
    def closeWindow(self):
        self.__webDriver.quit()
