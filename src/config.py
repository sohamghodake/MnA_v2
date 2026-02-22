import os
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

class Neo4jConfig(BaseModel):
    uri: str = Field(default=os.getenv("NEO4J_URI", "bolt://localhost:7687"))
    user: str = Field(default=os.getenv("NEO4J_USER", "neo4j"))
    password: str = Field(default=os.getenv("NEO4J_PASSWORD", "password"))

class OllamaConfig(BaseModel):
    base_url: str = Field(default=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"))
    model: str = Field(default=os.getenv("OLLAMA_MODEL", "llama3:70b"))

class Config(BaseModel):
    neo4j: Neo4jConfig = Field(default_factory=Neo4jConfig)
    ollama: OllamaConfig = Field(default_factory=OllamaConfig)
    environment: str = Field(default=os.getenv("ENV", "development"))

settings = Config()
