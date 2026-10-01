# Cloud Event Processing Platform

Cloud Event Processing Platform is a production-oriented project demonstrating how to design, build, deploy, monitor, and operate a distributed, event-driven backend platform using Python, Apache Kafka, and Kubernetes.

## Architecture

### System Architecture

The platform follows a microservices architecture communicating asynchronously via Apache Kafka.

```mermaid
flowchart TD
    subgraph Clients
        Client([Client Applications])
    end

    subgraph Microservices
        OrderAPI[Order Service<br>FastAPI]
        PaymentAPI[Payment Service<br>FastAPI]
        InventoryAPI[Inventory Service<br>FastAPI]
    end

    subgraph Messaging
        Kafka[Apache Kafka<br>Event Broker]
    end

    subgraph Storage
        Postgres[(PostgreSQL)]
        Redis[(Redis)]
    end
    
    subgraph Infrastructure
        LocalStack[LocalStack<br>AWS Mocks]
    end

    Client -->|REST API| OrderAPI
    Client -->|REST API| PaymentAPI
    Client -->|REST API| InventoryAPI

    OrderAPI <-->|Pub/Sub| Kafka
    PaymentAPI <-->|Pub/Sub| Kafka
    InventoryAPI <-->|Pub/Sub| Kafka

    OrderAPI -->|SQL| Postgres
    PaymentAPI -->|SQL| Postgres
    InventoryAPI -->|Redis Protocol| Redis

    Microservices -.->|Optional| LocalStack
```

### Event Flow (Choreography)

When an order is created, the system uses an event-driven choreography pattern to process inventory and payment in parallel.

```mermaid
sequenceDiagram
    participant C as Client
    participant OS as Order Service
    participant K as Kafka Broker
    participant IS as Inventory Service
    participant PS as Payment Service

    C->>OS: POST /orders (Create Order)
    OS->>OS: Save Order (Status: PENDING)
    OS->>K: Publish 'OrderCreated' (orders.events)
    OS-->>C: 201 Created (Order ID)

    par Inventory Processing
        K->>IS: Consume 'OrderCreated'
        IS->>IS: Process Inventory
        alt Success
            IS->>K: Publish 'InventoryResult' (SUCCESS)
        else Failure
            IS->>K: Publish 'InventoryResult' (FAILED)
        end
    and Payment Processing
        K->>PS: Consume 'OrderCreated'
        PS->>PS: Process Payment
        alt Success
            PS->>K: Publish 'PaymentResult' (SUCCESS)
        else Failure
            PS->>K: Publish 'PaymentResult' (FAILED)
        end
    end

    K->>OS: Consume 'InventoryResult' & 'PaymentResult'
    OS->>OS: Update Order State (CONFIRMED / CANCELLED)
```

- **Language:** Python
- **Framework:** FastAPI
- **Messaging:** Apache Kafka
- **Database:** PostgreSQL, Redis
- **Infrastructure:** Docker, Kubernetes, LocalStack
- **Automation:** GitHub Actions, custom `kubeops` CLI

## Structure

- `/services` - Microservices (Order, Payment, Inventory)
- `/kubeops` - Custom CLI for Kubernetes operations
- `/infrastructure` - LocalStack and Terraform configuration
- `/deploy` - Helm charts and Kubernetes manifests
- `/docs` - Project documentation

## Getting Started

*(Documentation to be completed)*

## Local Development Environment

### Prerequisites
- Docker and Docker Compose
- Python 3.12+
- Poetry (or pip)

### Startup Procedure
To build and start the complete local application including infrastructure (PostgreSQL, Redis, Kafka, LocalStack) and all microservices (Order, Payment, Inventory):
```bash
docker compose up --build -d
```
Check if all services and infrastructure containers are healthy:
```bash
docker compose ps
```

### Shutdown/Reset Procedure
To stop the services:
```bash
docker compose stop
```
To completely remove the services and their data (reset state):
```bash
docker compose down -v
```
