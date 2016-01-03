import enum


class ModuloEnum(enum.Enum):
    def __add__(self, other):
        new_value = ((self.value - 1 + int(other)) % len(self.__class__)) + 1
        return self.__class__(new_value)

    def __sub__(self, other):
        new_value = ((self.value - 1 - int(other)) % len(self.__class__)) + 1
        return self.__class__(new_value)


class AutoNumberEnum(enum.Enum):
    def __new__(cls):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj
