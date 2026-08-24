/** Dialog / lightbox on a blurred veil. Esc and backdrop close. */
export interface ModalProps {
  open: boolean;
  onClose: () => void;
  title?: React.ReactNode;
  children: React.ReactNode;
  /** Action row, e.g. Buttons */
  footer?: React.ReactNode;
  /** 'lightbox' = chromeless dark surface for fan art */
  variant?: 'panel' | 'lightbox';
  labelledBy?: string;
}
