export class SpecialFolderResolver {
  private baseHome: string = 'C:/Users/DefaultUser';
  private projectRoot: string = 'C:/Projects/Nova-AI';

  setBaseHome(homePath: string) {
    this.baseHome = homePath.replace(/\\/g, '/');
  }

  setProjectRoot(projectPath: string) {
    this.projectRoot = projectPath.replace(/\\/g, '/');
  }

  resolveSpecialFolder(input: string): string | null {
    if (!input) return null;
    const clean = input.trim().toLowerCase();

    if (clean.includes('desktop')) return `${this.baseHome}/Desktop`;
    if (clean.includes('documents') || clean.includes('docs')) return `${this.baseHome}/Documents`;
    if (clean.includes('downloads')) return `${this.baseHome}/Downloads`;
    if (clean.includes('pictures') || clean.includes('images')) return `${this.baseHome}/Pictures`;
    if (clean.includes('videos')) return `${this.baseHome}/Videos`;
    if (clean.includes('music')) return `${this.baseHome}/Music`;
    if (clean === 'home' || clean === 'user profile') return this.baseHome;
    if (clean.includes('project') || clean.includes('workspace') || clean.includes('repo')) return this.projectRoot;
    if (clean.includes('frontend')) return `${this.projectRoot}/apps/frontend`;
    if (clean.includes('backend')) return `${this.projectRoot}/apps/backend`;

    return null;
  }
}
