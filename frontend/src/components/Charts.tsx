// Minimal dependency-free SVG charts (keeps the frontend dependency set small).

interface Point {
  label: string;
  value: number;
}

export function LineChart({
  points,
  height = 180,
  width = 640,
}: {
  points: Point[];
  height?: number;
  width?: number;
}) {
  if (points.length === 0) return <p className="muted">No data.</p>;
  const pad = 28;
  const values = points.map((p) => p.value);
  const min = Math.min(...values);
  const max = Math.max(...values);
  const span = max - min || 1;
  const stepX = (width - pad * 2) / Math.max(points.length - 1, 1);

  const coords = points.map((p, i) => {
    const x = pad + i * stepX;
    const y = height - pad - ((p.value - min) / span) * (height - pad * 2);
    return { x, y };
  });
  const path = coords
    .map((c, i) => `${i === 0 ? "M" : "L"} ${c.x.toFixed(1)} ${c.y.toFixed(1)}`)
    .join(" ");

  return (
    <svg className="chart" viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Line chart">
      <path d={path} className="chart__line" fill="none" />
      {coords.map((c, i) => (
        <circle key={i} cx={c.x} cy={c.y} r={2.5} className="chart__dot" />
      ))}
    </svg>
  );
}

export function BarChart({
  items,
  height = 220,
  width = 640,
}: {
  items: { label: string; value: number; highlight?: boolean }[];
  height?: number;
  width?: number;
}) {
  if (items.length === 0) return <p className="muted">No data.</p>;
  const pad = 28;
  const max = Math.max(...items.map((i) => i.value)) || 1;
  const barW = (width - pad * 2) / items.length;

  return (
    <svg className="chart" viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Bar chart">
      {items.map((it, i) => {
        const h = ((it.value / max) * (height - pad * 2)) | 0;
        const x = pad + i * barW + barW * 0.15;
        const y = height - pad - h;
        return (
          <g key={it.label}>
            <rect
              x={x}
              y={y}
              width={barW * 0.7}
              height={h}
              className={it.highlight ? "chart__bar chart__bar--hl" : "chart__bar"}
            />
            <text x={x + barW * 0.35} y={height - pad + 12} className="chart__label">
              {it.label}
            </text>
          </g>
        );
      })}
    </svg>
  );
}
