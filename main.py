from fastapi import FastAPI,status,Depends,HTTPException
from pydantic import BaseModel, Field,ConfigDict
import models
from database import Base,engine,get_db
from sqlalchemy.orm import Session
from sqlalchemy import select

Base.metadata.create_all(bind=engine)
app=FastAPI()

class TaskCreate(BaseModel):
    #id: int
    title:str = Field(min_length=1,max_length=100)
    description:str|None = Field(default=None,max_length=100)
    completed:bool = False

    model_config=ConfigDict(from_attributes=True)

class TaskResponse(TaskCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)

class TaskUpdate(BaseModel):
    title:str| None = Field(default=None,min_length=1,max_length=100)
    description:str|None = Field(default=None,max_length=100)
    completed:bool | None = None

@app.get("/health")
def health_check():
    return {"status":"ok"}

@app.post("/tasks",status_code=status.HTTP_201_CREATED,response_model=TaskResponse,)
def create_task(task:TaskCreate,db: Session=Depends(get_db)):
    db_task = models.Task(**task.model_dump())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    return db_task

@app.get("/tasks",response_model=list[TaskResponse])
def lis_tasks(completed:bool|None=None,db: Session=Depends(get_db)):
    statement = select(models.Task)

    if completed is not None:
        statement = statement.where(models.Task.completed == completed)

    return db.scalars(statement).all()

@app.get("/tasks/{task_id}",response_model=TaskResponse)
def get_task(task_id:int,db:Session=Depends(get_db)):
    task = db.get(models.Task,task_id)
    if task is None:
        raise HTTPException(status_code=404,detail ="Task not found")
    return task

@app.patch("/tasks/{task_id}",response_model=TaskResponse)
def update_task(task_id:int,task_update:TaskUpdate,db:Session=Depends(get_db)):
    task = db.get(models.Task,task_id)
    if task is None:
        raise HTTPException(status_code=404,detail="Task Not Found")
    changes = task_update.model_dump(exclude_unset=True)

    for field,value in changes.items():
        setattr(task,field,value)

    db.commit()
    db.refresh(task)

    return task

@app.delete("/tasks/{task_id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int,db:Session=Depends(get_db)):
    task = db.get(models.Task,task_id)

    if task is None:
        raise HTTPException(status_code=404,detail="Task Not Found")
    db.delete(task)
    db.commit()
