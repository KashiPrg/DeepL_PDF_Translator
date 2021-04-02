class classproperty(property):
    pass


class ClassProperty(type):
    def __new__(cls, name, bases, namespace):
        props = [(k, v) for k, v in namespace.items() if type(v) == classproperty]
        for k, v in props:
            setattr(cls, k, v)
            del namespace[k]
        return type.__new__(cls, name, bases, namespace)
