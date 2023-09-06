from sqlalchemy import MetaData, Table, Column, String, Integer, ForeignKey

metadata = MetaData()

file = Table(
    "file",
    metadata,
    Column("id", String, primary_key=True),
    Column("fileName", String, nullable=False),
    Column("converted_id", String, nullable=False),
    Column("stage", Integer, ForeignKey("stage.id")),
)

stage = Table(
    "stage",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("stepOfDevelopment", String),
)