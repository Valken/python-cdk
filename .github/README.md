# GitHub Copilot Custom Resources

This directory contains custom GitHub Copilot agents, instructions, and prompts tailored for AWS serverless development with CDK and FastAPI.

## 📁 Directory Structure

```
.github/
├── agents/                    # Specialized AI agents for specific tasks
│   ├── aws-cdk-infrastructure-expert.agent.md
│   └── aws-lambda-powertools-expert.agent.md
├── instructions/              # Best practices and coding standards
│   ├── general.instructions.md
│   ├── aws-cdk-python.instructions.md
│   └── aws-lambda-powertools-python.instructions.md
└── prompts/                   # Reusable prompt templates
    └── generate-lambda-api-route.prompt.md
```

## 🤖 Agents

### AWS CDK Infrastructure Expert
**File**: `agents/aws-cdk-infrastructure-expert.agent.md`

Expert agent for AWS Cloud Development Kit (CDK) infrastructure development. Specializes in:
- **AWS CDK with Python**: Infrastructure as code patterns and best practices
- **Serverless Architecture**: Lambda, API Gateway, DynamoDB, SSM Parameter Store
- **Docker-based Lambdas**: Container deployments with optimization
- **IAM & Security**: Least-privilege policies, role management
- **Observability**: X-Ray tracing, CloudWatch logs and metrics
- **Cost Optimization**: Lambda memory sizing, resource allocation

**Usage**: `@aws-cdk-infrastructure-expert <your question>`

**Example Questions**:
- "How should I configure Lambda memory for my API?"
- "How do I grant DynamoDB permissions to my Lambda function?"
- "What's the best way to structure my CDK stacks?"
- "How do I set up X-Ray tracing for my Lambda?"

### FastAPI Expert
**File**: `agents/aws-lambda-powertools-expert.agent.md` *(Note: This agent still uses the old filename but now focuses on FastAPI)*

Expert agent for FastAPI API development on AWS Lambda. Specializes in:
- **FastAPI with Mangum**: API development with Lambda adapter
- **Validation**: Pydantic integration, request/response models
- **Route Organization**: RESTful API design, parameter handling
- **Error Handling**: HTTP exceptions, custom responses
- **Testing**: Unit test patterns for route handlers
- **AWS Integration**: DynamoDB, SSM Parameter Store, CloudWatch

**Usage**: `@aws-lambda-powertools-expert <your question>`

**Example Questions**:
- "How do I add query parameters with validation to my GET endpoint?"
- "What's the best way to organize my API routes?"
- "How do I use Pydantic discriminated unions for polymorphic data?"
- "How do I integrate FastAPI with DynamoDB?"

## 📋 Instructions

### General Instructions
**File**: `instructions/general.instructions.md`

Controls how GitHub Copilot and agents respond to requests:
- Never generate summary files (SUMMARY.md, CHANGES.md) unless explicitly requested
- Provide clear, informative explanations in the tool window
- Be action-oriented and take immediate action on clear requests
- Explain reasoning and approach before implementing
- Use structured output for clarity

### AWS CDK Python Best Practices
**File**: `instructions/aws-cdk-python.instructions.md`

Comprehensive best practices for CDK development including:
- Project structure and organization
- Lambda configuration patterns
- IAM and security guidelines
- API Gateway setup
- DynamoDB integration
- Environment management
- Cost optimization strategies

### FastAPI Python Best Practices
**File**: `instructions/aws-lambda-powertools-python.instructions.md` *(Note: This file still uses the old filename but now covers FastAPI)*

Best practices for FastAPI development on AWS Lambda including:
- FastAPI router pattern implementation
- Path and query parameter handling with FastAPI syntax
- Request body validation with Pydantic
- Error handling with HTTPException
- Testing strategies with FastAPI TestClient
- AWS service integration (DynamoDB, SSM)
- Mangum adapter configuration

## 🎯 Prompts

### Generate Lambda API Route
**File**: `prompts/generate-lambda-api-route.prompt.md`

Template for generating new API route handlers following best practices.

**Usage**: `/generate-lambda-api-route <resource name and requirements>`

**Example**:
```
/generate-lambda-api-route add a user route with GET (list and detail),
POST, and DELETE. Include fields: email, name, role.
```

This will generate:
- `api/user_routes.py` with all route handlers
- Pydantic models for request/response
- Unit tests in `api/tests/test_user_routes.py`
- Instructions to update `handler.py`

## 🚀 Quick Start

### Using Agents

To get help from the specialized agents, mention them in your chat:

**For infrastructure questions:**
```
@aws-cdk-infrastructure-expert How should I configure Lambda memory for my API?
```

```
@aws-cdk-infrastructure-expert How do I grant DynamoDB permissions to my Lambda?
```

**For API development questions:**
```
@aws-lambda-powertools-expert How do I add query parameters to my GET endpoint?
```

```
@aws-lambda-powertools-expert What's the best way to organize my routes?
```

### Applying Instructions

Instructions are automatically applied to matching files. They guide Copilot to follow best practices when:
- Creating new CDK stacks
- Writing Lambda handlers
- Implementing API routes
- Configuring infrastructure

### Using Prompts

Prompts are invoked with the `/` command:

```
/generate-lambda-api-route create a product route with full CRUD operations
```

## 📚 Examples

### Example: Creating a New API Resource

1. **Generate the route**:
   ```
   /generate-lambda-api-route create an order route with GET list, GET detail,
   POST create, and PUT update. Include: customer_id, items (list), total (float),
   status (pending/completed/cancelled)
   ```

2. **Review generated files**:
   - `api/order_routes.py`
   - `api/tests/test_order_routes.py`

3. **Update handler.py**:
   ```python
   from api.order_routes import router as order_router
   app.include_router(order_router)
   ```

4. **Deploy infrastructure**:
   ```
   @aws-cdk-infrastructure-expert How do I add permissions for the order table?
   ```

### Example: Adding DynamoDB Permissions

```
@aws-cdk-infrastructure-expert I need to grant my Lambda function read/write
access to a DynamoDB table and query access to the OrderStatusIndex GSI.
```

### Example: Implementing Validation

```
@aws-lambda-powertools-expert How do I validate that an email field is a valid
email address in my Pydantic model?
```

## 🎨 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     API Gateway (HTTP API)                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Lambda Function (Docker-based)                 │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  handler.py - FastAPI with Mangum                     │  │
│  │    ├─ include_router(thing_router, prefix="/stuff")  │  │
│  │    └─ include_router(post_router)                    │  │
│  └────────────────────────────────────────────────��──────┘  │
│                                                              │
│  ┌────────────────────┐      ┌─────────────────────────┐   │
│  │  thing_routes.py   │      │   post_routes.py        │   │
│  │  - APIRouter()     │      │   - APIRouter()         │   │
│  │  - GET /           │      │   - GET /posts          │   │
│  │  - POST /pets      │      │   - GET /posts/{id}     │   │
│  │  - GET /{thing_id} │      │   - POST /posts         │   │
│  └────────────────────┘      └─────────────────────────┘   │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  schemas.py - Pydantic Models                        │  │
│  │    - Model, Cat, Dog, Lizard, Post                   │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  DynamoDB Table                             │
│                  SSM Parameters                             │
│                  CloudWatch Logs                            │
│                  X-Ray Tracing                              │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Customization

To customize these resources for your project:

1. **Edit agents**: Modify agent expertise and examples in `.github/agents/`
2. **Update instructions**: Add project-specific patterns in `.github/instructions/`
3. **Create new prompts**: Add reusable templates in `.github/prompts/`

## 📖 Best Practices

### File Naming Conventions
- Agents: `<topic>-<role>.agent.md`
- Instructions: `<technology>-<aspect>.instructions.md`
- Prompts: `<action>-<resource>.prompt.md`

### Agent Guidelines
- Be specific about expertise areas
- Include concrete examples
- Reference official documentation
- Provide troubleshooting tips

### Instruction Guidelines
- Focus on one technology/pattern per file
- Use code examples liberally
- Include anti-patterns to avoid
- Keep content up-to-date

### Prompt Guidelines
- Provide clear templates
- Include usage examples
- Document expected outputs
- Explain customization options

## 🤝 Contributing

To add new resources:

1. Create the file in the appropriate directory
2. Follow the naming conventions
3. Include clear examples and documentation
4. Test the resource with GitHub Copilot
5. Update this README

## 📝 License

These custom resources are part of your project and follow the same license.

## 🔗 References

- [AWS CDK Documentation](https://docs.aws.amazon.com/cdk/)
- [AWS Lambda Powertools Python](https://docs.powertools.aws.dev/lambda/python/)
- [GitHub Copilot Documentation](https://docs.github.com/en/copilot)
- [Pydantic Documentation](https://docs.pydantic.dev/)

---

**Last Updated**: December 6, 2025
