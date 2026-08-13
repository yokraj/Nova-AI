import { ResponseBlock } from '../types/message';

export interface StreamUpdatePayload {
  thinkingStage?: string;
  streamingContent?: string;
  isComplete?: boolean;
  blocks?: ResponseBlock[];
}

export function generateNovaMockResponseBlocks(prompt: string): ResponseBlock[] {
  const lower = prompt.toLowerCase().trim();

  if (lower.includes('quantum')) {
    return [
      {
        id: 'b-01',
        type: 'text',
        content:
          'Quantum computing fundamentally alters computational physics by manipulating quantum mechanics phenomena such as superposition and entanglement.',
      },
      {
        id: 'b-02',
        type: 'markdown',
        content:
          '### Superposition & Entanglement Breakdown\n\nUnlike classical binary transistors bound strictly to `0` or `1`, quantum bits (qubits) exist in continuous Hilbert state spaces described by state vectors $|\\psi\\rangle = \\alpha|0\\rangle + \\beta|1\\rangle$.',
      },
      {
        id: 'b-03',
        type: 'code',
        codeData: {
          language: 'python',
          filename: 'quantum_bell_state.py',
          code: 'from qiskit import QuantumCircuit\n\n# Bell state creation\nqc = QuantumCircuit(2)\nqc.h(0)\nqc.cx(0, 1)\nqc.measure_all()\nprint("Quantum Circuit Initialized.")',
        },
      },
      {
        id: 'b-04',
        type: 'table',
        tableData: {
          headers: ['Metric', 'Classical Bit', 'Quantum Qubit'],
          rows: [
            ['State Representation', 'Discrete 0 or 1', 'Superposition |ψ⟩'],
            ['Information Density', '1 bit per cell', '2^N complex amplitudes'],
            ['Primary Gate Operations', 'AND, OR, NOT, XOR', 'Hadamard, CNOT, Pauli-X/Y/Z'],
          ],
        },
      },
      {
        id: 'b-05',
        type: 'citation',
        citationsData: [
          {
            id: 'cit-01',
            title: 'Quantum Computation & Information Fundamentals',
            source: 'Cambridge Physics Press',
            snippet: 'Exhaustive reference manual on qubit decoherence and gate synthesis.',
          },
          {
            id: 'cit-02',
            title: 'Fault-Tolerant Quantum Architecture',
            source: 'Physical Review Letters',
            snippet: 'Surface code error correction protocols for fault-tolerant quantum chips.',
          },
        ],
      },
    ];
  }

  if (lower.includes('sort') || lower.includes('python') || lower.includes('program')) {
    return [
      {
        id: 'b-06',
        type: 'text',
        content: 'Here is an optimized Python QuickSort algorithm with random pivot selection and timing benchmarks.',
      },
      {
        id: 'b-07',
        type: 'code',
        codeData: {
          language: 'python',
          filename: 'quicksort_benchmark.py',
          code: `import random
import time

def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = random.choice(arr)
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)

# Benchmark execution
if __name__ == "__main__":
    sample = [random.randint(1, 100000) for _ in range(25000)]
    start = time.perf_counter()
    result = quicksort(sample)
    print(f"Successfully sorted {len(result)} items in {time.perf_counter() - start:.4f}s")`,
        },
      },
    ];
  }

  if (lower.includes('analyze') || lower.includes('project') || lower.includes('report')) {
    return [
      {
        id: 'b-08',
        type: 'text',
        content: 'Initiating full Nova monorepo architecture analysis across backend microservices and frontend design tokens.',
      },
      {
        id: 'b-09',
        type: 'agent_activity',
        agentData: {
          agentName: 'Solution Architect Agent',
          agentAvatar: 'SA',
          division: 'Engineering Division',
          status: 'running',
          task: 'Parsing FastAPI routes & Pydantic V2 schemas',
          progress: 82,
        },
      },
      {
        id: 'b-10',
        type: 'mission',
        missionData: {
          missionId: 'msn_monorepo_audit_01',
          title: 'Full Repository Architecture & Code Coverage Audit',
          category: 'SOFTWARE ENGINEERING',
          status: 'running',
          subtasksCompleted: 4,
          subtasksTotal: 5,
          progress: 80,
        },
      },
      {
        id: 'b-11',
        type: 'markdown',
        content: '### Codebase Audit Summary\n\n- **Backend**: 13 Specialized Divisions compiled, 6/6 test modules passing cleanly.\n- **Frontend**: Universal Command Center & Nova Core identity unified with 0 backend dependencies.\n- **Security**: Strict zero-trust permission barriers active.',
      },
    ];
  }

  if (lower.includes('light') || lower.includes('turn on') || lower.includes('device')) {
    return [
      {
        id: 'b-12',
        type: 'text',
        content: 'Requesting permission to invoke external IoT Hardware Device Control API.',
      },
      {
        id: 'b-13',
        type: 'approval',
        approvalData: {
          id: 'app-01',
          title: 'Control Smart Lighting Node (192.168.1.250)',
          actionType: 'Device Control Permission',
          riskLevel: 'MEDIUM',
          status: 'pending',
        },
      },
    ];
  }

  // Default response
  return [
    {
      id: 'b-default',
      type: 'text',
      content: `I have processed your request regarding "${prompt}". Nova's multi-agent runtime is ready to assist across reasoning, code, research, and operating system orchestration.`,
    },
    {
      id: 'b-default-2',
      type: 'markdown',
      content: '### Capability Overview\n\n- **Universal Intelligence**: Local LLM reasoning via Ollama (Qwen 3 8B)\n- **Memory & Knowledge**: Semantic vector store & ontological entity graph\n- **Device Mesh**: Trusted cross-platform desktop & phone orchestration',
    },
  ];
}

export function simulateStreamingResponse(
  prompt: string,
  onUpdate: (payload: StreamUpdatePayload) => void
) {
  const blocks = generateNovaMockResponseBlocks(prompt);

  // Stage 1: Understanding
  onUpdate({ thinkingStage: 'UNDERSTANDING', streamingContent: 'Understanding request intent...' });

  // Stage 2: Reasoning
  setTimeout(() => {
    onUpdate({ thinkingStage: 'REASONING', streamingContent: 'Reasoning across knowledge graph & memory...' });
  }, 600);

  // Stage 3: Planning
  setTimeout(() => {
    onUpdate({ thinkingStage: 'PLANNING', streamingContent: 'Preparing structured response blocks...' });
  }, 1200);

  // Stage 4: Streaming Blocks
  setTimeout(() => {
    onUpdate({
      thinkingStage: undefined,
      blocks,
      isComplete: true,
    });
  }, 1800);
}
