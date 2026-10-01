import logging
from kubernetes import client, config
from kubernetes.client.rest import ApiException

logger = logging.getLogger(__name__)

def audit_pods(namespace: str) -> int:
    """Scans pods in a namespace for issues like CrashLoopBackOff, missing probes, missing resource limits, and failed states."""
    try:
        config.load_kube_config()
        v1 = client.CoreV1Api()
    except Exception as e:
        logger.error(f"Failed to connect to Kubernetes API: {e}")
        return 1

    issues_found = 0

    try:
        pods = v1.list_namespaced_pod(namespace)
        for pod in pods.items:
            pod_name = pod.metadata.name
            
            # Check Pod Phase
            if pod.status.phase == "Pending":
                logger.warning(f"[AUDIT] Pod {pod_name} is in Pending state.")
                issues_found += 1
            elif pod.status.phase == "Failed":
                logger.warning(f"[AUDIT] Pod {pod_name} has Failed.")
                issues_found += 1

            # Check Container Statuses for CrashLoopBackOff
            if pod.status.container_statuses:
                for status in pod.status.container_statuses:
                    if status.state.waiting and status.state.waiting.reason == "CrashLoopBackOff":
                        logger.error(f"[AUDIT] Pod {pod_name} container {status.name} is in CrashLoopBackOff!")
                        issues_found += 1
                    
                    if status.restart_count > 5:
                        logger.warning(f"[AUDIT] Pod {pod_name} container {status.name} has high restart count: {status.restart_count}")
                        issues_found += 1

            # Check Resource Limits/Requests & Probes & Tags
            for container in pod.spec.containers:
                if not container.resources or not container.resources.limits:
                    logger.warning(f"[AUDIT] Pod {pod_name} container {container.name} is missing resource limits.")
                    issues_found += 1
                
                if not container.resources or not container.resources.requests:
                    logger.warning(f"[AUDIT] Pod {pod_name} container {container.name} is missing resource requests.")
                    issues_found += 1
                    
                if container.image.endswith(":latest"):
                    logger.warning(f"[AUDIT] Pod {pod_name} container {container.name} is using 'latest' image tag.")
                    issues_found += 1
                
                if not container.liveness_probe:
                    logger.warning(f"[AUDIT] Pod {pod_name} container {container.name} is missing a liveness probe.")
                    issues_found += 1
                
                if not container.readiness_probe:
                    logger.warning(f"[AUDIT] Pod {pod_name} container {container.name} is missing a readiness probe.")
                    issues_found += 1
                    
        # Check PVCs
        pvcs = v1.list_namespaced_persistent_volume_claim(namespace)
        for pvc in pvcs.items:
            if pvc.status.phase != "Bound":
                logger.warning(f"[AUDIT] PVC {pvc.metadata.name} is not Bound (Current phase: {pvc.status.phase}).")
                issues_found += 1

        if issues_found == 0:
            logger.info("Audit completed: No issues found. Workload quality is excellent.")
        else:
            logger.warning(f"Audit completed: Found {issues_found} potential issue(s).")

        return 0 if issues_found == 0 else 1

    except ApiException as e:
        logger.error(f"Failed to retrieve pods for audit: {e}")
        return 1

def audit_command(args) -> int:
    """CLI entrypoint for triggering a Kubernetes workload audit in the specified namespace."""
    namespace = getattr(args, 'namespace', 'default')
    logger.info(f"Executing Kubernetes audit on namespace: {namespace}...")
    return audit_pods(namespace)
