import graphene
from graphene import Int, String, Schema, List, ObjectType, Field, Mutation
from fastapi import FastAPI
from starlette.graphql import GraphQLApp
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import model
from model import Base, Notes

engine = create_engine("sqlite:///back.db")
session_local = sessionmaker(engine)
model.Base.metadata.create_all(engine)


class NotesType(ObjectType):
    id = Int(required=True)
    title = String(required=True)
    description = String(required=True)


class View(ObjectType):
    get_notes = List(NotesType)

    def resolve_get_notes(self, info):
        session = session_local()
        result = session.query(model.Notes).all()
        return result


class CreateNote(Mutation):
    id = graphene.Int()
    title = graphene.String()
    description = graphene.String()

    class Arguments:
        title = graphene.String()
        description = graphene.String()

    def mutate(self, info, title, description):
        new_note = Notes(title=title, description=description)
        session = session_local()
        session.add(new_note)
        session.commit()
        return CreateNote(id=new_note.id, title=new_note.title, description=new_note.description)


class Mutation(ObjectType):
    create_note = CreateNote.Field()

"""
class DeleteNote(Mutation):
    id = graphene.Int()
    title = graphene.String()
    description = graphene.String()

    class Arguments:
        id = graphene.Int()

        def mutate(self, id):
            session = session_local()
            note = session.query(Notes).get(id)
            session.delete(note)
            session.commit()
            return DeleteNote(id=note.id)


class DeletNote(ObjectType):
    delete_note = DeleteNote.id
"""

app = FastAPI()
app.add_route("/", GraphQLApp(
    schema=Schema(query=View, mutation=Mutation)
)
              )
