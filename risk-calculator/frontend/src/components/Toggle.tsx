type Props = {
  on: boolean;
  onChange: (next: boolean) => void;
  label: string;
};

export default function Toggle({ on, onChange, label }: Props) {
  return (
    <label className="inline-flex items-center gap-2 cursor-pointer select-none">
      <span className="text-xs font-semibold text-ink">{label}</span>
      <button
        type="button"
        role="switch"
        aria-checked={on}
        onClick={() => onChange(!on)}
        className={
          "relative w-10 h-5 rounded-full border border-ink transition-colors " +
          (on ? "bg-input-blue" : "bg-button-grey")
        }
      >
        <span
          className={
            "absolute top-0.5 w-3.5 h-3.5 rounded-full bg-canvas border border-ink transition-all " +
            (on ? "left-[22px]" : "left-0.5")
          }
        />
      </button>
    </label>
  );
}
