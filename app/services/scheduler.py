from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.db.models import Cluster, Deployment, DeploymentStatus
from app.schemas.deployment import DeploymentCreate

class SchedulerService:
    def __init__(self, db: Session):
        self.db = db

    def can_allocate_resources(self, cluster: Cluster, deployment: DeploymentCreate) -> bool:
        """Check if cluster has enough resources for the deployment."""
        return (
            cluster.available_cpu >= deployment.required_cpu
            and cluster.available_ram >= deployment.required_ram
            and cluster.available_gpu >= deployment.required_gpu
        )

    def allocate_resources(self, cluster: Cluster, deployment: DeploymentCreate) -> None:
        """Allocate resources from cluster to deployment."""
        cluster.available_cpu -= deployment.required_cpu
        cluster.available_ram -= deployment.required_ram
        cluster.available_gpu -= deployment.required_gpu
        self.db.commit()

    def release_resources(self, cluster: Cluster, deployment: Deployment) -> None:
        """Release resources back to cluster."""
        cluster.available_cpu += deployment.required_cpu
        cluster.available_ram += deployment.required_ram
        cluster.available_gpu += deployment.required_gpu
        self.db.commit()

    def get_queued_deployments(self, cluster_id: int) -> List[Deployment]:
        """Get all queued deployments for a cluster, ordered by priority."""
        return (
            self.db.query(Deployment)
            .filter(
                Deployment.cluster_id == cluster_id,
                Deployment.status == DeploymentStatus.QUEUED
            )
            .order_by(Deployment.priority.desc())
            .all()
        )

    def schedule_deployment(self, deployment: Deployment) -> bool:
        """Attempt to schedule a deployment."""
        cluster = self.db.query(Cluster).filter(Cluster.id == deployment.cluster_id).first()
        
        if not cluster:
            return False

        if self.can_allocate_resources(cluster, deployment):
            self.allocate_resources(cluster, deployment)
            deployment.status = DeploymentStatus.RUNNING
            deployment.started_at = datetime.utcnow()
            self.db.commit()
            return True
        
        deployment.status = DeploymentStatus.QUEUED
        self.db.commit()
        return False

    def preempt_deployments(self, new_deployment: Deployment) -> bool:
        """Attempt to preempt lower priority deployments to schedule a higher priority one."""
        cluster = self.db.query(Cluster).filter(Cluster.id == new_deployment.cluster_id).first()
        if not cluster:
            return False

        # Get all running deployments ordered by priority (ascending)
        running_deployments = (
            self.db.query(Deployment)
            .filter(
                Deployment.cluster_id == cluster.id,
                Deployment.status == DeploymentStatus.RUNNING
            )
            .order_by(Deployment.priority.asc())
            .all()
        )

        # Calculate total resources needed
        needed_cpu = new_deployment.required_cpu
        needed_ram = new_deployment.required_ram
        needed_gpu = new_deployment.required_gpu

        # Try to preempt lower priority deployments
        for deployment in running_deployments:
            if deployment.priority >= new_deployment.priority:
                continue

            # Release resources from lower priority deployment
            self.release_resources(cluster, deployment)
            deployment.status = DeploymentStatus.QUEUED
            deployment.completed_at = datetime.utcnow()

            # Check if we have enough resources now
            if (
                cluster.available_cpu >= needed_cpu
                and cluster.available_ram >= needed_ram
                and cluster.available_gpu >= needed_gpu
            ):
                # Schedule the new deployment
                self.allocate_resources(cluster, new_deployment)
                new_deployment.status = DeploymentStatus.RUNNING
                new_deployment.started_at = datetime.utcnow()
                self.db.commit()
                return True

        # If we couldn't schedule the deployment, queue it
        new_deployment.status = DeploymentStatus.QUEUED
        self.db.commit()
        return False

    def process_queue(self, cluster_id: int) -> None:
        """Process the deployment queue for a cluster."""
        queued_deployments = self.get_queued_deployments(cluster_id)
        
        for deployment in queued_deployments:
            if self.schedule_deployment(deployment):
                continue
            
            # If we can't schedule it normally, try preemption
            if deployment.priority > 0:  # Only try preemption for non-zero priority deployments
                self.preempt_deployments(deployment) 