#!/bin/python3

import argparse
import re
from os import path
from xml.etree import ElementTree as ET
from csv import DictWriter
from typing import List


class Node():
    """A MindMap Node."""

    def __init__(self, node, parent=None):
        self.node = node
        self.parent = parent

    @property
    def id(self) -> str:
        return self.node.attrib['ID']

    @property
    def name(self) -> str:
        return self.node.attrib.get('TEXT', self.id)

    @property
    def name_filtered(self):
        regex = re.compile('\s\(\w+\)$')
        name = self.name
        name = re.sub(regex, '', name)
        return name

    @property
    def children(self) -> List['Node']:
        nodes = self.node.findall("./node")
        return [Node(node, self) for node in nodes]

    def __str__(self) -> str:
        return 'Node {} "{}"'.format(self.id, self.name)

    __repr__ = __str__


class MindMap():
    """Class representing the mindmap document."""
    filename = None  # type: str
    xml = None  # type: ET
    current_node = None  # type: Node

    def __init__(self, filename: str) -> None:
        self.filename = filename
        self.load()

    def load(self):
        self.xml = ET.parse(self.filename)

    @property
    def root(self):
        node = self.xml.getroot().find('./node')
        return Node(node)


def select(node: Node, with_parent: bool=False):
    children = node.children
    index = 1 if with_parent else 0
    for node in children:
        print('{} {}'.format(index, node))
        index += 1
    print('\n')
    select = input('Your selection: ')
    if select == '':
        return None
    select = int(select, base=10)
    if with_parent and select == 0:
        return node.parent
    if with_parent:
        select -= 1
    return children[select]


def main():
    """Main input loop."""
    parser = argparse.ArgumentParser(description='Extract a taxonomie from a Mindmap.')
    parser.add_argument('file')
    args = parser.parse_args()
    mindmap = MindMap(args.file)

    next_node = mindmap.root

    while next_node:
        mindmap.current_node = next_node
        print('\n\n')
        print('Current Node: {}'.format(mindmap.current_node.name_filtered))
        print('\n')
        if mindmap.current_node.parent:
            print('{} .. {}'.format(0, mindmap.current_node.parent))
            next_node = select(mindmap.current_node, True)
        else:
            next_node = select(mindmap.current_node)

    print('\n\n')
    print('Your selected node is: {}'.format(mindmap.current_node))
    print('\n\n')

    name = input('Enter filename: ')

    with open('{}.csv'.format(name), 'w') as csvfile:
        fieldnames = ['name', 'parent']
        writer = DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        nodes = [mindmap.current_node]
        while nodes:
            node = nodes.pop()
            nodes = nodes + node.children

            def nodename(node: Node) -> str:
                if node is mindmap.current_node:
                    return 'root'
                elif (node is None) or (node is mindmap.current_node.parent):
                    return ''
                else:
                    return node.name_filtered
            writer.writerow({'name': nodename(node), 'parent': nodename(node.parent)})


if __name__ == '__main__':
    main()
