import fnmatch

import parsley

from . import tileset


def enum_match_set(enum, expr):
    value = {x for x in enum if fnmatch.fnmatch(x.name, expr)}
    if not value:
        raise ValueError('No enum values matched', enum, expr)
    else:
        return value


tileset_parser_bindings = {
    'TileFeature': tileset.TileFeature,
    'TileGrass': tileset.TileGrass,
    'create_feature': lambda name, subfeatures: tileset.Feature.get_class(name)(subfeatures),
    'create_subfeature': lambda name: tileset.Subfeature.get_class(name)(),
    'get_feature_direction': lambda x: enum_match_set(tileset.FeatureAttachment, x),
    'get_grass_direction': lambda x: enum_match_set(tileset.GrassAttachment, x),
}


tileset_parser = parsley.makeGrammar("""
identifier = <letter letterOrDigit*>
int = <digit+>:x -> int(x)
sp = ' ' | '\t'
nl = '\n'
ws = sp | nl

feature_direction = <(anything:x ?(x in 'NESW*?')){1,2}>:expr -> get_feature_direction(expr)
feature_directions = feature_directions:rest sp* '+' sp* feature_direction:this -> rest | this
                   | feature_directions:rest sp* '-' sp* feature_direction:this -> rest - this
                   | feature_direction
feature_attachment = sp+ 'at' sp+ feature_directions
grass_direction = <(anything:x ?(x in 'NESW12*?')){1,2}>:expr -> get_grass_direction(expr)
grass_directions = grass_directions:rest sp* '+' sp* grass_direction:this -> rest | this
                 | grass_directions:rest sp* '-' sp* grass_direction:this -> rest - this
                 | grass_direction
grass_attachment = sp+ 'at' sp+ grass_directions

feature_id = sp+ '[' sp* identifier:id sp* ']' -> id
subfeature = identifier:id -> create_subfeature(id)
subfeatures = sp+ '{' sp* subfeature:first (sp* ',' sp* subfeature)*:rest sp* '}' -> [first] + rest
feature = 'feature' feature_id?:id sp+ identifier:kind subfeatures?:subf feature_attachment?:attach
        -> TileFeature(create_feature(kind, subf), attach, id)

touching = sp+ 'touching' sp+ '[' sp* identifier:first (sp* ',' sp* identifier)*:rest sp* ']' -> [first] + rest
grass = 'grass' grass_attachment:attach touching?:touching -> TileGrass(attach, touching)

feature_or_grass = ws* (feature | grass)
features = '{' feature_or_grass:first (sp* (nl | ',') feature_or_grass)*:rest ws* '}' -> [first] + rest

tiledef = 'tile' sp+ identifier:id ws+ features:features -> ('tiledef', id, features)

use_tile = ws* identifier:id ( sp* '*' sp* int:n -> (id, n)
                             | -> (id, 1))
tiles = '{' use_tile:first (sp* (nl | ',') use_tile)*:rest ws* '}' -> [first] + rest
tileset = 'tileset' sp+ identifier:id ws+ tiles:tiles -> ('tileset', id, tiles)

tiledef_or_tileset = ws* (tiledef | tileset)

toplevel = tiledef_or_tileset:first (ws+ tiledef_or_tileset)*:rest ws* end -> [first] + rest
""", tileset_parser_bindings)


def load_tilesets(stream):
    items = tileset_parser(stream.read()).toplevel()
    collection = tileset.TileCollection(tileset.Tile(id, contains)
                                        for k, id, contains in items
                                        if k == 'tiledef')
    tilesets = [collection.create_tileset(id, contains)
                for k, id, contains in items
                if k == 'tileset']
    return collection, tilesets


if __name__ == '__main__':
    import sys, pprint
    collection, tilesets = load_tilesets(open(sys.argv[1]))
    pprint.pprint(collection)
    pprint.pprint(tilesets)
