import pyreadstat
import attr
from pandas import DataFrame
import sqlalchemy


@attr.s
class Feeder:
    conn_string = attr.ib()
    data_file = attr.ib()
    engine = sqlalchemy.engine.create_engine(conn_string, pool_recycle=3600)

    def feed(self):
        dataframe, meta = pyreadstat.read_sav(self.data_file)
        data = dataframe.drop(dataframe.columns[269:525], axis=1).drop(dataframe.columns[526:], axis=1)
        weights = dataframe.drop(dataframe.columns[1:268], axis=1)
        # df(dataframe).to_sql("raw_data", self.engine, if_exists='replace', index=False)
        DataFrame(data).to_sql("questionnaire_data", self.engine, if_exists='replace', index=False)
        DataFrame(weights).to_sql("weights_data", self.engine, if_exists='replace', index=False)


string_file = open("strings_file", 'r')
Feeder(conn_string=string_file.readline(), data_file=string_file.readline()) \
    .feed()
