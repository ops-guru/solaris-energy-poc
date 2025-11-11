"""Vector store stack - OpenSearch for RAG."""
import aws_cdk as cdk
from aws_cdk import aws_opensearchservice as opensearch
from aws_cdk import aws_ec2 as ec2
from constructs import Construct


class VectorStoreStack(cdk.Stack):
    """OpenSearch vector store for RAG."""

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        vpc: ec2.IVpc = None,
        security_group: ec2.ISecurityGroup = None,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # OpenSearch domain with k-NN plugin
        self.domain = opensearch.Domain(
            self,
            "VectorStoreDomain",
            domain_name="solaris-poc-vector-store",
            version=opensearch.EngineVersion.OPENSEARCH_2_19,  # Align with console configuration
            capacity=opensearch.CapacityConfig(
                master_nodes=0,
                data_nodes=2,
                data_node_instance_type="t3.medium.search",
            ),
            ebs=opensearch.EbsOptions(
                volume_size=50,
                volume_type=ec2.EbsDeviceVolumeType.GP3,
            ),
            zone_awareness=opensearch.ZoneAwarenessConfig(
                enabled=False,  # Single AZ for POC
            ),
            encryption_at_rest=opensearch.EncryptionAtRestOptions(enabled=True),
            node_to_node_encryption=True,
            enforce_https=True,
            vpc=vpc,
            vpc_subnets=[
                ec2.SubnetSelection(
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    # Select only first AZ subnet since zone awareness disabled
                    availability_zones=[vpc.availability_zones[0]]
                    if vpc
                    else None,
                )
            ],
            security_groups=[security_group] if security_group else None,
            fine_grained_access_control=opensearch.AdvancedSecurityOptions(
                master_user_name="admin",
                # Note: After deployment, configure master user to use IAM ARN
                # See docs/iam-authentication-migration.md for instructions
            ),
            enable_version_upgrade=True,
            automated_snapshot_start_hour=1,  # Backup at 1 AM UTC
            removal_policy=cdk.RemovalPolicy.DESTROY,  # POC data, safe to delete
        )

        # Output domain endpoint
        cdk.CfnOutput(
            self,
            "OpenSearchEndpoint",
            value=self.domain.domain_endpoint,
            description="OpenSearch domain endpoint",
        )

