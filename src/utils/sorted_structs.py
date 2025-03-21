import heapq

class SortedDict:
    def __init__(self, mapping=None):
        """
        Initializes the SortedDict.
        :param mapping: Optional dictionary to initialize the sorted dict.
        """
        self._dict = {}
        self._keys = []
        if mapping:
            for key, value in mapping.items():
                self[key] = value

    def __setitem__(self, key, value):
        """
        Sets a key-value pair and maintains sorted order by key.
        """
        if key not in self._dict:
            heapq.heappush(self._keys, key)
        self._dict[key] = value

    def __delitem__(self, key):
        """
        Removes a key from the dictionary.
        """
        if key in self._dict:
            self._keys.remove(key)
            heapq.heapify(self._keys)
            del self._dict[key]
        else:
            raise KeyError(f"Key {key} not found in SortedDict.")

    def __getitem__(self, key):
        """
        Retrieves a value by key.
        """
        return self._dict[key]

    def pop(self):
        """
        Removes and returns the key with the smallest key.
        """
        if not self._keys:
            raise KeyError("pop from empty SortedDict")
        key = heapq.heappop(self._keys)
        value = self._dict.pop(key)
        return key, value

    def items(self):
        """
        Returns sorted (key, value) pairs.
        """
        return [(key, self._dict[key]) for key in sorted(self._keys)]

    def keys(self):
        """
        Returns keys in sorted order.
        """
        return sorted(self._keys)

    def values(self):
        """
        Returns values sorted by their corresponding keys.
        """
        return [self._dict[key] for key in sorted(self._keys)]

    def __len__(self):
        """
        Returns the number of items in the dictionary.
        """
        return len(self._dict)

    def __iter__(self):
        """
        Returns an iterator over keys sorted by their values.
        """
        return iter(self.keys())

    def __repr__(self):
        """
        Returns a string representation of the sorted dictionary.
        """
        return f"SortedDict({self.items()})"

    def contains_key(self, key):
        """
        Checks if the key exists in the dictionary.
        """
        return key in self._dict


class SortedList:
    def __init__(self, iterable=None):
        """
        Initializes the SortedList.
        :param iterable: Optional initial iterable to populate the list.
        """
        self._heap = []
        if iterable:
            for item in iterable:
                heapq.heappush(self._heap, item)

    def add(self, item):
        """
        Adds an item to the sorted list.
        :param item: The item to add.
        """
        heapq.heappush(self._heap, item)

    def remove(self, item):
        """
        Removes an item from the sorted list.
        :param item: The item to remove.
        """
        try:
            self._heap.remove(item)
            heapq.heapify(self._heap)  # Reorder the heap after removal
        except ValueError:
            raise ValueError(f"Item {item} not found in SortedList.")

    def pop(self):
        """
        Removes and returns the smallest item from the sorted list.
        """
        if not self._heap:
            raise IndexError("pop from empty SortedList")
        return heapq.heappop(self._heap)

    def __getitem__(self, index):
        """
        Allows indexing to retrieve sorted elements.
        """
        return sorted(self._heap)[index]

    def __len__(self):
        """
        Returns the number of elements in the sorted list.
        """
        return len(self._heap)

    def __iter__(self):
        """
        Returns an iterator over the sorted elements.
        """
        return iter(sorted(self._heap))

    def __repr__(self):
        """
        Returns a string representation of the sorted list.
        """
        return f"SortedList({sorted(self._heap)})"
