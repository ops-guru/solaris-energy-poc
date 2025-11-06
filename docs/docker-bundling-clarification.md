# Docker Bundling in CDK - Clarification

**Question**: Does the CI/CD pipeline have Docker available, and is it required?

## Answer

### GitHub Actions Has Docker by Default

**Yes, GitHub Actions `ubuntu-latest` runners come with Docker pre-installed.**

This is a **known fact** about GitHub Actions, not an assumption:
- All GitHub-hosted runners (`ubuntu-latest`, `windows-latest`, `macos-latest`) have Docker installed
- Docker daemon is running by default
- No additional setup required in the workflow

### CDK Docker Bundling Requirements

When CDK uses `BundlingOptions` with Docker:

1. **During `cdk synth` or `cdk deploy`**:
   - CDK will use Docker to build the Lambda package
   - It runs a Docker container with the Python runtime image
   - Installs dependencies from `requirements.txt` inside the container
   - Copies the installed packages to the Lambda deployment package

2. **Docker Must Be Running**:
   - On local machines: Docker Desktop must be running
   - On GitHub Actions: Docker daemon is already running (no action needed)
   - CDK will automatically detect and use Docker

3. **What Happens in GitHub Actions**:
   - CDK runs `cdk deploy` 
   - CDK detects Docker is available
   - CDK automatically uses Docker to bundle Lambda dependencies
   - No additional workflow steps needed

### Our Current Workflow

Looking at `.github/workflows/deploy.yml`:
- Uses `runs-on: ubuntu-latest` (has Docker)
- Runs `cdk deploy --all`
- CDK will automatically use Docker for bundling
- **No changes needed** to the workflow

### Potential Issues

**If Docker is NOT available** (unlikely on GitHub Actions, but possible locally):
- CDK will fail with an error like: "Docker is not running" or "Cannot connect to Docker daemon"
- Solution: Start Docker Desktop (local) or ensure Docker is available (CI/CD)

**If Docker is available but CDK bundling fails**:
- Check Docker daemon is running
- Check Docker has enough resources
- Check network connectivity for pulling Docker images

### Verification

To verify Docker bundling works:

1. **Local Test**:
   ```bash
   # Ensure Docker is running
   docker ps
   
   # CDK will use Docker automatically
   cdk synth
   ```

2. **CI/CD Test**:
   - GitHub Actions has Docker by default
   - CDK deploy will automatically use it
   - No manual Docker commands needed in workflow

### Summary

- ✅ **GitHub Actions has Docker**: Known fact, pre-installed on `ubuntu-latest`
- ✅ **CDK will use it automatically**: No workflow changes needed
- ✅ **Docker bundling will work**: As long as Docker daemon is running (which it is on GitHub Actions)
- ⚠️ **Local development**: Requires Docker Desktop to be running

### Alternative: If Docker Isn't Available

If for some reason Docker bundling fails, alternatives:
1. **Lambda Layers**: Pre-build dependencies in a layer
2. **Manual Bundling**: Build deployment package manually and upload
3. **CI/CD Pre-build Step**: Build package in CI/CD, then deploy

But for our use case, **Docker bundling should work fine** in GitHub Actions.

