# THIS MODULE IMPLEMENTS THE STRATEGY PATTERN FROM GANG OF FOUR
# --> https://refactoring.guru/design-patterns/strategy

from abc import ABC, abstractmethod
from crawling_service.spiders.spiders import IdealistaSpider, ImmobiliareSpider




class SearchStrategy(ABC):
    """Search Strategy Interface"""
    @abstractmethod
    def get_spider(self):
        raise NotImplementedError("Method search not implemented")
    

class IdealistaStrategy(SearchStrategy):
    """Idealista Search Strategy"""
    def get_spider(self):
        return IdealistaSpider
    

class ImmobiliareStrategy(SearchStrategy):
    """Immobiliare Search Strategy"""
    def get_spider(self):
        return ImmobiliareSpider


class SearchContext:
    """Apply the strategy pattern to the search

    Same purpose: Collect data on houses 
    Different strategy: Based on the website. Even for the same website, the search strategy can change.

    Args:
        search_strategy (SearchStrategy): The search strategy to use
    
    Returns:
        Spider: The spider for the client to use
    
    https://refactoring.guru/design-patterns/strategy 
    """
    def __init__(self, search_strategy):
        self.search_strategy = search_strategy

    def provide_search_spider(self):
        return self.search_strategy.get_spider()