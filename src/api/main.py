from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sys
from pathlib import Path
import time
from fastapi.responses import FileResponse

# Prometheus imports
from prometheus_client import Counter, Histogram, generate_latest
from prometheus_fastapi_instrumentator import Instrumentator

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from retrieval.hybrid import HybridSearch
from generation.generator import AnswerGenerator
from api.models import QueryRequest, QueryResponse, HealthResponse, StatsResponse, Source

from dotenv import load_dotenv
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="RAG System API",
    description="Production RAG system with hybrid search",
    version="1.0.0"
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics
query_counter = Counter('rag_queries_total', 'Total RAG queries')
query_latency = Histogram('rag_query_latency_seconds', 'RAG query latency')
tokens_counter = Counter('rag_tokens_used_total', 'Total tokens used')

# Instrument app with Prometheus
Instrumentator().instrument(app).expose(app)

# Global components
search_engine = None
generator = None

# Statistics
stats = {
    'total_queries': 0,
    'total_latency': 0,
    'total_tokens': 0
}

@app.on_event("startup")
async def startup_event():
    """Initialize components on startup"""
    global search_engine, generator
    
    print("\n" + "="*60)
    print("🚀 Starting RAG API...")
    print("="*60)
    
    # Load search index
    try:
        print("\n📂 Loading search index...")
        search_engine = HybridSearch()
        search_engine.load('data/embeddings/hybrid_index')
        print("✅ Search index loaded")
    except Exception as e:
        print(f"❌ Failed to load search index: {e}")
        raise
    
    # Initialize generator
    try:
        print("🤖 Initializing generator...")
        generator = AnswerGenerator()
        print("✅ Generator initialized")
    except Exception as e:
        print(f"❌ Failed to initialize generator: {e}")
        raise
    
    print("\n" + "="*60)
    print("✅ RAG API READY!")
    print("="*60)
    print("\n🌐 Access the API:")
    print("   Docs:       http://localhost:8000/docs")
    print("   Health:     http://localhost:8000/health")
    print("   Metrics:    http://localhost:8000/metrics")
    print("")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "RAG System API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "metrics": "/metrics"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        index_loaded=search_engine is not None,
        total_chunks=len(search_engine.vector_search.chunks) if search_engine else 0
    )

@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """Query the RAG system with Prometheus metrics"""
    
    # Increment query counter
    query_counter.inc()
    
    start_time = time.time()
    
    try:
        # Retrieve context
        retrieved_chunks = search_engine.search(request.question, k=request.top_k)
        
        # Generate answer
        result = generator.generate(request.question, retrieved_chunks)
        
        # Calculate latency
        latency_ms = (time.time() - start_time) * 1000
        latency_seconds = (time.time() - start_time)
        
        # Update Prometheus metrics
        query_latency.observe(latency_seconds)
        tokens_counter.inc(result['tokens_used'])
        
        # Update internal stats
        stats['total_queries'] += 1
        stats['total_latency'] += latency_ms
        stats['total_tokens'] += result['tokens_used']
        
        # Create response
        response_data = {
            'question': request.question,
            'answer': result['answer'],
            'sources': [
                Source(
                    chunk_id=s['chunk_id'],
                    doc_title=s['doc_title'],
                    content=s['content'],
                    score=s['score']
                )
                for s in result['sources']
            ],
            'metadata': {
                'latency_ms': round(latency_ms, 2),
                'tokens_used': result['tokens_used'],
                'num_sources': len(result['sources']),
                'model': result['model']
            }
        }
        
        return QueryResponse(**response_data)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Get system statistics"""
    avg_latency = stats['total_latency'] / max(stats['total_queries'], 1)
    avg_tokens = stats['total_tokens'] / max(stats['total_queries'], 1)
    
    return StatsResponse(
        total_queries=stats['total_queries'],
        avg_latency_ms=round(avg_latency, 2),
        total_tokens_used=stats['total_tokens'],
        avg_tokens_per_query=round(avg_tokens, 2)
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

   


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Return a simple favicon or 204 No Content"""
    from fastapi import Response
    return Response(status_code=204)