import { WorkflowDefinition, WorkflowNode, WorkflowEdge, WorkflowVariable, WorkflowVersion } from '../types/workflowStudio.js';

export class WorkflowBuilder {
  private workflow: WorkflowDefinition;

  constructor(name: string = 'Untitled Workflow', description: string = '') {
    this.workflow = {
      id: `wf-${Date.now()}-${Math.random().toString(36).substr(2, 4)}`,
      name,
      description,
      nodes: [],
      edges: [],
      variables: [],
      tags: [],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      version: 1,
      versionsHistory: [],
      trusted: true,
    };
  }

  static fromDefinition(def: WorkflowDefinition): WorkflowBuilder {
    const builder = new WorkflowBuilder(def.name, def.description);
    builder.workflow = JSON.parse(JSON.stringify(def));
    if (!builder.workflow.variables) builder.workflow.variables = [];
    if (!builder.workflow.versionsHistory) builder.workflow.versionsHistory = [];
    return builder;
  }

  addNode(node: Omit<WorkflowNode, 'id'>): WorkflowNode {
    const newNode: WorkflowNode = {
      ...node,
      id: `node-${Date.now()}-${Math.random().toString(36).substr(2, 4)}`,
    };
    this.workflow.nodes.push(newNode);
    this.workflow.updatedAt = new Date().toISOString();
    return newNode;
  }

  duplicateNode(nodeId: string): WorkflowNode | null {
    const original = this.workflow.nodes.find((n) => n.id === nodeId);
    if (!original) return null;

    const copy = this.addNode({
      ...JSON.parse(JSON.stringify(original)),
      label: `${original.label} (Copy)`,
      x: original.x + 30,
      y: original.y + 30,
    });

    return copy;
  }

  deleteNode(nodeId: string): boolean {
    const initialLen = this.workflow.nodes.length;
    this.workflow.nodes = this.workflow.nodes.filter((n) => n.id !== nodeId);
    this.workflow.edges = this.workflow.edges.filter((e) => e.sourceNodeId !== nodeId && e.targetNodeId !== nodeId);
    this.workflow.updatedAt = new Date().toISOString();
    return this.workflow.nodes.length < initialLen;
  }

  reorderNodes(nodeIdsInOrder: string[]): void {
    const newNodes: WorkflowNode[] = [];
    for (const id of nodeIdsInOrder) {
      const node = this.workflow.nodes.find((n) => n.id === id);
      if (node) newNodes.push(node);
    }
    this.workflow.nodes = newNodes;
    this.workflow.updatedAt = new Date().toISOString();
  }

  addEdge(sourceNodeId: string, targetNodeId: string, condition?: string): WorkflowEdge | null {
    const sourceExists = this.workflow.nodes.some((n) => n.id === sourceNodeId);
    const targetExists = this.workflow.nodes.some((n) => n.id === targetNodeId);

    if (!sourceExists || !targetExists) return null;

    const edge: WorkflowEdge = {
      id: `edge-${sourceNodeId}-${targetNodeId}`,
      sourceNodeId,
      targetNodeId,
      condition,
    };

    this.workflow.edges.push(edge);
    this.workflow.updatedAt = new Date().toISOString();
    return edge;
  }

  addVariable(variable: WorkflowVariable): void {
    const idx = this.workflow.variables.findIndex((v) => v.name === variable.name);
    if (idx >= 0) {
      this.workflow.variables[idx] = variable;
    } else {
      this.workflow.variables.push(variable);
    }
    this.workflow.updatedAt = new Date().toISOString();
  }

  removeVariable(variableName: string): boolean {
    const initialLen = this.workflow.variables.length;
    this.workflow.variables = this.workflow.variables.filter((v) => v.name !== variableName);
    this.workflow.updatedAt = new Date().toISOString();
    return this.workflow.variables.length < initialLen;
  }

  assignAgentRole(nodeId: string, role: string): boolean {
    const node = this.workflow.nodes.find((n) => n.id === nodeId);
    if (!node) return false;

    node.assignedAgentRole = role;
    this.workflow.updatedAt = new Date().toISOString();
    return true;
  }

  createNewVersion(changeSummary: string = 'Updated workflow definition'): number {
    const snapshot: WorkflowVersion = {
      versionNumber: this.workflow.version,
      createdAt: new Date().toISOString(),
      author: 'LocalOperator',
      changeSummary,
      nodes: JSON.parse(JSON.stringify(this.workflow.nodes)),
      edges: JSON.parse(JSON.stringify(this.workflow.edges)),
      variables: JSON.parse(JSON.stringify(this.workflow.variables)),
    };

    this.workflow.versionsHistory.push(snapshot);
    this.workflow.version += 1;
    this.workflow.updatedAt = new Date().toISOString();
    return this.workflow.version;
  }

  rollbackToVersion(versionNumber: number): boolean {
    const targetVer = this.workflow.versionsHistory.find((v) => v.versionNumber === versionNumber);
    if (!targetVer) return false;

    this.workflow.nodes = JSON.parse(JSON.stringify(targetVer.nodes));
    this.workflow.edges = JSON.parse(JSON.stringify(targetVer.edges));
    this.workflow.variables = JSON.parse(JSON.stringify(targetVer.variables));
    this.workflow.updatedAt = new Date().toISOString();
    return true;
  }

  validateWorkflow(): { valid: boolean; errors: string[] } {
    const errors: string[] = [];

    if (this.workflow.nodes.length === 0) {
      errors.push('Workflow must contain at least one node.');
    }

    const hasTrigger = this.workflow.nodes.some((n) => n.type === 'TRIGGER');
    if (!hasTrigger) {
      errors.push('Workflow must contain a TRIGGER node.');
    }

    const nodeIds = new Set(this.workflow.nodes.map((n) => n.id));
    for (const edge of this.workflow.edges) {
      if (!nodeIds.has(edge.sourceNodeId)) {
        errors.push(`Edge refers to missing source node: ${edge.sourceNodeId}`);
      }
      if (!nodeIds.has(edge.targetNodeId)) {
        errors.push(`Edge refers to missing target node: ${edge.targetNodeId}`);
      }
    }

    return {
      valid: errors.length === 0,
      errors,
    };
  }

  getTopologicalOrder(): WorkflowNode[] {
    const inDegree: Map<string, number> = new Map();
    const adj: Map<string, string[]> = new Map();

    for (const node of this.workflow.nodes) {
      inDegree.set(node.id, 0);
      adj.set(node.id, []);
    }

    for (const edge of this.workflow.edges) {
      inDegree.set(edge.targetNodeId, (inDegree.get(edge.targetNodeId) || 0) + 1);
      adj.get(edge.sourceNodeId)?.push(edge.targetNodeId);
    }

    const queue: string[] = [];
    for (const [id, deg] of inDegree.entries()) {
      if (deg === 0) queue.push(id);
    }

    const order: WorkflowNode[] = [];
    while (queue.length > 0) {
      const u = queue.shift()!;
      const node = this.workflow.nodes.find((n) => n.id === u);
      if (node) order.push(node);

      for (const v of adj.get(u) || []) {
        inDegree.set(v, (inDegree.get(v) || 0) - 1);
        if (inDegree.get(v) === 0) {
          queue.push(v);
        }
      }
    }

    return order.length === this.workflow.nodes.length ? order : this.workflow.nodes;
  }

  getWorkflow(): WorkflowDefinition {
    return { ...this.workflow };
  }
}
