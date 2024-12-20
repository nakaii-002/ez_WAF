from sqlalchemy import Column
from sqlalchemy.types import CHAR, Integer, String, Text, DATETIME
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


BaseModel = declarative_base()
DB_CONNECT_STRING = 'mysql+mysqldb://root@localhost:13306/waf?charset=utf8'
engine = create_engine(DB_CONNECT_STRING, echo=False)
DB_Session = sessionmaker(bind=engine)


class Block(BaseModel):
    __tablename__ = 'block_behavior'

    TIME = Column(DATETIME(20), primary_key=True)
    IP = Column(CHAR(60), primary_key=True)
    PORT = Column(Integer, primary_key=True)
    TYPE = Column(String(20))
    METHOD = Column(String(20))
    URI = Column(Text)
    INFO = Column(Text)


def init_db():
    BaseModel.metadata.create_all(engine)

# def drop_db():
#     BaseModel.metadata.drop_all(engine)


def log_block(addr, req, block_type, src_time):
    if block_type == "not-white-uri" or block_type == "in-black-uri" or block_type == "uri" or block_type == "arg":
        info = req.uri
    elif block_type == "user-agent":
        info = req.headers['user-agent']
    elif block_type == "cookie":
        info = req.headers['cookie']
    elif block_type == "post-data":
        info = req.body
    elif block_type == "ml_detect":
        info = req.uri + "  |  " + ''.join(req.body)
    try:
        print("Attack detected! :   " + src_time + "   " + addr[0] + "   " + str(addr[1]) + "   " + block_type + "   "
              + req.method + "   " + req.uri + "   " + str(info))

        session = DB_Session()
        b = Block(TIME=src_time, IP=addr[0], PORT=addr[1], TYPE=block_type,
                  METHOD=req.method, URI=req.uri, INFO=info)
        session.add(b)
        session.commit()
        session.close()
    except Exception as e:
        print("DataBase related errors : " + str(e))


if __name__ == '__main__':
    init_db()
