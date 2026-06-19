import React from "react";

export interface CardProps {
  children?: React.ReactNode;
  /** Uppercase eyebrow title in the header row */
  title?: string;
  subtitle?: string;
  /** Right-aligned header slot (button, link, badge) */
  action?: React.ReactNode;
  /** Material Symbols glyph beside the title */
  icon?: string;
  /** @default "default" */
  variant?: "default" | "low" | "glass";
  /** Inner padding in px. @default 24 */
  padding?: number;
  /** Lift + brighten border on hover */
  hover?: boolean;
  style?: React.CSSProperties;
}

/**
 * Base surface container — hairline border, no shadow (borders over shadows).
 * @startingPoint section="Display" subtitle="Cards, stat tiles & panels" viewport="700x260"
 */
export function Card(props: CardProps): JSX.Element;
