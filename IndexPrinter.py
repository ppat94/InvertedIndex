import string
import math

# Positional inverted index, postings in form:
# <document id, term frequency in document, term positions in document>
class InvertedIndex:

	num_documents = 0
	inverted_index = {}

	# Cached indices of positions last returned by prev/next calls for a term.
	prev_cache = {}
	next_cache = {}

	# Read from a file and build the inverted index
	def build_index(self, filename):
		f = open(filename, 'r')

		# Documents separated by newline
		current_document = 1
		# Term position within document
		current_position = 1

		# Read file line by line
		for line in f:
			# Check if line is only newline.
			# If so, new document and reset term position.
			if line == "\n":
				current_document += 1
				current_position = 1
			else:
				# Read line word by word ignoring whitespace
				for word in line.split():

					# Strip punctuation and convert to lowercase
					word = word.translate(
						str.maketrans("", "", string.punctuation))
					word = word.lower()

					# Case when stripping punctuation leaves the empty string
					if word == "":
						continue

					# First occurrence of the word:
					# add an entry in the dictionary
					if word not in self.inverted_index:

						# <docid, term frequency in doc, occurrences in doc>
						self.inverted_index[word] = [
							[current_document, 1, [current_position]]]

					# Word seen before: add occurrence
					else:
						postings = self.inverted_index[word]

						# Check if first occurrence of this document by
						# checking last document posting.
						# If so, new posting
						if (postings[-1][0] != current_document):

							postings += [
								[current_document, 1, [current_position]]]

						# Same document, increment freq, add occurrence
						else:
							postings[-1][1] += 1
							postings[-1][2] += [current_position]


					# Increment current_position.
					current_position += 1

		self.num_documents = current_document
		f.close();

	# Returns the first occurrence of term t in the index
	def first(self, t):
		if t in self.inverted_index:
			postings = self.inverted_index[t]
			# (docid, position)
			return (postings[0][0], postings[0][2][0])
		else:
			return "infinity"

	# Returns the last occurrence of term t in the index
	def last(self, t):
		if t in self.inverted_index:
			postings = self.inverted_index[t]
			# (docid, position)
			return (postings[-1][0], postings[-1][2][-1])
		else:
			return "infinity"

	# Returns the previous occurrence of term t before position current
	# Uses galloping search
	def prev(self, t, current):
		if t not in self.inverted_index:
			return "-infinity"

		# Check if current is before the first position in postings,
		# thus no previous occurrence exists.

		first_position = (
			self.inverted_index[t][0][0], self.inverted_index[t][0][2][0])

		# first_position >= current
		if self.compare_positions(first_position, current) >= 0:
			return "-infinity"

		# Last position in postings is less than current, return.

		last_position = (
			self.inverted_index[t][-1][0], self.inverted_index[t][-1][2][-1])

		# last_position < current
		if self.compare_positions(last_position, current) < 0:
			self.prev_cache[t] = self.num_positions(t) - 1
			return last_position

		# Initialize high after cached position from the last time prev was
		# called if >= current, else start at last position in postings

		high = self.num_positions(t) - 1

		if (t in self.prev_cache and
				self.prev_cache[t] < self.num_positions(t) - 1):

			cache_position = self.index_to_position(t, self.prev_cache[t] + 1)

			# cache_position >= current
			if self.compare_positions(cache_position, current) >= 0:
				high = self.prev_cache[t] + 1

		jump = 1
		low = high - jump

		# Begin galloping search, increase size of jumps until low
		# passes current or end of positions.

		if low >= 0:
			low_position = self.index_to_position(t, low)

		while (low >= 0 and
				self.compare_positions(low_position, current) >= 0):

			high = low
			jump = 2*jump
			low = high - jump

			if low >= 0:
				low_position = self.index_to_position(t, low)

		# Jumped past 0, cap at first position
		if low < 0:
			low = 0

		# Binary search interval that current is contained in.
		self.prev_cache[t] = self.binary_search(t, low, high, current, False)
		return self.index_to_position(t, self.prev_cache[t])

	# Returns the next occurrence of term t after position current
	# Uses galloping search
	def next(self, t, current):
		if t not in self.inverted_index:
			return "infinity"

		# Check if current is past all positions in postings,
		# thus no next occurrence exists.

		last_position = (
			self.inverted_index[t][-1][0], self.inverted_index[t][-1][2][-1])

		# last_position <= current
		if self.compare_positions(last_position, current) <= 0:
			return "infinity"

		# First position in postings is greater than current, return.

		first_position = (
			self.inverted_index[t][0][0], self.inverted_index[t][0][2][0])

		# first_position > current
		if self.compare_positions(first_position, current) > 0:
			self.next_cache[t] = 0
			return first_position

		# Initialize low before cached position from the last time next was
		# called if <= current, else start at first position in postings

		low = 0

		if t in self.next_cache and self.next_cache[t] > 0:
			cache_position = self.index_to_position(t, self.next_cache[t] - 1)

			# cache_position <= current
			if self.compare_positions(cache_position, current) <= 0:
				low = self.next_cache[t] - 1

		jump = 1
		high = low + jump

		# Begin galloping search, increase size of jumps until high
		# passes current or end of positions.

		high_position = self.index_to_position(t, high)
		while (high < self.num_positions(t) and
				self.compare_positions(high_position, current) <= 0):

			low = high
			jump = 2*jump
			high = low + jump
			high_position = self.index_to_position(t, high)

		# Jumped past last position, cap high at last position
		if high >= self.num_positions(t):
			high = self.num_positions(t) - 1

		# Binary search interval that current is contained in.
		self.next_cache[t] = self.binary_search(t, low, high, current, True)
		return self.index_to_position(t, self.next_cache[t])

	# Binary search through postings of term t in the index.
	# Returns the next biggest or smallest posting after current
	# depending on is_next
	def binary_search(self, t, low, high, current, is_next):
		# Loop until current is either low or high, or low and high exactly
		# surround current.
		while high - low > 1:
			mid = low + math.floor((high - low)/2)

			mid_position = self.index_to_position(t, mid)

			# If looking for position bigger than current,
			# keep value at high larger than current.
			if is_next:
				# mid_position <= current
				if self.compare_positions(mid_position, current) <= 0:
					low = mid
				else:
					high = mid

			# Looking for position smaller than current,
			# keep value at low smaller than current.
			else:
				# mid_position < current
				if self.compare_positions(mid_position, current) < 0:
					low = mid
				else:
					high = mid

		if is_next:
			return high
		else:
			return low

	# Helper function that compares two term positions of form (doc, position)
	# pos1 < pos2 == -1
	# pos1 == pos2 == 0
	# pos1 > pos2 == 1
	def compare_positions(self, pos1, pos2):
		if pos1 == "infinity":
			return 1
		if pos1 == "-infinity":
			return -1
		if pos2 == "infinity":
			return -1
		if pos2 == "-infinity":
			return 1

		# pos1's doc is less than pos2's
		if pos1[0] < pos2[0]:
			return -1
		# same documents, check document positions
		elif pos1[0] == pos2[0]:
			if pos1[1] < pos2[1]:
				return -1
			elif pos1[1] == pos2[1]:
				return 0
			else:
				return 1
		else:
			return 1

	# Helper function that returns size of a term's total positions in the
	# inverted index
	def num_positions(self, t):
		result = 0
		postings = self.inverted_index[t]

		for posting in postings:
			result += len(posting[2])

		return result

	# Helper function that takes a term and an index and finds the
	# corresponding position in the term's postings, as if all the term's
	# document positions were in one list.
	def index_to_position(self, t, index):
		postings = self.inverted_index[t]

		for posting in postings:
			positions = posting[2]

			# index is contained in this posting's positions
			if len(positions) > index:
				# (docid, doc_position)
				return (posting[0], positions[index])

			# index refers to position in a further posting
			else:
				index -= len(positions)

		# Index greater than total positions
		return "infinity"
