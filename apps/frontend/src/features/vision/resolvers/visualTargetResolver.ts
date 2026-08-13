import { VisionTarget } from '../types/visionTarget';

export class VisualTargetResolver {
  private minConfidenceThreshold = 0.8;

  resolveTargetFromObservation(targetDescription: string, targets: VisionTarget[]): VisionTarget | null {
    if (!targetDescription || !targets || targets.length === 0) return null;
    const clean = targetDescription.trim().toLowerCase();

    for (const target of targets) {
      if (target.confidence < this.minConfidenceThreshold) continue;

      const labelMatch = target.label.toLowerCase().includes(clean);
      const textMatch = target.text ? target.text.toLowerCase().includes(clean) : false;
      const typeMatch = clean.includes(target.type.toLowerCase());

      if (labelMatch || textMatch || typeMatch) {
        return target;
      }
    }

    return null;
  }
}
