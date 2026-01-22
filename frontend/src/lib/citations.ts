/**
 * Citation utilities for KnowBook.
 *
 * Handles parsing and formatting of citations in AI responses.
 * Citation format: [[cite:CHUNK_ID]]
 * Chunk ID format: {source_id}_page_{N}_chunk_{M}
 */

// Regex pattern for citations
const CITATION_PATTERN = /\[\[cite:([a-zA-Z0-9_-]+_page_\d+_chunk_\d+)\]\]/g;

/**
 * Parse citation markers from text and assign sequential numbers.
 *
 * @param text - Text containing [[cite:chunk_id]] markers
 * @returns Object with unique citations and marker-to-number mapping
 */
export function parseCitations(text: string): {
  uniqueCitations: string[];
  markerToNumber: Map<string, number>;
} {
  if (!text) {
    return { uniqueCitations: [], markerToNumber: new Map() };
  }

  const uniqueCitations: string[] = [];
  const markerToNumber = new Map<string, number>();
  const seen = new Set<string>();

  // Find all citation matches
  let match;
  const regex = new RegExp(CITATION_PATTERN.source, 'g');

  while ((match = regex.exec(text)) !== null) {
    const fullMarker = match[0]; // [[cite:chunk_id]]
    const chunkId = match[1]; // chunk_id

    if (!seen.has(chunkId)) {
      seen.add(chunkId);
      uniqueCitations.push(chunkId);
      markerToNumber.set(fullMarker, uniqueCitations.length);
    } else {
      // Set the same number for duplicate markers
      const existingNumber = uniqueCitations.indexOf(chunkId) + 1;
      markerToNumber.set(fullMarker, existingNumber);
    }
  }

  return { uniqueCitations, markerToNumber };
}

/**
 * Split text into alternating text and citation segments.
 *
 * @param text - Text containing [[cite:chunk_id]] markers
 * @returns Array of segments with type and content
 */
export function splitTextWithCitations(
  text: string
): Array<{ type: 'text' | 'citation'; content: string }> {
  if (!text) {
    return [];
  }

  const segments: Array<{ type: 'text' | 'citation'; content: string }> = [];
  const regex = new RegExp(CITATION_PATTERN.source, 'g');

  let lastIndex = 0;
  let match;

  while ((match = regex.exec(text)) !== null) {
    // Add text before citation
    if (match.index > lastIndex) {
      segments.push({
        type: 'text',
        content: text.slice(lastIndex, match.index),
      });
    }

    // Add citation
    segments.push({
      type: 'citation',
      content: match[1], // chunk_id
    });

    lastIndex = regex.lastIndex;
  }

  // Add remaining text
  if (lastIndex < text.length) {
    segments.push({
      type: 'text',
      content: text.slice(lastIndex),
    });
  }

  return segments;
}

/**
 * Check if text contains any citations.
 *
 * @param text - Text to check
 * @returns True if text contains citations
 */
export function hasCitations(text: string): boolean {
  if (!text) return false;
  return new RegExp(CITATION_PATTERN.source).test(text);
}

/**
 * Remove all citation markers from text.
 *
 * @param text - Text containing [[cite:chunk_id]] markers
 * @returns Clean text without citations
 */
export function stripCitations(text: string): string {
  if (!text) return '';
  return text.replace(new RegExp(CITATION_PATTERN.source, 'g'), '');
}

/**
 * Parse a chunk ID into its components.
 *
 * @param chunkId - Format: {source_id}_page_{N}_chunk_{M}
 * @returns Object with source_id, page_number, chunk_index or null
 */
export function parseChunkId(chunkId: string): {
  sourceId: string;
  pageNumber: number;
  chunkIndex: number;
} | null {
  const match = chunkId.match(/^(.+)_page_(\d+)_chunk_(\d+)$/);
  if (!match) return null;

  return {
    sourceId: match[1],
    pageNumber: parseInt(match[2], 10),
    chunkIndex: parseInt(match[3], 10),
  };
}
