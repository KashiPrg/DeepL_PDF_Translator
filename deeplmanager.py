import platform
import re
import selenium.common.exceptions as sce
import wx

from enum import Enum
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from sys import stderr
from time import sleep


class Browser(Enum):
    CHROME = "Chrome"
    EDGE = "Edge"
    FIREFOX = "FireFox"


# DeepLでの翻訳を管理する
class DeepLManager:
    webDriverURLs = {
        Browser.CHROME.value:
            "https://sites.google.com/a/chromium.org/chromedriver/downloads",
        Browser.EDGE.value:
            "https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/#downloads",
        Browser.FIREFOX.value:
            "https://github.com/mozilla/geckodriver/releases"
    }

    def __init__(self, browser):
        try:
            if platform.system() == "Windows":
                # Windowsなら実行ファイルに拡張子が付く
                if browser == Browser.CHROME.value:
                    self.__webDriver = webdriver.Chrome("./drivers/chromedriver.exe")
                elif browser == Browser.EDGE.value:
                    self.__webDriver = webdriver.Edge("./drivers/msedgedriver.exe")
                elif browser == Browser.FIREFOX.value:
                    # Firefoxはなぜかexecutable_pathで指定しないとエラーが起きる
                    self.__webDriver = webdriver.Firefox(executable_path="./drivers/geckodriver.exe")
                else:
                    self.__invalidBrowser()
            else:
                # MacやLinux(Windows以外)なら拡張子は付かない
                if browser == Browser.CHROME.value:
                    self.__webDriver = webdriver.Chrome("./drivers/chromedriver")
                elif browser == Browser.EDGE.value:
                    self.__webDriver = webdriver.Edge("./drivers/msedgedriver")
                elif browser == Browser.FIREFOX.value:
                    self.__webDriver = webdriver.Firefox(executable_path="./drivers/geckodriver")
                else:
                    self.__invalidBrowser()
        except sce.WebDriverException:
            wx.LogError(browser + "、または" + browser + "のWebDriverがインストールされていません。\n\n" + browser + "をインストールするか、" + browser + "のWebDriverを\n" + self.webDriverURLs[browser] + " から入手し、driversディレクトリに配置してください。")
            exit(1)

    def __invalidBrowser(self):
        wx.LogError("ブラウザの指定が無効な値です。")
        exit(1)

    # DeepLのタブを開く
    def openDeepLPage(self):
        # 今のタブがDeepLなら何もしない
        try:
            if self.__webDriver.current_url == \
               "https://www.deepl.com/translator":
                return
        except AttributeError:
            print("Error: webDriver is not initiated.", file=stderr)
            exit(1)

        # 他のタブにそのページがあるならそれを開いて終わり
        for tab in self.__webDriver.window_handles:
            self.__webDriver.switch_to.window(tab)
            if self.__webDriver.current_url == \
               "https://www.deepl.com/translator":
                return

        # もしDeepLのページを開いているタブが無ければ新たに開く
        # 新しいタブを開き、そのタブに移動
        self.__webDriver.execute_script("window.open('', '_blank');")
        self.__webDriver.switch_to.window(self.__webDriver.window_handles[-1])
        # DeepLに接続
        self.__webDriver.get("https://www.deepl.com/translator")

    # 渡された文を翻訳にかけ、訳文を返す
    def translate(self, text, first_wait_secs=10, wait_secs_max=60):
        # DeepLのページが開かれていなければ開く
        self.openDeepLPage()

        # 原文の入力欄を取得
        source_textarea = self.__webDriver.find_element_by_css_selector(
            "textarea.lmt__textarea.lmt__source_textarea."
            "lmt__textarea_base_style"
        )
        # Ctrl+Aで全選択し、前の文を消しつつ原文を入力
        source_textarea.send_keys(Keys.CONTROL, Keys.COMMAND, "a")
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
                    "div.lmt__progress_popup.lmt__progress_popup--visible."
                    "lmt__progress_popup--visible_2")
            except sce.NoSuchElementException:
                # ポップアップが無く、かつ[...]が無ければ翻訳完了として抜け出す
                translated = self.__webDriver.find_element_by_css_selector(
                    "textarea.lmt__textarea.lmt__target_textarea."
                    "lmt__textarea_base_style"
                ).get_property("value")
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
            "textarea.lmt__textarea.lmt__target_textarea."
            "lmt__textarea_base_style"
        ).get_property("value")

        return translated

    # ブラウザのウィンドウを閉じる
    def closeWindow(self):
        self.__webDriver.quit()
