import { Skill } from '../types/skill';

export interface SkillMatchResult {
  skill: Skill;
  confidenceScore: number; // 0 to 100
  matchedPattern: string;
  extractedVariables: Record<string, string>;
  reason: string;
}

export class SkillMatcher {
  matchSkill(query: string, availableSkills: Skill[]): SkillMatchResult[] {
    const activeSkills = availableSkills.filter((s) => s.status === 'active');
    const results: SkillMatchResult[] = [];

    const cleanQuery = query.toLowerCase().trim();

    for (const skill of activeSkills) {
      let highestPatternScore = 0;
      let matchedPatternStr = '';
      const extractedVars: Record<string, string> = {};

      for (const trigger of skill.triggerPatterns) {
        const pattern = trigger.naturalLanguagePattern.toLowerCase();
        const score = this.calculatePatternSimilarity(cleanQuery, pattern, skill, extractedVars);

        if (score > highestPatternScore) {
          highestPatternScore = score;
          matchedPatternStr = trigger.naturalLanguagePattern;
        }
      }

      // Check name / description matches if trigger pattern score is moderate
      if (highestPatternScore < 50) {
        if (cleanQuery.includes(skill.name.toLowerCase())) {
          highestPatternScore = Math.max(highestPatternScore, 70);
          matchedPatternStr = skill.name;
        }
      }

      // Weight by historical success rate and recency
      const successWeight = skill.successRate * 10; // Up to 10 points
      const finalScore = Math.min(100, Math.round(highestPatternScore + successWeight));

      if (finalScore >= 50) {
        results.push({
          skill,
          confidenceScore: finalScore,
          matchedPattern: matchedPatternStr || skill.name,
          extractedVariables: extractedVars,
          reason: `Matched pattern "${matchedPatternStr}" with confidence score ${finalScore}%.`,
        });
      }
    }

    // Sort descending by confidence score
    return results.sort((a, b) => b.confidenceScore - a.confidenceScore);
  }

  private calculatePatternSimilarity(
    userQuery: string,
    pattern: string,
    skill: Skill,
    extractedVarsOut: Record<string, string>
  ): number {
    // 1. Exact match
    if (userQuery === pattern) return 95;

    // 2. Contains match
    if (userQuery.includes(pattern) || pattern.includes(userQuery)) return 85;

    // 3. Keyword token matching
    const queryTokens = userQuery.split(/\s+/).filter((t) => t.length > 2);
    const patternTokens = pattern.split(/\s+/).filter((t) => t.length > 2);

    let matchCount = 0;
    for (const qt of queryTokens) {
      if (patternTokens.includes(qt)) {
        matchCount++;
      }
    }

    const tokenRatio = matchCount / Math.max(1, patternTokens.length);
    let score = Math.round(tokenRatio * 80);

    // 4. Try extracting variable bindings from user query
    // e.g. Pattern: "Create a React project called {{projectName}} on Desktop"
    // User query: "Use my Build My Project skill for SolarApp"
    for (const v of skill.variables) {
      const varKeyInQuery = new RegExp(`(?:for|called|named|with|project|app)\\s+([A-Za-z0-9_-]+)`, 'i');
      const match = userQuery.match(varKeyInQuery);
      if (match && match[1]) {
        extractedVarsOut[v.name] = match[1];
        score += 10;
      }
    }

    return Math.min(95, score);
  }
}
