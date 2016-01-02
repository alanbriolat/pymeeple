import fnmatch

import parsley

from .tileset import FeatureAttachment, GrassAttachment


def enum_match_set(enum, expr):
    value = {x for x in enum if fnmatch.fnmatch(x.name, expr)}
    if not value:
        raise ValueError('No enum values matched', enum, expr)
    else:
        return value


tileset_parser_bindings = {
    'get_feature_direction': lambda x: enum_match_set(FeatureAttachment, x),
    'get_grass_direction': lambda x: enum_match_set(GrassAttachment, x),
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
subfeatures = sp+ '{' sp* identifier:first (sp* ',' sp* identifier)*:rest sp* '}' -> [first] + rest
feature = 'feature' feature_id?:id sp+ identifier:kind subfeatures?:subf feature_attachment?:attach -> (id, kind, subf, attach)

touching = sp+ 'touching' sp+ '[' sp* identifier:first (sp* ',' sp* identifier)*:rest sp* ']' -> [first] + rest
grass = 'grass' grass_attachment:attach touching?:touching -> ('grass', attach, touching)

feature_or_grass = ws* (feature | grass)
features = '{' feature_or_grass:first (sp* (nl | ',') feature_or_grass)*:rest ws* '}' -> [first] + rest

tiledef = 'tile' sp+ identifier:id ws+ features:features -> ('tile', id, features)

use_tile = ws* identifier:id ( sp* '*' sp* int:n -> (id, n)
                             | -> (id, 1))
tiles = '{' use_tile:first (sp* (nl | ',') use_tile)*:rest ws* '}' -> [first] + rest
tileset = 'tileset' sp+ identifier:id ws+ tiles:tiles -> ('tileset', id, tiles)

tiledef_or_tileset = ws* (tiledef | tileset)

toplevel = tiledef_or_tileset:first (ws+ tiledef_or_tileset)*:rest ws* end -> [first] + rest
""", tileset_parser_bindings)


if __name__ == '__main__':
    import sys, pprint
    pprint.pprint(tileset_parser(open(sys.argv[1]).read()).toplevel())