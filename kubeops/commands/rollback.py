import logging
import subprocess
import time
from kubernetes import client, config

logger = logging.getLogger(__name__)

def rollback_command(args) -> int:
    """Rolls back a specified Kubernetes deployment to its previous version and waits for stabilization."""
    namespace = args.namespace
    deployment_name = args.deployment
    
    logger.info(f"Rolling back deployment '{deployment_name}' in namespace '{namespace}'...")
    
    # We use subprocess to call kubectl rollout undo because the python kubernetes client 
    # doesn't have a native 'undo' method, and patching replica sets manually is error-prone.
    try:
        cmd = ["kubectl", "rollout", "undo", f"deployment/{deployment_name}", "-n", namespace]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"Rollback failed: {result.stderr}")
            return 1
            
        logger.info(f"Rollback initiated: {result.stdout.strip()}")
        
        # Verify rollback by waiting for it to stabilize
        from .deploy import wait_for_rollout
        try:
            config.load_kube_config()
            apps_v1 = client.AppsV1Api()
            logger.info("Waiting for rollback to complete...")
            # We wait up to 120 seconds for the rollback to finish
            if wait_for_rollout(apps_v1, namespace, deployment_name, timeout=120):
                logger.info(f"Rollback of '{deployment_name}' completed successfully.")
                return 0
            else:
                logger.error(f"Rollback of '{deployment_name}' failed to stabilize.")
                return 1
        except Exception as e:
            logger.error(f"Failed to verify rollback: {e}")
            return 1
            
    except FileNotFoundError:
        logger.error("kubectl not found in PATH. Cannot perform rollback.")
        return 1
    except Exception as e:
        logger.error(f"An error occurred during rollback: {e}")
        return 1
