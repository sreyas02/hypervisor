from typing import List, Optional, Dict
from datetime import datetime
from sqlalchemy.orm import Session
from app.db.models import Cluster, Deployment, DeploymentStatus
from app.schemas.deployment import DeploymentCreate

class SchedulerService:
    def __init__(self, db: Session):
        self.db = db

    def can_allocate_resources(self, cluster: Cluster, deployment: Deployment) -> bool:
        """Check if cluster has enough resources for the deployment."""
        return (
            cluster.available_cpu >= deployment.required_cpu
            and cluster.available_ram >= deployment.required_ram
            and cluster.available_gpu >= deployment.required_gpu
        )

    def allocate_resources(self, cluster: Cluster, deployment: Deployment) -> None:
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
        """Get all queued deployments for a cluster."""
        return (
            self.db.query(Deployment)
            .filter(
                Deployment.cluster_id == cluster_id,
                Deployment.status == DeploymentStatus.QUEUED
            )
            .all()
        )

    def optimize_resource_packing(self, cluster: Cluster, queued_deployments: List[Deployment]) -> List[Deployment]:
        """Optimize resource utilization by packing deployments efficiently."""
        # Calculate resource density (resource requirements / priority)
        def get_resource_density(deployment: Deployment) -> float:
            total_resources = deployment.required_cpu + deployment.required_ram + deployment.required_gpu
            return total_resources / (deployment.priority + 1)  # Add 1 to avoid division by zero

        # Sort by resource density (ascending) and priority (descending)
        return sorted(
            queued_deployments,
            key=lambda d: (get_resource_density(d), -d.priority)
        )

    def ensure_fairness(self, cluster: Cluster, queued_deployments: List[Deployment]) -> List[Deployment]:
        """Ensure fair resource distribution among users/organizations."""
        # Group deployments by user
        user_deployments: Dict[int, List[Deployment]] = {}
        for deployment in queued_deployments:
            if deployment.user_id not in user_deployments:
                user_deployments[deployment.user_id] = []
            user_deployments[deployment.user_id].append(deployment)

        # Sort each user's deployments by priority
        for user_id in user_deployments:
            user_deployments[user_id].sort(key=lambda d: -d.priority)

        # Round-robin scheduling among users
        fair_queue = []
        while any(user_deployments.values()):
            for user_id in list(user_deployments.keys()):
                if user_deployments[user_id]:
                    fair_queue.append(user_deployments[user_id].pop(0))

        return fair_queue

    def handle_resource_fragmentation(self, cluster: Cluster) -> None:
        """Handle resource fragmentation by consolidating resources."""
        # Calculate fragmentation metrics
        cpu_fragmentation = cluster.available_cpu / cluster.total_cpu
        ram_fragmentation = cluster.available_ram / cluster.total_ram
        gpu_fragmentation = cluster.available_gpu / cluster.total_gpu

        # If fragmentation is high, consider preempting and rescheduling
        if min(cpu_fragmentation, ram_fragmentation, gpu_fragmentation) < 0.2:
            self.defragment_resources(cluster)

    def defragment_resources(self, cluster: Cluster) -> None:
        """Defragment resources by preempting and rescheduling deployments."""
        # Get all running deployments
        running_deployments = (
            self.db.query(Deployment)
            .filter(
                Deployment.cluster_id == cluster.id,
                Deployment.status == DeploymentStatus.RUNNING
            )
            .order_by(Deployment.priority.asc())
            .all()
        )

        # Preempt lower priority deployments
        for deployment in running_deployments:
            if deployment.priority < 5:  # Only preempt low priority deployments
                self.release_resources(cluster, deployment)
                deployment.status = DeploymentStatus.QUEUED
                deployment.completed_at = datetime.utcnow()
                self.db.commit()

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
        """Process the deployment queue with improved optimization."""
        queued_deployments = self.get_queued_deployments(cluster_id)
        cluster = self.db.query(Cluster).filter(Cluster.id == cluster_id).first()
        
        if not cluster:
            return

        # Handle resource fragmentation
        self.handle_resource_fragmentation(cluster)
        
        # Optimize resource packing
        optimized_deployments = self.optimize_resource_packing(cluster, queued_deployments)
        
        # Ensure fairness
        fair_deployments = self.ensure_fairness(cluster, optimized_deployments)
        
        # Schedule deployments
        for deployment in fair_deployments:
            if self.schedule_deployment(deployment):
                continue
            
            if deployment.priority > 0:
                self.preempt_deployments(deployment) 