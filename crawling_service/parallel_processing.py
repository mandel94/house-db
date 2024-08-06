import multiprocessing
from twisted.internet import reactor
from scrapy.utils.log import configure_logging
from scrapy.crawler import CrawlerRunner
from scrapy import crawler

def start_parallel_process(target, params):
    """This function creates and starts a parallel process using the 
    multiprocessing library.

    Args:
        target (function): The function to be executed in parallel.
        params (tuple): The parameters to be passed to the function."""
    process = multiprocessing.Process(target=target, args=(params,))
    process.start()
    return process


def parallel_task(func):
    def wrapper(*args, **kwargs):
        process = start_parallel_process(func, *args, **kwargs)
        process.join()
    return wrapper

