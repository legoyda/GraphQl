import graphene
from graphene import Int, String, Schema, List, ObjectType
from fastapi import FastAPI
from starlette.graphql import GraphQLApp
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import model

engine = create_engine("sqlite:///back.db")
session_local = sessionmaker(engine)
model.Base.metadata.create_all(engine)


class NotesType(ObjectType):
    id = Int()
    title = String()
    description = String()


class Query(ObjectType):
    hello = String(name=String(default_value="Stranger"))
    get_notes = List(NotesType)

    def resolve_get_notes(self,info):
        session = session_local()
        result = session.query(model.Notes).all()\

        return result


app = FastAPI()
app.add_route("/", GraphQLApp(schema=Schema(query=Query)))
