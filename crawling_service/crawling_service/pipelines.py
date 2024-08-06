# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import json
import logging
from .data_modeling import generate_sql_schema
from .items import House, Address
import sqlite3

ITEMS = [House, Address]


def with_polyseme(item):
    polyseme = "polyseme_id"
    item["global_id"] = polyseme
    return item


class AddPolysemePipeline:
    def process_item(self, item, spider):
        return with_polyseme(item)


class WriteToJsonLines:
    def open_spider(self, spider):
        logging.info("Opening items.jl file")
        self.file = open("items.jl", "w")

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(ItemAdapter(item).asdict()) + "\n"
        self.file.write(line)
        return item


class WriteToSQLite:
    def open_spider(self, spider):
        # Create connector to DB
        self.conn = sqlite3.connect("house.db")
        self.cursor = self.conn.cursor()
        for item in ITEMS:
            sql_schema = generate_sql_schema(item)
            self.create_table(sql_schema)

    def process_item(self, item, spider):
        self.insert_in_db(item)
        return item

    def close_spider(self, spider):
        logging.info("Closing connection to DB")
        self.conn.close()

    def create_table(self, sql_schema):
        self.cursor.execute(sql_schema)
        self.conn.commit()
        res = self.cursor.execute("SELECT name FROM sqlite_master")
        # Check that result is not empty
        logging.info(f"Check if table was created: {res.fetchall()}")

    def insert_in_db(self, item):
        # Class name is the table name
        table_name = item.__class__.__name__.lower()
        fields = item.keys()
        values = [item[field] for field in fields]
        columns = ", ".join(fields)
        placeholders = ", ".join("?" * len(fields))
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        self.cursor.execute(query, values)
        self.conn.commit()


class HousePipeline:
    def process_item(self, item, spider):
        return item

    def close_spider(self, spider):
        pass


class ItemPipeline:
    def process_item(self, item, spider):
        return item
