export class ImageTargetResolver {
  resolveImageSource(filePathOrUrl: string) {
    const isPdf = filePathOrUrl.toLowerCase().endsWith('.pdf');
    return {
      type: isPdf ? ('PDF' as const) : ('IMAGE' as const),
      sourceId: filePathOrUrl,
      name: filePathOrUrl.split('/').pop() || 'Image Asset',
      permission: 'GRANTED' as const,
    };
  }
}
