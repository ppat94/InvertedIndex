import sys
import math
from IndexPrinter import InvertedIndex
from BooleanRetrieval import construct_tree, all_solution, convert_to_infix


def normalize(vector):
    magnitude = 0;
    for x in vector:
      magnitude += x*x
    
    magnitude = math.sqrt(magnitude)

    if magnitude == 0:
      return vector

    result = []
    for x in vector:
      result += [x/magnitude]

    return result

def dot_product(vector1, vector2):
    result = 0
    for x in range(len(vector1)):
      result += vector1[x]*vector2[x]

    return result

# Compute cosine rank of documents containing
# terms in query_terms, returning max of num_docs.
# Query is conjunctive.
def rank_cosine (query_terms, num_docs, inverted_index):
    result = []

    # List of documents containing all terms in query
    documents = documents_containing_query(query_terms, inverted_index)

    if len(documents) == 0:
      return result

    # Compute query vector
    query_vector = generate_query_vector(query_terms, inverted_index)

    for document in documents:
      # Compute document vector
        document_vector = generate_document_vector(document, inverted_index)

        # Compute score
        score = dot_product(normalize(document_vector), normalize(query_vector))

        result += [(document, score)]

	# sort by score, descending order
    result.sort(key = lambda x: -x[1])
    return result[0:num_docs]

# Compute cosine rank of documents in case of Boolean Retrieval containing
# terms in query_terms, returning max of num_docs.
# Query is conjunctive.

def rank_cosine_bool (query_terms, num_docs, documents, inverted_index):
    
	result = []

	if len(documents) == 0:
		return result

	# Compute query vector
	query_vector = generate_query_vector(query_terms, inverted_index)

	for document in documents:
		# Compute document vector
		document_vector = generate_document_vector(document, inverted_index)

		# Compute score
		score = dot_product(normalize(document_vector), normalize(query_vector))

		result += [(document, score)]

	# sort by score, descending order
	result.sort(key = lambda x: -x[1])
	return result[0:num_docs]
	
# Returns list of documents that contain all of the terms in
# query_terms.
def documents_containing_query(query_terms, inverted_index):
	documents_per_term = []

	# For each term, get the documents that contain them
	for term in query_terms:
		if term in inverted_index.inverted_index:
			documents = []

			for posting in inverted_index.inverted_index[term]:
				documents += [posting[0]]

			documents_per_term += [documents]

		# term not in vocabulary, no documents contain all terms
		else:
			return []

	# Get the intersection of all the lists of documents for each term
	common_documents = set()
	if len(documents_per_term) > 0:
		common_documents = set(documents_per_term[0])

		for documents in documents_per_term:
			common_documents = common_documents.intersection(set(documents))

	return list(common_documents)


# Creates the document vector for a document, where each component in the
# vector is the TF-IDF value that corresponds to a term in the vocabulary
# of inverted_index.
def generate_document_vector(doc_id, inverted_index):
	document_vector = []

	for term in inverted_index.inverted_index:
		document_has_term = False

		for posting in inverted_index.inverted_index[term]:
			# term appears in this document
			if posting[0] == doc_id:
				document_has_term = True

				# calculate TF: log(freq_t,d) + 1 if freq_t,d > 0
				# else 0
				tf = 0
				# term frequency in document > 0
				if posting[1] > 0:
					tf = math.log(posting[1], 2) + 1

				# calculate IDF: log(N/N_t)
				# aka log(num docs in collection / num docs term appears in)
				idf = math.log(
					inverted_index.num_documents/
					len(inverted_index.inverted_index[term]), 2)

				document_vector += [tf*idf]

		# Component is zero if term not in document
		if not document_has_term:
			document_vector += [0]

	return document_vector

# Creates a query vector for a list of query terms, where each component
# in the vector is the TF-IDF value that corresponds to a term in the
# vocabulary of inverted_index.
def generate_query_vector(query_terms, inverted_index):
	query_vector = []

	for term in inverted_index.inverted_index:
		if term in query_terms:
			# calculate TF: log(freq in query) + 1 if freq > 0
			# else 0
			tf = 0

			# Count frequency of term in query
			freq = 0
			for query_term in query_terms:
				if term == query_term:
					freq += 1

			if freq > 0:
				tf = math.log(freq, 2) + 1

			# calculate IDF: log(N/N_t)
			# aka log(num docs in collection / num docs term appears in)
			idf = math.log(
				inverted_index.num_documents/
				len(inverted_index.inverted_index[term]), 2)

			query_vector += [tf*idf]

		# term not in query
		else:
			query_vector += [0]

	return query_vector

# Compute proximity rank of documents containing terms in
# query_terms, returning a max of num_docs.
# Query is conjunctive.
def rank_proximity(query_terms, num_docs, inverted_index):
	result = []

	cover = next_cover(query_terms, "-infinity", inverted_index)

	# stores previous cover's u to keep track of different documents
	d = cover[0]
	score = 0

	#while u < infinity
	while inverted_index.compare_positions(cover[0], "infinity") < 0:
		# doc_id of u changed, record info about last doc_id
		if d[0] < cover[0][0]:
			result += [(d[0], score)]
			d = cover[0]
			score = 0
		score += 1/(cover[1][1] - cover[0][1] + 1)
		cover = next_cover(query_terms, cover[0], inverted_index)

	# record last score if not recorded
	if inverted_index.compare_positions(d, "infinity") < 0:
		result += [(d[0], score)]

	# sort by score, descending order
	result.sort(key = lambda x: -x[1])
	return result[0:num_docs]

# Returns the next smallest cover of query_terms in the collection from
# position.
def next_cover(query_terms, position, inverted_index):
	# next positions of all query_terms
	next_positions = [
		inverted_index.next(term, position) for term in query_terms]

	# v is max position of cover
	v = next_positions[0]
	for position in next_positions:
		# position > v
		if inverted_index.compare_positions(position, v) > 0:
			v = position

	if v == "infinity":
		return ["infinity", "infinity"]

	prev_positions = [
		inverted_index.prev(term, (v[0], v[1]+1)) for term in query_terms]

	# u is min position of cover
	u = prev_positions[0]
	for position in prev_positions:
		# position < u
		if inverted_index.compare_positions(position, u) < 0:
			u = position

	# same document, return cover
	if u[0] == v[0]:
		return [u, v]

	else:
		return next_cover(query_terms, u, inverted_index)

if __name__== "__main__":
    # Handle input

    filename = sys.argv[1]
    num_results = int(sys.argv[2])
    query = sys.argv[3]

    # Build inverted index
    index = InvertedIndex()
    index.build_index(filename)

    boolean_retrieval = False
    # find all terms
    arguments = []
    for argument in query.split(' '):
        if argument != '_OR' and argument != '_AND':
           arguments.append(argument)
        else:
           boolean_retrieval = True
           continue
    #boolean retrieval
    doc_ids = []
    if boolean_retrieval:
        boolean_retrieval_query = []
        for x in query.split(' '):
            if x != '_AND' and x != '_OR':
                boolean_retrieval_query.append(x.lower())
            else:
                boolean_retrieval_query.append(x)
        root = construct_tree(boolean_retrieval_query)
        doc_ids = all_solution(root, index.num_documents, index)
        doc_ids = [i for i in doc_ids if i]

	# Strip punctuation and convert query to lower case
	# query = query.translate(str.maketrans("", "", string.punctuation))
	# query = query.lower()
    arguments = [x.lower() for x in arguments]

	# Proximity Ranked retrieval
    results = []
    
    if not boolean_retrieval: 
       results = rank_cosine(set(arguments), num_results, index)
    else:
       results = rank_cosine_bool (set(arguments), num_results, doc_ids, index)
	# results = rank_proximity(set(arguments), num_results, index)

	# for docid in results:
	# 	if docid[0] not in doc_ids:
	# 		results.remove(docid)

# doc_ids & results?
	# Print results
    print("Boolean Retrieval results: " + str(doc_ids))
    print("DocId Score")
    for document, score in results:
      print(str(document) + " " + str("%.4f" % score))
