import React from "react";

export interface EmptyStateProps {
  /** Material Symbols glyph (ignored when `code` is set) */
  icon?: string;
  title: string;
  message?: string;
  /** Big error code (e.g. "403", "404") shown instead of the icon */
  code?: string;
  /** Action slot (usually a Button) */
  action?: React.ReactNode;
  style?: React.CSSProperties;
}

/**
 * Centered placeholder for empty tables and 403/404 error screens.
 * @startingPoint section="Feedback" subtitle="Empty & error states" viewport="700x320"
 */
export function EmptyState(props: EmptyStateProps): JSX.Element;
