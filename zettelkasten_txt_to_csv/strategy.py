"""Zettelkasten converter
Eugene Ho, 16 Aug 2020

Implmenting strategy pattern from 
https://refactoring.guru/design-patterns/strategy/python/example

Strategy is a behavioral design pattern. It enables an algorithm's behavior to
be selected at runtime. We can implement it by creating a common (abstract)
interface and subclassing it with a new class for each strategy, how it's done
in [1], or by creating a single class and replacing a method of that class with
a different function, how it's done in [2]. The latter implementation is
possible because in Python functions are first class objects.
"""

from __future__ import annotations
from typing import List, Dict
from zettelkasten_txt_to_csv import Zettelkasten

class Context():
	"""
	The Context defines the interface of interest to clients.
	"""

	def __init__(self, strategy: Strategy) -> None:
		"""
		Usually, the Context accepts a strategy through the constructor, but
		also provides a setter to change it at runtime.
		"""

		self._strategy = strategy

	@property
	def strategy(self) -> Strategy:
		"""
		The Context maintains a reference to one of the Strategy objects. The
		Context does not know the concrete class of a strategy. It should work
		with all strategies via the Strategy interface.
		"""

		return self._strategy

	@strategy.setter
	def strategy(self, strategy: Strategy) -> None:
		"""
		Usually, the Context allows replacing a Strategy object at runtime.
		"""

		self._strategy = strategy

	def do_some_business_logic(self) -> None:
		"""
		The Context delegates some work to the Strategy object instead of
		implementing multiple versions of the algorithm on its own.
		"""

		# ...

		print("Context: Sorting data using the strategy (not sure how it'll do it)")
		result = self._strategy.do_algorithm({})
		print(len(result))

		# ...

class Strategy(Zettelkasten):
	"""
	The Strategy interface declares operations common to all supported versions	of some algorithm.

	The Context uses this interface to call the algorithm defined by Concrete Strategies.
	"""

	# @abstractmethod
	def do_algorithm(self, data: List):
		pass

"""
Concrete Strategies implement the algorithm while following the base Strategy
interface. The interface makes them interchangeable in the Context.
"""

class import_csv(Strategy):
	def do_algorithm(self, data: Dict) -> Dict:
		file_path = 'C:/Users/Eugene/Documents/GitHub/zettelkasten_txt_to_csv/data/Zettelkasten v0_2.csv'
		return self.import_csv_zk(file_path = file_path)

class import_txt(Strategy):
	def do_algorithm(self, data: List) -> List:
		file_path = 'C:/Users/Eugene/Documents/GitHub/zettelkasten_txt_to_csv/data/00 Gardening zettlelkasten.txt'
		return self.import_txt_zk(file_path = file_path)


if __name__ == "__main__":
	# The client code picks a concrete strategy and passes it to the context.
	# The client should be aware of the differences between strategies to make the right choice.

	context = Context(import_csv())
	print("Client: Strategy is set to import csv.")
	context.do_some_business_logic()
	print()

	print("Client: Strategy is set to import txt.")
	context.strategy = import_txt()
	context.do_some_business_logic()