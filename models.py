from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
from sqlalchemy import MetaData
from flask_sqlalchemy import SQLAlchemy

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)

class User(db.Model,SerializerMixin):
    __tablename__ = "user_table"
    serialize_rules = ("-blog_list.user_object",)
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    blog_list = db.relationship("Blog", back_populates="user_object")

    @validates("name")
    def validate_name(self, key: str, name: str):
        if len(name) < 1:
            raise ValueError("name must be at least 1 character")
        return name

    def to_dict(self):
        return {"id": self.id, "name": self.name}


class Blog(db.Model, SerializerMixin):
    __tablename__ = "blog_table"
    serialize_rules = ("-user_object.blog_list", "-comment_list.blog_object",)
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user_table.id"))
    content = db.Column(db.String)
    title = db.Column(db.String)

    user_object = db.relationship("User", back_populates="blog_list")

    comment_list = db.relationship("Comment", back_populates="blog_object")


    @validates('content')
    def validate_content(self, key:str, content:str):
        if len(content.split(' ')) < 5:
            raise ValueError('Blogs must be at least 5 words')
        return content

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "content": self.content,
            "title": self.title,
        }


class Comment(db.Model, SerializerMixin):

    serialize_rules = ("-blog_object.comment_list")
    
    __tablename__ = "comment_table"
    id = db.Column(db.Integer, primary_key = True)
    blog_id = db.Column(db.Integer, db.ForeignKey('blog_table.id'))
    content = db.Column(db.String)

    blog_object = db.relationship("Blog", back_populates="comment_list")