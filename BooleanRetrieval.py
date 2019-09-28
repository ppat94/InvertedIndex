import math

import IndexPrinter


class Node:
    # Constructor to create a new node
    def __init__(self, data):
        self.data = data
        self.left = None
        self.right = None

def buildTree(inOrder, preOrder, inStrt, inEnd):
    if (inStrt > inEnd):
        return None

    # Pich current node from Preorder traversal using
    # preIndex and increment preIndex
    tNode = Node(preOrder[buildTree.preIndex])
    buildTree.preIndex += 1

    # If this node has no children then return
    if inStrt == inEnd:
        return tNode

        # Else find the index of this node in Inorder traversal
    inIndex = search(inOrder, inStrt, inEnd, tNode.data)

    # Using index in Inorder Traversal, construct left
    # and right subtrees
    tNode.left = buildTree(inOrder, preOrder, inStrt, inIndex - 1)
    tNode.right = buildTree(inOrder, preOrder, inIndex + 1, inEnd)

    return tNode


# UTILITY FUNCTIONS
# Function to find index of vaue in arr[start...end]
# The function assumes that value is rpesent in inOrder[]

def search(arr, start, end, value):
    for i in range(start, end + 1):
        if arr[i] == value:
            return i


# Static variable preIndex

def convert_to_infix(query):
    myStack = []
    # inputWords = query.split(" ")
    query = query[-1::-1]
    # output = ' '.join(inputWords)
    for term in query:
        if term == 'and':
            query = myStack.pop()
            query = query + ' and ' + myStack.pop()
            myStack.append(query)
        elif term == 'or':
            query1 = myStack.pop()
            # nextSolution()
            query2 = myStack.pop()
            # nextSolution()
            myStack.append(query1 + ' or ' + query2)
        else:
            myStack.append(term)
    return myStack


def doc_right(root, position, index):
    if root.data == 'or' or root.data == 'and':
        doc_right_l = doc_right(root.left, position, index)
        doc_right_r = doc_right(root.right, position, index)
        is_infinity = boundery_check(doc_right_l, doc_right_r, root.data)
        if is_infinity is None:
            if root.data == 'or':
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


def boundery_check(l, r, command):
    if command == 'and':
        if l == 'infinity' or r == 'infinity':
            return 'infinity'
    else:
        if l == 'infinity' and r != 'infinity':
            return r
        if l != 'infinity' and r == 'infinity':
            return l

    if l == 'infinity' and r == 'infinity':
        return 'infinity'
    else:
        return None


def doc_left(root, position, index):
    if root.data == 'or' or root.data == 'and':
        doc_left_r = doc_left(root.left, position, index)
        doc_left_l = doc_left(root.right, position, index)
        is_infinity = boundery_check(doc_left_l, doc_left_r, root.data)
        if is_infinity is None:
            if root.data == 'or':
                return max(doc_left_r, doc_left_l)
            else:
                return min(doc_left_r, doc_left_l)
        else:
            return is_infinity
    else:
        res = index.prev(root.data, (position, 0))
        if res != 'infinity' and res != position:
            return res[0]
        else:
            return "infinity"


def next_solution(query, position, index):
    docid_right = doc_right(query, position, index)
    if docid_right == "infinity":
        return ""
    else:
        docid_left = doc_left(query, docid_right + 1, index)
        if docid_left == docid_left:
            return docid_left
        else:
            return next_solution(query, docid_right, index)


def all_solution(query, m, index):
    doc_id = []
    for u in range(m):
        doc_id.append(next_solution(query, u, index))
    return set(doc_id)


# The main function to construct BST from given preorder
# traversal. This function mailny uses constructTreeUtil()
def construct_tree(inOrder, preOrder):
    buildTree.preIndex = 0
    inOrder = str(inOrder).split(' ')
    root = buildTree(inOrder, preOrder, 0, len(inOrder) - 1)
    return root
