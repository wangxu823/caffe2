from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from caffe2.proto import hsm_pb2

'''
    Hierarchical softmax utility methods that can be used to:
    1) create TreeProto structure given list of word_ids or NodeProtos
    2) create HierarchyProto structure using the user-inputted TreeProto
'''


def create_node_with_words(words):
    node = hsm_pb2.NodeProto()
    for word in words:
        node.word_ids.append(word)
    return node


def create_node_with_nodes(nodes):
    node = hsm_pb2.NodeProto()
    for child_node in nodes:
        new_child_node = node.children.add()
        new_child_node.MergeFrom(child_node)
    return node


def create_hierarchy(tree_proto):
    max_index = 0

    def create_path(path, word):
        path_proto = hsm_pb2.PathProto()
        path_proto.word_id = word
        for entry in path:
            new_path_node = path_proto.path_nodes.add()
            new_path_node.index = entry[0]
            new_path_node.length = entry[1]
            new_path_node.target = entry[2]
        return path_proto

    def recursive_path_builder(node_proto, path, hierarchy_proto, max_index):
        path.append([max_index,
                    len(node_proto.word_ids) + len(node_proto.children), 0])
        max_index += len(node_proto.word_ids) + len(node_proto.children)
        if hierarchy_proto.size < max_index:
            hierarchy_proto.size = max_index
        for target, node in enumerate(node_proto.children):
            path[-1][2] = target
            max_index = recursive_path_builder(node, path, hierarchy_proto,
                                               max_index)
        for target, word in enumerate(node_proto.word_ids):
            path[-1][2] = target
            path_entry = create_path(path, word)
            new_path_entry = hierarchy_proto.paths.add()
            new_path_entry.MergeFrom(path_entry)
        del path[-1]
        return max_index

    node = tree_proto.root_node
    hierarchy_proto = hsm_pb2.HierarchyProto()
    path = []
    max_index = recursive_path_builder(node, path, hierarchy_proto, max_index)
    return hierarchy_proto
