# A simple FastAPI server that returns a  list of books.
import random
import time

from opentelemetry import trace
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Link
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor


from fastapi import FastAPI
from pydantic import BaseModel

tracer_provider = TracerProvider(resource=Resource.create({
    "SERVICE_NAME": "books_service",
}))
cloud_trace_exporter = CloudTraceSpanExporter(project_id="oval-cyclist-347918")
tracer_provider.add_span_processor(
    BatchSpanProcessor(cloud_trace_exporter)
)

trace.set_tracer_provider(tracer_provider)

tracer = trace.get_tracer(__name__)

app = FastAPI()

FastAPIInstrumentor().instrument_app(app)

class Book(BaseModel):
    id: int
    title: str


DATA = [{"id": 0, "title": "Harry Potter"}, {"id": 1, "title": "Lord of the Rings"}]


@app.get("/")
async def read_root():
    return {"Hello": "World"}


# Get book by id.
@app.get("/books/{book_id}", response_model=Book)
async def get_book(book_id: int):
    with tracer.start_as_current_span("get_book_by_id") as span:
        span.set_attribute("book_id", book_id)
        with tracer.start_as_current_span("pause_for_books"):
            time.sleep(random.random())
        with tracer.start_as_current_span("fetch_data"):
            time.sleep(random.random())
            return next((book for book in DATA if book["id"] == book_id), None)
