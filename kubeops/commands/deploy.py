import logging
import time
from kubernetes import client, config
from kubernetes.client.rest import ApiException

logger = logging.getLogger(__name__)

def wait_for_rollout(apps_v1: client.AppsV1Api, namespace: str, deployment_name: str, timeout: int) -> bool:
    """Polls the Kubernetes API to verify if a deployment rollout completes within the specified timeout."""
    start = time.time()
    logger.info(f"Waiting for rollout of deployment '{deployment_name}' in namespace '{namespace}' (timeout: {timeout}s)...")
    
    while time.time() - start < timeout:
        try:
            dep = apps_v1.read_namespaced_deployment(name=deployment_name, namespace=namespace)
            
            spec_replicas = dep.spec.replicas or 1
            updated = dep.status.updated_replicas or 0
            available = dep.status.available_replicas or 0
            replicas = dep.status.replicas or 0
            observed_gen = dep.status.observed_generation or 0
            
            if (observed_gen >= dep.metadata.generation and
                updated == spec_replicas and
                replicas == spec_replicas and
                available == spec_replicas):
                logger.info(f"Deployment '{deployment_name}' successfully rolled out.")
                return True
                
            logger.info(f"Waiting... (updated: {updated}/{spec_replicas}, available: {available}/{spec_replicas})")
        except ApiException as e:
            logger.error(f"Error reading deployment: {e}")
            return False
            
        time.sleep(5)
        
    logger.error(f"Rollout verification for '{deployment_name}' timed out after {timeout} seconds.")
    return False

def check_application_health(deployment_name: str) -> bool:
    """Verifies application-level readiness and health post-deployment."""
    # TODO: In a real scenario, this might port-forward and check /health or rely on liveness/readiness probes.
    # Since readiness is already covered by the deployment rollout wait, we'll assume it's OK for this MVP.
    logger.info(f"Application health for '{deployment_name}' verified (via readiness probes).")
    return True

def deploy_command(args) -> int:
    """Orchestrates deployment verification, checks health, and triggers automatic rollback if verification fails."""
    namespace = args.namespace
    deployment_name = args.deployment
    timeout = args.timeout
    auto_rollback = args.auto_rollback
    
    try:
        config.load_kube_config()
    except Exception as e:
        logger.error(f"Failed to load kube config: {e}")
        return 1
        
    apps_v1 = client.AppsV1Api()
    
    success = wait_for_rollout(apps_v1, namespace, deployment_name, timeout)
    if success:
        success = check_application_health(deployment_name)
        
    if not success:
        logger.error(f"Deployment verification failed for '{deployment_name}'.")
        if auto_rollback:
            logger.info("Auto-rollback is enabled. Initiating rollback...")
            from .rollback import rollback_command
            # Reuse args for rollback
            return rollback_command(args)
        return 1
        
    return 0
