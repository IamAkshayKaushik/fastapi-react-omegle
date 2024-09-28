from diagrams import Cluster, Diagram
from diagrams.onprem.client import Users
from diagrams.onprem.compute import Server
from diagrams.onprem.network import Nginx
from diagrams.onprem.container import Docker
from diagrams.onprem.database import PostgreSQL
from diagrams.onprem.monitoring import Prometheus, Grafana
from diagrams.onprem.inmemory import Redis
from diagrams.programming.framework import Django, React
from diagrams.programming.language import Python

with Diagram("Omegle-Like Random Video Chat App", show=False):
    users = Users("users")

    with Cluster("Frontend"):
        frontend = React("web app")

    with Cluster("Backend"):
        backend = Django("backend")
        matchmaking = Python("matchmaking")
        celery = Python("background tasks")
        channels = Python("WebSocket")

    with Cluster("Infrastructure"):
        load_balancer = Nginx("load balancer")
        server = Server("web server")
        containers = [Docker("container 1"), Docker("container 2")]

    with Cluster("Database"):
        db = PostgreSQL("user logs")

    with Cluster("Real-time Communication"):
        redis = Redis("in-memory store")

    with Cluster("Monitoring"):
        prometheus = Prometheus("metrics")
        grafana = Grafana("monitoring dashboard")

    users >> frontend >> load_balancer >> server >> backend >> db
    users >> frontend >> channels >> matchmaking >> redis
    backend >> celery
    prometheus >> grafana
    redis >> prometheus
    server >> containers
