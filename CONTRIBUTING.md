# Contributing to Solaris Energy POC

Thank you for contributing to the AWS AgentCore POC project! This guide will help you get started.

## Development Setup

### Prerequisites

- Python 3.12+
- Node.js 18+ (for frontend development)
- AWS CLI configured
- AWS CDK CLI (`npm install -g aws-cdk`)
- Git

### Local Development

1. Clone the repository
2. Set up infrastructure environment:
   ```bash
   cd infrastructure
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. Set up Lambda functions:
   ```bash
   cd ../lambda
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

4. Set up frontend:
   ```bash
   cd ../frontend
   npm install
   npm run dev
   ```

## Development Workflow

1. Create a feature branch from `main`
2. Make your changes
3. Write/update tests
4. Ensure all tests pass
5. Update documentation
6. Submit a pull request

## Code Style

### Python

- Follow PEP 8 style guide
- Use type hints
- Maximum line length: 100 characters
- Use `black` for formatting
- Use `pylint` or `ruff` for linting

### TypeScript/JavaScript

- Use ESLint for linting
- Use Prettier for formatting
- Follow React best practices

## Testing

### Unit Tests

```bash
# Python
cd lambda
pytest tests/unit/

# TypeScript
cd frontend
npm test
```

### Integration Tests

```bash
cd tests/integration
pytest
```

### End-to-End Testing

See [tests/README.md](tests/README.md) for E2E test setup.

## Infrastructure Changes

### CDK Deployment

1. Synthesize templates:
   ```bash
   cd infrastructure
   cdk synth
   ```

2. Review diff:
   ```bash
   cdk diff
   ```

3. Deploy:
   ```bash
   cdk deploy --all
   ```

### AgentCore Changes

Bedrock resources may require manual setup:
1. Use AWS Console for AgentCore configuration
2. Document manual steps in `docs/deployment.md`
3. Update IaC when CDK support is available

## Documentation

- Update README files when adding features
- Document API changes in `docs/api-spec.yaml`
- Update architecture diagrams in `docs/`
- Add inline code comments for complex logic

## Pull Request Process

1. Fork the repository
2. Create your feature branch
3. Commit changes with descriptive messages
4. Push to your fork
5. Create a pull request

### PR Checklist

- [ ] Code follows style guidelines
- [ ] Tests added/updated
- [ ] All tests passing
- [ ] Documentation updated
- [ ] No breaking changes (or clearly documented)
- [ ] Reviewed by at least one team member

## Questions?

Contact the development team or open an issue.

