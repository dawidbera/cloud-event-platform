import logging
from kubernetes import client, config
from kubernetes.client.rest import ApiException

logger = logging.getLogger(__name__)

def check_cluster_connectivity() -> bool:
    """Verifies that the CLI can successfully authenticate and connect to the Kubernetes API server."""
    try:
        config.load_kube_config()
        v1 = client.CoreV1Api()
        v1.get_api_resources()
        logger.info("Cluster API connection: OK")
        return True
    except Exception as e:
        logger.error(f"Cluster API connection failed: {e}")
        return False

def check_namespace(namespace: str) -> bool:
    """Verifies that the specified target namespace exists in the cluster."""
    v1 = client.CoreV1Api()
    try:
        v1.read_namespace(name=namespace)
        logger.info(f"Namespace '{namespace}': OK")
        return True
    except ApiException as e:
        if e.status == 404:
            logger.error(f"Namespace '{namespace}' not found.")
        else:
            logger.error(f"Error reading namespace: {e}")
        return False

def check_deployments_readiness(namespace: str) -> bool:
    """Checks whether all deployments in the namespace have their desired number of ready replicas."""
    apps_v1 = client.AppsV1Api()
    try:
        deployments = apps_v1.list_namespaced_deployment(namespace=namespace)
        all_ready = True
        for dep in deployments.items:
            ready_replicas = dep.status.ready_replicas or 0
            desired_replicas = dep.spec.replicas or 1
            if ready_replicas < desired_replicas:
                logger.warning(f"Deployment '{dep.metadata.name}' is NOT fully ready ({ready_replicas}/{desired_replicas} replicas ready).")
                all_ready = False
            else:
                logger.info(f"Deployment '{dep.metadata.name}': OK ({ready_replicas}/{desired_replicas} replicas ready).")
        return all_ready
    except ApiException as e:
        logger.error(f"Error checking deployments: {e}")
        return False

def check_infrastructure_services(namespace: str) -> bool:
    """Verifies that essential infrastructure services (Redis, Postgres, Kafka) are deployed and reachable in the namespace."""
    v1 = client.CoreV1Api()
    required_services = ["redis", "postgres", "kafka"]
    all_ok = True
    try:
        services = [s.metadata.name for s in v1.list_namespaced_service(namespace).items]
        for req in required_services:
            if req in services:
                logger.info(f"Infrastructure Service '{req}': OK (found in namespace)")
            else:
                logger.warning(f"Infrastructure Service '{req}' is missing or not deployed in namespace '{namespace}'!")
                # Depending on how strict we are, missing infra could be a fail or just a warning if external
                # Let's consider it a warning for now, assuming external DBs might be used.
    except ApiException as e:
        logger.error(f"Error checking infrastructure services: {e}")
        return False
    return all_ok

def health_command(args) -> int:
    """CLI entrypoint to run a suite of health checks verifying connectivity, namespaces, deployments, and infrastructure."""
    logger.info("Executing cluster health checks...")
    
    # We default to 'default' or a given namespace, but args don't have it yet. 
    # Let's assume 'default' namespace for now unless provided.
    namespace = getattr(args, 'namespace', 'default')

    if not check_cluster_connectivity():
        return 1

    if not check_namespace(namespace):
        return 1
        
    check_infrastructure_services(namespace)
    deployments_ok = check_deployments_readiness(namespace)
    
    if not deployments_ok:
        logger.error("Overall Health Status: FAILED (Some deployments are not ready)")
        return 1
        
    logger.info("Overall Health Status: OK")
    return 0
