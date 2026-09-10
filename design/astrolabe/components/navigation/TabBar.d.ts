/** Six tabs: Home · Sky · Chart · Letters · Practice · Settings.
 * At 360px that is 60px each, so the icon carries the weight — but the label
 * always stays: an unlabelled icon row is a memory test. Selection is a filled
 * icon AND a gilt hem AND full-ink label; never colour alone.
 */
export interface TabBarProps {
  tabs?: { id: string; label: string; icon: string }[];
  active?: string;
  /** Unread dots, keyed by tab id: { practice: 3 } */
  badges?: Record<string, number>;
  onChange?: (id: string) => void;
}
export declare function TabBar(props: TabBarProps): JSX.Element;
export declare const TABS: { id: string; label: string; icon: string }[];
