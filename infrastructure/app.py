#!/usr/bin/env python3

import aws_cdk as cdk
from solaris_poc.network_stack import NetworkStack
from solaris_poc.storage_stack import StorageStack
from solaris_poc.vector_store_stack import VectorStoreStack
from solaris_poc.compute_stack import ComputeStack
from solaris_poc.bedrock_stack import BedrockStack
from solaris_poc.api_stack import ApiStack
from solaris_poc.observability_stack import ObservabilityStack


app = cdk.App()

# Environment configuration
env = cdk.Environment(
    account=app.node.try_get_context("account"),
    region=app.node.try_get_context("region") or "us-east-1",
)

# Instantiate stacks in dependency order
network_stack = NetworkStack(app, "NetworkStack", env=env)

storage_stack = StorageStack(
    app,
    "StorageStack",
    vpc=network_stack.vpc,
    env=env,
)

vector_store_stack = VectorStoreStack(
    app,
    "VectorStoreStack",
    vpc=network_stack.vpc,
    security_group=network_stack.opensearch_security_group,
    env=env,
)

compute_stack = ComputeStack(
    app,
    "ComputeStack",
    vpc=network_stack.vpc,
    security_group=network_stack.lambda_security_group,
    documents_bucket=storage_stack.documents_bucket,
    sessions_table=storage_stack.sessions_table,
    opensearch_domain=vector_store_stack.domain,
    opensearch_endpoint=vector_store_stack.domain.domain_endpoint,
    env=env,
)

# TODO: Implement remaining stacks
# bedrock_stack = BedrockStack(...)
# api_stack = ApiStack(...)
# observability_stack = ObservabilityStack(...)

# Add tags to all resources
cdk.Tags.of(app).add("Project", "SolarisEnergyPOC")
cdk.Tags.of(app).add("Environment", "Development")
cdk.Tags.of(app).add("ManagedBy", "CDK")

app.synth()

