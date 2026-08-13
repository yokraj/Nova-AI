import { VisionObservation } from '../types/visionObservation';

export class ImageProvider {
  async extractTextFromImage(imagePathOrBase64: string): Promise<{ text: string; confidence: number }> {
    return {
      text: 'Extracted text content from visual document/image asset.',
      confidence: 0.96,
    };
  }

  async analyzePdfDocument(pdfPath: string): Promise<VisionObservation> {
    return {
      id: `pdf-obs-${Date.now()}`,
      source: { type: 'PDF', sourceId: pdfPath, permission: 'GRANTED' },
      timestamp: new Date().toISOString(),
      width: 1920,
      height: 1080,
      textExtracted: 'PDF Invoice & Contract document text.',
      detectedTargets: [
        { id: 't-pdf-1', type: 'TEXT', label: 'Invoice Subtotal', confidence: 0.98, actionable: false },
        { id: 't-pdf-2', type: 'BUTTON', label: 'Download PDF', confidence: 0.95, actionable: true },
      ],
      confidenceScore: 0.97,
      containsSensitiveData: false,
    };
  }
}
