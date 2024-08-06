from flask import Flask, request, jsonify, render_template
from scrapy.utils.log import configure_logging
from scrapy import crawler
from scrapy.utils.project import get_project_settings
from storage import get_db_connection
from strategy import SearchContext, IdealistaStrategy, ImmobiliareStrategy
from crawling_service.items import House


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
        search_ctx = SearchContext(ImmobiliareStrategy())
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


@app.route("/explore/houses", methods=["GET"])
def house_tables():
    conn = get_db_connection(db_name="house.db")
    try:
        with conn:
            houses = conn.execute("SELECT * FROM house").fetchall()
        column_headers = [
            desc[1] for desc in conn.execute("PRAGMA table_info(house)").fetchall()
        ]
        # The command above extracts the column names from the table schema, using the PRAGMA table_info command.
        # PRAGMA commands are special commands that provide information about the database. They are not SQL commands, but
        # rather SQLite-specific commands. For a complete list of PRAGMA commands, refer to the official SQLite documentation
        # at https://www.sqlite.org/pragma.html.
        # return jsonify({"headers": column_headers})
        return (
            render_template(
                "bootstrap_table.html",
                title="Explore house table",
                data=houses,
                headers=column_headers,
            ),
            200,
        )
    except Exception as e:
        return jsonify({"message": str(e)}), 404
    
@app.route("/explore/addresses", methods=["GET"])
def address_tables():
    conn = get_db_connection(db_name="house.db")
    try:
        with conn:
            addresses = conn.execute("SELECT * FROM address").fetchall()
        column_headers = [
            desc[1] for desc in conn.execute("PRAGMA table_info(address)").fetchall()
        ]
        return (
            render_template(
                "bootstrap_table.html",
                title="Explore address table",
                data=addresses,
                headers=column_headers,
            ),
            200,
        )
    except Exception as e:
        return jsonify({"message": str(e)}), 404


if __name__ == "__main__":
    # Accept json data
    app.run(host="0.0.0.0", port=5000, debug=True)
