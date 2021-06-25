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
    get_notes = List(NotesType, search=graphene.String())

    def resolve_get_notes(self, info, search=None, **kwargs):
        session = session_local()
        result_query = session.query(model.Notes)
        if search:
            result_query = result_query.filter(Notes.title.ilike(search))
        return result_query.all()


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


class DeleteNote(Mutation):
    id = graphene.Int()

    class Arguments:
        id = graphene.String()

    def mutate(self, info, id):
        session = session_local()
        delete_note = session.query(Notes).get(id)
        session.delete(delete_note)
        session.commit()
        return DeleteNote(id=id)


class Mutation(ObjectType):
    create_note = CreateNote.Field()
    delete_note = DeleteNote.Field()


"""
@app.delete("/todo/{id}", tags=["todos"])
async def delete_todo(id: int):
    note = db.session.query(Note).get(id)
    db.session.delete(note)
    db.session.commit()
    return note
"""

app = FastAPI()
app.add_route("/", GraphQLApp(
    schema=Schema(query=View, mutation=Mutation)
)
              )
