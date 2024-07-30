from flask import Flask, request, jsonify
from scrapy.utils.log import configure_logging
from scrapy import crawler
from scrapy.utils.project import get_project_settings
import logging
from strategy import SearchContext, IdealistaBaseStrategy, ImmobiliareSitemapStrategy


app = Flask(__name__)

spiders = ["immobiliare"]


@app.route("/")
def index():
    return "Crawling Service!"


@app.route("/crawl/onsale", methods=["GET"])
def onsales():
    try:
        where = request.args.get("where")
        publication_type = "onsale"
        settings = get_project_settings()
        search_ctx = SearchContext(ImmobiliareSitemapStrategy())
        configure_logging(settings)
        crawler_process = crawler.CrawlerProcess(settings)
        crawler_process.crawl(
            search_ctx.provide_search_spider(),
            where=where,
            publication_type=publication_type,
        )
        crawler_process.start()
        return jsonify({"message": "Crawling completed!"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500


if __name__ == "__main__":
    # Accept json data
    app.run(host="0.0.0.0", port=5000, debug=True)
