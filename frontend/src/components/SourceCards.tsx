import type { Source } from "../types";

interface SourceCardsProps {
  sources: Source[];
}

export function SourceCards({ sources }: SourceCardsProps) {
  return (
    <div className="source-cards">
      <div className="source-cards-title">Sources</div>
      <div className="source-cards-grid">
        {sources.map((source) => (
          <article key={source.id} className="source-card">
            <div className="source-card-header">
              <span className="source-reference">
                Chapter {source.chapter ?? "?"}, Verse {source.verse_number ?? "?"}
              </span>
              <span className="source-score">{source.score.toFixed(2)}</span>
            </div>
            <p className="source-preview">{source.preview}</p>
          </article>
        ))}
      </div>
    </div>
  );
}
