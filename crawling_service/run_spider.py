from flask import Flask, request, jsonify
import multiprocessing
from twisted.internet import reactor
from twisted.internet.task import deferLater
from scrapy.utils.log import configure_logging
from spider_factory import SpiderFactory
from scrapy import crawler



app = Flask(__name__)

sources = ["idealista"]

def create_spider_task(spider, params):
    def start_task():
        runner = crawler.CrawlerRunner()
        d = runner.crawl(spider, params)
        d.addBoth(lambda _: reactor.stop())
        reactor.run()
    return start_task

@app.route('/scrape/onsales', methods=['POST'])
def onsales():
    try:
        data = request.get_json()
        where = data["where"]
        processes = []
        for source in sources:
            spider = SpiderFactory.create_spider("idealista", source)
            task = create_spider_task(spider, data)
            processes.append(multiprocessing.Process(target=task))
        for process in processes:
            process.start()
        for process in processes:
            process.join()    
        return jsonify({"message": "Crawling completed"})
    except Exception as e:
        return jsonify({"message": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
