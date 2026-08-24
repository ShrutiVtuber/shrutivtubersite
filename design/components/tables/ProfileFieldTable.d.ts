/** VTuber profile vocabulary as an almanac index — dotted leaders, serif values. */
export interface ProfileFieldTableProps {
  /** e.g. Birthday, Height, Debut, Fan name, Oshi mark, Stream tag, Fan-art tag */
  fields: Array<{ label: string; value: React.ReactNode }>;
  columns?: 1 | 2;
}
