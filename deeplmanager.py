import re
import selenium.common.exceptions as sce
import wx

from data import Browser
from re import search
from selenium import webdriver
from settings import Settings
from sys import stderr
from time import sleep
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager


# DeepLでの翻訳を管理する
class DeepLManager:
    def __init__(self):
        browser_setting = Settings.web_browser
        try:
            # 使用するウェブブラウザの設定に沿ってWebDriverを取得
            # webdriver_managerのおかげで自動でダウンロードしてくれる
            if browser_setting == Browser.CHROME.value:
                self.__webDriver = webdriver.Chrome(ChromeDriverManager().install())
            elif browser_setting == Browser.EDGE.value:
                self.__webDriver = webdriver.Edge(EdgeChromiumDriverManager().install())
            elif browser_setting == Browser.FIREFOX.value:
                # Firefoxはなぜかexecutable_pathで指定しないとエラーが起きる
                self.__webDriver = webdriver.Firefox(executable_path=GeckoDriverManager().install())
            else:
                # 設定が壊れているなどで無効な値のときはエラーを発生させる
                DeepLManager.invalidBrowser()
        except sce.WebDriverException:
            # この状況でこの例外が発生するなら、指定のウェブブラウザがインストールされていない
            wx.LogError(browser_setting + "がインストールされていません。\n\n" + browser_setting + "をインストールするか、インストール済みの他の対応Webブラウザを選択してください。")
            exit(1)

        self.__webDriverRect = self.__webDriver.get_window_rect()

    def __isWebDriverAlive(self):
        """
        WebDriverが取得された後にウインドウを閉じられていないか確認する

        Returns:
            bool: WebDriverが閉じられていないならTrue
        """
        try:
            # この操作で例外が発生するなら、
            # 一度取得したが何らかの要因でそのWebDriverのセッションが終了したということ
            self.__webDriver.get_window_position()
            # そうでなければ今もウェブブラウザが開いている
            return True
        except sce.WebDriverException:
            return False

    @staticmethod
    def invalidBrowser():
        wx.LogError("ブラウザの指定が無効な値です。")
        exit(1)

    def openDeepLPage(self):
        """
        DeepLのタブを開く
        """
        # 今のタブがDeepLなら何もしない
        try:
            if search(r"^https://www.deepl.com/translator", self.__webDriver.current_url):
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

    def translate(self, text, lang="ja-JA", first_wait_secs=10, wait_secs_max=60):
        """
        DeepLで翻訳を行う

        Args:
            text (string): 原文
            lang (str, optional): 翻訳先の言語 Settings.target_language_for_translateで取得可能
            first_wait_secs (int, optional): 翻訳時に何秒待ってから翻訳完了の判定を行うか
            wait_secs_max (int, optional): 翻訳が不可能であったと見なす時間

        Returns:
            string: 翻訳文
        """
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
                # 先頭は翻訳の失敗を伝えるメッセージで、残りは空白
                num_pars = len(text.splitlines())
                messages = ["(翻訳に" + str(wait_secs_max) + "秒以上を要するため失敗と見なしました)"] + ["" for _ in range(num_pars - 1)]
                return "\n".join(messages)

        # 訳文の出力欄を取得し、訳文を取得
        translated = self.__webDriver.find_element_by_css_selector(
            "textarea.lmt__textarea.lmt__target_textarea.lmt__textarea_base_style").get_property("value")

        return translated

    def MinimizeWindow(self):
        """
        ブラウザのウインドウを最小化する
        """
        self.__webDriverRect = self.__webDriver.get_window_rect()
        self.__webDriver.minimize_window()

    def RestoreWindow(self):
        """
        ブラウザのウインドウをもとの大きさに戻す
        """
        self.__webDriver.set_window_rect(
            x=self.__webDriverRect["x"],
            y=self.__webDriverRect["y"],
            width=self.__webDriverRect["width"],
            height=self.__webDriverRect["height"]
        )

    def closeWindow(self):
        """
        ブラウザが駆動しているならそのウインドウを閉じる
        """
        if self.__isWebDriverAlive():
            self.__webDriver.quit()
