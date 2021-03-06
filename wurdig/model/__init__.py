"""The application's model objects"""
import sqlalchemy as sa
from sqlalchemy import orm, schema, types
from sqlalchemy.sql import and_
from wurdig.model import meta

import datetime

def init_model(engine):
    """Call me before using any of the tables or classes in the model"""
    ## Reflected tables must be defined and mapped here
    #global reflected_table
    #reflected_table = sa.Table("Reflected", meta.metadata, autoload=True,
    #                           autoload_with=engine)
    #orm.mapper(Reflected, reflected_table)
    #
    sm = orm.sessionmaker(autoflush=True, autocommit=False, bind=engine)

    meta.engine = engine
    meta.Session = orm.scoped_session(sm)

def now():
    return datetime.datetime.now()

pages_table = schema.Table('pages', meta.metadata,
    schema.Column('id', types.Integer,
        schema.Sequence('page_seq_id', optional=True), primary_key=True),
    schema.Column('title', types.Unicode(255), default=u'Untitled Page'),
    schema.Column('slug', types.Unicode(125), nullable=False, unique=True),
    schema.Column('content', types.Text(), nullable=False),
    schema.Column('created_on', types.TIMESTAMP(), default=now()),
)

posts_table = schema.Table('posts', meta.metadata,
    schema.Column('id', types.Integer,
        schema.Sequence('post_seq_id', optional=True), primary_key=True),
    schema.Column('title', types.Unicode(255), default=u'Untitled Post'), 
    schema.Column('slug', types.Unicode(125), nullable=False, unique=True),
    schema.Column('content', types.Text(), nullable=False),
    schema.Column('comments_allowed', types.Boolean(), default=True),
    schema.Column('created_on', types.TIMESTAMP(), default=now(), index=True),
    schema.Column('draft', types.Boolean(), default=True),
    schema.Column('posted_on', types.TIMESTAMP(), index=True),
)

comments_table = schema.Table('comments', meta.metadata,
    schema.Column('id', types.Integer,
        schema.Sequence('comment_seq_id', optional=True), primary_key=True),
    schema.Column('post_id', types.Integer,
        schema.ForeignKey('posts.id'), nullable=False),
    schema.Column('content', types.Text(), nullable=False),
    schema.Column('name', types.Unicode(255), nullable=False),
    schema.Column('email', types.Unicode(255), nullable=False),
    schema.Column('url', types.Unicode(150), default=u''),
    schema.Column('created_on', types.TIMESTAMP(), default=now()),
    schema.Column('approved', types.Boolean(), default=False),
)

tags_table = schema.Table('tags', meta.metadata,
    schema.Column('id', types.Integer,
        schema.Sequence('tag_seq_id', optional=True), primary_key=True),
    schema.Column('name', types.Unicode(40), nullable=False, unique=True),
    schema.Column('slug', types.Unicode(40), nullable=False, unique=True),
)

poststags_table = schema.Table('posts_tags', meta.metadata,
    schema.Column('id', types.Integer,
        schema.Sequence('posttag_seq_id', optional=True), primary_key=True),
    schema.Column('post_id', types.Integer, schema.ForeignKey('posts.id')),
    schema.Column('tag_id', types.Integer, schema.ForeignKey('tags.id')),
)

class Page(object):
    pass

class Post(object):
    pass

class Comment(object):
    pass

class Tag(object):
    pass

orm.mapper(Comment, comments_table)
orm.mapper(Tag, tags_table, order_by='name')
orm.mapper(Page, pages_table, order_by='title')
orm.mapper(Post, posts_table, order_by='posted_on DESC', polymorphic_identity='posts', properties={
    'comments':orm.relation(Comment, backref='posts', cascade='all',order_by='created_on', 
                            primaryjoin=and_(
                                             posts_table.c.id==comments_table.c.post_id, 
                                             comments_table.c.approved==True
                                             )
                            ),
    'tags':orm.relation(Tag, secondary=poststags_table)
})
