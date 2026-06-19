import React from "react";

export type BadgeTone = "primary" | "success" | "danger" | "warning" | "neutral";

export interface BadgeProps {
  children?: React.ReactNode;
  /** @default "neutral" */
  tone?: BadgeTone;
  /** @default "soft" */
  variant?: "soft" | "solid";
  /** Leading status dot */
  dot?: boolean;
  /** Material Symbols glyph name */
  icon?: string;
  style?: React.CSSProperties;
}

/**
 * Status pill for states like Active / Overdue / At-Risk.
 * @startingPoint section="Display" subtitle="Badges, tags & status dots" viewport="700x150"
 */
export function Badge(props: BadgeProps): JSX.Element;
