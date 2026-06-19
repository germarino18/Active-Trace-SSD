import React from "react";

export interface AvatarProps {
  /** Image URL; falls back to initials when absent */
  src?: string;
  /** Full name — used for initials + alt */
  name?: string;
  size?: "xs" | "sm" | "md" | "lg";
  /** Violet 2px ring */
  ring?: boolean;
  /** Presence dot */
  status?: "online" | "busy" | "away" | "offline";
  alt?: string;
  style?: React.CSSProperties;
}

/** Circular avatar with initials fallback + optional presence dot. */
export function Avatar(props: AvatarProps): JSX.Element;
