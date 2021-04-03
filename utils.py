import wx


class classproperty(property):
    pass


class ClassProperty(type):
    def __new__(cls, name, bases, namespace):
        props = [(k, v) for k, v in namespace.items() if type(v) == classproperty]
        for k, v in props:
            setattr(cls, k, v)
            del namespace[k]
        return type.__new__(cls, name, bases, namespace)


class ProgressBar:
    def __init__(self, parent, pos, size, maxprogress=100):
        # 進捗の最大段階(最低1)
        self.__progress = 0
        self.__maxprogress = maxprogress
        # ゲージ背景
        self.__background = wx.Panel(parent, pos=pos, size=size)
        self.__background.SetBackgroundColour("#BBBBBB")
        # ゲージ本体
        self.__gauge = wx.Panel(parent, pos=pos, size=(0, size[1]))
        self.__gauge.SetBackgroundColour("#18CC27")
        # 無効っぽくしたときの本体
        # Freezeをイベントで呼び出すとSetBackgroundColourが効かないので、
        # あらかじめFreeze用のゲージを作っておく必要がある
        self.__frozengauge = wx.Panel(parent, pos=pos, size=(0, size[1]))
        self.__frozengauge.SetBackgroundColour("#CCCCCC")
        self.__frozengauge.Hide()   # 普段は隠しておく

    def ChangeMaxProgress(self, maxprogress):
        self.__maxprogress = maxprogress
        self.__progress = max(0, min(self.__maxprogress, self.__progress))
        self.Update(self.__progress)

    def Update(self, progress):
        """
        バーの進み具合を更新する

        Args:
            progress (int): 進み具合
        """
        # 0～最大の間に収める
        self.__progress = max(0, min(self.__maxprogress, progress))
        bg_rect = self.__background.GetRect()
        # ゲージ背景の長さと進み具合から、ゲージ本体の長さを算出
        gauge_width = max(0, min(bg_rect[2], int(bg_rect[2] * progress / self.__maxprogress)))
        gauge_rect = bg_rect
        gauge_rect[2] = gauge_width
        # 長さを更新
        self.__gauge.SetRect(gauge_rect)
        self.__frozengauge.SetRect(gauge_rect)

    def Freeze(self):
        """
        バーの色を無効っぽく変える
        """
        self.__frozengauge.Show()
