import json
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from pathlib import Path

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)

# Load results
with open('data/evaluation/evaluation_results.json') as f:
    data = json.load(f)

results = data['individual_results']
aggregate = data['aggregate_metrics']

# Create output directory
output_dir = Path('data/evaluation/charts')
output_dir.mkdir(parents=True, exist_ok=True)

print("📊 Creating visualizations...")

# 1. Quality Metrics Bar Chart
print("  Creating quality metrics chart...")
fig, ax = plt.subplots(figsize=(10, 6))

metrics = {
    'Answer\nRelevancy': aggregate['avg_relevancy'] / 5,
    'Faithfulness': aggregate['avg_faithfulness'],
    'Context\nPrecision': aggregate['avg_precision'],
    'Overall\nScore': aggregate['avg_overall_score']
}

colors = ['#2ecc71', '#3498db', '#9b59b6', '#e74c3c']
bars = ax.bar(metrics.keys(), metrics.values(), color=colors, alpha=0.8)

# Add value labels
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{height:.1%}',
            ha='center', va='bottom', fontsize=12, fontweight='bold')

ax.set_ylim(0, 1.1)
ax.set_ylabel('Score', fontsize=12)
ax.set_title('RAG System Quality Metrics', fontsize=16, fontweight='bold')
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.0%}'))

plt.tight_layout()
plt.savefig(output_dir / '1_quality_metrics.png', dpi=300, bbox_inches='tight')
plt.close()

# 2. Performance Metrics
print("  Creating performance metrics chart...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Latency
latencies = {
    'Average': aggregate['avg_latency_ms'],
    'P95': aggregate['p95_latency_ms'],
    'P99': aggregate['p99_latency_ms']
}

bars = ax1.bar(latencies.keys(), latencies.values(), color=['#3498db', '#e67e22', '#e74c3c'], alpha=0.8)
for bar in bars:
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height,
            f'{height:.0f}ms',
            ha='center', va='bottom', fontsize=11, fontweight='bold')

ax1.set_ylabel('Latency (ms)', fontsize=12)
ax1.set_title('Query Latency', fontsize=14, fontweight='bold')

# Tokens
ax2.bar(['Avg Tokens\nper Query'], [aggregate['avg_tokens_per_query']], 
        color='#9b59b6', alpha=0.8, width=0.5)
ax2.text(0, aggregate['avg_tokens_per_query'],
        f"{aggregate['avg_tokens_per_query']:.0f}",
        ha='center', va='bottom', fontsize=12, fontweight='bold')
ax2.set_ylabel('Tokens', fontsize=12)
ax2.set_title('Token Usage', fontsize=14, fontweight='bold')

plt.tight_layout()
plt.savefig(output_dir / '2_performance_metrics.png', dpi=300, bbox_inches='tight')
plt.close()

# 3. Distribution Charts
print("  Creating distribution charts...")
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))

# Relevancy distribution
relevancy_scores = [r['metrics']['answer_relevancy'] for r in results]
ax1.hist(relevancy_scores, bins=10, color='#2ecc71', alpha=0.7, edgecolor='black')
ax1.axvline(aggregate['avg_relevancy'], color='red', linestyle='--', linewidth=2, label=f'Avg: {aggregate["avg_relevancy"]:.2f}')
ax1.set_xlabel('Relevancy Score (0-5)', fontsize=11)
ax1.set_ylabel('Frequency', fontsize=11)
ax1.set_title('Answer Relevancy Distribution', fontsize=13, fontweight='bold')
ax1.legend()

# Faithfulness distribution
faithfulness_scores = [r['metrics']['faithfulness'] for r in results]
ax2.hist(faithfulness_scores, bins=[0, 0.5, 1.0], color='#3498db', alpha=0.7, edgecolor='black')
ax2.set_xlabel('Faithfulness (0=False, 1=True)', fontsize=11)
ax2.set_ylabel('Frequency', fontsize=11)
ax2.set_title('Answer Faithfulness Distribution', fontsize=13, fontweight='bold')
ax2.set_xticks([0, 1])
ax2.set_xticklabels(['Unfaithful', 'Faithful'])

# Latency distribution
latencies = [r['performance']['total_time_ms'] for r in results]
ax3.hist(latencies, bins=15, color='#e67e22', alpha=0.7, edgecolor='black')
ax3.axvline(aggregate['avg_latency_ms'], color='red', linestyle='--', linewidth=2, label=f'Avg: {aggregate["avg_latency_ms"]:.0f}ms')
ax3.set_xlabel('Latency (ms)', fontsize=11)
ax3.set_ylabel('Frequency', fontsize=11)
ax3.set_title('Query Latency Distribution', fontsize=13, fontweight='bold')
ax3.legend()

# Tokens distribution
tokens = [r['performance']['tokens_used'] for r in results]
ax4.hist(tokens, bins=15, color='#9b59b6', alpha=0.7, edgecolor='black')
ax4.axvline(aggregate['avg_tokens_per_query'], color='red', linestyle='--', linewidth=2, label=f'Avg: {aggregate["avg_tokens_per_query"]:.0f}')
ax4.set_xlabel('Tokens Used', fontsize=11)
ax4.set_ylabel('Frequency', fontsize=11)
ax4.set_title('Token Usage Distribution', fontsize=13, fontweight='bold')
ax4.legend()

plt.tight_layout()
plt.savefig(output_dir / '3_distributions.png', dpi=300, bbox_inches='tight')
plt.close()

# 4. Performance by Category
print("  Creating category analysis...")
df = pd.DataFrame([
    {
        'category': r['category'],
        'difficulty': r['difficulty'],
        'relevancy': r['metrics']['answer_relevancy'],
        'overall': r['metrics']['overall_score'],
        'latency': r['performance']['total_time_ms']
    }
    for r in results
])

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# By category
category_stats = df.groupby('category')['overall'].mean().sort_values(ascending=False)
bars = ax1.barh(range(len(category_stats)), category_stats.values, color='#3498db', alpha=0.8)
ax1.set_yticks(range(len(category_stats)))
ax1.set_yticklabels(category_stats.index)
ax1.set_xlabel('Overall Score', fontsize=11)
ax1.set_title('Performance by Question Category', fontsize=13, fontweight='bold')
for i, v in enumerate(category_stats.values):
    ax1.text(v, i, f' {v:.1%}', va='center', fontsize=10)

# By difficulty
difficulty_stats = df.groupby('difficulty')['overall'].mean().reindex(['easy', 'medium', 'hard'])
colors_diff = ['#2ecc71', '#f39c12', '#e74c3c']
bars = ax2.bar(range(len(difficulty_stats)), difficulty_stats.values, color=colors_diff, alpha=0.8)
ax2.set_xticks(range(len(difficulty_stats)))
ax2.set_xticklabels([d.capitalize() for d in difficulty_stats.index])
ax2.set_ylabel('Overall Score', fontsize=11)
ax2.set_title('Performance by Question Difficulty', fontsize=13, fontweight='bold')
for i, v in enumerate(difficulty_stats.values):
    ax2.text(i, v, f'{v:.1%}', ha='center', va='bottom', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig(output_dir / '4_category_analysis.png', dpi=300, bbox_inches='tight')
plt.close()

# 5. Summary Dashboard
print("  Creating summary dashboard...")
fig = plt.figure(figsize=(16, 10))
gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

# Title
fig.suptitle('RAG System Evaluation Dashboard', fontsize=20, fontweight='bold', y=0.98)

# Top row - Key metrics
ax1 = fig.add_subplot(gs[0, 0])
ax1.text(0.5, 0.7, f"{aggregate['avg_relevancy']:.2f}/5", 
         ha='center', va='center', fontsize=36, fontweight='bold', color='#2ecc71')
ax1.text(0.5, 0.3, 'Answer Relevancy', ha='center', va='center', fontsize=14)
ax1.axis('off')

ax2 = fig.add_subplot(gs[0, 1])
ax2.text(0.5, 0.7, f"{aggregate['avg_faithfulness']:.0%}", 
         ha='center', va='center', fontsize=36, fontweight='bold', color='#3498db')
ax2.text(0.5, 0.3, 'Faithfulness', ha='center', va='center', fontsize=14)
ax2.axis('off')

ax3 = fig.add_subplot(gs[0, 2])
ax3.text(0.5, 0.7, f"{aggregate['avg_latency_ms']:.0f}ms", 
         ha='center', va='center', fontsize=36, fontweight='bold', color='#e67e22')
ax3.text(0.5, 0.3, 'Avg Latency', ha='center', va='center', fontsize=14)
ax3.axis('off')

# Middle row - Distributions
ax4 = fig.add_subplot(gs[1, :])
metrics_comparison = {
    'Relevancy\n(scaled)': aggregate['avg_relevancy'] / 5,
    'Faithfulness': aggregate['avg_faithfulness'],
    'Precision': aggregate['avg_precision'],
    'Overall': aggregate['avg_overall_score']
}
colors = ['#2ecc71', '#3498db', '#9b59b6', '#e74c3c']
bars = ax4.bar(metrics_comparison.keys(), metrics_comparison.values(), color=colors, alpha=0.8)
for bar in bars:
    height = bar.get_height()
    ax4.text(bar.get_x() + bar.get_width()/2., height,
            f'{height:.1%}', ha='center', va='bottom', fontsize=12, fontweight='bold')
ax4.set_ylim(0, 1.1)
ax4.set_ylabel('Score', fontsize=12)
ax4.set_title('Quality Metrics Comparison', fontsize=14, fontweight='bold')
ax4.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.0%}'))

# Bottom row - Stats
ax5 = fig.add_subplot(gs[2, 0])
stats_text = f"""Total Questions: {aggregate['total_questions']}
Avg Tokens: {aggregate['avg_tokens_per_query']:.0f}
Total Cost: ${aggregate['total_tokens'] * 0.00000025:.3f}"""
ax5.text(0.1, 0.5, stats_text, ha='left', va='center', fontsize=13, family='monospace')
ax5.set_title('Cost Metrics', fontsize=12, fontweight='bold', pad=10)
ax5.axis('off')

ax6 = fig.add_subplot(gs[2, 1])
perf_text = f"""P50: {aggregate['avg_latency_ms']:.0f}ms
P95: {aggregate['p95_latency_ms']:.0f}ms
P99: {aggregate['p99_latency_ms']:.0f}ms"""
ax6.text(0.1, 0.5, perf_text, ha='left', va='center', fontsize=13, family='monospace')
ax6.set_title('Latency Percentiles', fontsize=12, fontweight='bold', pad=10)
ax6.axis('off')

ax7 = fig.add_subplot(gs[2, 2])
system_text = f"""Model: Claude Haiku
Chunks: 7,712
Embed Dim: 384
Search: Hybrid"""
ax7.text(0.1, 0.5, system_text, ha='left', va='center', fontsize=13, family='monospace')
ax7.set_title('System Config', fontsize=12, fontweight='bold', pad=10)
ax7.axis('off')

plt.savefig(output_dir / '5_dashboard.png', dpi=300, bbox_inches='tight')
plt.close()

print("\n✅ All charts created!")
print(f"📁 Saved to: {output_dir}")
print("\nGenerated charts:")
print("  1. Quality Metrics")
print("  2. Performance Metrics")
print("  3. Distributions")
print("  4. Category Analysis")
print("  5. Summary Dashboard")