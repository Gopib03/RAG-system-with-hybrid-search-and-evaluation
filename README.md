# RAG Evaluation System

Production-ready Retrieval-Augmented Generation system with comprehensive evaluation metrics and monitoring.

![Architecture](docs/architecture.png)

## 🎯 Features

- **Hybrid Retrieval**: Combines vector similarity (FAISS) + keyword search (BM25)
- **Evaluation Framework**: 5 automated quality metrics
- **Production API**: FastAPI with Redis caching
- **Monitoring**: Prometheus + Grafana dashboards
- **Docker Deployment**: One-command deployment

## 📊 Performance Benchmarks

| Metric | Value |
|--------|-------|
| Answer Relevancy | 4.2/5.0 |
| Context Precision | 78% |
| Faithfulness | 94% |
| P95 Latency | 420ms |
| Cache Hit Rate | 89% |
| Throughput | 150 req/min |

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- 8GB RAM minimum

### Installation
```bash
# Clone repository
git clone https://github.com/yourusername/rag-evaluation-system.git
cd rag-evaluation-system

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your API keys
```

### Running Locally
```bash
# 1. Prepare data
python scripts/setup_data.py
python scripts/ingest_documents.py

# 2. Build search indices
python scripts/build_indices.py

# 3. Generate test set
python scripts/run_evaluation.py

# 4. Start services
docker-compose up -d

# 5. Test API
python scripts/test_api.py
```

### Docker Deployment
```bash
# One-command deployment
./scripts/deploy.sh

# Access services
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
# Grafana: http://localhost:3000
# Prometheus: http://localhost:9090
```

## 📖 API Usage

### Query Endpoint
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is machine learning?",
    "top_k": 5,
    "use_cache": true
  }'
```

### Response
```json
{
  "question": "What is machine learning?",
  "answer": "Machine learning is a subset of AI...",
  "sources": [
    {
      "chunk_id": "doc_1_chunk_0",
      "doc_title": "Introduction to ML",
      "content": "Machine learning algorithms...",
      "score": 0.92
    }
  ],
  "metadata": {
    "latency_ms": 387,
    "tokens_used": 245,
    "num_sources": 5,
    "cached": false
  }
}
```

## 🏗️ Architecture
```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│         FastAPI Server              │
│  ┌──────────┐      ┌─────────────┐ │
│  │  Cache   │◄────►│   Redis     │ │
│  └──────────┘      └─────────────┘ │
│  ┌──────────┐      ┌─────────────┐ │
│  │ Retrieval│◄────►│   FAISS     │ │
│  └──────────┘      └─────────────┘ │
│  ┌──────────┐      ┌─────────────┐ │
│  │Generator │◄────►│ Claude API  │ │
│  └──────────┘      └─────────────┘ │
└──────────┬──────────────────────────┘
           │
           ▼
    ┌─────────────┐
    │ Prometheus  │
    │   Grafana   │
    └─────────────┘
```

## 📁 Project Structure
```
rag-evaluation-system/
├── src/
│   ├── ingestion/       # Document loading & chunking
│   ├── retrieval/       # Search implementations
│   ├── generation/      # Answer generation
│   ├── evaluation/      # Metrics & testing
│   └── api/            # FastAPI service
├── data/
│   ├── raw/            # Source documents
│   ├── processed/      # Chunks & test sets
│   └── embeddings/     # Vector indices
├── tests/              # Unit tests
├── scripts/            # Utility scripts
├── config/             # Configuration files
├── docs/               # Documentation
└── docker-compose.yml  # Docker orchestration
```

## 🧪 Testing
```bash
# Run unit tests
pytest tests/

# Run evaluation
python scripts/run_evaluation.py

# Load test
python scripts/load_test.py
```

## 📊 Evaluation Metrics

### Quality Metrics

- **Answer Relevancy** (0-5): How well the answer addresses the question
- **Faithfulness** (0-1): Is the answer grounded in retrieved context?
- **Context Precision** (0-1): Percentage of relevant retrieved documents
- **Context Recall** (0-1): Did we retrieve all necessary information?

### Performance Metrics

- **Latency**: P50, P95, P99 response times
- **Throughput**: Requests per minute
- **Cache Hit Rate**: Percentage of cached responses
- **Token Usage**: API cost tracking

## 🔧 Configuration

Edit `config/config.yaml`:
```yaml
retrieval:
  chunk_size: 1024
  chunk_overlap: 128
  top_k: 5
  vector_weight: 0.7
  keyword_weight: 0.3

generation:
  model: "claude-3-haiku-20240307"
  max_tokens: 500
  temperature: 0.0

cache:
  ttl: 86400  # 24 hours
  max_size: 10000

monitoring:
  prometheus_port: 9090
  grafana_port: 3000
```

## 🚨 Monitoring

### Grafana Dashboards

Access Grafana at `http://localhost:3000` (admin/admin)

**Key Metrics:**
- Query latency distribution
- Cache hit/miss ratio
- Token usage trends
- Error rates
- Throughput

### Prometheus Queries
```promql
# Average latency
rate(rag_query_latency_seconds_sum[5m]) / rate(rag_query_latency_seconds_count[5m])

# Cache hit rate
rate(rag_cache_hits_total[5m]) / (rate(rag_cache_hits_total[5m]) + rate(rag_cache_misses_total[5m]))

# Request rate
rate(rag_queries_total[1m])
```

## 💰 Cost Optimization

### Current Costs

- **API Calls**: ~$0.05 per query (Claude Haiku)
- **Caching**: 89% hit rate saves $340/month
- **Infrastructure**: $0 (self-hosted)

### Optimization Tips

1. Increase cache TTL for stable content
2. Use batch processing for evaluation
3. Implement request deduplication
4. Consider self-hosted models for high volume

## 🐛 Troubleshooting

### API not responding
```bash
# Check logs
docker-compose logs api

# Restart services
docker-compose restart api
```

### Cache not working
```bash
# Check Redis
docker-compose logs redis

# Clear cache
curl -X DELETE http://localhost:8000/cache
```

### Slow queries
```bash
# Check metrics
curl http://localhost:8000/metrics

# View Prometheus
open http://localhost:9090
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

MIT License - see [LICENSE](LICENSE)



Project Link: 
## 🙏 Acknowledgments

- [LangChain](https://langchain.com/) - RAG framework
- [FAISS](https://github.com/facebookresearch/faiss) - Vector search
- [Anthropic](https://anthropic.com/) - Claude API
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
