from prometheus_client import Counter, Histogram

# Custom metrics for event processing
EVENTS_PROCESSED = Counter(
    "app_events_processed_total",
    "Total number of events processed",
    ["event_type", "service"]
)

EVENTS_FAILED = Counter(
    "app_events_failed_total",
    "Total number of failed event processings",
    ["event_type", "service"]
)

EVENTS_RETRIED = Counter(
    "app_events_retried_total",
    "Total number of events retried",
    ["event_type", "service"]
)

EVENT_PROCESSING_LATENCY = Histogram(
    "app_event_processing_seconds",
    "Time spent processing an event",
    ["event_type", "service"],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 5.0, 10.0]
)
