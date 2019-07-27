"""duflat
Produces a flat summary of disc usage.

Usage:
    duflat [--dir=<root_dir>] [--num_lines=<num_lines>]
    duflat (-h | --help)
    duflat --version

Options:
    --dir=<root_dir>            Where to scan [default: .].
    --num_lines=<num_lines>     How many lines of output we should provide [default: 10].
    -h --help                   Show this screen.
    --version                   Show version.
"""

from docopt import docopt
from pprint import pprint
import sys
from pathlib import Path
from typing import Dict, Optional, List, Tuple
from subprocess import Popen, PIPE
from collections import deque

from duflat.version import __version__


def get_size(path: Path) -> int:
    if path.is_file() or path.is_symlink():
        return path.stat().st_size

    if not path.is_dir():
        print('{} is funny: ', path, file=sys.stderr)

    print('scanning ', path, file=sys.stderr)
    with Popen(['du', '-s', '--bytes', str(path)], stdout=PIPE) as p:
        stdout = p.stdout.read()
    return int(stdout.split(b'\t')[0])

def get_children(path: Path) -> List[Path]:
    if not path.is_dir():
        return []
    return [
        p for p in path.iterdir()
    ]


class SearchNode:
    def __init__(self, path: Path, size: int):
        self.path = path
        self.size = size # num bytes
        self.children = None  # Optional[List['SearchNode']]

    def __repr__(self) -> str:
        return '{:>12} -> {}'.format(self.size, self.path)

    def expand_children(self, min_size_to_expand: int):
        if self.size < min_size_to_expand:
            return
        if self.children is None:
            self.children = [ SearchNode(p, get_size(p)) for p in sorted(get_children(self.path)) ]
        for child in self.children:
            child.expand_children(min_size_to_expand)

    def _find_node_closest_to_size(self, desired_size: int) -> Tuple[int, List[int]]:
        """
        the returned tuple is
            best_diff
            child indexes to get to that node; first element represents the deepest level.
        """
        best = (abs(desired_size - self.size), [])
        if self.children is not None:
            for i, child in enumerate(self.children):
                new = child._find_node_closest_to_size(desired_size)
                # lowest difference between to desired.
                # On ties, prefer the first child.
                if new[0] < best[0] or (new[0] == best[0] and best[1] == []):
                    best = new
                    best[1].append(i)
        return best

    def _pop_deep_node(self, index_stack: List[int]) -> 'SearchNode':
        if index_stack == []:
            return self
        i = index_stack.pop()
        child = self.children[i]
        if index_stack == []:
            deep_node = child
            del self.children[i]  # if we contain the deep_node, we stop containing it.
        else:
            deep_node = child._pop_deep_node(index_stack)
        self.size -= deep_node.size
        return deep_node

    def pop_node_of_similar_size(self, desired_size: int) -> 'SearchNode':
        _, index_stack = self._find_node_closest_to_size(desired_size)
        return self._pop_deep_node(index_stack)

def make_duflat(root: Path, max_nodes: int) -> List[SearchNode]:
    root_node = SearchNode(root, get_size(root))
    out = [root_node]
    for num_remaining in range(max_nodes, 1, -1):
        desired_size = (root_node.size // num_remaining)+1
        root_node.expand_children(desired_size)
        node = root_node.pop_node_of_similar_size(desired_size)
        if node is root_node:
            break  # root node should be empty at this point.
        out.append(node)
    out.sort(key=lambda node: (node.path, -node.size))
    return out

def main():
    arguments = docopt(__doc__, version=__version__)
    max_nodes = int(arguments['--num_lines'])
    root = Path(arguments['--dir'])
    nodes = make_duflat(root, max_nodes)
    for node in nodes:
        print(node)

if __name__ == '__main__':
    main()
