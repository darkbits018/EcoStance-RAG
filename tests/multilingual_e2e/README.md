# Multilingual End-to-End Testing Suite

Comprehensive end-to-end testing framework for multilingual capabilities in the EcoStance Agent system.

## Overview

This test suite validates the complete multilingual pipeline from document ingestion through extraction, cleanup, BGE-M3 embedding generation, retrieval, RAG processing, and agent interaction using the `logistics-multilanguage.pdf` as the primary test source.

## Test Structure

```
tests/multilingual_e2e/
├── conftest.py                      # Pytest configuration and fixtures
├── test_config.py                   # Environment setup and configuration tests
├── test_document_processing.py      # Document processing pipeline tests
├── test_embedding_validation.py     # BGE-M3 embedding validation tests
├── test_search_retrieval.py         # Multilingual search and retrieval tests
├── test_rag_pipeline.py            # RAG pipeline validation tests
├── test_agent_conversation.py      # Agent conversation tests
├── test_api_integration.py         # API endpoint integration tests
├── test_performance_benchmarks.py  # Performance benchmark tests
├── test_semantic_accuracy.py       # Semantic accuracy validation tests
├── run_e2e_tests.py                # Main test runner
├── fixtures/                        # Test fixtures
│   ├── api_client.py               # API test client
│   └── __init__.py
└── utils/                          # Utility modules
    ├── test_data_utils.py          # Test data management
    ├── cleanup_utils.py            # Resource cleanup utilities
    ├── reporting_utils.py          # Test reporting and metrics
    └── __init__.py
```

## Installation

Install test dependencies:

```bash
pip install -r tests/multilingual_e2e/requirements-test.txt
```

Or install individual packages:

```bash
pip install pytest pytest-asyncio hypothesis httpx PyPDF2 numpy
```

## Running Tests

### Run All Tests

```bash
python tests/multilingual_e2e/run_e2e_tests.py
```

### Run Quick Smoke Tests

```bash
python tests/multilingual_e2e/run_e2e_tests.py --smoke
```

### Run Specific Test Categories

```bash
python tests/multilingual_e2e/run_e2e_tests.py --categories config document_processing
```

### Run Property-Based Tests Only

```bash
python tests/multilingual_e2e/run_e2e_tests.py --property-only --max-examples 100
```

### Run Performance Tests Only

```bash
python tests/multilingual_e2e/run_e2e_tests.py --performance-only
```

### Skip Property or Performance Tests

```bash
python tests/multilingual_e2e/run_e2e_tests.py --no-property --no-performance
```

### Using Pytest Directly

```bash
# Run all tests
pytest tests/multilingual_e2e/ -v

# Run specific test file
pytest tests/multilingual_e2e/test_config.py -v

# Run tests with specific marker
pytest tests/multilingual_e2e/ -m property_test -v

# Run with coverage
pytest tests/multilingual_e2e/ --cov=app --cov-report=html
```

## Test Categories

### 1. Configuration Tests (`test_config.py`)
- Environment setup validation
- Multilingual configuration loading
- Integration service initialization
- Test data availability

### 2. Document Processing Tests (`test_document_processing.py`)
- PDF upload via API
- Processing status monitoring
- Language detection validation
- Text cleaning and enrichment
- Embedding generation validation
- Qdrant storage verification

**Property Test**: Document processing pipeline completeness

### 3. Embedding Validation Tests (`test_embedding_validation.py`)
- Embedding dimension verification (1024)
- Vector normalization validation (unit length)
- Language metadata verification
- Collection naming validation (_ml suffix)
- Embedding completeness verification

**Property Test**: BGE-M3 embedding consistency

### 4. Search & Retrieval Tests (`test_search_retrieval.py`)
- Query language detection
- Semantic search across languages
- Cross-language search effectiveness
- Result metadata and confidence scores
- Search performance thresholds

**Property Test**: Cross-language search effectiveness

### 5. RAG Pipeline Tests (`test_rag_pipeline.py`)
- Multilingual context retrieval
- Information synthesis across languages
- Response language consistency
- Factual accuracy across languages
- Source citation with language indicators

**Property Test**: Multilingual RAG coherence

### 6. Agent Conversation Tests (`test_agent_conversation.py`)
- Agent session initialization
- Language detection and context maintenance
- Multilingual tool invocation
- Cross-language knowledge base search
- Conversation coherence across languages

**Property Test**: Agent conversation consistency

### 7. API Integration Tests (`test_api_integration.py`)
- File upload API with multilingual content
- Knowledge base listing API
- Search API with multilingual queries
- Agent chat API session management
- System status API multilingual info

**Property Test**: API interface compliance

### 8. Performance Benchmarks (`test_performance_benchmarks.py`)
- Document processing: <30s for <10MB files
- Embedding generation: >100 blocks/min
- Search queries: <2s response time
- Agent responses: <5s response time
- Concurrent operations: within 20% of baseline

**Property Test**: Performance benchmarks

### 9. Semantic Accuracy Tests (`test_semantic_accuracy.py`)
- Semantic meaning preservation in embeddings
- Cross-language semantic equivalence
- Factual consistency across languages
- Language detection accuracy: >95%
- Relevance score correlation with human judgment

**Property Test**: Semantic accuracy preservation

## Property-Based Testing

The test suite uses Hypothesis for property-based testing with a minimum of 100 iterations per property test. Each property test validates universal properties across all inputs:

- **Property 1**: Document processing pipeline completeness
- **Property 2**: BGE-M3 embedding consistency
- **Property 3**: Cross-language search effectiveness
- **Property 4**: Multilingual RAG coherence
- **Property 5**: Agent conversation consistency
- **Property 6**: API interface compliance
- **Property 7**: Performance benchmarks
- **Property 8**: Semantic accuracy preservation

## Performance Thresholds

The test suite validates the following performance thresholds:

| Operation | Threshold |
|-----------|-----------|
| Document Processing | <30 seconds (for files <10MB) |
| Embedding Generation | >100 blocks/minute |
| Search Queries | <2 seconds |
| Agent Responses | <5 seconds |
| Concurrent Degradation | <20% of baseline |

## Test Reports

Test reports are automatically generated in the `test_results/` directory:

- **JSON Report**: Detailed test results in JSON format
- **HTML Report**: Human-readable HTML report with metrics and visualizations

## Cleanup

### Automatic Cleanup

Test resources are automatically cleaned up after each test run.

### Manual Cleanup

```bash
# Emergency cleanup of all test resources
python tests/multilingual_e2e/run_e2e_tests.py --emergency-cleanup
```

## Configuration

Test configuration is managed through:

- `conftest.py`: Pytest fixtures and configuration
- `test_config.py`: Environment setup and validation
- Environment variables (see `.env.example`)

### Key Configuration Variables

```bash
MULTILINGUAL_ENABLED=true
EMBEDDING_MODEL_TYPE=bge-m3
LANGUAGE_DETECTION_ENABLED=true
LANGUAGE_DETECTION_MIN_CONFIDENCE=0.7
BGE_M3_BATCH_SIZE=16
```

## Troubleshooting

### Tests Fail to Import Modules

```bash
# Install missing dependencies
pip install -r tests/multilingual_e2e/requirements-test.txt
```

### Test PDF Not Found

Ensure `logistics-multilanguage.pdf` exists in the project root directory.

### Multilingual Services Not Available

Check that multilingual features are enabled in your configuration:

```bash
# Verify configuration
python -c "from app.config.multilingual_app_config import get_multilingual_config_info; print(get_multilingual_config_info())"
```

### Cleanup Issues

If test resources are not cleaned up properly:

```bash
# Run emergency cleanup
python tests/multilingual_e2e/run_e2e_tests.py --emergency-cleanup
```

## Development

### Adding New Tests

1. Create test file in appropriate category
2. Use existing fixtures from `conftest.py`
3. Follow naming convention: `test_*.py`
4. Add property tests where applicable
5. Register cleanup for test resources

### Running Tests During Development

```bash
# Run with verbose output and stop on first failure
pytest tests/multilingual_e2e/ -v -x

# Run specific test
pytest tests/multilingual_e2e/test_config.py::TestEnvironmentSetup::test_environment_configuration -v

# Run with debugging
pytest tests/multilingual_e2e/ -v --pdb
```

## CI/CD Integration

The test suite can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run Multilingual E2E Tests
  run: |
    pip install -r tests/multilingual_e2e/requirements-test.txt
    python tests/multilingual_e2e/run_e2e_tests.py --no-performance
```

## Support

For issues or questions about the test suite, refer to:

- Spec files in `.kiro/specs/multilingual-e2e-testing/`
- Design document for architecture details
- Requirements document for acceptance criteria

## License

Part of the EcoStance Agent project.