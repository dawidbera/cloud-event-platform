import argparse
import sys
import logging

from .commands.audit import audit_command
from .commands.health import health_command
from .commands.report import report_command
from .commands.deploy import deploy_command
from .commands.rollback import rollback_command

logger = logging.getLogger("kubeops")

def setup_logging():
    """Configures the standard logging format and level for the CLI."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def main():
    """Parses command-line arguments and routes execution to the appropriate Kubernetes operation."""
    setup_logging()
    
    parser = argparse.ArgumentParser(description="kubeops - Kubernetes Operations CLI for Cloud Event Platform")
    parser.add_argument('--version', action='version', version='%(prog)s 0.1.0')
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Audit command
    audit_parser = subparsers.add_parser("audit", help="Audit Kubernetes resources")
    audit_parser.add_argument("-n", "--namespace", default="default", help="Kubernetes namespace to audit")
    audit_parser.set_defaults(func=audit_command)
    
    # Health command
    health_parser = subparsers.add_parser("health", help="Check cluster and application health")
    health_parser.add_argument("-n", "--namespace", default="default", help="Kubernetes namespace to check")
    health_parser.set_defaults(func=health_command)
    
    # Report command
    report_parser = subparsers.add_parser("report", help="Generate consolidated report")
    report_parser.add_argument("-n", "--namespace", default="default", help="Kubernetes namespace")
    report_parser.add_argument("-f", "--format", choices=["markdown", "json"], default="markdown", help="Output format")
    report_parser.set_defaults(func=report_command)
    
    # Deploy command
    deploy_parser = subparsers.add_parser("deploy", help="Wait for and verify a deployment")
    deploy_parser.add_argument("-n", "--namespace", default="default", help="Kubernetes namespace")
    deploy_parser.add_argument("-d", "--deployment", required=True, help="Name of the deployment to verify")
    deploy_parser.add_argument("-t", "--timeout", type=int, default=300, help="Rollout timeout in seconds")
    deploy_parser.add_argument("--auto-rollback", action="store_true", help="Automatically rollback if verification fails")
    deploy_parser.set_defaults(func=deploy_command)
    
    # Rollback command
    rollback_parser = subparsers.add_parser("rollback", help="Rollback a deployment")
    rollback_parser.add_argument("-n", "--namespace", default="default", help="Kubernetes namespace")
    rollback_parser.add_argument("-d", "--deployment", required=True, help="Name of the deployment to rollback")
    rollback_parser.set_defaults(func=rollback_command)
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        sys.exit(1)
        
    try:
        exit_code = args.func(args)
        sys.exit(exit_code)
    except Exception as e:
        logger.error(f"Command execution failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
