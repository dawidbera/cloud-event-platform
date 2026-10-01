import logging
import json
import datetime
from kubernetes import client, config

logger = logging.getLogger(__name__)

def generate_report(namespace: str, format: str) -> str:
    """Retrieves cluster state and compiles a summary report of resources and critical issues in either JSON or Markdown format."""
    try:
        config.load_kube_config()
        v1 = client.CoreV1Api()
        apps_v1 = client.AppsV1Api()
    except Exception as e:
        return f"Error connecting to cluster: {e}"
        
    report_data = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "namespace": namespace,
        "resources_checked": {
            "pods": 0,
            "deployments": 0
        },
        "critical_problems": [],
        "warnings": [],
        "recommendations": []
    }
    
    # Check Deployments
    try:
        deployments = apps_v1.list_namespaced_deployment(namespace)
        report_data["resources_checked"]["deployments"] = len(deployments.items)
        for dep in deployments.items:
            ready = dep.status.ready_replicas or 0
            desired = dep.spec.replicas or 1
            if ready < desired:
                report_data["critical_problems"].append(f"Deployment {dep.metadata.name} has missing replicas ({ready}/{desired})")
                report_data["recommendations"].append(f"Check pod logs for deployment {dep.metadata.name}")
    except Exception as e:
        report_data["critical_problems"].append(str(e))
        
    if format == "json":
        return json.dumps(report_data, indent=2)
    else:
        # Markdown
        md = f"# Kubernetes Audit Report\n\n"
        md += f"**Timestamp:** {report_data['timestamp']}\n"
        md += f"**Namespace:** {report_data['namespace']}\n\n"
        md += f"## Critical Problems\n"
        for p in report_data["critical_problems"]:
            md += f"- [CRITICAL] {p}\n"
        if not report_data["critical_problems"]:
            md += "- None\n"
            
        md += f"\n## Recommendations\n"
        for r in report_data["recommendations"]:
            md += f"- [RECOMMENDATION] {r}\n"
        if not report_data["recommendations"]:
            md += "- None\n"
        return md

def report_command(args) -> int:
    """CLI entrypoint that generates and outputs a consolidated cluster health and audit report."""
    namespace = getattr(args, 'namespace', 'default')
    output_format = getattr(args, 'format', 'markdown')
    logger.info(f"Generating consolidated report for '{namespace}' in {output_format} format...")
    
    report = generate_report(namespace, output_format)
    print("\n" + report + "\n")
    return 0
