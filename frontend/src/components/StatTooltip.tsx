
import { Info } from "lucide-react";

interface StatTooltipProps {
  label: string;
  description: string;
}

export default function StatTooltip({
  label,
  description,
}: StatTooltipProps) {
  return (
    <span className="stat-tooltip">
      <span className="stat-tooltip-label">{label}</span>
      <span className="stat-tooltip-icon" tabIndex={0} aria-label={description}>
        <Info size={12} />
        <span className="stat-tooltip-popup" role="tooltip">
          {description}
        </span>
      </span>
    </span>
  );
}
