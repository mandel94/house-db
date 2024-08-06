import scrapy
from .items import House
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



def generate_sql_schema(item):
    """Generate SQL schema from an item class"""
    try:
        table_name = item.__name__.lower()
        fields = item.fields.keys()
        sql_columns = []
        for field in fields:
            field_type = "TEXT"
            sql_columns.append(f"{field} {field_type}")   
        sql_columns_str = ",\n    ".join(sql_columns)
        sql_schema = f"CREATE TABLE IF NOT EXISTS {table_name} (\n    {sql_columns_str}\n);"
        
        return sql_schema
    except Exception as e:
        logger.error(f"Error generating SQL schema: {str(e)}", exc_info=True)

