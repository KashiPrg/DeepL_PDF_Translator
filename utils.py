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
