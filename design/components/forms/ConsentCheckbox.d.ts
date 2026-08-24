/** One consent decision, designed as a decision.
 * Always starts unticked, always carries its own explanation, and is never bundled with
 * another consent. `basis` labels the lawful basis so the design shows that these are
 * different kinds of agreement — contract vs consent vs marketing consent. */
export interface ConsentCheckboxProps {
  /** The decision, in plain words and the first person */
  label: React.ReactNode;
  /** What is stored and why — required for explicit-consent items */
  explanation?: React.ReactNode;
  /** Shown as a mono eyebrow, e.g. 'explicit consent · GDPR Art. 9' */
  basis?: string;
  /** Required consents are the contract ones only; special-category consent is never required */
  required?: boolean;
  /** Error line, shown when a required consent is unticked on submit */
  error?: React.ReactNode;
  checked?: boolean;
  onChange?: (e: any) => void;
  name?: string;
  /** Withdrawal note for the settings screen, e.g. 'Given 12 Aug 2026 · withdraw any time' */
  meta?: string;
}
