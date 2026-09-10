/** The top bar of a screen. Title in EB Garamond — the app talks in her voice
 * even in its chrome. The hem beneath takes the ruling hour's colour: the one
 * place the sky is allowed to tint the shell. */
export interface AppBarProps {
  title: string;
  subtitle?: string;
  /** Show a back arrow (a pushed screen). */
  back?: boolean;
  onBack?: () => void;
  /** IconButtons, right-aligned. */
  actions?: React.ReactNode;
  /** Tint the hem with the ruling planetary hour. Default true. */
  hour?: boolean;
  /** 72px bar with a 26px title — Practice and Settings roots. */
  large?: boolean;
  sticky?: boolean;
}
export declare function AppBar(props: AppBarProps): JSX.Element;
