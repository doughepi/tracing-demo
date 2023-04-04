# A FastAPI server that returns a list of customers and books they have checked out by id.
import random 
import time
import requests

from fastapi import FastAPI
from pydantic import BaseModel

from typing import List

from opentelemetry import trace
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Link
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor


BOOKS_SERVER = "http://localhost:8000/books"

# Create a tracer provider with a resource attached.
tracer_provider = TracerProvider(resource=Resource.create({
    "SERVICE_NAME": "customer_service",
}))

cloud_trace_exporter = CloudTraceSpanExporter(project_id="oval-cyclist-347918")
tracer_provider.add_span_processor(
    BatchSpanProcessor(cloud_trace_exporter)
)

trace.set_tracer_provider(tracer_provider)

tracer = trace.get_tracer(__name__)

RequestsInstrumentor().instrument()


app = FastAPI()

FastAPIInstrumentor().instrument_app(app)


class Customer(BaseModel):
    id: int
    name: str
    books: List[str]


DATA = [
    {"id": 0, "name": "John Doe", "books": [0, 1]},
    {"id": 1, "name": "Jane Doe", "books": [1]},
]


@app.get("/")
async def read_root():
    return {"Hello": "World"}


# Get customer by ID.
@app.get("/customers/{customer_id}", response_model=Customer)
async def get_customer(customer_id: int):
    with tracer.start_as_current_span("get_customer_by_id") as span:
        span.set_attribute("customer_id", customer_id)
        with tracer.start_as_current_span("pause_for_customers"):
            time.sleep(random.random())
        with tracer.start_as_current_span("fetch_data") as fetch_data_span:
            time.sleep(random.random())
            fetch_data_span.add_event("got_data")

            customer = next((customer for customer in DATA if customer["id"] == customer_id), None)
            if customer is not None:
                books = []
                for book_id in customer["books"]:

                    with tracer.start_as_current_span("check_policy") as check_policy_span:
                        check_policy_span.set_attribute("repo", "")
                        check_policy_span.set_attribute("ref", "")
                        check_policy_span.set_attribute("action", "read")
                        check_policy_span.set_attribute("user", "user")
                        check_policy_span.set_attribute("resource", "resource")

                        

                        book = requests.get(f"{BOOKS_SERVER}/{book_id}").json()
                        books.append(book["title"])
            return {
                "id": customer["id"],
                "name": customer["name"],
                "books": books,
            }
            

            
