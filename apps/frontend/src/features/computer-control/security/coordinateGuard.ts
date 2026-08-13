export interface CoordinateBounds {
  minX: number;
  maxX: number;
  minY: number;
  maxY: number;
}

export class CoordinateGuard {
  private bounds: CoordinateBounds = {
    minX: 0,
    maxX: 3840,
    minY: 0,
    maxY: 2160,
  };

  validateCoordinates(x?: number, y?: number): { valid: boolean; reason?: string } {
    if (x === undefined || y === undefined) {
      return { valid: false, reason: 'Coordinates x and y must be specified.' };
    }

    if (isNaN(x) || isNaN(y)) {
      return { valid: false, reason: 'Malformed numeric coordinate payload.' };
    }

    if (x < this.bounds.minX || x > this.bounds.maxX) {
      return { valid: false, reason: `X coordinate (${x}) is outside screen bounds [0, ${this.bounds.maxX}].` };
    }

    if (y < this.bounds.minY || y > this.bounds.maxY) {
      return { valid: false, reason: `Y coordinate (${y}) is outside screen bounds [0, ${this.bounds.maxY}].` };
    }

    return { valid: true };
  }
}
