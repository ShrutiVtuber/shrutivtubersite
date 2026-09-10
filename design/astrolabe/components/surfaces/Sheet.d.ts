/** A bottom sheet: the place picker, the sunrise convention, a share row.
 * 28px top corners, a grab handle, a tappable scrim. It never covers the whole
 * screen — that is a full-screen Dialog, which is a different thing. */
export interface SheetProps {
  open?: boolean;
  title?: string;
  onClose?: () => void;
  /** Buttons pinned to the bottom, above the safe area. */
  actions?: React.ReactNode;
  children?: React.ReactNode;
  maxHeight?: string;
}
export declare function Sheet(props: SheetProps): JSX.Element;
