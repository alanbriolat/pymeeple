from collections import OrderedDict
from itertools import chain

from .util import ModuloEnum, AutoNumberEnum


class FeatureAttachment(AutoNumberEnum, ModuloEnum):
    """Points on a tile which features can touch.

    8 compass points are used to define parts of a tile edge that a feature can
    touch for visual purposes. For adjacency purposes (when traversing features
    on a board), an :attr:`opposite` property is provided for the 4 cardinal
    directions - it gives the corresponding attachment point on an adjacent
    tile.
    """
    NW = ()
    N = ()
    NE = ()
    E = ()
    SE = ()
    S = ()
    SW = ()
    W = ()

    @property
    def opposite(self):
        if self.value % 2 != 0:
            raise ValueError('opposite only valid for cardinal directions (N,S,E,W)', self)
        return self + 4


class GrassAttachment(AutoNumberEnum, ModuloEnum):
    """Points on a tile which grass can touch.

    Grass works differently to other features, filling the gaps in between and
    connecting to adjacent tiles via a different system. Grass has 2 attachment
    points per edge, to correspond to either side of a road. These are numbered
    clockwise.

    The :attr:`opposite` property  gives the corresponding attachment point on
    an adjacent tile.
    """
    N1 = ()
    N2 = ()
    E1 = ()
    E2 = ()
    S1 = ()
    S2 = ()
    W1 = ()
    W2 = ()

    @property
    def opposite(self):
        return self + 5 if self.value % 2 else self + 3


class FeatureBase:
    @classmethod
    def get_class(cls, name):
        for c in cls.__subclasses__():
            if c.__name__ == name:
                return c
        else:
            raise ValueError('No such subclass of %r' % cls, name)

    def rotate(self, n):
        return self

    def __repr__(self):
        return '<{}>'.format(self.__class__.__name__)

class Subfeature(FeatureBase):
    pass


class Shield(Subfeature):
    pass


class Feature(FeatureBase):
    ALLOWED_SUBFEATURES = []

    def __init__(self, subfeatures=None):
        self.subfeatures = subfeatures or []
        for sf in self.subfeatures:
            if sf.__class__ not in self.ALLOWED_SUBFEATURES:
                raise ValueError('Invalid subfeature', sf, self.ALLOWED_SUBFEATURES)

    def __repr__(self):
        if self.subfeatures:
            return '<{}({})>'.format(self.__class__.__name__,
                                   ', '.join(repr(sf) for sf in self.subfeatures))
        else:
            return super().__repr__()

    def rotate(self, n):
        return self.__class__([sf.rotate(n) for sf in self.subfeatures])


class Road(Feature):
    pass


class Monastery(Feature):
    pass


class City(Feature):
    ALLOWED_SUBFEATURES = [Shield]


class TileFeature:
    def __init__(self, feature, attachments=None, name=None):
        self.feature = feature
        self.attachments = attachments or set()
        self.name = name or None

    def __repr__(self):
        return '{}(feature={!r}, attachments={!r}'.format(self.__class__.__name__,
                                                          self.feature,
                                                          {x.name for x in self.attachments})

    def rotate(self, n):
        return self.__class__(self.feature.rotate(n), {a + n for a in self.attachments})


class TileGrass:
    def __init__(self, attachments, touching=None):
        self.attachments = attachments
        self.touching = touching or set()

    def __repr__(self):
        return '<{}: {!r}>'.format(self.__class__.__name__, {x.name for x in self.attachments})

    def rotate(self, n):
        return self.__class__({a + n for a in self.attachments})


class Tile:
    def __init__(self, name, features):
        self.name = name
        self.features = features

    def __repr__(self):
        return '{}({!r}, {!r})'.format(self.__class__.__name__, self.name, self.features)

    def rotate(self, n):
        return self.__class__(self.name,
                              [(id, tf.rotate(n)) for id, tf in self.features])


class TileCollection:
    def __init__(self, tiles=None):
        self._tiles = OrderedDict()
        tiles = tiles or []
        for tile in tiles:
            self.append(tile)

    def __repr__(self):
        return '<{}: {!r}>'.format(self.__class__.__name__,
                                   list(self._tiles.keys()))

    def append(self, tile):
        if tile.name in self._tiles:
            raise ValueError('Duplicate tile name', tile)
        self._tiles[tile.name] = tile

    def __getitem__(self, item):
        return self._tiles[item]

    def create_tileset(self, name, specs):
        return list(chain(*([self[tname]] * count for tname, count in specs)))
