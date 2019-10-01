
class Node:
    def __init__(self, data):
        self.data = data
        self.left = None
        self.right = None

def convert_to_infix(query):
    myStack = []
    query = query[-1::-1]
    for term in query:
        if term.data == '_AND':
            term.left = myStack.pop()
            term.right = myStack.pop()
            myStack.append(term)
        elif term.data == '_OR':
            term.left = myStack.pop()
            term.right = myStack.pop()
            myStack.append(term)
        else:
            myStack.append(term)
    return myStack


def doc_right(root, position, index):
    if root.data == '_OR' or root.data == '_AND':
        doc_right_l = doc_right(root.left, position, index)
        doc_right_r = doc_right(root.right, position, index)
        is_infinity = infinity_check_right(doc_right_l, doc_right_r, root.data)
        if is_infinity is None:
            if root.data == '_OR':
                return min(doc_right_r, doc_right_l)
            else:
                return max(doc_right_r, doc_right_l)
        else:
            return is_infinity
    else:
        res = index.next(root.data, (position + 1, 0))
        if res != 'infinity' and res != position:
            return res[0]
        else:
            return "infinity"


def infinity_check_right(l, r, argument):
    if argument == '_AND':
        if l == 'infinity' or r == 'infinity':
            return 'infinity'
        else:
            return None
    if argument == '_OR':
        if l == 'infinity' and r != 'infinity':
            return r
        if l != 'infinity' and r == 'infinity':
            return l
        if l == 'infinity' and r == 'infinity':
            return 'infinity'
        else:
            return None


def infinity_check_left(l, r, argument):
    if argument == '_AND':
        if l == '-infinity' or r == '-infinity':
            return '-infinity'
        else:
            return None
    if argument == '_OR':
        if l == '-infinity' and r != '-infinity':
            return r
        if l != '-infinity' and r == '-infinity':
            return l
        if l == '-infinity' and r == '-infinity':
            return '-infinity'
        else:
            return None


def doc_left(root, position, index):
    if root.data == '_OR' or root.data == '_AND':
        doc_left_r = doc_left(root.left, position, index)
        doc_left_l = doc_left(root.right, position, index)
        is_infinity = infinity_check_left(doc_left_l, doc_left_r, root.data)
        if is_infinity is None:
            if root.data == '_OR':
                return max(doc_left_r, doc_left_l)
            else:
                return min(doc_left_r, doc_left_l)
        else:
            return is_infinity
    else:
        res = index.prev(root.data, (position, 0))
        if res != '-infinity' and res != position:
            return res[0]
        else:
            return "-infinity"


def next_solution(query, position, index):
    docid_right = doc_right(query, position, index)
    if docid_right == "infinity":
        return None
    else:
        docid_left = doc_left(query, docid_right + 1, index)
        if docid_right == docid_left:
            return docid_left
        else:
            return next_solution(query, docid_right, index)


def all_solution(query, m, index):
    doc_id = []
    for u in range(m):
        doc_id.append(next_solution(query, u, index))
    return set(doc_id)

def construct_tree(preOrder):
    preOrder_node_list = []
    for data in preOrder:
        preOrder_node_list.append(Node(data))
    root = convert_to_infix(preOrder_node_list)[0]
    return root
