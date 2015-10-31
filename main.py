#!/usr/bin/python
# encoding:utf-8
import os.path
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import torndb  # need easy_install torndb

# import tornado.auth
# import unicodedata
# from tornado import gen
# from tornado.web import asynchronous
from tornado.options import define, options
from datetime import datetime

# defines, they should be used config file to define,next
define("port", default=8002, help="run on the given port", type=int)
define("host", default="127.0.0.1:3306", help="database host")
define("db", default="pricipal_data", help="database name")
define("user", default="root", help="database user")
define("pw", default="cynztt", help="database password")


class Application(tornado.web.Application):
    """ application"""

    def __init__(self):
        handlers = [
            (r'/', DateHandler), ]

        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            debug=True
        )

        tornado.web.Application.__init__(self, handlers, **settings)
        # database define
        self.db = torndb.Connection(
            host="localhost",
            database="pricipal_data",
            user="root",
            password="cynztt",
            charset="utf8"
        )


class DateHandler(tornado.web.RequestHandler):

    @property
    def db(self):
        return self.application.db

    @property
    def current_year(self):
        """Get current year"""
        return int(datetime.now().strftime('%Y'))

    def get(self):
        sql = "SELECT TIMESTAMPDIFF(DAY,writer_date,reply_date) as diff_date,writer_date,reply_date FROM writer_reply WHERE extract(YEAR FROM writer_date)>='2015' ORDER BY diff_date DESC"
        # total_num = self.contents_count_by_year(first_year=2005)
        # text = '<h1>%s</h1>' % total_num
        results = self.decade_num()
        # self.write(str(results[0]))
        # self.write(text)
        # year_values = []
        # for result in results:
        #     year_values.append({'year': result['y'],'value': result['num']}
        #         )
        # year = results[0]['y']
        # print year_values
        self.render('index.html', results=results )

    def contents_count_by_year(self, first_year=2005, last_year=0):
        """
        to calculate the total number of the contents
        first_year is the year to start to count, which is 2005 in the database, and default is 2005
        last_year is the current year
        """
        if not last_year:
            last_year = self.current_year
        sql = " SELECT COUNT(*) as num FROM writer_reply WHERE EXTRACT(YEAR FROM writer_date) BETWEEN %s AND %s" % (
            first_year, last_year)
        return self.db.query(sql)[0]['num']

    def decade_num(self):
        """show decade number"""
        current_year = self.current_year
        first_year = current_year - 10  # Just show ten years data
        sql = 'select YEAR(writer_date) as y,count(id) as num from writer_reply  where YEAR(writer_date) between %s and %s group by Year(writer_date) ' % (
            first_year, current_year)
        results = self.db.query(sql)
        return results


def main():
    """main"""
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()
