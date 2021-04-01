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
    __webDriver = None
    __window_position = None
    __window_size = None

    @classmethod
    def GetWebDriver(cls):
        # WebDriverが取得されていなければ取る
        if not (cls.__webDriver is None):
            try:
                # この操作で例外が発生するなら、
                # 一度取得したが何らかの要因でそのWebDriverのセッションが終了した
                cls.RestoreWindow()
                return
            except sce.WebDriverException:
                pass

        # 設定を引っ張ってくる
        settings = Settings()
        browser = settings.settings["main_window"]["str_web_browser"]

        try:
            if browser == Browser.CHROME.value:
                cls.__webDriver = webdriver.Chrome(ChromeDriverManager().install())
            elif browser == Browser.EDGE.value:
                cls.__webDriver = webdriver.Edge(EdgeChromiumDriverManager().install())
            elif browser == Browser.FIREFOX.value:
                # Firefoxはなぜかexecutable_pathで指定しないとエラーが起きる
                cls.__webDriver = webdriver.Firefox(executable_path=GeckoDriverManager().install())
            else:
                DeepLManager.invalidBrowser()
        except sce.WebDriverException:
            wx.LogError(browser + "がインストールされていません。\n\n" + browser + "をインストールするか、インストール済みの他の対応Webブラウザを選択してください。")
            exit(1)

        cls.__window_position = cls.__webDriver.get_window_position()
        cls.__window_size = cls.__webDriver.get_window_size()

    @staticmethod
    def invalidBrowser():
        wx.LogError("ブラウザの指定が無効な値です。")
        exit(1)

    # DeepLのタブを開く
    @classmethod
    def openDeepLPage(cls):
        # WebDriverが取得されていなければ取得する
        cls.GetWebDriver()

        # 今のタブがDeepLなら何もしない
        try:
            if search(r"^https://www.deepl.com/translator", cls.__webDriver.current_url):
                return
        except AttributeError:
            print("Error: webDriver is not initiated.", file=stderr)
            exit(1)

        # 他のタブにそのページがあるならそれを開いて終わり
        for tab in cls.__webDriver.window_handles:
            cls.__webDriver.switch_to.window(tab)
            if cls.__webDriver.current_url == "https://www.deepl.com/translator":
                return

        # もしDeepLのページを開いているタブが無ければ新たに開く
        # 新しいタブを開き、そのタブに移動
        cls.__webDriver.execute_script("window.open('', '_blank');")
        cls.__webDriver.switch_to.window(cls.__webDriver.window_handles[-1])
        # DeepLに接続
        cls.__webDriver.get("https://www.deepl.com/translator")

    # 渡された文を翻訳にかけ、訳文を返す
    @classmethod
    def translate(cls, text, lang="ja-JA", first_wait_secs=10, wait_secs_max=60):
        # DeepLのページが開かれていなければ開く
        cls.openDeepLPage()

        # 訳文の言語を選択するタブを開く
        cls.__webDriver.find_element_by_xpath("//button[@dl-test='translator-target-lang-btn']").click()
        # 訳文の言語のボタンを押す
        cls.__webDriver.find_element_by_xpath("//button[@dl-test='translator-lang-option-" + lang + "']").click()

        # 原文の入力欄を取得
        source_textarea = cls.__webDriver.find_element_by_css_selector(
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
                _ = cls.__webDriver.find_element_by_css_selector(
                    "div.lmt__progress_popup.lmt__progress_popup--visible.lmt__progress_popup--visible_2")
            except sce.NoSuchElementException:
                # ポップアップが無く、かつ[...]が無ければ翻訳完了として抜け出す
                translated = cls.__webDriver.find_element_by_css_selector(
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
        translated = cls.__webDriver.find_element_by_css_selector(
            "textarea.lmt__textarea.lmt__target_textarea.lmt__textarea_base_style").get_property("value")

        return translated

    @classmethod
    def MinimizeWindow(cls):
        """
        ブラウザのウインドウを最小化する
        """
        cls.__window_position = cls.__webDriver.get_window_position()
        cls.__window_size = cls.__webDriver.get_window_size()
        cls.__webDriver.minimize_window()

    @classmethod
    def RestoreWindow(cls):
        cls.__webDriver.set_window_rect(
            x=cls.__window_position["x"],
            y=cls.__window_position["y"],
            height=cls.__window_size["height"],
            width=cls.__window_size["width"]
        )

    @classmethod
    def closeWindow(cls):
        if not (cls.__webDriver is None):
            cls.__webDriver.quit()
