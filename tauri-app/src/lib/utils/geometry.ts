export function buildPolylinePoints(
  x1: number,
  y1: number,
  x2: number,
  y2: number,
  waypoints?: [number, number][]
): [number, number][] {
  const points: [number, number][] = [[x1, y1]];
  if (waypoints) {
    for (const wp of waypoints) {
      points.push(wp);
    }
  }
  points.push([x2, y2]);
  return points;
}

export function interpolatePolyline(
  points: [number, number][],
  t: number
): { x: number; y: number } {
  if (points.length === 0) return { x: 0, y: 0 };
  if (points.length === 1) return { x: points[0][0], y: points[0][1] };

  // Calculate total length
  let totalLength = 0;
  const segLengths: number[] = [];
  for (let i = 1; i < points.length; i++) {
    const dx = points[i][0] - points[i - 1][0];
    const dy = points[i][1] - points[i - 1][1];
    const len = Math.sqrt(dx * dx + dy * dy);
    segLengths.push(len);
    totalLength += len;
  }

  if (totalLength === 0) return { x: points[0][0], y: points[0][1] };

  const targetLen = t * totalLength;
  let accumulated = 0;
  for (let i = 0; i < segLengths.length; i++) {
    if (accumulated + segLengths[i] >= targetLen) {
      const segT =
        segLengths[i] === 0 ? 0 : (targetLen - accumulated) / segLengths[i];
      return {
        x: points[i][0] + (points[i + 1][0] - points[i][0]) * segT,
        y: points[i][1] + (points[i + 1][1] - points[i][1]) * segT,
      };
    }
    accumulated += segLengths[i];
  }

  const last = points[points.length - 1];
  return { x: last[0], y: last[1] };
}

export function findInsertIndex(
  x: number,
  y: number,
  polyPoints: [number, number][]
): number {
  if (polyPoints.length < 2) return 0;

  let bestIdx = 0;
  let bestDist = Infinity;

  for (let i = 0; i < polyPoints.length - 1; i++) {
    const dist = pointToSegmentDist(
      x,
      y,
      polyPoints[i][0],
      polyPoints[i][1],
      polyPoints[i + 1][0],
      polyPoints[i + 1][1]
    );
    if (dist < bestDist) {
      bestDist = dist;
      bestIdx = i;
    }
  }

  return bestIdx;
}

function pointToSegmentDist(
  px: number,
  py: number,
  x1: number,
  y1: number,
  x2: number,
  y2: number
): number {
  const dx = x2 - x1;
  const dy = y2 - y1;
  const lenSq = dx * dx + dy * dy;
  if (lenSq === 0) {
    const ddx = px - x1;
    const ddy = py - y1;
    return Math.sqrt(ddx * ddx + ddy * ddy);
  }
  let t = ((px - x1) * dx + (py - y1) * dy) / lenSq;
  t = Math.max(0, Math.min(1, t));
  const projX = x1 + t * dx;
  const projY = y1 + t * dy;
  const ddx = px - projX;
  const ddy = py - projY;
  return Math.sqrt(ddx * ddx + ddy * ddy);
}
